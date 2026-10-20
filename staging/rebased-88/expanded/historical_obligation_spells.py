"""Physical obligations for historical spells, independent of their sources.

Private payloads hold physical snapshots; public rule operands carry only keys.
Turn-limited obligations expire by the global turn, even after control changes.
"""
from copy import deepcopy
from engine.game import Card
from engine.cards import UnsupportedCard
from .generation_cards import pool,discover

PREFIX='historical_utility_obligation_'
def op(name,*args):return (PREFIX+name,)+args
TOKEN_RULES={
 'BAR_323':('none',[op('yoink')]),
 'YOP_024':('none',[op('guidance')]),
 'YOP_024t':('none',[op('guidance_both')]),
 'BT_753':('none',[op('mana_burn')]),
 'NEW1_036':('none',[op('shout'),('draw',1)]),
 'AV_269':('none',[op('flanking')]),
 'AV_269t':('none',[]),
 'DMF_224':('none',[op('performers')]),
 'BT_036t':('none',[]),
 'DMF_249':('none',[op('acrobatics')]),
 'SCH_305':('none',[op('passage')]),
 'ULD_286':('minion',[op('shadows')]),
 'ULD_286t':('none',[op('shadow_summon')]),
 'GDB_873':('none',[discover(pool(card_type='MINION',mechanic='COMBO',classes='own_or_neutral')),op('comet')]),
}
CAST_EFFECTS={'ULD_286t':(op('shadow_summon'),)}
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

def sequence(game,ctx,operations):
 operations=tuple(operations)
 if not operations:return ('batch30_noop',),()
 first,tail=game._split_fixed_summon(operations[0],ctx)
 return first,tuple(tail)+operations[1:]

def queue(game,owner,operations,cid):
 game._rule_events.append(('captured_effects',dict(operations=tuple(operations),context=dict(owner=owner,source=None,target=0,bonus=0,lifesteal=False,card_id=cid)),[]))

def split(game,operation,ctx):
 name=operation[0];owner=ctx['owner'];p=game.players[owner]
 if name==op('acrobatics')[0]:
  states=({},{});key=game._new_id()
  state=dict(key=key,turn=game.turn,remaining=set(),draws=states)
  tasks=getattr(p,'_historical_acrobatics',[]);tasks.append(state);p._historical_acrobatics=tasks
  return sequence(game,ctx,(('historical_draw_capture',None,'random',states[0]),('historical_draw_capture',None,'random',states[1]),op('acrobatics_arm',key)))
 if name==op('passage')[0]:
  saved=p.hand;p.hand=[]
  # Being set aside removes the hand-granted Temporary enchantment.
  for card in saved:
   if 'TEMPORARY' not in game._card_mechanics(card):getattr(card,'rule_state',{}).pop('temporary',None)
  key=game._new_id();tasks=getattr(p,'_historical_passages',{});first=not tasks
  tasks[key]=dict(hand=saved,borrowed=set());p._historical_passages=tasks
  # Passage moves cards; it is not four draws and does not trigger on-draw rules.
  count=min(4,len(p.deck));chosen=game.rng.sample(range(len(p.deck)),count)
  moved=[]
  for index in sorted(chosen,reverse=True):
   card=p.deck.pop(index)
   if not isinstance(card,Card):card=Card(game._new_id(),card)
   moved.append(card)
  game.rng.shuffle(moved)
  for card in moved:
   tasks[key]['borrowed'].add(card.uid);game._enter_hand(owner,card)
  # The earliest Passage retains its ordinary trigger position. Nested
  # Passages unwind together in reverse order when that trigger resolves.
  if first:game._schedule_turn_effect(game.current,'end',0,1,(op('passage_restore',key,owner),),source_card_id='SCH_305')
  game._refresh_auras()
  return ('batch30_noop',),()
 if name in (op('flanking')[0],op('performers')[0]):
  kind='flanking' if name==op('flanking')[0] else 'performers'
  key=game._new_id();state=dict(key=key,kind=kind,turn=game.turn,remaining=set(),armed=False,created=0)
  tasks=getattr(p,'_historical_summon_obligations',[]);tasks.append(state);p._historical_summon_obligations=tasks
  return sequence(game,ctx,[op('watched_summon','AV_269t' if kind=='flanking' else 'BT_036t',key)]*(1 if kind=='flanking' else 7)+[op('summon_arm',key)])
 return None

def summoned(game,minion):
 p=game.players[minion.owner]
 if getattr(p,'historical_shout_turn',None)==game.turn:
  minion.rule_state['historical_shout_turn']=game.turn

def paid(game,owner,card):
 p=game.players[owner]
 for task in tuple(getattr(p,'_historical_acrobatics',())):
  if task['turn']!=game.turn:continue
  if card.uid in task['remaining']:
   task['remaining'].remove(card.uid)
   if not task['remaining']:
    p._historical_acrobatics.remove(task)
    queue(game,owner,(('draw',2),),'DMF_249')

def event(game,kind,data):
 if kind!='minion_died':return
 uid=data['source']
 # The spell's owner retains the obligation if a watched minion changes sides.
 for owner,p in enumerate(game.players):
  for task in tuple(getattr(p,'_historical_summon_obligations',())):
   if task['turn']!=game.turn or uid not in task['remaining']:continue
   task['remaining'].remove(uid)
   if task['kind']=='flanking':
    queue(game,owner,(('summon','AV_269t',1),),'AV_269')
   elif task['armed'] and not task['remaining']:
    queue(game,owner,(('summon','BT_036t',7),),'DMF_224')
   if not task['remaining'] and (task['kind']=='flanking' or task['armed']):p._historical_summon_obligations.remove(task)

def execute(game,operation,ctx):
 if not operation[0].startswith(PREFIX):return False
 name=operation[0][len(PREFIX):];owner=ctx['owner'];p=game.players[owner]
 if name=='yoink':
  from .historical_copy_batches import BASIC_POWERS
  from .pools import require_fixed_cards
  require_fixed_cards(tuple(BASIC_POWERS.values()),game.cards)
  if game.pending_choice is not None:raise UnsupportedCard('Cannot overwrite Yoink choice')
  values=[dict(card_id=cid,hero_class=hero) for hero,cid in BASIC_POWERS.items() if hero!=p.hero_class]
  game.pending_choice=dict(owner=owner,kind='historical_obligation',mode='yoink',context=dict(ctx),options=game.rng.sample(values,min(3,len(values))))
  game.phase='choice'
 elif name=='yoink_used':
  power=p.primary_power
  if power is not None and power.get('uid')==operation[1] and 'yoink_remaining' in power:
   power['yoink_remaining']-=1
   if power['yoink_remaining']<=0:game._replace_primary_power(owner,power['yoink_restore'])
 elif name=='guidance':
  if game.pending_choice is not None:raise UnsupportedCard('Cannot overwrite Guidance choice')
  values=game._generation_discover_candidates(pool(card_type='SPELL',classes='own_or_neutral'),ctx)
  offered=tuple(game.rng.sample(list(values),min(2,len(values))))
  if offered:
   options=[dict(card_id=cid,both=False) for cid in offered]
   options.append(dict(card_id='YOP_024t',both=True))
   game.pending_choice=dict(owner=owner,kind='historical_obligation',mode='guidance',context=dict(ctx),offered=offered,options=options)
   game.phase='choice'
 elif name=='guidance_both':
  payload=getattr(ctx.get('physical_card'),'_historical_guidance_spells',None)
  if payload is None:raise UnsupportedCard('Spirit Path requires its captured Guidance offer')
  for cid in payload:game._add(owner,cid)
  from .historical_resource_batches import add_overload
  add_overload(game,owner,1)
 elif name=='mana_burn':
  other=game.players[1-owner]
  other.historical_mana_burn_next=getattr(other,'historical_mana_burn_next',0)+2
 elif name=='shout':
  p.historical_shout_turn=game.turn
  for minion in p.minions:minion.rule_state['historical_shout_turn']=game.turn
 elif name=='acrobatics_arm':
  task=next(t for t in p._historical_acrobatics if t['key']==operation[1])
  task['remaining']={state['card'].uid for state in task.pop('draws') if state.get('card') is not None}
  # Fewer than two actual draws can never satisfy 'both'.
  if len(task['remaining'])!=2:p._historical_acrobatics.remove(task)
 elif name=='passage_restore':
  key,recipient=operation[1:];player=game.players[recipient]
  tasks=getattr(player,'_historical_passages',{})
  if key in tasks:
   for pending in reversed(tuple(tasks)):
    task=tasks.pop(pending)
    returned=[card for card in player.hand if card.uid in task['borrowed']]
    player.hand[:]=[card for card in player.hand if card.uid not in task['borrowed']]
    player.deck.extend(returned)
    if returned:game.rng.shuffle(player.deck)
    for card in task['hand']:game._enter_hand(recipient,card)
   game._refresh_auras()
 elif name=='watched_summon':
  cid,key=operation[1:];task=next(t for t in p._historical_summon_obligations if t['key']==key)
  before={m.uid for m in p.all_minions}
  game._summon(owner,cid,entry_origin='effect',entry_site=ctx.get('card_id'))
  added={m.uid for m in p.all_minions if m.uid not in before}
  task['remaining'].update(added);task['created']+=len(added)
 elif name=='summon_arm':
  task=next((t for t in getattr(p,'_historical_summon_obligations',()) if t['key']==operation[1]),None)
  if task is not None:
   task['armed']=True
   if not task['remaining']:
    p._historical_summon_obligations.remove(task)
    if task['kind']=='performers' and task['created']:queue(game,owner,(('summon','BT_036t',7),),'DMF_224')
 elif name=='shadows':
  minion=game._force_live(ctx.get('target'))
  if minion is not None:
   cards=[]
   for _ in range(3):
    card=Card(game._new_id(),'ULD_286t');card._historical_shadow=deepcopy(minion);cards.append(card)
   p.deck.extend(cards);game.rng.shuffle(p.deck)
   game._record_deck_insertion(owner,owner,len(cards),'shuffle',cards=tuple(cards))
 elif name=='shadow_summon':
  card=ctx.get('physical_card');minion=getattr(card,'_historical_shadow',None)
  if minion is None:raise UnsupportedCard('Shadow requires its captured physical minion')
  game._summon(owner,minion.card_id,copy_from=minion,entry_origin='copy',entry_site='shadow_of_death')
 elif name=='comet':p.historical_comet_charges=getattr(p,'historical_comet_charges',0)+1
 else:return False
 return True


def resolve_choice(game,choice,selected):
 if choice['kind']!='historical_obligation':return False
 owner=choice['owner'];p=game.players[owner]
 if choice['mode']=='yoink':
  restore=deepcopy(p.primary_power)
  game._replace_primary_power(owner,dict(card_id=selected['card_id'],basic_starting_class=selected['hero_class'],cost=0,yoink_remaining=2,yoink_restore=restore))
 elif choice['mode']=='guidance':
  values=choice['offered'] if selected['both'] else (selected['card_id'],)
  for cid in values:game._add(owner,cid)
  if selected['both']:
   from .historical_resource_batches import add_overload
   add_overload(game,owner,1)
   physical=choice['context'].get('physical_card')
   if physical is not None:
    game._b60_state(physical)['historical_guidance_overload']=True
    pending=getattr(p,'historical_play_overloads',{})
    if physical.uid in pending:
     pending[physical.uid]+=1
     if p.played_history and p.played_history[-1]['card_id']=='YOP_024':p.played_history[-1]['overload_card']=True
 else:return False
 return True
