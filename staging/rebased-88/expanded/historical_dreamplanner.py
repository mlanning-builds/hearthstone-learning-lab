"""Fixed Dreamplanner tours, with complete literal pools and no board scoring.

Observed pool membership and all new behavior remain unvalidated.
"""
from engine.cards import UnsupportedCard
from .pools import require_fixed_cards
POOLS={'WORK_027t1': ('EX1_259', 'CS2_026', 'CS2_032', 'EX1_312', 'CS2_093', 'NEW1_007', 'NEW1_004', 'EX1_309', 'EX1_303', 'EX1_407', 'EX1_334', 'EX1_626', 'EX1_197', 'EX1_619', 'CS2_028', 'CS2_012', 'CS1_112', 'EX1_246', 'CS2_022'), 'WORK_027t2': ('EX1_323', 'EX1_383', 'CS1_113', 'EX1_016', 'EX1_573', 'EX1_559', 'EX1_354', 'EX1_572', 'NEW1_008', 'EX1_298', 'EX1_295', 'EX1_144', 'EX1_105'), 'WORK_027t3': ('CS2_029', 'CS2_024', 'EX1_384', 'CS2_011', 'EX1_124', 'EX1_238', 'EX1_241', 'CS2_039', 'EX1_308', 'EX1_408', 'EX1_414', 'EX1_116', 'NEW1_010', 'DS1_233')}

def execute(game,op,ctx):
 name=op[0];owner=ctx['owner'];p=game.players[owner]
 if name=='historical_tour_begin':
  require_fixed_cards(tuple(cid for values in POOLS.values() for cid in values),game.cards)
  if game.pending_choice is not None:raise UnsupportedCard('Cannot overwrite tour choice')
  game.pending_choice=dict(owner=owner,kind='historical_tour',options=[dict(card_id=cid) for cid in POOLS],context=dict(ctx),_automatic=bool(ctx.get('automatic_choices',False)))
  game.phase='choice';return True
 if name=='historical_tour_generate':
  values=POOLS.get(op[1])
  if not values:raise UnsupportedCard('Unknown Dreamplanner tour')
  require_fixed_cards(values,game.cards)
  selected=tuple(game.rng.choice(values) for _ in range(2))
  for cid in selected:game._add(owner,cid)
  return True
 return False

def resolve_choice(game,choice,selected):
 if choice['kind']!='historical_tour':return False
 cid=selected.get('card_id')
 if cid not in {row['card_id'] for row in choice['options']}:raise UnsupportedCard('Tour was not offered')
 game._log('travel_tour_chosen',player=choice['owner'],card=cid)
 execute(game,('historical_tour_generate',cid),choice['context'])
 return True

def legacy_effect(game,op,ctx):
 name=op[0];owner=ctx['owner'];p=game.players[owner]
 target=game._force_live(ctx.get('target',0))
 if name=='historical_tour_mind_control':
  if target is not None and target.owner!=owner and len(p.board)<7:
   game.players[target.owner].board.remove(target);target.owner=owner;p.board.append(target)
   target.summoned_turn=game.turn;target.attacks=0
   for field in ('_control_return','_control_no_attack_until'):
    if hasattr(target,field):delattr(target,field)
   game._refresh_auras()
 elif name=='historical_tour_swipe':
  enemies=tuple([game.hero_id(1-owner)]+[m.uid for m in game.players[1-owner].minions if m.health>0 and not m.dormant])
  with game._damage_batch():
   game._deal_effect(ctx.get('target',0),4,ctx)
   for uid in enemies:
    if uid!=ctx.get('target'):game._deal_effect(uid,1,ctx)
 elif name=='historical_tour_shadowflame':
  if target is not None and target.owner==owner:
   amount=target.attack;target.health=0
   with game._damage_batch():
    for m in tuple(game.players[1-owner].minions):
     if m.health>0 and not m.dormant:game._deal_effect(m.uid,amount,ctx)
 elif name=='historical_tour_brawl':
  values=[m for player in game.players for m in player.minions if m.health>0 and not m.dormant]
  if values:
   survivor=game.rng.choice(values)
   for m in values:
    if m is not survivor:m.health=0
 elif name=='historical_tour_eviscerate':game._deal_effect(ctx.get('target',0),4 if ctx.get('combo') else 2,ctx)
 elif name=='historical_tour_mortal':game._deal_effect(ctx.get('target',0),6 if p.health<=12 else 4,ctx)
 else:return False
 return True
