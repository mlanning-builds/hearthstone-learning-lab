"""Literal Un'Goro pack dependencies; newly written and unvalidated."""
from copy import deepcopy
from engine.game import Card
from .generation_cards import pool,discover
from .pools import require_fixed_cards
from .selectors import has_tribe

def execute(game,op,ctx):
 name=op[0];owner=ctx['owner'];p=game.players[owner];target=game._force_live(ctx.get('target',0))
 if name=='historical_ungoro_living_crystals':
  from .mana_accounting import destroy_permanent
  destroy_permanent(p,op[1])
 elif name=='historical_ungoro_stampede':
  state=getattr(p,'historical_stampede',{})
  p.historical_stampede=dict(turn=game.turn,count=(state.get('count',0) if state.get('turn')==game.turn else 0)+1)
 elif name=='historical_ungoro_mana_bind':
  card=game._copy_card(op[1],source_owner=1-owner);game._set_card_cost(card,0);game._enter_hand(owner,card)
 elif name=='historical_ungoro_mist':
  key=game._new_id()
  for player in game.players:
   for minion in player.minions:
    if minion.health>0 and not minion.dormant:minion.rule_state.setdefault('ungoro_mist',[]).append(key)
  game._schedule_turn_effect(owner,'start',1,1,(('historical_ungoro_mist_destroy',key),),source_card_id='UNG_831')
 elif name=='historical_ungoro_mist_destroy':
  victims=[m for player in game.players for m in player.minions if op[1] in m.rule_state.get('ungoro_mist',()) and m.health>0 and not m.dormant]
  for minion in victims:minion.health=0
 elif name=='historical_ungoro_explore':
  require_fixed_cards(('UNG_922t1',),game.cards)
  p.deck=[Card(game._new_id(),'UNG_922t1') for _ in p.deck]
  game._refresh_auras()
 elif name=='historical_ungoro_dinomancy':game._replace_primary_power(owner,dict(card_id='UNG_917t1'))
 elif name=='historical_ungoro_feeding':
  from .adapt import ADAPTATIONS,PLANT
  from engine.cards import UnsupportedCard
  if game.pending_choice is not None:raise UnsupportedCard('Feeding Time cannot overwrite an Adapt choice')
  require_fixed_cards(('UNG_834t1',)+tuple(ADAPTATIONS)+(PLANT,),game.cards)
  before={m.uid for m in p.minions}
  for _ in range(3):
   minion=game._summon(owner,'UNG_834t1',entry_origin='effect',entry_site='feeding_time')
  targets=[m.uid for m in p.minions if m.uid not in before and m.card_id=='UNG_834t1' and m.health>0 and not m.dormant]
  if targets:
   options=game.rng.sample(sorted(ADAPTATIONS),3)
   game.pending_choice=dict(owner=owner,kind='historical_adapt',targets=tuple(targets),options=[dict(card_id=cid) for cid in options])
   game.phase='choice'
 elif name=='historical_ungoro_mimic':
  card=game._draw(owner,include_burned=True)
  if card is not None:game._enter_hand(owner,game._copy_card(card))
 elif name=='historical_ungoro_scales':
  if target is not None:game._gain_armor(owner,max(0,target.attack))
 elif name=='historical_ungoro_envenom':
  if p.weapon:
   keywords=set(p.weapon.get('historical_keywords',()));keywords.add('POISONOUS');p.weapon['historical_keywords']=tuple(sorted(keywords))
 elif name=='historical_ungoro_spore':
  game._effect(discover(pool(classes=game.players[1-owner].hero_class)),ctx)
 elif name=='historical_ungoro_cleave':
  if target is not None:
   board=game.players[target.owner].board;index=board.index(target)
   neighbors=tuple(board[i] for i in (index-1,index+1) if 0<=i<len(board) and board[i] in game.players[target.owner].minions and not board[i].dormant)
   with game._damage_batch():
    game._deal_effect(target.uid,op[1],ctx)
    for value in neighbors:game._deal_effect(value.uid,op[2],ctx)
 elif name=='historical_ungoro_reflection':
  if target is not None:game._summon(owner,target.card_id,copy_from=deepcopy(target),entry_origin='copy',entry_site='molten_reflection')
 elif name=='historical_ungoro_genesis':
  values=tuple(deepcopy(m) for m in p.minions if m.health>0 and m.health<m.max_health and not m.dormant)
  for donor in values:game._summon(owner,donor.card_id,copy_from=donor,entry_origin='copy',entry_site='sudden_genesis')
 elif name=='historical_ungoro_echo':
  # Death resets enchantments; each bearer returns its own identity, not a
  # randomly selected friendly death from the shared death history.
  for minion in tuple(p.minions):
   if minion.health>0 and not minion.dormant:
    minion.attached_death_effects.append(('add',minion.card_id,1));minion.keywords.add('DEATHRATTLE')
 else:return False
 return True


def split(game,op,ctx):
 if op[0]!='historical_ungoro_living':return None
 p=game.players[ctx['owner']]
 require_fixed_cards(('UNG_111t1',),game.cards)
 count=min(p.max_mana,max(0,7-len(p.board)))
 # Determine and destroy the crystals before any summon triggers can alter
 # the board. Each summon is a separate native continuation checkpoint.
 return ('historical_ungoro_living_crystals',count),tuple(('summon','UNG_111t1',1) for _ in range(count))
