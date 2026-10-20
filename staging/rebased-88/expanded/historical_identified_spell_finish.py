"""Physical Unidentified spell families and their explicit identified outcomes."""
from copy import deepcopy

FORMS={
 'DAL_366':tuple('DAL_366t'+str(i) for i in range(1,5)),
 'LOOT_278':tuple('LOOT_278t'+str(i) for i in range(1,5)),
 'LOOT_285':('LOOT_285t','LOOT_285t2','LOOT_285t3','LOOT_285t4'),
}
def op(name,*args):return ('historical_utility_identified_'+name,)+args
TOKEN_RULES={
 'DAL_366':('minion',[('destroy',)]),
 'DAL_366t1':('minion',[('destroy',),('summon','EX1_522',1)]),
 'DAL_366t2':('minion',[op('recruit')]),
 'DAL_366t3':('minion',[('destroy',),('add','GAME_005',2)]),
 'DAL_366t4':('minion',[op('turncoat')]),
 'LOOT_278':('minion',[('buff',2,2)]),
 'LOOT_278t1':('minion',[('buff',2,2),('keyword','LIFESTEAL')]),
 'LOOT_278t2':('minion',[('buff',2,2),('keyword','DIVINE_SHIELD')]),
 'LOOT_278t3':('minion',[('buff',2,2),op('shadow')]),
 'LOOT_278t4':('minion',[('buff',2,2),op('hope')]),
 'LOOT_285':('none',[('armor',5)]),
 'LOOT_285t':('none',[('armor',5),('armor',10)]),
 'LOOT_285t2':('character',[('armor',5),('damage',5)]),
 'LOOT_285t3':('none',[('armor',5),('summon','LOOT_285t3t',1)]),
 'LOOT_285t4':('none',[('armor',5),('equip','LOOT_285t4t')]),
 'LOOT_285t3t':('none',[]),
 'LOOT_285t4t':('none',[]),
}
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

def identify(game,card):
 forms=FORMS.get(card.card_id)
 if forms:
  from .pools import require_fixed_cards
  require_fixed_cards(forms,game.cards)
  card.card_id=game.rng.choice(forms)

def split(game,operation,ctx):
 name=operation[0]
 if name not in (op('recruit')[0],op('turncoat')[0]):return None
 target=game._force_live(ctx.get('target'))
 if target is None:return ('batch30_noop',),()
 snapshot=deepcopy(target)
 if name==op('recruit')[0]:
  return ('destroy',),(('historical_copy_target_snapshot',snapshot,'hand',1,None,None,None,False),)
 board=game.players[target.owner].board;index=board.index(target)
 victims=tuple(board[i].uid for i in (index-1,index+1) if 0<=i<len(board) and board[i] in game.players[target.owner].minions)
 return ('destroy',),(op('adjacent',snapshot,victims,target.attack,tuple(game._effective_keywords(target))),)

def execute(game,operation,ctx):
 prefix='historical_utility_identified_'
 if not operation[0].startswith(prefix):return False
 name=operation[0][len(prefix):];owner=ctx['owner']
 if name=='shadow':
  target=game._force_live(ctx.get('target'))
  if target is not None:game._summon(owner,target.card_id,copy_from=target,entry_stats=(1,1),entry_origin='copy',entry_site='elixir_of_shadows')
 elif name=='hope':
  target=game._force_live(ctx.get('target'))
  if target is not None:target.attached_death_effects.append(op('return'));target.keywords.add('DEATHRATTLE')
 elif name=='return':
  source=ctx.get('source')
  if source is not None and not source.rule_state.get('historical_identified_returned'):
   source.rule_state['historical_identified_returned']=True
   if source in game.players[source.owner].minions:game._bounce(source)
   else:game._enter_hand(owner,game._fresh_replay_card(source))
 elif name=='adjacent':
  source,victims,amount,keywords=operation[1:]
  with game._damage_batch():
   for uid in victims:
    dealt=game._damage(uid,amount,'POISONOUS' in keywords,damage_source=source,damage_owner=source.owner)
    if dealt and 'LIFESTEAL' in keywords:game._heal(game.hero_id(source.owner),dealt,healer=source.owner)
 else:return False
 return True
