"""Explicit iconic-hand Secrets, held upgrades and resumable choices."""
TOKEN_RULES={
 'LOOT_051':('minion',[('damage',2)]),
 'LOOT_051t1':('minion',[('damage',4)]),
 'LOOT_051t2':('minion',[('damage',6)]),
 'LOOT_080':('none',[('summon','LOOT_077t',2)]),
 'LOOT_080t2':('none',[('summon','LOOT_077t',3)]),
 'LOOT_080t3':('none',[('summon','LOOT_077t',4)]),
 'LOOT_077t':('none',[]),
 'LOOT_054':('none',[('historical_utility_paths',2)]),
 'LOOT_054b':('none',[('board_buff',1,0)]),
 'LOOT_054c':('none',[('armor',6)]),
 'LOOT_054d':('none',[('draw',1)]),
 'ICC_054':('none',[('historical_utility_plague',)]),
 'EX1_295':('none',[('secret','EX1_295')]),
 'VAN_EX1_295':('none',[('secret','VAN_EX1_295')]),
}
JASPER={'LOOT_051':'LOOT_051t1','LOOT_051t1':'LOOT_051t2'}
EMERALD={'CORE_FB_Champs_LOOT_080':'LOOT_080t2','LOOT_080':'LOOT_080t2','LOOT_080t2':'LOOT_080t3'}
PATHS={'LOOT_054d':(('draw',1),),'LOOT_054b':(('board_buff',1,0),),'LOOT_054c':(('armor',6),)}

def split(game,op,ctx):
 if op[0]=='historical_utility_plague':
  if len(game.players[ctx['owner']].board)>=7:return ('batch30_noop',),()
  return ('summon','ICC_832t4',1),(('historical_utility_plague_again',),)
 if op[0]=='historical_utility_plague_again':
  p=game.players[ctx['owner']];q=game.players[1-ctx['owner']]
  return split(game,('historical_utility_plague',),ctx) if len(p.minions)<len(q.minions) and len(p.board)<7 else (('batch30_noop',),())
 return None

def execute(game,op,ctx):
 owner=ctx['owner'];p=game.players[owner]
 if op[0]=='historical_utility_paths':
  if op[1]<=0:return True
  from .pools import require_fixed_cards
  from engine.cards import UnsupportedCard
  require_fixed_cards(PATHS,game.cards)
  if game.pending_choice is not None:raise UnsupportedCard('Branching Paths cannot overwrite a choice')
  game.pending_choice=dict(owner=owner,kind='historical_utility_paths',remaining=op[1],context=dict(ctx),options=[dict(card_id=cid) for cid in PATHS],_automatic=bool(ctx.get('automatic_choices',False)))
  game.phase='choice'
 elif op[0]=='historical_utility_ice_block':
  p.historical_ice_block_turn=game.turn
  game._log('immune',player=owner,until_turn=game.turn,source='EX1_295')
 else:return False
 return True

def resolve_choice(game,choice,selected):
 if choice['kind']!='historical_utility_paths':return False
 from engine.cards import UnsupportedCard
 cid=selected.get('card_id')
 if cid not in PATHS:raise UnsupportedCard('Invalid Branching Paths option')
 operations=PATHS[cid]+((('historical_utility_paths',choice['remaining']-1),) if choice['remaining']>1 else ())
 game._rule_events.append(('captured_effects',dict(operations=operations,context=dict(choice['context'])),[]))
 return True

def prevent_fatal(game,owner,amount):
 if owner==game.current:return False
 from .historical_secret_batches import blocked
 if blocked(game):return False
 p=game.players[owner]
 if amount<p.health+p.armor or game._onyxia_active(owner):return False
 for secret in tuple(p.secrets):
  if secret.card_id not in ('EX1_295','VAN_EX1_295'):continue
  game._trigger_secret_program(owner,secret,(('historical_utility_ice_block',),),dict(owner=owner,source=None,target=0,bonus=0,lifesteal=False,card_id=secret.card_id))
  game._log('prevent_damage',player=owner,amount=amount,card=secret.card_id)
  return True
 return False
