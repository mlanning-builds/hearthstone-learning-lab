"""Explicit school transformations and remembered spells; unvalidated."""
from copy import deepcopy
from engine.game import Card
from .generation_cards import pool,discover
from .selectors import has_class

NAZJAR={'ARCANE':'TID_709t','FIRE':'TID_709t2','FROST':'TID_709t3'}
CARRESS_EFFECTS={
 'ARCANE':(('draw',2),),'FIRE':(('damage_enemy_hero',6),),
 'FROST':(('historical_hand_forms_freeze',),),
 'NATURE':(('buff_self',2,2),('keyword_self','TAUNT')),
 'HOLY':(('heal_own_hero',6),),'SHADOW':(('destroy_random_enemy',2),),
 'FEL':(('area_damage','enemy_minions',2),),
}
# Ordering is literal to each frozen form, including Frost and Shadow/Fel pairs.
CARRESS_PAIRS=(('ARCANE','FIRE'),('ARCANE','FROST'),('ARCANE','NATURE'),
 ('ARCANE','HOLY'),('ARCANE','SHADOW'),('ARCANE','FEL'),('FIRE','FROST'),
 ('FIRE','NATURE'),('FIRE','HOLY'),('FIRE','SHADOW'),('FIRE','FEL'),
 ('NATURE','FROST'),('HOLY','FROST'),('SHADOW','FROST'),('FEL','FROST'),
 ('NATURE','HOLY'),('NATURE','SHADOW'),('NATURE','FEL'),('HOLY','SHADOW'),
 ('HOLY','FEL'),('FEL','SHADOW'))
CARRESS_IDS=tuple('VAC_449t'+(str(index) if index else '') for index in range(21))
CARRESS_FORMS={frozenset(pair):cid for pair,cid in zip(CARRESS_PAIRS,CARRESS_IDS)}
RULES={cid:('none',[]) for cid in ('TID_709','VAC_449','WW_364','SCH_714')}
TOKEN_RULES={
 'TID_709t':('none',[('historical_hand_forms_nazjar_discount',)]),
 'TID_709t2':('enemy_minion',[('historical_hand_forms_nazjar_fire',)]),
 'TID_709t3':('none',[('armor',8)]),
 'WW_364t':('none',[]),
}
for cid,pair in zip(CARRESS_IDS,CARRESS_PAIRS):
 TOKEN_RULES[cid]=('none',list(CARRESS_EFFECTS[pair[0]]+CARRESS_EFFECTS[pair[1]]))
TRIGGERS={
 'WW_364t':(('historical_event','source_attacked'),[discover(pool(classes='other'),cost_delta=-3)]),
 'SCH_714':(('historical_event','any_spell_played'),[('historical_hand_forms_remember',)]),
}
DEATH_EFFECTS={'SCH_714':[('historical_hand_forms_shuffle',)]}

def held_event(game,kind,data):
 if kind not in ('spell_cast','spell_played','minion_played','dormant_other_card_played'):return
 owner=data['owner'];p=game.players[owner];cid=data.get('card_id')
 if cid is None:return
 metadata=game.cards[cid];school=metadata.get('spellSchool')
 for card in list(p.hand):
  replacement=None
  if kind=='spell_cast' and card.card_id in ('TID_709',)+tuple(NAZJAR.values()) and school in NAZJAR:
   replacement=NAZJAR[school]
  elif kind=='spell_played' and card.card_id=='VAC_449' and school in CARRESS_EFFECTS:
   state=game._b60_state(card);schools=state.setdefault('historical_carress_schools',[])
   if school not in schools:schools.append(school)
   if len(schools)>=2:replacement=CARRESS_FORMS[frozenset(schools[:2])]
  elif kind!='spell_cast' and card.card_id=='WW_364' and not has_class(metadata,p.hero_class) and not has_class(metadata,'NEUTRAL'):
   replacement='WW_364t'
  if replacement:
   game._b60_transform_card(card,replacement);game._log('hand_transformed',player=owner,entity=card.uid)

def split(game,op,ctx):
 if op[0]!='historical_hand_forms_nazjar_fire':return None
 victim=next((m for p in game.players for m in p.minions if m.uid==ctx.get('target')),None)
 if victim is None:return ('batch30_noop',),()
 board=game.players[victim.owner].board;position=board.index(victim)
 adjacent=[board[index].uid for index in (position-1,position+1) if 0<=index<len(board) and board[index] in game.players[victim.owner].minions]
 return ('damage',5),tuple(('replay_context',(('damage',2),),dict(ctx,target=uid)) for uid in adjacent)

def execute(game,op,ctx):
 name=op[0]
 if not name.startswith('historical_hand_forms_'):return False
 owner=ctx['owner'];p=game.players[owner];source=ctx.get('source')
 if name=='historical_hand_forms_nazjar_discount':
  for card in p.hand:
   if game._card_data(card)['type']=='SPELL':card.cost_delta-=1
 elif name=='historical_hand_forms_freeze':
  values=[m.uid for m in game.players[1-owner].minions if m.health>0]
  for uid in game.rng.sample(values,min(3,len(values))):game._freeze(uid)
 elif name=='historical_hand_forms_remember':
  if source is not None:
   event=ctx['event'];card=event.get('physical_card')
   if card is None:card=Card(game._new_id(),event['card_id'])
   source.rule_state.setdefault('historical_elekk_spells',[]).append((event['owner'],deepcopy(card)))
 elif name=='historical_hand_forms_shuffle':
  memory=getattr(source,'rule_state',{}).get('historical_elekk_spells',())
  cards=[game._copy_card(card,source_owner=caster) for caster,card in memory]
  if cards:
   p.deck.extend(cards);game.rng.shuffle(p.deck);game._record_deck_insertion(owner,owner,len(cards),'shuffle',cards=cards);game._refresh_auras()
 else:return False
 return True
