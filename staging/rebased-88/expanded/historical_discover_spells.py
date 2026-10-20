"""Complete-pool Discover and physical deck-choice spell declarations."""
from engine.cards import UnsupportedCard
from .generation_cards import pool,discover,random_cards
from .selectors import has_school
from .pools import deck_choice_options
from .historical_saidan import add as add_stat
TOKEN_RULES={
 'MIS_305':('none',[discover(pool(card_type='MINION',minimum=8,classes='own_or_neutral'),destination='board',dormant_turns=2)]),
 'MIS_700':('none',[discover(pool(era='past',card_type='WEAPON',classes='PALADIN'),attack=1,health=1)]),
 'NX2_029':('none',[discover(pool(card_type='MINION',mechanic='TAUNT',classes='own_or_neutral'),follow='NX2_029')]),
 'TTN_317':('none',[discover(pool(card_type='SPELL',school='NATURE',classes='own_or_neutral'),follow='TTN_317')]),
 'RLK_917':('none',[discover(pool(card_type='MINION',tribe='DRAGON',classes='own_or_neutral')),('historical_discover_bronze',)]),
 'RLK_917t':('none',[]),
 'TOY_374':('none',[discover(pool(card_type='MINION',minimum=3,maximum=3,classes='own_or_neutral'),destination='board'),('historical_discover_repeat_empty',)]),
 'TOY_643':('none',[('historical_discover_blind_box',)]),
 'WW_818':('none',[discover(pool(card_type='MINION',minimum=2,maximum=2,classes='own_or_neutral'),destination='board',stats=(1,2))]),
 'ETC_083':('none',[('historical_discover_demonic',)]),
 'DEEP_026':('none',[('historical_discover_deck','pendant')]),
 'TTN_728':('none',[('historical_discover_deck','pit')]),
 'TTN_735':('none',[('historical_discover_deck','navigation')]),
 'RLK_817':('none',[('historical_discover_deck','quiver')]),
 'TOY_851':('none',[('historical_discover_deck','chest')]),
 'TTN_430':('none',[('historical_discover_deck','copy_one')]),
 'TTN_430t':('none',[('historical_discover_deck','copy_two')]),
}
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)
FOLLOW_RULES={cid:tuple(TOKEN_RULES[cid][1]) for cid in ('NX2_029','TTN_317')}
FILTERS={'pendant':(('type','eq','MINION'),),'pit':(('type','eq','MINION'),('tribe','eq','MECHANICAL')),
 'navigation':(('type','eq','SPELL'),),'quiver':(('type','eq','SPELL'),),'chest':(),
 'copy_one':(('type','eq','MINION'),),'copy_two':(('type','eq','MINION'),)}


def split(game,op,ctx):
 owner=ctx['owner'];name=op[0]
 if name=='historical_discover_bronze':return game._split_fixed_summon(('summon','RLK_917t',1),ctx) if game.players[owner].max_mana>=7 else (('batch30_noop',),())
 if name=='historical_discover_repeat_empty':
  if any(game._card_data(card)['type']=='MINION' for card in game.players[owner].deck):return ('batch30_noop',),()
  return game._split_fixed_summon(discover(pool(card_type='MINION',minimum=3,maximum=3,classes='own_or_neutral'),destination='board'),ctx)
 if name in ('historical_discover_blind_box','historical_discover_demonic'):
  if name=='historical_discover_blind_box' and not ctx.get('outcast'):return game._split_fixed_summon(random_cards(pool(card_type='MINION',tribe='DEMON'),2),ctx)
  mods=dict(attack=1,health=2) if name=='historical_discover_demonic' and ctx.get('finale') else {}
  operation=discover(pool(card_type='MINION',tribe='DEMON',classes='own_or_neutral'),**mods)
  first,tail=game._split_fixed_summon(operation,ctx)
  return first,tuple(tail)+(operation,)
 return None


def execute(game,op,ctx):
 if op[0]!='historical_discover_deck':return False
 owner=ctx['owner'];mode=op[1];p=game.players[owner]
 if game.pending_choice is not None:raise UnsupportedCard('Cannot overwrite deck Discover')
 indices=[i for i,card in enumerate(p.deck) if game._matches_filter(card,FILTERS[mode],zone_owner=owner)]
 cards=[p.deck[i] for i in indices]
 options=deck_choice_options(cards,game.cards,3,game.rng)
 for option in options:
  index=indices[option['index']];card=p.deck[index]
  option.update(index=index,uid=getattr(card,'uid',None))
 if options:
  game.pending_choice=dict(owner=owner,kind='historical_deck_spell',mode=mode,context=dict(ctx),options=options)
  game.phase='choice'
 return True


def resolve_choice(game,choice,selected):
 if choice['kind']!='historical_deck_spell':return False
 owner=choice['owner'];p=game.players[owner];mode=choice['mode'];uid=selected.get('uid')
 index=next((i for i,card in enumerate(p.deck) if getattr(card,'uid',None)==uid),None) if uid is not None else selected['index']
 if index is None or not 0<=index<len(p.deck) or game._card_data(p.deck[index])['id']!=selected['card_id']:return True
 original=p.deck[index]
 if mode in ('copy_one','copy_two'):
  for _ in range(2 if mode=='copy_two' else 1):
   card=game._copy_card(original,source_owner=owner);game._discovery_result=game._enter_hand(owner,card)
  return True
 cost=game._card_stat(original,'cost',owner)
 copy_chest=mode=='chest' and game._spell_damage(owner)>0
 card=game._take_deck_draw(owner,index,include_burned=True)
 if card is None:return True
 game._discovery_result=card
 if mode=='pendant':game._heal(game.hero_id(owner),cost,healer=owner,spell=choice['context'].get('spell',False))
 elif mode=='pit':add_stat(card,'attack_bonus',2);add_stat(card,'health_bonus',1)
 elif mode=='quiver' and has_school(game._card_data(card),'ARCANE'):card.spell_damage_bonus=getattr(card,'spell_damage_bonus',0)+1
 elif mode=='navigation' and has_school(game._card_data(card),'FROST'):
  targets=[m for m in game.players[1-owner].minions if m.health>0]
  if targets:game._freeze(game.rng.choice(targets).uid)
 elif copy_chest:game._enter_hand(owner,game._copy_card(card,source_owner=owner))
 return True
