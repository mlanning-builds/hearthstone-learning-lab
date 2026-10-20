"""Physical movement totals for The Ceaseless Expanse; fidelity unvalidated.

Opening/mulligan card exchanges are setup, not in-game draw actions.
Summons, copies, transformations and ordinary spell resolution are not counted
as destruction. The callers identify actual destruction transitions explicitly.
"""
def record(game,kind):
 if kind not in ('drawn','played','destroyed'):raise ValueError('Unknown card movement')
 if getattr(game,'phase',None)=='mulligan':return
 state=getattr(game,'historical_card_movements',None)
 if state is None:
  state=dict(drawn=0,played=0,destroyed=0);game.historical_card_movements=state
 state[kind]+=1
