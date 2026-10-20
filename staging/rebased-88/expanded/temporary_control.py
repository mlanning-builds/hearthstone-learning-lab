"""Ordered temporary control enchantments with independent expiry deadlines."""
from engine.cards import UnsupportedCard
RULES={'CATA_496':('enemy_minion',[('temporary_control',)])}

class TemporaryControl:
 def _control_state(self,m):
  state=getattr(m,'_control_return',None)
  if state is None:return None
  if 'layers' not in state:
   # Compatibility with physical definitions created before layered timers.
   original=state['owner'];due=state['due']
   state=dict(base=original,expected=m.owner,owner=original,due=due,layers=[dict(token=state.get('historical_madness',self._new_id()),controller=m.owner,return_owner=original,deadline_owner=original,due=due,end_timer='historical_madness' in state)])
   m._control_return=state
  return state

 def _observe_control_changes(self):
  # Permanent steals supersede previously attached temporary control layers.
  # Shared aura checkpoints run after control changes, including simultaneous
  # rotations, so a later permanent change cannot be undone by an older timer.
  for player in self.players:
   for m in player.all_minions:
    state=self._control_state(m)
    if state is not None and state['expected']!=m.owner:del m._control_return

 def _add_control_layer(self,m,owner,*,deadline_owner,due,token=None,ready=False,end_timer=False):
  self._observe_control_changes()
  original=m.owner;state=self._control_state(m)
  if state is None:state=dict(base=original,expected=original,layers=[])
  layer=dict(token=self._new_id() if token is None else token,controller=owner,return_owner=original,deadline_owner=deadline_owner,due=due,end_timer=end_timer)
  state['layers'].append(layer);state.update(expected=owner,owner=original,due=due)
  m._control_return=state
  self.players[original].board.remove(m);m.owner=owner;self.players[owner].board.append(m)
  m.summoned_turn=self.turn-1 if ready else self.turn;m.attacks=0
  if ready:
   if hasattr(m,'_control_no_attack_until'):del m._control_no_attack_until
  else:m._control_no_attack_until=self.turn
  return layer['token']

 def _expire_control_layers(self,predicate):
  self._observe_control_changes()
  for player in self.players:
   for m in tuple(player.all_minions):
    state=self._control_state(m)
    if state is None:continue
    old=state['layers'];layers=[layer for layer in old if not predicate(layer)]
    if len(old)==len(layers):continue
    destination=layers[-1]['controller'] if layers else state['base']
    if layers:
     state['layers']=layers;state.update(expected=destination,owner=layers[-1]['return_owner'],due=layers[-1]['due'])
    else:del m._control_return
    if m.health<=0 or m.owner==destination:continue
    if len(self.players[destination].board)>=7:m.health=0
    else:
     self.players[m.owner].board.remove(m);m.owner=destination;self.players[destination].board.append(m)
     m.summoned_turn=self.turn;m.attacks=0
  self._refresh_auras()

 def _temporary_control_effect(self,op,ctx):
  if op[0]!='temporary_control':return False
  owner=ctx['owner'];p=self.players[owner]
  m=next((m for m in self.players[1-owner].minions if m.uid==ctx['target'] and m.health>0),None)
  if m is None:return True
  if len(p.board)>=7:raise UnsupportedCard('Temporary control requires board space')
  original=m.owner
  self._add_control_layer(m,owner,deadline_owner=original,due=self.players[original].turns_taken+1)
  self._refresh_auras()
  return True

 def _return_temporary_control(self,owner):
  self._expire_control_layers(lambda layer:not layer['end_timer'] and layer['deadline_owner']==owner and layer['due']<=self.players[owner].turns_taken)
  self._settle(allow_event_choices=True)
