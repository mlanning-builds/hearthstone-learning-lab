"""Remaining historical Spellstone families and physical held upgrades."""
from .identities import canonical_identity

def op(name,*args):return ('historical_utility_stone_finish_'+name,)+args
FORMS={
 'amethyst':({'LOOT_043':'LOOT_043t2','LOOT_043t2':'LOOT_043t3'},1),
 'pearl':({'LOOT_091':'LOOT_091t1','LOOT_091t1':'LOOT_091t2'},3),
 'mithril':({'LOOT_203':'LOOT_203t2','LOOT_203t2':'LOOT_203t3'},1),
 'obsidian':({'LOOT_503':'LOOT_503t','LOOT_503t':'LOOT_503t2'},3),
 'diamond':({'LOOT_507':'LOOT_507t','LOOT_507t':'LOOT_507t2'},4),
}
TOKEN_RULES={
 'LOOT_043':('minion',[('damage',3)]),'LOOT_043t2':('minion',[('damage',5)]),'LOOT_043t3':('minion',[('damage',7)]),
 'LOOT_091':('none',[('summon','LOOT_091t',1)]),'LOOT_091t1':('none',[('summon','LOOT_091t1t',1)]),'LOOT_091t2':('none',[('summon','LOOT_091t2t',1)]),
 'LOOT_091t':('none',[]),'LOOT_091t1t':('none',[]),'LOOT_091t2t':('none',[]),
 'LOOT_203':('none',[('summon','LOOT_203t4',1)]),'LOOT_203t2':('none',[('summon','LOOT_203t4',2)]),'LOOT_203t3':('none',[('summon','LOOT_203t4',3)]),'LOOT_203t4':('none',[]),
 'LOOT_503':('none',[('historical_utility_archive_destroy_sample',1)]),'LOOT_503t':('none',[('historical_utility_archive_destroy_sample',2)]),'LOOT_503t2':('none',[('historical_utility_archive_destroy_sample',3)]),
 'LOOT_507':('none',[op('diamond',2)]),'LOOT_507t':('none',[op('diamond',3)]),'LOOT_507t2':('none',[op('diamond',4)]),
 'ONY_016':('none',[('summon','BT_922t',2)]),'ONY_016t':('none',[('summon','BT_922t',3)]),'ONY_016t2':('none',[('summon','BT_922t',4)]),
 'DAL_008':('none',[op('scheme','armor')]),
 'DAL_011':('enemy_minion',[op('scheme','attack')]),
}
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)
SCHEMES={'DAL_007','DAL_008','DAL_011'}

def progress(game,owner,family,amount=1):
 if amount<=0:return
 forms,needed=FORMS[family]
 for c in tuple(game.players[owner].hand):
  if c.card_id not in forms:continue
  state=game._b60_state(c);key='historical_finish_'+family;value=state.get(key,0)+amount
  if value>=needed:
   c.card_id=forms[c.card_id];state[key]=0
  else:state[key]=value

def event(game,kind,data):
 if kind=='damage' and data.get('target',0)<0 and data.get('amount',0)>0 and data.get('damage_cause')!='fatigue':
  owner=-data['target']-1
  if data.get('damage_owner')==owner:progress(game,owner,'amethyst')
 elif kind=='historical_healed' and data.get('healer') in (0,1):progress(game,data['healer'],'pearl',data.get('restored',0))
 elif kind=='historical_weapon_equipped':progress(game,data['owner'],'mithril')
 elif kind=='spell_cast':progress(game,data['owner'],'diamond')

def paid(game,owner,cid):
 if 'DEATHRATTLE' in game.cards[cid].get('mechanics',()):progress(game,owner,'obsidian')

def turn_entries(game,phase):
 if phase!='start':return []
 return [dict(source=None,order=c.uid,operations=(op('tick',c.uid),)) for c in game.players[game.current].hand if c.card_id in SCHEMES]

def split(game,operation,ctx):
 if operation[0]!=op('diamond')[0]:return None
 owner=ctx['owner'];values=list(game.players[owner].death_records);selected=[]
 for _ in range(operation[1]):
  if not values:break
  r=game.rng.choice(values);selected.append(r['card_id']);identity=canonical_identity(game.cards[r['card_id']],game.cards)
  values=[other for other in values if canonical_identity(game.cards[other['card_id']],game.cards)!=identity]
 operations=tuple(('summon',cid,1) for cid in selected)
 if not operations:return ('batch30_noop',),()
 first,tail=game._split_fixed_summon(operations[0],ctx)
 return first,tuple(tail)+operations[1:]

def execute(game,operation,ctx):
 name=operation[0];owner=ctx['owner'];p=game.players[owner]
 if name==op('tick')[0]:
  c=next((c for c in p.hand if c.uid==operation[1] and c.card_id in SCHEMES),None)
  if c is not None:
   state=game._b60_state(c)
   if state.get('historical_finish_scheme_tick')!=game.turn:
    state['historical_finish_scheme_tick']=game.turn;state['historical_finish_scheme_age']=state.get('historical_finish_scheme_age',0)+1
  return True
 if name==op('scheme')[0]:
  c=ctx.get('physical_card');amount=1+getattr(c,'rule_state',{}).get('historical_finish_scheme_age',0)
  if operation[1]=='armor':game._gain_armor(owner,amount)
  else:game._effect(('historic_temporary_attack','target',-amount,'next_start'),ctx)
  return True
 return False
