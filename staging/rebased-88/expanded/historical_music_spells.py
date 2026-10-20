"""Complete seven-Movement Symphony, three Riffs and Forbidden Fruit branches."""
from engine.game import Card
from engine.cards import UnsupportedCard
from .pools import require_fixed_cards
from .historical_draw_batches import draw
from .historical_saidan import add as add_stat
MOVEMENTS=('ETC_085t','ETC_085t2','ETC_085t3','ETC_085t4','ETC_085t6','ETC_085t7','ETC_085t8')
RIFFS=('ETC_363','ETC_364','ETC_365')
TOKEN_RULES={
 'ETC_085':('none',[('historical_music_symphony',)]),
 'ETC_085t':('none',[('historical_music_envy',)]),
 'ETC_085t2':('none',[draw((('type','eq','MINION'),),'discount',(6,),'highest')]),
 'ETC_085t3':('none',[('area_damage','all_characters',6)]),
 'ETC_085t4':('none',[('historical_music_gluttony',)]),
 'ETC_085t6':('none',[('damage_enemy_hero',6)]),
 'ETC_085t7':('none',[('draw',6)]),
 'ETC_085t8':('none',[('summon','ETC_t8t',1)]),
 'ETC_t8t':('none',[]),
 'ETC_365t':('none',[]),'ETC_365t2':('none',[]),
 'YOG_529':('none',[]),
 'YOG_529a':('none',[('historical_music_forbidden','attack')]),
 'YOG_529b':('none',[('historical_music_forbidden','armor')]),
}
for cid in RIFFS:TOKEN_RULES[cid]=('none',[('historical_music_riff',cid)])
CHOICES={'YOG_529':[
 ('Sinful Sampling','none',[('historical_music_forbidden','attack')]),
 ('Reject Temptation','none',[('historical_music_forbidden','armor')]),
]}
TOKEN_RULES.update({
 'ETC_387':('none',[]),'ETC_387t':('none',[]),
 'ETC_387b':('none',[('historical_music_roots',2,'ETC_387bt')]),
 'ETC_387c':('none',[('historical_music_roots',4,'ETC_387ct')]),
 'ETC_387ct':('none',[]),
})
for cid in ('ETC_387','ETC_387t'):
 CHOICES[cid]=[
  ("Ancient's Melody",'none',[('historical_music_roots',2,'ETC_387bt')]),
  ("Giant's Dance",'none',[('historical_music_roots',4,'ETC_387ct')]),
 ]
TOKEN_RULES['TOY_378']=('none',[('historical_music_projection',)])
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)


def split(game,op,ctx):
 owner=ctx['owner'];p=game.players[owner];name=op[0]
 if name=='historical_music_projection':
  groups={}
  for record in tuple(getattr(p,'_historical_cast_records',())):
   card=record['card'];data=game._card_data(card)
   if data['type']=='SPELL' and data['id']!='TOY_378':groups.setdefault(data.get('cost',0),[]).append(card)
  operations=tuple(('historical_copy_replay_cast',game._fresh_replay_card(game.rng.choice(groups[cost])),'prefer_enemies') for cost in sorted(groups))
  if not operations:return ('batch30_noop',),()
  head,tail=game._split_fixed_summon(operations[0],ctx)
  return head,tuple(tail)+operations[1:]
 if name=='historical_music_riff':
  cid=op[1];previous=getattr(p,'historical_last_riff',None);replay=getattr(ctx.get('physical_card'),'rule_state',{}).get('historical_riff_replay',False)
  if not replay:p.historical_last_riff=cid
  if cid=='ETC_363':operations=(('hero_attack',2),('armor',2))
  elif cid=='ETC_364':operations=(draw((('type','eq','MINION'),),'buff',(3,3),'random'),)
  else:operations=(('summon','ETC_365t',1),('summon','ETC_365t2',1))
  if ctx.get('finale') and previous in RIFFS and not replay:operations+=(('historical_music_replay',previous),)
  first,tail=game._split_fixed_summon(operations[0],ctx)
  return first,tuple(tail)+operations[1:]
 if name=='historical_music_replay':
  card=Card(game._new_id(),op[1]);game._b60_state(card)['historical_riff_replay']=True
  return game._cast_spell_split(('cast_physical_spell',card,'random'),ctx)
 return None


def execute(game,op,ctx):
 owner=ctx['owner'];p=game.players[owner];name=op[0]
 if name=='historical_music_roots':
  require_fixed_cards((op[2],),game.cards)
  game._schedule_turn_effect(owner,'start',op[1],1,(('summon',op[2],3),),source_card_id='ETC_387')
  p.scheduled_effects[-1]['historical_private_roots']=True
 elif name=='historical_music_symphony':
  require_fixed_cards(MOVEMENTS+('ETC_t8t',),game.cards)
  if game.pending_choice is not None:raise UnsupportedCard('Cannot overwrite Movement Discover')
  game.pending_choice=dict(owner=owner,kind='historical_music_movement',context=dict(ctx),options=[dict(card_id=cid) for cid in game.rng.sample(list(MOVEMENTS),3)])
  game.phase='choice'
 elif name=='historical_music_shuffle_movements':
  cards=[Card(game._new_id(),cid) for cid in MOVEMENTS if cid!=op[1]]
  p.deck.extend(cards);game.rng.shuffle(p.deck);game._record_deck_insertion(owner,owner,len(cards),'shuffle',cards=tuple(cards))
 elif name=='historical_music_envy':
  q=game.players[1-owner]
  for _ in range(min(6,len(q.deck))):
   card=q.deck.pop();game._zone_card_removed(1-owner,card,'deck','destroy');game._log('remove_deck_card',player=1-owner,card=game._card_data(card)['id'])
  game._refresh_auras()
 elif name=='historical_music_gluttony':
  for zone_name in ('hand','deck'):
   cards=[card for card in getattr(p,zone_name) if game._card_data(card)['type']=='MINION']
   if cards:
    card=game.rng.choice(cards);add_stat(card,'attack_bonus',6);add_stat(card,'health_bonus',6)
  minions=[m for m in p.minions if m.health>0]
  if minions:game._buff(game.rng.choice(minions),6,6)
 elif name=='historical_music_forbidden':
  if 'historical_forbidden_mana' not in ctx:
   ctx['historical_forbidden_mana']=p.mana;amount=p.mana;p.mana=0;game._b60_spend_mana(owner,amount)
  amount=ctx['historical_forbidden_mana'];game._effect(('hero_attack',amount) if op[1]=='attack' else ('armor',2*amount),ctx)
 else:return False
 return True


def resolve_choice(game,choice,selected):
 if choice['kind']!='historical_music_movement':return False
 operations=(('cast_fixed_spell',selected['card_id'],'random'),('historical_music_shuffle_movements',selected['card_id']))
 game._rule_events.append(('captured_effects',dict(operations=operations,context=dict(choice['context'])),[]))
 return True
