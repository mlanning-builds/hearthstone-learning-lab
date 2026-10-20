"""Historical Beast component behavior, separate from complete offer pools.

No source admission or generation-pool filtering is performed here. Native
operations execute against the physical composite, preserving its full Attack
for Rat Pack and its generated identity for adaptation and summons.
"""
from .minion_forge import ForgePart
from .generation_cards import pool, random_cards, discover
SOURCE='Pinned 36.6.0.251952 metadata and explicit native handlers; pool membership separate'
def part(cid, *, target='none', operations=(), death=(), keywords=(), intrinsics=()):
 return ForgePart(cid,target,tuple(operations),tuple(death),tuple(keywords),SOURCE,tuple(intrinsics))
PARTS={
 'AT_058':part('AT_058',operations=(('historical_batch_joust','MINION',True,()),)),
 'CFM_315':part('CFM_315',operations=(('summon','CFM_315t',1),)),
 'CFM_316':part('CFM_316',death=(('historical_batch_attack_summons','CFM_316t'),)),
 'CS2_203':part('CS2_203',target='minion',operations=(('silence',),)),
 'CORE_CS2_203':part('CORE_CS2_203',target='minion',operations=(('silence',),)),
 'FP1_011':part('FP1_011',death=(random_cards(pool(card_type='MINION',tribe='BEAST')),)),
 'CORE_FP1_011':part('CORE_FP1_011',death=(random_cards(pool(card_type='MINION',tribe='BEAST')),)),
 'GIL_212':part('GIL_212',operations=(random_cards(pool(card_type='MINION',minimum=1,maximum=1),count=2),)),
 'KAR_005':part('KAR_005',death=(('death_summon','KAR_005a',1),)),
 'LOE_046':part('LOE_046',death=(('damage_random_enemy',1),)),
 'LOE_047':part('LOE_047',operations=(discover(pool(card_type='MINION',tribe='BEAST',classes='own_or_neutral')),)),
 'NEW1_041':part('NEW1_041',operations=(('historic_destroy_random_small',2),)),
 'OG_179':part('OG_179',death=(('damage_random_enemy',1),)),
 'OG_216':part('OG_216',death=(('death_summon','OG_216a',2),)),
 'TRL_348':part('TRL_348',keywords=('RUSH',),operations=(('add','TRL_348t',1),)),
 'CORE_TRL_348':part('CORE_TRL_348',keywords=('RUSH',),operations=(('add','TRL_348t',1),)),
 'UNG_912':part('UNG_912',operations=(random_cards(pool(card_type='MINION',tribe='BEAST')),)),
 'UNG_914':part('UNG_914',death=(('historical_prime_shuffle','UNG_914t1'),)),
 'UNG_915':part('UNG_915',target='friendly_beast',operations=(('historical_upgrade_adapt','target'),)),
}

# Explicit tribe-scoped properties and native event selectors survive stitching;
# they are not keyed to the source card id after construction.
PARTS.update({
 'DS1_175':part('DS1_175',intrinsics=(('beast_attack',1),)),
 'DS1_178':part('DS1_178',intrinsics=(('beast_charge',True),)),
 'CS2_237':part('CS2_237',intrinsics=(('trigger',(('summon','friendly','BEAST'),(('draw',1),))),)),
 'EX1_531':part('EX1_531',intrinsics=(('trigger',(('historical_event','friendly_beast_death'),(('buff_self',2,1),))),)),
 'CORE_EX1_531':part('CORE_EX1_531',intrinsics=(('trigger',(('historical_event','friendly_beast_death'),(('buff_self',2,1),))),)),
})

# Recipes cover behavior separately from whether each source is eligible for a
# client-curated offer stage. Neither Prepare nor Tradeable is inferred at run time.
PARTS.update({
 'CORE_SW_072':part('CORE_SW_072',keywords=('TRADEABLE',),operations=(('destroy_enemy_weapon',),)),
 'JAIL_395':part('JAIL_395',target='friendly_deathrattle',keywords=('PREPARE',),operations=(('replay_friendly_deathrattle',),),intrinsics=(('prepare',True),)),
 'JAIL_453':part('JAIL_453',keywords=('TAUNT',),intrinsics=(('prepare_discount',True),)),
})
