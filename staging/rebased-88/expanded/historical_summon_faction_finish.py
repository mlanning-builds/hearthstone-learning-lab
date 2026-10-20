"""Historical summon families, physical faction draws and printed continuations.

Card identity sets are explicit; StarCraft factions are not minion tribes.
"""
from engine.game import Card
from .generation_cards import pool,discover
from .historical_draw_batches import draw
from .selectors import has_tribe,SCHOOLS
from .historical_saidan import add as add_stat

ZERG_CARDS=('SC_000','SC_001','SC_002','SC_003','SC_003t','SC_004','SC_006','SC_008','SC_009','SC_010','SC_011','SC_012','SC_015','SC_018','SC_019','SC_019t','SC_020','SC_021','SC_022','SC_023')
TERRAN_CARDS=('SC_400','SC_401','SC_403','SC_403a','SC_403b','SC_403c','SC_403d','SC_403f','SC_403t','SC_404','SC_405','SC_406','SC_407','SC_408','SC_409','SC_410','SC_411','SC_412','SC_412t','SC_413','SC_413t','SC_414','SC_414t')
PIECES=('SC_403a','SC_403b','SC_403c','SC_403d','SC_403f')
DRAENEI=pool(card_type='MINION',tribe='DRAENEI')
DEMON=pool(card_type='MINION',tribe='DEMON',maximum=3)
def op(name,*args):return ('historical_utility_summon_finish_'+name,)+args
TOKEN_RULES={
 'DAL_007':('none',[op('scheme')]),
 'LOOT_217':('none',[op('companions')]),
 'TRL_127':('none',[op('cannon')]),
 'WC_022':('minion',[('historical_utility_damage_finish_hit',1,'adventurer')]),
 'GDB_473':('character',[('damage',2),('historical_copy_literal_family','crewmate','hand')]),
 'GDB_119':('none',[op('meeting',DEMON)]),
 'SC_001':('none',[op('banelings')]),
 'SC_019t':('none',[]),
 'SC_015':('none',[draw((('id','in',ZERG_CARDS),),'discount',(1,))]*2),
 'SC_410':('none',[draw((('id','in',TERRAN_CARDS),))]*2+[('summon_fixed_random',PIECES)]),
 'SC_020':('historical_finish_friendly_location',[op('consume'),('heal_own_hero',8)]),
 'SW_320':('none',[op('rat')]*7),
 'WORK_020':('none',[op('banana')]*8),
 'WC_020':('none',[('historical_utility_repeat_batch_start','flame')]),
 'WON_064':('historical_finish_attack_four',[('destroy',)]),
 'WON_064ts':('none',[op('forbid')]),
 'SCH_521':('historical_finish_coerce',[('destroy',)]),
 'TRL_302':('none',[op('time_out')]),
 'VAC_308':('none',[op('siren'),op('siren')]),
 'VAC_533':('none',[('summon_opponent','VAC_533t',1)]),
 'VAC_533t':('none',[]),
 'GDB_439':('minion',[('buff',1,1),('keyword','DIVINE_SHIELD')]),
 'GDB_462':('none',[discover(DRAENEI),op('orbital_discover')]),
 'GDB_475':('minion',[('keyword','TAUNT'),('keyword','LIFESTEAL'),op('orbital_reborn')]),
}
DEATH_EFFECTS={'SC_019t':[op('explode')],'VAC_533t':[op('entree')]}
LOCATION_RULES={'SC_000':'none','SC_019':'none','SC_403':'none'}
LOCATION_EFFECTS={'SC_000':[('add','SC_010',1)],'SC_019':[('area_damage','enemies',1)],'SC_403':[('summon_fixed_random',PIECES)]}
LOCATION_DEATHS={'SC_000':[op('zerg_rush')],'SC_019':[('summon','SC_006',1)]}
TOKEN_RULES.update({cid:('none',[]) for cid in LOCATION_RULES})
DEATH_EFFECTS.update(LOCATION_DEATHS)
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

def adjacent(game,card):
 return getattr(card,'rule_state',{}).get('historical_orbital_adjacent_turn')==game.turn

def targets(game,cid,owner,mode):
 if mode=='historical_finish_friendly_location':return [loc.uid for loc in game.players[owner].locations if loc.durability>0]
 if mode=='historical_finish_attack_four':return [uid for uid in game._targets_for(cid,owner,'minion') if uid>0 and game._find(uid).attack==4]
 if mode=='historical_finish_coerce':return game._targets_for(cid,owner,'minion' if game.players[owner].cards_played else 'damaged_minion')
 return None

def requests_for(game,cid,owner):
 if cid!='VAC_308':return set()
 return {pool(card_type='SPELL',school=school) for school in SCHOOLS-set(getattr(game.players[owner],'historical_spell_schools',()))}

def sequence(game,ctx,operations):
 operations=tuple(operations)
 if not operations:return ('batch30_noop',),()
 first,tail=game._split_fixed_summon(operations[0],ctx)
 return first,tuple(tail)+operations[1:]

def split(game,operation,ctx):
 prefix='historical_utility_summon_finish_'
 if not operation[0].startswith(prefix):return None
 name=operation[0][len(prefix):];owner=ctx['owner'];p=game.players[owner]
 if name=='scheme':
  amount=1+getattr(ctx.get('physical_card'),'rule_state',{}).get('historical_finish_scheme_age',0)
  return game._split_fixed_summon(('summon','DAL_751t',amount),ctx)
 if name=='companions':
  count=(1 if any(game._card_data(c)['type']=='MINION' for c in p.deck) else 2)+p.companion_extra
  game._companion_ids(owner)
  return game._split_fixed_summon(('companion_random_series',count),ctx)
 if name=='cannon':return sequence(game,ctx,(('damage_random_enemy',3),)*(1+sum(m.health>0 and has_tribe(game._card_data(m),'PIRATE') for m in p.minions)))
 if name=='banelings':
  from .historical_copy_batches import ZERG_IDS
  count=2 if any(m.health>0 and m.card_id in ZERG_IDS for m in p.minions) else 1
  return sequence(game,ctx,(('add','SC_019t',1),)*count)
 if name=='orbital_discover':
  return game._split_fixed_summon(discover(DRAENEI),ctx) if adjacent(game,ctx.get('physical_card')) else (('batch30_noop',),())
 if name=='entree':
  other=dict(ctx,owner=1-owner,source=None,spell=False,bonus=0,lifesteal=False)
  return game._split_fixed_summon(('replay_context',(('historical_copy_recruit_one','deck',None,None,None),),other),ctx)
 return None

def execute(game,operation,ctx):
 prefix='historical_utility_summon_finish_'
 if not operation[0].startswith(prefix):return False
 name=operation[0][len(prefix):];owner=ctx['owner'];p=game.players[owner]
 if name=='meeting':
  from .historical_copy_batches import CREWMATES
  from .pools import require_fixed_cards
  require_fixed_cards(CREWMATES,game.cards)
  values=game._generation_candidates(operation[1],owner)
  first=game._add(owner,game.rng.choice(CREWMATES));second=game._add(owner,game.rng.choice(CREWMATES))
  if values:
   demon=game._add(owner,game.rng.choice(values))
   if demon is not None and demon in p.hand:
    p.hand.remove(demon)
    index=p.hand.index(second) if second in p.hand else p.hand.index(first)+1 if first in p.hand else len(p.hand)
    p.hand.insert(index,demon)
 elif name=='consume':
  location=next((loc for loc in p.locations if loc.uid==ctx.get('target')),None)
  if location is not None:
   location.durability-=1
   if location.durability<=0:game._remove_location(location)
 elif name=='explode':
  source=ctx.get('source')
  if source is not None:
   with game._damage_batch():
    for m in tuple(game.players[1-owner].minions):
     if m.health>0:game._deal_effect(m.uid,source.attack,dict(ctx,spell=False,bonus=0))
 elif name=='rat':
  if len(p.board)<7:game._summon(owner,'SW_455t',entry_origin='effect',entry_site='rats_extraordinary_size')
  else:
   card=Card(game._new_id(),'SW_455t');add_stat(card,'attack_bonus',4);add_stat(card,'health_bonus',4);game._enter_hand(owner,card)
 elif name=='banana':
  if len(p.hand)<getattr(p,'hand_capacity',10):game._add(owner,'EX1_014t')
  else:
   choices=[m for m in p.minions if m.health>0]
   if choices:game._buff(game.rng.choice(choices),1,1)
 elif name=='forbid':
  for player in game.players:
   for m in player.minions:
    if m.attack==4:m.health=0
 elif name=='time_out':p.hero_immune_expiry_players.append(owner)
 elif name=='zerg_rush':p.historical_zerg_rush_turn=game.turn
 elif name=='siren':
  values=tuple(sorted({cid for request in requests_for(game,'VAC_308',owner) for cid in game._generation_candidates(request,owner)}))
  if values:game._add(owner,game.rng.choice(values))
 elif name=='orbital_reborn':
  m=game._force_live(ctx.get('target'))
  if m is not None and adjacent(game,ctx.get('physical_card')):m.keywords.add('REBORN')
 else:return False
 return True
