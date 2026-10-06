"""Retain Rewind outcomes as successive effect resolutions, paying once.

This captures the replacement at play entry and preserves each outcome's
mutations. It never merges two whole-game snapshots or pays for a second play.
"""
from copy import deepcopy
from .generation_cards import pool,discover
REWIND_POOL=pool(mechanic='REWIND')
RULES={'END_036':('none',[discover(REWIND_POOL)])}
def requests_for(cid):return {REWIND_POOL} if cid=='END_036' else set()
class Morchie:
 def _morchie_operations(self,operations,context):
  state=getattr(self,'_rewind_state',None)
  if not state or not state.get('keep_all'):return operations
  count=state['remaining']+1;result=[]
  for i in range(count):
   ctx=dict(context);card=deepcopy(context['physical_card'])
   self._b60_state(card)['rewinds_remaining']=count-i-1;ctx['physical_card']=card
   result.append(('replay_context',tuple(operations),ctx))
  self._rewind_state=None
  return result
