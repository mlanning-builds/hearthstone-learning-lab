"""Last historical spell-root families with explicit generated dependencies."""
from copy import deepcopy
from collections import defaultdict,deque
from engine.game import Card
from engine.cards import UnsupportedCard
from .generation_cards import pool,board_pool
from .selectors import has_class,has_tribe,HERO_CLASSES
from .pools import require_fixed_cards

PREFIX='historical_utility_final_roots_'
def op(name,*args):return (PREFIX+name,)+args
ALLIANCE=('LOE_077','EX1_559','EX1_350','EX1_383','AT_072')
HORDE=('BAR_080','EX1_110','EX1_016','RLK_593','EX1_414')
TWOS=board_pool(pool(card_type='MINION',minimum=2,maximum=2))
TOKEN_RULES={
 'AV_400':('none',[('historical_utility_aura_finish_aura','graveyard')]),
 'GDB_140':('none',[('historical_utility_aura_finish_aura','celestial')]),
 'BOT_912':('none',[op('kangor')]),
 'GDB_233':('none',[op('dwarf',TWOS)]),
 'ONY_033':('none',[op('impfestation')]),
 'AV_316t':('none',[]),
 'OG_118':('none',[op('darkness',False)]),
 'VAC_941':('none',[op('darkness',True)]),
 'WON_113':('none',[op('champions')]),
 'WON_113a':('none',[op('champion_side','alliance')]),
 'WON_113b':('none',[op('champion_side','horde')]),
}
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

def sequence(game,ctx,operations):
 operations=tuple(operations)
 if not operations:return ('batch30_noop',),()
 first,tail=game._split_fixed_summon(operations[0],ctx)
 return first,tuple(tail)+operations[1:]

def requests_for(game,cid,owner):
 if cid=='OG_118':return {pool(classes=hero) for hero in HERO_CLASSES if hero!='WARLOCK'}
 if cid=='VAC_941':return {pool(classes='WARLOCK')}
 return set()

def split(game,operation,ctx):
 name=operation[0];owner=ctx['owner'];p=game.players[owner]
 if name==op('dwarf')[0]:
  values=game._generation_created_candidates(operation[1],ctx)
  if not values:return ('batch30_noop',),()
  state=dict(summoned=[],mode='random_enemy_character')
  return sequence(game,ctx,[op('dwarf_one',tuple(values),state)]*max(0,7-len(p.board))+[('force_group_attacks',state)])
 if name==op('impfestation')[0]:
  require_fixed_cards(('AV_316t',),game.cards)
  return sequence(game,ctx,(op('imp_pair',m.uid) for m in tuple(game.players[1-owner].minions) if m.health>0))
 if name==op('imp_pair')[0]:
  if game._force_live(operation[1]) is None or len(p.board)>=7:return ('batch30_noop',),()
  state=dict(summoned=[],target=operation[1])
  return op('imp_summon',state),(op('imp_attacks',state),)
 if name==op('imp_attacks')[0]:
  state=operation[1]
  return sequence(game,ctx,(('force_pair',uid,state['target']) for uid in state['summoned']))
 if name==op('kangor')[0]:
  records=defaultdict(deque)
  for record in p.death_records:records[record['card_id']].append(record['entity'])
  eligible=[]
  for cid in p.death_history:
   entity=records[cid].popleft() if records[cid] else cid
   if has_tribe(game._card_data(cid),'MECHANICAL'):eligible.append(entity)
  selected=game.rng.sample(eligible,min(3,len(eligible)))
  return sequence(game,ctx,(op('mech_return',deepcopy(entity)) for entity in selected))
 return None

def celestial_bonuses(game,desired):
 """Snapshot the set-stat adjustment on activation, rather than heal each tick.

 The developer-confirmed rule preserves prior damage and permits later buffs.
 A second minion detaches the adjustment; returning to one creates a new one.
 """
 from .historical_aura_finish_batch import layers
 for owner,p in enumerate(game.players):
  active=[m for m in p.minions if m.health>0 and not m.dormant]
  for aura in layers(game,owner,'celestial'):
   target=active[0] if len(active)==1 else None
   if target is None:
    aura.pop('celestial_target',None);aura.pop('celestial_adjustment',None);continue
   if aura.get('celestial_target')!=target.uid:
    attack,health=desired[target.uid]
    aura['celestial_target']=target.uid
    aura['celestial_adjustment']=(10-(target.attack-target.aura_attack+attack),10-(target.max_health-target.aura_health+health))
   attack,health=aura['celestial_adjustment']
   desired[target.uid][0]+=attack;desired[target.uid][1]+=health

def execute(game,operation,ctx):
 if not operation[0].startswith(PREFIX):return False
 name=operation[0][len(PREFIX):];owner=ctx['owner'];p=game.players[owner]
 if name=='dwarf_one':
  values,state=operation[1:]
  if len(p.board)<7:
   cid=game.rng.choice(values);before={m.uid for m in p.minions}
   game._summon(owner,cid,entry_origin='effect',entry_site='dwarf_planet')
   state['summoned'].extend(m.uid for m in p.minions if m.uid not in before)
 elif name=='imp_summon':
  state=operation[1];before={m.uid for m in p.minions}
  game._summon(owner,'AV_316t',entry_origin='effect',entry_site='impfestation')
  state['summoned'].extend(m.uid for m in p.minions if m.uid not in before)
 elif name=='mech_return':
  entity=operation[1];cid=getattr(entity,'card_id',entity)
  card=game._fresh_replay_card(entity)
  before={m.uid for m in p.minions}
  game._summon(owner,cid,entry_source=card,entry_zone='hand',entry_origin='resurrection',entry_site='kangors_endless_army')
  parts=getattr(entity,'_magnetic_upgrades',())
  for minion in tuple(p.minions):
   if minion.uid in before:continue
   for part,grants in parts:
    physical=game._copy_card(part,source_owner=owner)
    game._magnetic_attach(physical,owner,p.board.index(minion),grants,notify=False)
 elif name=='darkness':
  announce=operation[1]
  from .historical_copy_batches import BASIC_POWERS
  heroes=('WARLOCK',) if announce else tuple(sorted(HERO_CLASSES-{'WARLOCK'}))
  # Resolve every possible class pool before the random class selection.
  candidates={hero:game._generation_created_candidates(pool(classes=hero),ctx) for hero in heroes}
  require_fixed_cards(tuple(BASIC_POWERS[hero] for hero in heroes),game.cards)
  hero=heroes[0] if len(heroes)==1 else game.rng.choice(heroes)
  values=candidates[hero]
  if not values:raise UnsupportedCard('Darkness replacement class has no collectible cards')
  game._replace_primary_power(owner,dict(card_id=BASIC_POWERS[hero],basic_starting_class=hero,cost=game.cards[BASIC_POWERS[hero]]['cost']))
  for zone_name in ('hand','deck'):
   zone=getattr(p,zone_name)
   for index,old in enumerate(zone):
    warlock=has_class(game._card_data(old),'WARLOCK')
    if warlock==announce:continue
    card=Card(game._new_id(),game.rng.choice(values));card.cost_delta=-1
    game._carry_origin(old,card)
    if zone_name=='hand':card._hand_entry_turn=getattr(old,'_hand_entry_turn',game.turn)
    zone[index]=card
  game._refresh_auras()
 elif name=='champions':
  require_fixed_cards(ALLIANCE+HORDE,game.cards)
  if game.pending_choice is not None:raise UnsupportedCard('Cannot overwrite faction choice')
  game.pending_choice=dict(owner=owner,kind='historical_final_roots',options=[dict(card_id='WON_113a',side='alliance'),dict(card_id='WON_113b',side='horde')],context=dict(ctx));game.phase='choice'
 elif name=='champion_side':
  ids=ALLIANCE if operation[1]=='alliance' else HORDE
  require_fixed_cards(ids,game.cards)
  for _ in range(2):
   card=Card(game._new_id(),game.rng.choice(ids));card.cost_delta=-2;game._enter_hand(owner,card)
 else:return False
 return True

def resolve_choice(game,choice,selected):
 if choice['kind']!='historical_final_roots':return False
 execute(game,op('champion_side',selected['side']),choice['context'])
 return True
