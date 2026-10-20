"""Physical Starship assembly and launch; implementation-only, unvalidated.

Assembly uses printed/base definitions, never a dying piece's damage or ordinary
buffs. Piece rules are admitted separately; this module does not prune pools.
"""
from copy import deepcopy
from engine.game import Card,Action
from engine.cards import UnsupportedCard
from .permanents import Permanent

CONSTRUCTION='GDB_100t1'
NAMES={'DEATHKNIGHT':'GDB_100t4','DEMONHUNTER':'GDB_100t5','DRUID':'GDB_100t6','HUNTER':'GDB_100t7','ROGUE':'GDB_100t8','WARLOCK':'GDB_100t9'}
STARSHIPS=frozenset(NAMES.values())|{'GDB_100t2','SC_999t'}
TOKEN_IDS=STARSHIPS|{CONSTRUCTION}


def building(game,owner):
 return next((obj for obj in game.players[owner].permanents if hasattr(obj,'_historical_ship_parts')),None)


def launch_cost(game,owner):
 return max(0,5-getattr(game.players[owner],'historical_ship_discount',0))


def definition(game,parts):
 from .base_stats import base_stats
 attack=health=0;keywords={'STARSHIP'}
 for cid in parts:
  a,h=base_stats(game,cid)
  attack+=a;health+=h
  keywords.update(game.cards[cid].get('mechanics',()))
 keywords.difference_update(('STARSHIP_PIECE','BATTLECRY','TRIGGER_VISUAL','AURA'))
 return dict(parts=tuple(parts),attack=attack,health=max(1,health),keywords=tuple(sorted(keywords)))


def ensure_building(game,owner,position=-1):
 player=game.players[owner];parts=getattr(player,'_historical_ship_pending',())
 if not parts:return None
 obj=building(game,owner)
 if obj is None:
  if len(player.board)>=7:return None
  obj=Permanent(game._new_id(),CONSTRUCTION,owner)
  obj._historical_ship_parts=tuple(parts)
  player.board.insert(len(player.board) if position<0 else min(position,len(player.board)),obj)
  game._log('starship_construction_started',player=owner,entity=obj.uid)
 else:obj._historical_ship_parts=tuple(parts)
 return obj


def capture_piece(game,minion,position=-1):
 if minion.silenced or 'STARSHIP_PIECE' not in game._card_data(minion).get('mechanics',()):return
 owner=minion.owner;player=game.players[owner]
 player._historical_ship_pending=tuple(getattr(player,'_historical_ship_pending',()))+(minion.card_id,)
 ensure_building(game,owner,position)
 game._log('starship_piece_assembled',player=owner,card=minion.card_id)


def actions(game):
 owner=game.current;obj=building(game,owner)
 if obj is None or game.players[owner].mana<launch_cost(game,owner):return []
 return [Action('activate',obj.uid)]


def activate(game,action):
 owner=game.current;player=game.players[owner];obj=building(game,owner)
 if obj is None or action.source!=obj.uid:raise ValueError('Missing Starship construction')
 cost=launch_cost(game,owner)
 if player.mana<cost:raise ValueError('Not enough mana to launch')
 player.mana-=cost;game._b60_spend_mana(owner,cost)
 player.historical_ship_discount=0
 game._start_play_effects((('historical_ship_launch',),),dict(owner=owner,source=None,target=0,bonus=0,lifesteal=False))


def launch(game,owner):
 from .pools import require_fixed_cards
 player=game.players[owner];obj=building(game,owner)
 if obj is None:return None
 parts=tuple(obj._historical_ship_parts)
 require_fixed_cards(parts,game.cards)
 data=definition(game,parts)
 cid='SC_999t' if any(part.startswith('SC_') for part in parts) else NAMES.get(player.hero_class,'GDB_100t2')
 require_fixed_cards((cid,),game.cards)
 card=Card(game._new_id(),cid);card._historical_ship_definition=data
 card.base_stat_override=(data['attack'],data['health'])
 position=player.board.index(obj);player.board.remove(obj)
 player._historical_ship_pending=()
 player.historical_ship_discount=0
 player.historical_ship_launches=getattr(player,'historical_ship_launches',0)+1
 result=game._summon(owner,cid,position=position,entry_origin='starship_launch',entry_site='starship',entry_source=card)
 if result is not None:
  history=getattr(player,'_historical_launched_ships',[]);history.append(deepcopy(card));player._historical_launched_ships=history
  programs=[program for piece in parts for program in (LAUNCH_EFFECTS.get(piece),) if program]
  game.rng.shuffle(programs)
  operations=tuple(effect for program in programs for effect in program)
  if operations:
   context=dict(owner=owner,source=result,target=0,bonus=0,lifesteal=False,card_id=cid)
   game._rule_events.append(('captured_effects',dict(operations=operations,context=context),[]))
 game._log('starship_launched',player=owner,card=cid,pieces=len(parts))
 return result


def initialize(game,minion,entry_source,copy_from):
 if minion is None:return
 data=getattr(entry_source,'_historical_ship_definition',None)
 if copy_from is not None:return
 if data is None:return
 minion._historical_ship_definition=deepcopy(data)
 minion.rule_state['historical_ship_parts']=tuple(data['parts'])
 minion.keywords.update(data['keywords'])
 for cid in data['parts']:
  minion.attached_death_effects.extend(deepcopy(game._printed_death_operations(cid)))


def view(game,obj):
 if not hasattr(obj,'_historical_ship_parts'):return {}
 data=definition(game,obj._historical_ship_parts)
 return dict(starship_pieces=list(data['parts']),attack=data['attack'],health=data['health'],launch_cost=launch_cost(game,obj.owner))


def execute(game,op,ctx):
 name=op[0];owner=ctx['owner'];player=game.players[owner];source=ctx.get('source')
 if extra_effect(game,op,ctx):return True
 if name=='historical_ship_launch':launch(game,owner)
 elif name=='historical_ship_definition_required':
  if not hasattr(ctx.get('physical_card'),'_historical_ship_definition'):
   raise UnsupportedCard('A Starship requires its assembled physical definition')
 elif name=='historical_ship_welder':
  if building(game,owner) is not None and source is not None:game._buff(source,2,2)
 elif name=='historical_ship_discount':
  player.historical_ship_discount=getattr(player,'historical_ship_discount',0)+2
 elif name=='historical_ship_othaar':
  if building(game,owner) is not None:
   from .generation_cards import pool
   candidates=game._generation_candidates(pool(card_type='SPELL',school='ARCANE'),owner)
   for cid in game.rng.sample(list(candidates),min(3,len(candidates))):
    card=Card(game._new_id(),cid);card.cost_delta=-2;game._enter_hand(owner,card)
 elif name=='historical_ship_shipwright':
  from .generation_cards import pool
  candidates=game._generation_candidates(pool(card_type='MINION',mechanic='STARSHIP_PIECE',classes='other'),owner)
  if candidates:game._add(owner,game.rng.choice(candidates))
 else:return False
 return True

# Written explicitly from the frozen Starship Piece definitions.
SPELLBURST_PIECES={'GDB_104','GDB_106'}
TRIGGER_PIECES={'GDB_104':'historical_ship_thrusters','GDB_106':'historical_ship_guiding','GDB_107':'historical_ship_claw','GDB_108':'historical_ship_reactor','GDB_110':'historical_ship_battery'}
BATTLECRIES={'SC_405':(('historical_ship_capacitor',),),'SC_406':(('destroy_random_enemy',),),'SC_409':(('area_damage','enemies',1),)}
LAUNCH_EFFECTS=dict(BATTLECRIES,**{'GDB_466':(('historical_ship_displace',),),'SC_403a':(('armor',5),),'SC_403b':(('area_damage','enemy_minions',2),),'SC_403c':(('historical_ship_bonus',),),'SC_403d':(('damage_random_enemy',3),),'SC_403f':(('summon','SC_403t',2),)})
PROTOCOLS=('GDB_100a','GDB_100b','GDB_100c')


def components(minion):
 return tuple(minion.rule_state.get('historical_ship_parts',(minion.card_id,)))


def listeners(game):
 return [(m,(('historical_ship_trigger',index,cid),((TRIGGER_PIECES[cid],),)))
         for player in game.players for m in player.minions if m.health>0 and not m.silenced
         for index,cid in enumerate(components(m)) if cid in TRIGGER_PIECES]


def snapshot_spell(game,card,owner):
 card._historical_ship_spellburst_candidates=tuple((m.uid,index) for m in game.players[owner].minions if m.health>0 and not m.silenced
  for index,cid in enumerate(components(m)) if cid in SPELLBURST_PIECES and index not in m.rule_state.get('historical_ship_spellburst_used',()))


def matches(game,wanted,kind,data,minion):
 if not isinstance(wanted,tuple) or len(wanted)!=3 or wanted[0]!='historical_ship_trigger':return None
 index,cid=wanted[1:]
 if minion.silenced or minion.health<=0:return False
 if cid in SPELLBURST_PIECES:
  if kind!='spell_cast' or data['owner']!=minion.owner:return False
  if (minion.uid,index) not in getattr(data.get('physical_card'),'_historical_ship_spellburst_candidates',()):return False
  used=minion.rule_state.setdefault('historical_ship_spellburst_used',[])
  if index in used:return False
  used.append(index);return True
 if cid=='GDB_107':return kind=='minion_played' and data['owner']!=minion.owner
 if cid=='GDB_108':return kind=='spell_cast' and data['owner']==minion.owner and game.cards[data['card_id']].get('spellSchool')=='ARCANE'
 if cid=='GDB_110':return kind=='minion_attack' and data['source']==minion.uid
 return False


def cost_aura(game,card,owner,cost):
 if game._card_data(card)['type']!='SPELL' or getattr(game.players[owner],'historical_ship_spell_played_turn',None)==game.turn:return cost
 count=sum(components(m).count('GDB_103') for m in game.players[owner].minions if m.health>0 and not m.silenced)
 return cost-count


def split(game,op,ctx):
 name=op[0];owner=ctx['owner'];source=ctx.get('source');player=game.players[owner]
 if name=='historical_ship_tank':
  values=[m for m in game.players[1-owner].minions if m.health>0]
  if not values:return ('batch30_noop',),()
  minion=game.rng.choice(values)
  state=dict(target=minion.uid,excess=0,deployed=op[1])
  return ('historical_ship_tank_hit',state),(('historical_ship_tank_excess',state),)
 if name=='historical_ship_thor':
  repeats=getattr(player,'historical_ship_launches',0) if op[1] else 0
  operations=(('damage',5),)+tuple(('damage_random_enemy',5) for _ in range(repeats))
  head,tail=game._split_fixed_summon(operations[0],ctx)
  return head,tail+operations[1:]
 if name=='historical_ship_claw':
  target=ctx['event'].get('source')
  if source is None or game._force_live(source.uid) is None or game._force_live(target) is None:return ('batch30_noop',),()
  return game._force_split(('force_pair',source.uid,target),ctx)
 if name=='historical_ship_reactor':
  card=ctx['event'].get('physical_card')
  if card is None:return ('batch30_noop',),()
  return game._split_fixed_summon(('cast_physical_spell',game._copy_card(card,source_owner=owner),'random'),ctx)
 if name=='historical_ship_thrusters':
  if source is None:return ('batch30_noop',),()
  values=[m.uid for m in game.players[1-owner].minions if m.health>0]
  selected=game.rng.sample(values,min(2,len(values)))
  operations=tuple(('historical_ship_thruster_hit',uid,max(0,source.attack)) for uid in selected)
 elif name=='historical_ship_spire':
  if source is None:return ('batch30_noop',),()
  from .generation_cards import pool,board_pool
  candidates=game._generation_candidates(board_pool(pool(card_type='MINION',minimum=min(10,max(0,source.attack)),maximum=min(10,max(0,source.attack)))),owner)
  if not candidates:return ('batch30_noop',),()
  return game._split_fixed_summon(('summon',game.rng.choice(candidates),1),ctx)
 elif name=='historical_ship_battlecry':
  physical=ctx.get('physical_card');data=getattr(physical,'_historical_ship_definition',None)
  operations=tuple(effect for cid in (data or {}).get('parts',()) for effect in BATTLECRIES.get(cid,()))
 elif name=='historical_ship_exodar':
  if building(game,owner) is None:return ('batch30_noop',),()
  state={}
  return ('historical_ship_exodar_launch',state),(('historical_ship_exodar_choose',state),)
 elif name=='historical_ship_protocol':
  mode,state=op[1:]
  if mode=='GDB_100a':operations=(('armor',state['health']),)*2
  elif mode=='GDB_100b':operations=(('missiles','enemies',state['attack']),)
  else:operations=tuple(('historical_ship_crew',cid) for cid in state['parts'])
 else:return None
 if not operations:return ('batch30_noop',),()
 head,tail=game._split_fixed_summon(operations[0],ctx)
 return head,tail+operations[1:]


def extra_effect(game,op,ctx):
 name=op[0];owner=ctx['owner'];player=game.players[owner];enemy=game.players[1-owner];source=ctx.get('source')
 if name=='historical_ship_tank_hit':
  state=op[1];minion=game._force_live(state['target'])
  if minion is not None:
   before=minion.health;dealt=game._deal_effect(minion.uid,10,ctx)
   state['excess']=max(0,dealt-before)
 elif name=='historical_ship_tank_excess':
  if op[1]['deployed'] and op[1]['excess']>0:game._deal_effect(game.hero_id(1-owner),op[1]['excess'],ctx)
 elif name=='historical_ship_thruster_hit':
  victim=game._force_live(op[1])
  if victim is not None:game._deal_effect(victim.uid,op[2],ctx)
 elif name=='historical_ship_guiding':
  values=[m for m in player.minions if m.health>0 and game._death_operations(m)]
  if values:
   minion=game.rng.choice(values)
   game._rule_events.append(('captured_effects',dict(operations=tuple(game._death_operations(minion)),context=dict(owner=owner,source=minion,target=0,bonus=0,lifesteal=False)),[]))
 elif name=='historical_ship_battery':
  for minion in player.minions:
   if minion is not source:game._buff(minion,1,0)
 elif name=='historical_ship_biopod':
  if source is not None:
   target=game._force_target(owner,'random_enemy_character')
   if target:game._deal_effect(target,max(0,source.attack),ctx)
 elif name=='historical_ship_capacitor':
  if source in player.minions:game._buff(source,len(player.minions)-1,len(player.minions)-1)
 elif name=='historical_ship_displace':
  if source in player.minions:game._summon(owner,source.card_id,copy_from=source,entry_origin='starship_copy',entry_site='gravitational_displacer',entry_source=source)
 elif name=='historical_ship_bonus':
  if source in player.minions:game._grant_bonus_effects(source,2)
 elif name=='historical_ship_ghost':
  if building(game,owner) is not None and enemy.hand:
   minimum=min(game._cost(card,1-owner) for card in enemy.hand)
   card=game.rng.choice([card for card in enemy.hand if game._cost(card,1-owner)==minimum])
   enemy.hand.remove(card);game._zone_card_removed(1-owner,card,'hand','destroy');game._log('ghost_destroy',player=1-owner,card=card.card_id)
 elif name=='historical_ship_exodar_launch':
  ship=launch(game,owner)
  if ship is not None:op[1]['ship']=ship
 elif name=='historical_ship_exodar_choose':
  ship=op[1].get('ship')
  if ship is not None:
   state=dict(attack=max(0,ship.attack),health=max(0,ship.health),parts=tuple(getattr(ship,'_historical_ship_definition',{}).get('parts',())))
   if game.pending_choice is not None:raise UnsupportedCard('Cannot overwrite Exodar protocol choice')
   game.pending_choice=dict(owner=owner,kind='historical_ship_protocol',options=[dict(card_id=cid) for cid in PROTOCOLS],_state=state,_context=dict(ctx),_automatic=bool(ctx.get('automatic_choices',False)))
   game.phase='choice'
 elif name=='historical_ship_protocol_unbound':raise UnsupportedCard('Protocol requires its launched Starship context')
 elif name=='historical_ship_crew':
  card=Card(game._new_id(),op[1]);game._set_card_cost(card,1);game._enter_hand(owner,card)
 else:return False
 return True


def resolve_choice(game,choice,selected):
 if choice['kind']!='historical_ship_protocol':return False
 game._rule_events.append(('captured_effects',dict(operations=(('historical_ship_protocol',selected['card_id'],choice['_state']),),context=choice['_context']),[]))
 return True

TERRAN_FORMS={'SC_412':'SC_412t','SC_413':'SC_413t','SC_414':'SC_414t'}
TERRAN_ORIGINS={value:key for key,value in TERRAN_FORMS.items()}


def transform_terran_card(game,owner,card):
 if getattr(game.players[owner],'historical_ship_launches',0) and card.card_id in TERRAN_FORMS:
  before=card.card_id;card.card_id=TERRAN_FORMS[before]
  game._log('terran_transformed',player=owner,card=card.card_id)


def refresh_terran(game):
 for owner,player in enumerate(game.players):
  if not getattr(player,'historical_ship_launches',0):continue
  for card in list(player.hand)+list(player.deck)+list(player.all_minions):transform_terran_card(game,owner,card)


def relaunch(game,owner,card):
 player=game.players[owner];card=game._fresh_replay_card(card)
 data=getattr(card,'_historical_ship_definition',None)
 if data is None:raise UnsupportedCard('Relaunch requires a captured Starship construction')
 result=game._summon(owner,card.card_id,entry_source=card,entry_origin='starship_launch',entry_site='raynor_relaunch')
 if result is None:return
 player.historical_ship_launches=getattr(player,'historical_ship_launches',0)+1
 history=getattr(player,'_historical_launched_ships',[]);history.append(deepcopy(card));player._historical_launched_ships=history
 programs=[program for piece in data['parts'] for program in (LAUNCH_EFFECTS.get(piece),) if program]
 game.rng.shuffle(programs);operations=tuple(effect for program in programs for effect in program)
 if operations:game._rule_events.append(('captured_effects',dict(operations=operations,context=dict(owner=owner,source=result,target=0,bonus=0,lifesteal=False,card_id=card.card_id)),[]))
 game._log('starship_relaunched',player=owner,card=card.card_id,pieces=len(data['parts']))

TERRAN_MINIONS=frozenset(('SC_401','SC_403a','SC_403b','SC_403c','SC_403d','SC_403f','SC_403t','SC_405','SC_406','SC_408','SC_409','SC_412','SC_412t','SC_413','SC_413t','SC_414','SC_414t'))
def is_terran(minion):
 return minion.card_id in TERRAN_MINIONS or any(cid.startswith('SC_4') for cid in getattr(minion,'_historical_ship_definition',{}).get('parts',()))
