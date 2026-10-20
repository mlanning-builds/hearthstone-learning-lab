"""Soul Mirror's resumable full-roster summon and deferred-death combat."""
from copy import deepcopy

def split(game,op,ctx):
 name=op[0];owner=ctx['owner']
 if name=='historical_utility_soul_mirror':
  donors=tuple(deepcopy(m) for m in game.players[1-owner].minions if m.health>0)
  state={'pairs':[]}
  # Existing repetition guards retain death/hero checks across resumable
  # operations and choices while still draining ordinary child events.
  operations=tuple(('historical_utility_mirror_copy',donor,state) for donor in donors)+(('historical_utility_mirror_attacks',state),('spell_repeat_end',))
  return ('spell_repeat_begin',),operations
 if name=='historical_utility_mirror_attacks':
  operations=tuple(('historical_utility_mirror_attack',copy_uid,original_uid) for copy_uid,original_uid in op[1]['pairs'])
  if not operations:return ('batch30_noop',),()
  first,tail=split(game,operations[0],ctx)
  return first,tuple(tail)+operations[1:]
 if name=='historical_utility_mirror_attack':
  attacker=game._force_live(op[1]);defender=game._force_live(op[2])
  if attacker is None or defender is None:return ('batch30_noop',),()
  state={'source':attacker.uid,'target':defender.uid,'attacker':attacker}
  return ('force_begin',state),(('historical_utility_mirror_resolve',state),)
 return None

def execute(game,op,ctx):
 name=op[0];owner=ctx['owner']
 if name=='historical_utility_mirror_copy':
  donor,state=op[1:]
  if len(game.players[owner].board)>=7:return True
  body=game._summon(owner,donor.card_id,copy_from=donor,entry_origin='copy',entry_site='soul_mirror')
  if body is not None:state['pairs'].append((body.uid,donor.uid))
 elif name=='historical_utility_mirror_resolve':
  state=op[1];attacker=game._force_live(state['source']);target=state.get('target')
  resolves=bool(state.get('ready') and attacker is not None and target is not None and (target<0 and game.players[-target-1].health>0 or target>0 and game._force_live(target) is not None))
  # Native forced-combat handling rechecks death, replacements and windows.
  game._force_effect(('force_resolve',state),ctx)
  if resolves:state['attacker'].attacks+=1
 else:return False
 return True
