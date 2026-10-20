"""Remaining locations and exact owner-turn delayed play/payment effects."""
from engine.game import Card
RELICS=('REV_834','REV_943','REV_508')
TOKEN_RULES={cid:('none',[]) for cid in ('REV_750','REV_942','TOY_512','NX2_036','REV_750t2','NX2_036t')}
TOKEN_RULES.update({
 'TTN_744':('none',[('historical_location_timed_frozen',)]),
 'YOG_503':('none',[('historical_location_timed_curse',)]),
})
LOCATION_RULES={'REV_750':'none','REV_942':'none','TOY_512':'none','NX2_036':'friendly_minion'}
LOCATION_EFFECTS={
 'REV_750':[('historical_location_timed_ghost',)],
 'REV_942':[('historical_location_timed_vault',)],
 'TOY_512':[('historical_location_timed_cove',)],
 'NX2_036':[('destroy',),('historical_location_timed_hulk',)],
}
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)


def frozen_locked(game,owner,card):
 state=getattr(card,'rule_state',{}).get('historical_frozen_over')
 return bool(state and state['owner']==owner and state['owner_turn']==game.players[owner].turns_taken)


def relic_extra(game,owner,cid):
 p=game.players[owner];state=getattr(p,'historical_relic_vault',{})
 if cid not in RELICS or state.get('turn')!=game.turn:return 0
 count=state.get('count',0);p.historical_relic_vault=dict(turn=game.turn,count=0)
 return count


def entry(game,minion):
 p=game.players[minion.owner]
 if getattr(p,'historical_crystal_cove_turn',None)==game.turn:
  p.historical_crystal_cove_turn=None;game._set_entity_stats(minion,4,4)


def split(game,op,ctx):
 if op[0]!='historical_location_timed_frozen':return None
 owner=ctx['owner'];other=1-owner;states=({},{});operations=(('draw',2),)
 operations+=tuple(('replay_context',(('historical_draw_capture',None,'random',state),),dict(ctx,owner=other)) for state in states)
 operations+=(('historical_location_timed_lock',other,states),)
 return operations[0],operations[1:]


def execute(game,op,ctx):
 owner=ctx['owner'];p=game.players[owner];name=op[0]
 if name=='historical_location_timed_ghost':
  location=ctx.get('location_source');own_play=int(getattr(location,'rule_state',{}).get('historical_played_turn')==game.turn)
  size=1+max(0,p.cards_played-own_play)
  game._summon(owner,'REV_750t2',entry_stats=(size,size),entry_origin='location',entry_site='sinstone_graveyard')
 elif name=='historical_location_timed_vault':
  state=getattr(p,'historical_relic_vault',{});p.historical_relic_vault=dict(turn=game.turn,count=1+(state.get('count',0) if state.get('turn')==game.turn else 0))
 elif name=='historical_location_timed_cove':p.historical_crystal_cove_turn=game.turn
 elif name=='historical_location_timed_hulk':
  # Retain the archive's contradictory 5/5 record; the source effect says 4/5.
  card=Card(game._new_id(),'NX2_036t');card.base_stat_override=(4,5);card._historical_permanent_stats=True
  game._summon(owner,'NX2_036t',entry_source=card,entry_zone='deck',entry_origin='location',entry_site='construct_quarter')
 elif name=='historical_location_timed_lock':
  recipient=op[1];player=game.players[recipient]
  for state in op[2]:
   card=state.get('card')
   if card is not None and any(card is held for held in player.hand):game._b60_state(card)['historical_frozen_over']=dict(owner=recipient,owner_turn=player.turns_taken+1)
 elif name=='historical_location_timed_curse':
  target=game.players[1-owner];target.payment_effects.append(dict(kind='historical_minion_health_turn',owner_turn=target.turns_taken+1))
 else:return False
 return True
