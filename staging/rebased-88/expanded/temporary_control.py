"""Staged temporary control with an explicit original-controller deadline."""
from engine.cards import UnsupportedCard
RULES={'CATA_496':('enemy_minion',[('temporary_control',)])}

class TemporaryControl:
 def _temporary_control_effect(self,op,ctx):
  if op[0]!='temporary_control':return False
  owner=ctx['owner'];p=self.players[owner]
  m=next((m for m in self.players[1-owner].minions if m.uid==ctx['target'] and m.health>0),None)
  if m is None:return True
  if len(p.board)>=7:raise UnsupportedCard('Temporary control requires board space')
  if hasattr(m,'_control_return'):raise UnsupportedCard('Overlapping control timers require reviewed ordering')
  original=m.owner
  self.players[original].board.remove(m);m.owner=owner;p.board.append(m)
  m._control_return=dict(owner=original,due=self.players[original].turns_taken+1)
  m._control_no_attack_until=self.turn
  m.summoned_turn=self.turn;m.attacks=0
  self._refresh_auras()
  return True

 def _return_temporary_control(self,owner):
  for p in self.players:
   for m in tuple(p.all_minions):
    effect=getattr(m,'_control_return',None)
    if not effect or effect['owner']!=owner or effect['due']>self.players[owner].turns_taken:continue
    del m._control_return
    if m.health<=0 or m.owner==owner:continue
    destination=self.players[owner]
    if len(destination.board)>=7:
     m.health=0
    else:
     p.board.remove(m);m.owner=owner;destination.board.append(m);m.summoned_turn=self.turn;m.attacks=0
  self._refresh_auras()
  self._settle(allow_event_choices=True)
