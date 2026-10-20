"""Explicit recipes for the observed Nefarius component tables.

Source: https://hearthstone.wiki.gg/wiki/Victor_Nefarius (table revision observed
2026-10-15, page updated 2026-09-29). This module does not activate a runtime
pool or certify completeness against the pinned patch. All component behavior
is declared explicitly; no rules-text/line-count inference is performed.
"""
from .minion_forge import ForgePart
from .generation_cards import pool,random_cards,discover
SOURCE='Observed Nefarius component tables; explicit pinned behavior recipe'


def part(cid, *, target='none', operations=(), death=(), keywords=(), intrinsics=()):
    return ForgePart(cid,target,tuple(operations),tuple(death),tuple(keywords),SOURCE,tuple(intrinsics))


PARTS={
 'END_022':part('END_022',intrinsics=(('damaged_spell_damage',2),)),
 'CORE_NEW1_023':part('CORE_NEW1_023',keywords=('ELUSIVE',)),
 'EDR_571':part('EDR_571',death=(('filtered_draw',(('type','eq','SPELL'),('cost','ge',5)),1),)),
 'TTN_924':part('TTN_924',intrinsics=(('cost_floor',2),)),
 'TIME_056':part('TIME_056',keywords=('LIFESTEAL','DIVINE_SHIELD')),
 'TIME_045':part('TIME_045',keywords=('POISONOUS','REBORN')),
 'CATA_305':part('CATA_305',intrinsics=(('end_effects',(('full_health_buff',0,3),)),)),
 'CATA_898':part('CATA_898',intrinsics=(('enemy_taunt',True),)),
 'DRG_211':part('DRG_211',intrinsics=(('spell_damage',2),('overload',2))),
 'CORE_EX1_043':part('CORE_EX1_043',operations=(('self_hand_health',),)),
 'TIME_856':part('TIME_856',intrinsics=(('spell_damage',2),)),
 'TRL_526':part('TRL_526',operations=(('area_damage','other_minions',1),)),
 'TIME_720':part('TIME_720',keywords=('TAUNT',),operations=(('double_self_health',),)),
 'TIME_051':part('TIME_051',keywords=('RUSH',),operations=(('double_self_attack',),)),
 'BOT_066':part('BOT_066',death=(('death_summon','BOT_066t',1),)),
 'DEEP_006':part('DEEP_006',keywords=('DIVINE_SHIELD','TAUNT','LIFESTEAL','ELUSIVE')),
 'BRM_025':part('BRM_025',intrinsics=(('cost_rule','deaths_turn'),)),
 'CATA_723':part('CATA_723',death=(random_cards(pool(card_type='MINION',minimum=4,maximum=4),2,'board'),)),
 'SCH_711':part('SCH_711',death=(random_cards(pool(card_type='MINION',minimum=7,maximum=7),1,'board'),)),
 'RLK_503':part('RLK_503',operations=(('gain_corpses',1),)),
 'RLK_538':part('RLK_538',intrinsics=(('trigger',('b60_friendly_death',(('inherit_friendly_deathrattle',),))),)),
 'RLK_958':part('RLK_958',target='friendly_undead',operations=(('buff',2,0),)),
 'CORE_EX1_012':part('CORE_EX1_012',death=(('draw',1),),intrinsics=(('spell_damage',1),)),
 'CORE_WON_096':part('CORE_WON_096',operations=(discover(pool(minimum=1,maximum=1,classes='own_or_neutral')),)),
 'RLK_511':part('RLK_511',death=(('draw_school','FROST'),)),
 'JAM_021':part('JAM_021',keywords=('RUSH',),operations=(('historical_if_combo',('keyword_self','POISONOUS')),)),
 'ICC_913':part('ICC_913',keywords=('DIVINE_SHIELD',),intrinsics=(('spell_damage',1),)),
 'ULD_185':part('ULD_185',keywords=('REBORN',),intrinsics=(('damaged_attack',2),)),
 'CORE_NEW1_020':part('CORE_NEW1_020',intrinsics=(('trigger',('spell_cast',(('area_damage','all_minions',1),))),)),
 'ULD_205':part('ULD_205',keywords=('REBORN',)),
 'ICC_700':part('ICC_700',intrinsics=(('cost_rule','hero_healed'),)),
 'CORE_OG_149':part('CORE_OG_149',operations=(('area_damage','other_minions',1),)),
 'END_031':part('END_031',keywords=('STEALTH',),intrinsics=(('spell_damage',1),)),
 'ULD_275':part('ULD_275',keywords=('TAUNT','REBORN')),
 'ICC_820':part('ICC_820',keywords=('CHARGE','LIFESTEAL')),
 'TIME_617':part('TIME_617',intrinsics=(('suppress_draw',True),)),
 'JAM_007':part('JAM_007',keywords=('DIVINE_SHIELD','REBORN')),
 'DINO_435':part('DINO_435',operations=(('kindred',[('copy_self_right',1)]),)),
}
DRAGONS=('END_022','CORE_NEW1_023','EDR_571','TTN_924','TIME_056','TIME_045','CATA_305','CATA_898','DRG_211','CORE_EX1_043','TIME_856','TRL_526','TIME_720','TIME_051','BOT_066','DEEP_006','BRM_025','CATA_723','SCH_711')
UNDEAD=('RLK_503','RLK_538','RLK_958','CORE_EX1_012','CORE_WON_096','RLK_511','JAM_021','ICC_913','ULD_185','CORE_NEW1_020','ULD_205','ICC_700','CORE_OG_149','END_031','ULD_275','ICC_820','TIME_617','JAM_007','CATA_898','DINO_435')


def observed_contracts():
    """Unactivated recipes, for explicit fixture/review use only."""
    from copy import deepcopy
    return {('dragon',1):tuple(deepcopy(PARTS[cid]) for cid in DRAGONS),
            ('dragon',2):tuple(deepcopy(PARTS[cid]) for cid in UNDEAD)}
