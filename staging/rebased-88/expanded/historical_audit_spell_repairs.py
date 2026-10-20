"""Explicit remaining historical spell programs and resumable draws."""
from engine.game import Card

def op(name,*args):return ('historical_utility_audit_'+name,)+args
TOKEN_RULES={
 'AV_405':('none',[('historical_copy_history_replay','stash')]),
 'ICC_233':('minion',[op('doomerang')]),
 'AV_119':('none',[op('front')]),
 'ICC_201':('none',[op('bones')]),
 'VAC_528':('none',[op('different_types')]),
 'VAC_931':('minion',[op('skirt')]),
}
TOKEN_RULES.update({
 'WORK_017':('minion',[('temporary_keyword_target','IMMUNE','end'),('buff',2,2)]),
 'WORK_017t':('minion',[('silence',),('buff',-2,-2)]),
 'WORK_030':('minion',[op('icecrown')]),
 'WORK_030t':('minion',[op('blackrock')]),
})
# These are physical-zone choices, so duplicate copies remain separate offers
# for Telegram while Birdwatching uses normal Discover identity deduplication.
from .historical_play_batches import zone_offer
TOKEN_RULES.update({
 'VAC_408':('none',[zone_offer('own','deck',(('type','eq','MINION'),),'wrangler')]),
 'WON_078':('none',[zone_offer('enemy','hand',(),'shuffle',3,False),('historical_ritual_jade',False,False)]),
})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

def split(game,operation,ctx):
 name=operation[0];owner=ctx['owner'];p=game.players[owner]
 if name==op('doomerang')[0]:
  if not p.weapon:return ('batch30_noop',),()
  card=p.equipped_card
  if card is None:
   from engine.cards import UnsupportedCard
   raise UnsupportedCard('Doomerang requires the equipped physical weapon')
  state=dict(card=card,weapon=p.weapon)
  return op('weapon_hit',p.weapon['attack']),(op('weapon_return',state),)
 if name in (op('icecrown')[0],op('blackrock')[0]):
  target=game._force_live(ctx.get('target'))
  if target is None:return ('batch30_noop',),()
  board=game.players[target.owner].board;index=board.index(target)
  neighbors=tuple(m.uid for i,m in enumerate(board) if abs(i-index)==1 and m in game.players[target.owner].minions)
  return op('brochure_damage',target.uid,neighbors,name==op('icecrown')[0]),()
 if name==op('bones')[0]:
  state={}
  return ('historical_draw_capture',None,'random',state),(op('bones_continue',state),)
 if name==op('bones_continue')[0]:
  card=operation[1].get('card')
  if card is not None and 'DEATHRATTLE' in game._card_mechanics(card):
   # The card says cast again: use an actual spell frame, preserving automatic
   # casting attribution, targets, listeners and the shared continuation cursor.
   return game._split_fixed_summon(('cast_fixed_spell','ICC_201','random'),ctx)
  return ('batch30_noop',),()
 if name==op('different_types')[0]:
  for i,card in enumerate(p.deck):
   if not isinstance(card,Card):p.deck[i]=Card(game._new_id(),card)
  candidates=[card for card in p.deck if game._card_data(card)['type']=='MINION']
  chosen=game._distinct_type_group(candidates,3)
  operations=tuple(('tribal_draw_physical',card) for card in chosen)
  return (operations[0],operations[1:]) if operations else (('batch30_noop',),())
 return None

def execute(game,operation,ctx):
 name=operation[0];owner=ctx['owner'];p=game.players[owner]
 if name==op('weapon_hit')[0]:
  # Damage belongs to the spell, not to a weapon attack. The frozen card's
  # ImmuneToSpellpower tag excludes additive Spell Damage in _deal_effect.
  game._deal_effect(ctx.get('target'),operation[1],ctx)
 elif name==op('weapon_return')[0]:
  state=operation[1]
  # Damage listeners may have replaced or removed the original weapon.
  if p.weapon is state['weapon'] and p.equipped_card is state['card']:
   card=game._fresh_replay_card(state['card'])
   game._carry_origin(state['card'],card)
   p.weapon=None;p.equipped_card=None
   game._enter_hand(owner,card)
   game._refresh_auras()
 elif name==op('brochure_damage')[0]:
  uid,neighbors,ice=operation[1:]
  if ice:
   game._deal_effect(uid,3,ctx)
   for other in neighbors:
    if game._force_live(other) is not None:game._freeze(other)
  else:
   with game._damage_batch():
    game._deal_effect(uid,3,ctx)
    for other in neighbors:
     if game._force_live(other) is not None:game._deal_effect(other,1,ctx)
 elif name==op('front')[0]:
  p.cost_effects.append(dict(selector='MINION',amount=2,minimum=1,expires=game.turn,consume_on_play=False))
 elif name==op('skirt')[0]:
  target=game._force_live(ctx.get('target'))
  if target is not None:
   amount=min(4,max(0,target.attack))
   game._effect(('temporary_attack_buff',-amount),ctx)
   game._effect(('hero_attack',amount),ctx)
 else:return False
 return True
