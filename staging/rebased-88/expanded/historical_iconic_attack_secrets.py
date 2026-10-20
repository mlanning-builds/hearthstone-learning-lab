"""Physical attack-redirection Secret programs in native trigger order."""
from .generation_cards import pool,board_pool
IDS=frozenset(('LOOT_079','CORE_LOOT_079','EX1_533','VAN_EX1_533'))
MONSTERS=frozenset(('LOOT_079','CORE_LOOT_079'))
def alternatives(game,source,target):
 result=[game.hero_id(owner) for owner in (0,1) if game.players[owner].health>0 and not game._hero_immune(owner)]
 result.extend(m.uid for p in game.players for m in p.minions if m.health>0 and 'IMMUNE' not in game._effective_keywords(m))
 # Misdirection can hit Stealth and friendly characters; it cannot hit its
 # original attacker or defender. These are replacement, not chosen targets.
 return tuple(uid for uid in result if uid not in (source,target))

def redirect(game,owner,source,target,secret):
 from .historical_secret_archive import redirect as archive_redirect
 handled,replacement=archive_redirect(game,owner,source,target,secret)
 if handled:return handled,replacement
 if secret.card_id not in IDS or game.current==owner or target!=game.hero_id(owner):return False,target
 from .historical_secret_batches import blocked
 if blocked(game):return False,target
 if secret.card_id in MONSTERS:
  if len(game.players[owner].board)>=7:return False,target
  # Validate the complete cost pool before revealing the physical Secret.
  game._generation_created_candidates(board_pool(pool(card_type='MINION',minimum=3,maximum=3)),dict(owner=owner,source=None))
 elif not alternatives(game,source,target):return False,target
 state={'target':target}
 operation=('historical_utility_attack_secret',secret.card_id,source,target,state)
 game._trigger_secret_program(owner,secret,(operation,),dict(owner=owner,source=None,target=0,bonus=0,lifesteal=False,card_id=secret.card_id))
 game._settle(allow_event_choices=True)
 return True,state['target']

def execute(game,op,ctx):
 if op[0]!='historical_utility_attack_secret':return False
 owner=ctx['owner'];cid,source,target,state=op[1:]
 if cid in MONSTERS:
  if len(game.players[owner].board)>=7:return True
  candidates=game._generation_created_candidates(board_pool(pool(card_type='MINION',minimum=3,maximum=3)),ctx)
  if candidates:
   body=game._summon(owner,game.rng.choice(candidates),entry_origin='secret',entry_site='wandering_monster')
   if body is not None:state['target']=body.uid
 else:
  candidates=alternatives(game,source,target)
  if candidates:state['target']=game.rng.choice(candidates)
 game._log('attack_redirected',source=source,previous=target,target=state['target'],card=cid)
 return True
