"""Explicit Transfer Student board forms; board-root selection is staged.

No board distribution or default board is invented. Effects use full pools,
with unsupported generated dependencies rejected before sampling.
"""
from engine.cards import UnsupportedCard
from .generation_cards import pool,random_cards,discover
from .pools import require_fixed_cards,GenerationPool
from .generation import request_matches
from .identities import canonical_identity
PORTALS=('KAR_073','KAR_075','KAR_076','KAR_077','KAR_091')
PLAGUES=('ULD_172','ULD_707','ULD_715','ULD_717','ULD_718')
RANKED=('BAR_034','BAR_044','BAR_305','BAR_314','BAR_319','BAR_536','BAR_842','BAR_880','BAR_891','BAR_914')
DUAL_CLASS=('CATA_190h', 'CATA_497', 'CATA_722', 'END_001', 'END_002', 'END_004', 'END_005', 'END_007', 'END_008', 'END_010', 'END_011', 'END_013', 'END_014', 'END_016', 'END_017', 'END_019', 'END_020', 'END_022', 'END_023', 'END_025', 'END_026', 'END_028', 'END_029', 'END_031', 'END_032')
TOKEN_RULES={
 'SCH_199t':('none',[]), # Divine Shield is printed metadata.
 'SCH_199t2':('character',[('damage',2)]),
 'SCH_199t3':('friendly_minion',[('buff',1,2)]),
 'SCH_199t4':('none',[]), # Printed Stealth and Poisonous.
 'SCH_199t5':('none',[]),
 'SCH_199t6':('none',[('historical_prime_part',)]),
 'SCH_199t7':('none',[]),
 'SCH_199t8':('none',[]),
 'SCH_199t9':('none',[('historical_treasure_power','basic')]),
 'SCH_199t10':('none',[('generation_dynamic_summon','remaining_mana')]),
 'SCH_199t11':('none',[('historical_student_gift','portal')]),
 'SCH_199t12':('none',[('buff_random_hand_minion','friendly',2,2)]),
 'SCH_199t13':('none',[('historical_upgrade_adapt','self')]),
 'SCH_199t14':('none',[]),
 'SCH_199t15':('none',[('historical_copy_recruit_one','deck',(('cost','le',2),),None,None)]),
 'SCH_199t16':('none',[]), # Printed Echo/Rush use shared play/combat hooks.
 'SCH_199t17':('none',[('historical_student_omega',)]),
 'SCH_199t18':('none',[]),
 'SCH_199t19':('none',[('historical_family_lackeys',1)]),
 'SCH_199t20':('none',[]), # Printed Reborn.
 'SCH_199t21':('none',[discover(pool(card_type='MINION',tribe='DRAGON',classes='own_or_neutral'))]),
 'SCH_199t22':('none',[]), # Initial Dormant and awakening are explicit tables.
 'SCH_199t23':('none',[('historical_student_gift','dual')]),
 'SCH_199t24':('none',[random_cards(pool(card_type='WEAPON'))]),
 'SCH_199t25':('none',[('historical_student_gift','plague')]),
 'SCH_199t26':('none',[]), # Physical Corrupt transformation uses shared map.
 'SCH_199t26t':('none',[]), # Corrupted 4/4 printed body.
 'SCH_199t27':('none',[('historical_student_gift','ranked')]),
 'SCH_199t28':('friendly_minion',[('keyword','DIVINE_SHIELD')]),
 'SCH_199t29':('character',[('damage',1)]),
}
EXPANSION_FORMS={
 'SCH_199t30':'THE_SUNKEN_CITY','SCH_199t31':'REVENDRETH',
 'SCH_199t32':'RETURN_OF_THE_LICH_KING','SCH_199t33':'BATTLE_OF_THE_BANDS',
 'SCH_199t34':'TITANS','SCH_199t35':'WILD_WEST','SCH_199t36':'WHIZBANGS_WORKSHOP',
}
# Annual boards discover across every released expansion of that year.
# Mini-sets use their parent expansion set in the frozen archive.
YEAR_SETS={
 'YEAR_OF_THE_RAPTOR':('EMERALD_DREAM','THE_LOST_CITY','TIME_TRAVEL'),
 'YEAR_OF_THE_SCARAB':('CATACLYSM','ESCAPEFROM_VIOLET_HOLD'),
}
YEAR_FORMS={'SCH_199t37':'YEAR_OF_THE_RAPTOR','SCH_199t38':'YEAR_OF_THE_SCARAB'}
TOKEN_RULES.update({cid:('none',[('historical_student_expansion',expansion)]) for cid,expansion in {**EXPANSION_FORMS,**YEAR_FORMS}.items()})

DEATH_EFFECTS={
 'SCH_199t5':[random_cards(pool(card_type='MINION',mechanic='DEATHRATTLE'))],
 'SCH_199t6':[('historical_prime_part',)],
 'SCH_199t14':[('historical_copy_lich_gift',)],
}
END_EFFECTS={'SCH_199t7':[('discount_random_hand','friendly',(),2)]}
TRIGGERS={'SCH_199t8':('hero_power_used',[('draw',1)])}
OVERKILL={'SCH_199t18':[('draw',1)]}
HONORABLE={'SCH_199t29':[('buff_self',1,1)]}
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)
REQUIRED_SPELL_IDS=frozenset(PORTALS+PLAGUES+RANKED)

def split(game,op,ctx):
 if op[0]!='historical_student_awaken':return None
 targets=[m for m in game.players[1-ctx['owner']].minions if m.health>0 and not m.dormant]
 selected=game.rng.sample(targets,min(2,len(targets)))
 operations=tuple(('replay_context',(('damage',3),),dict(ctx,target=m.uid,spell=False,bonus=0)) for m in selected)
 if not operations:return ('batch30_noop',),()
 first,tail=game._split_fixed_summon(operations[0],ctx)
 return first,tuple(tail)+operations[1:]

def execute(game,op,ctx):
 if op[0]=='historical_student_omega':
  source=ctx.get('source')
  if source is not None and game.players[ctx['owner']].max_mana>=10:game._buff(source,5,5)
  return True
 if op[0]=='historical_student_expansion':
  expansion_discover(game,ctx,op[1])
  return True
 if op[0]=='historical_student_gift':
  pools={'portal':PORTALS,'plague':PLAGUES,'ranked':RANKED,'dual':DUAL_CLASS}
  values=pools[op[1]]
  if not values:raise UnsupportedCard('Empty frozen Transfer Student gift pool')
  require_fixed_cards(values,game.cards)
  game._add(ctx['owner'],game.rng.choice(values))
  return True
 return False


def expansion_discover(game,ctx,expansion):
 if expansion not in tuple(EXPANSION_FORMS.values())+tuple(YEAR_SETS):raise UnsupportedCard('Unknown Transfer Student expansion or year')
 selected_sets=YEAR_SETS.get(expansion,(expansion,))
 if game.pending_choice is not None:raise UnsupportedCard('Cannot overwrite pending choice')
 from .historical_generation_catalog import load_universe
 universe=load_universe();records=universe.records
 owner=ctx['owner'];request=pool(classes='own_or_neutral')
 # Membership uses the full archive, independent of executable coverage.
 # Explicit expansion Discover is not limited to the active Standard sets.
 members=tuple(sorted(cid for cid,data in records.items()
  if data.get('collectible') and data.get('set') in selected_sets
  and data.get('type') in ('MINION','SPELL','WEAPON','HERO','LOCATION')
  and request_matches(request,data,game.players[owner].hero_class)))
 contract=GenerationPool('Transfer Student '+expansion,members,
  'Full frozen build 251952 collectible expansion membership with ordinary Discover class/generation restrictions')
 values=contract.resolve(records,game.cards)
 creator=ctx.get('generation_creator_id',ctx.get('card_id'))
 identity=canonical_identity(records[creator],records) if creator in records else None
 values=tuple(cid for cid in values if identity is None or canonical_identity(records[cid],records)!=identity)
 if not values:return
 ids=game.rng.sample(list(values),min(3,len(values)))
 game._generation_choice_context=dict(context=dict(ctx),destination='hand',modifiers=())
 game.pending_choice=dict(owner=owner,kind='generation_discover',options=[dict(card_id=cid) for cid in ids])
 game.phase='choice'


BOARD_FORMS=frozenset(('SCH_199t',)+tuple('SCH_199t'+str(n) for n in range(2,39)))

def form_for(game,cid):
 if cid!='SCH_199':return cid
 selected=getattr(game,'transfer_student_form',None)
 if selected is None:raise UnsupportedCard('Transfer Student requires an explicit board form for this match')
 if selected not in BOARD_FORMS:raise UnsupportedCard('Invalid Transfer Student board form')
 if selected not in game.cards:raise UnsupportedCard('Selected Transfer Student board form is not implemented: '+selected)
 return selected


def normalize_card(game,card):
 card.card_id=form_for(game,card.card_id)
 return card


def setup(game):
 for player in game.players:
  for zone_name in ('hand','deck'):
   zone=getattr(player,zone_name)
   for index,card in enumerate(zone):
    if isinstance(card,str):zone[index]=form_for(game,card)
    else:normalize_card(game,card)
