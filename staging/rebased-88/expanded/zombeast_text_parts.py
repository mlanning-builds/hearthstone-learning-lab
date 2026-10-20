"""Explicit pinned Standard Beast behavior; offer membership is separate.

These recipes do not activate either Storm the Gates production pool. Each
identity declares its own printed effects; no supported-only pool or runtime
rules-text inference is used.
"""
from .minion_forge import ForgePart
from .generation_cards import pool,random_cards,discover
SOURCE='Pinned 36.6.0.251952 printed component behavior; stage membership reviewed separately'


def part(cid, *, target='none',operations=(),death=(),intrinsics=(),keywords=()):
    return ForgePart(cid,target,tuple(operations),tuple(death),tuple(keywords),SOURCE,tuple(intrinsics))


PARTS={
 'CORE_EX1_014':part('CORE_EX1_014',operations=(('add_opponent','EX1_014t',2),)),
 'CORE_GIL_622':part('CORE_GIL_622',operations=(('damage_enemy_heal_own',3,3),)),
 'CORE_UNG_084':part('CORE_UNG_084',target='character',operations=(('damage',3),)),
 'EDR_492':part('EDR_492',operations=(('summon','EDR_492t',3),)),
 'TIME_601':part('TIME_601',operations=(('draw_until',3),)),
 'TIME_042':part('TIME_042',operations=(('discard_entire_hand',),('add','TIME_042t',1))),
 'TLC_250':part('TLC_250',operations=(('prevent_enemy_hero_healing_until_next_turn',),)),
 'TLC_825':part('TLC_825',target='kindred_enemy_minion',operations=(('kindred',[('source_attack_damage',)]),)),
 'CORE_LOOT_413':part('CORE_LOOT_413',death=(('armor',3),)),
 'TIME_058':part('TIME_058',death=(random_cards(pool(card_type='MINION',minimum=2,maximum=2),destination='board',dormant_turns=2),)),
 'JAIL_878':part('JAIL_878',death=(random_cards(pool(card_type='MINION',minimum=1,maximum=1,mechanic='DEATHRATTLE'),destination='board'),)),
 'CORE_UNG_912':part('CORE_UNG_912',operations=(random_cards(pool(card_type='MINION',tribe='BEAST')),)),
 'CORE_LOE_039':part('CORE_LOE_039',operations=(('generation_if_other_tribe','MECHANICAL',discover(pool(card_type='MINION',tribe='MECHANICAL',classes='own_or_neutral'))),)),
 'DINO_435':part('DINO_435',operations=(('kindred',[('copy_self_right',1)]),)),
 'TLC_256':part('TLC_256',intrinsics=(('trigger',('spell_cast',(('keyword_self','DIVINE_SHIELD'),))),)),
}

PARTS.update({
 'CORE_EX1_162':part('CORE_EX1_162',intrinsics=(('adjacent_attack',1),)),
 'CORE_SCH_605':part('CORE_SCH_605',intrinsics=(('cleave',True),)),
 'CORE_BT_201':part('CORE_BT_201',death=(('attack_missiles',),)),
 'TLC_603':part('TLC_603',operations=(('b60_draw_remember',),),death=(('b60_discard_remembered',),)),
 'EDR_014':part('EDR_014',operations=(('force_cheap_attacks',),)),
 'TLC_102':part('TLC_102',operations=(('draw_kindred_pair',),)),
})

PARTS.update({
 'TLC_242':part('TLC_242',operations=(('choose_self_effect', (('Taunt', ('keyword_self', 'TAUNT')), ('Poisonous', ('keyword_self', 'POISONOUS')), ('+1/+1', ('buff_self', 1, 1)))),)),
 'TLC_245':part('TLC_245',operations=(('choose_self_effect', (('Attack', ('buff_self', 3, 0)), ('Divine Shield', ('keyword_self', 'DIVINE_SHIELD')), ('Plants', ('grant_death_self', (('death_summon', 'UNG_999t2t1', 2),))))),)),
 'TLC_246':part('TLC_246',operations=(('choose_self_effect', (('Stealth', ('temporary_keyword_self', 'STEALTH', 'next_start')), ('Elusive', ('keyword_self', 'ELUSIVE')), ('Windfury', ('keyword_self', 'WINDFURY')))),)),
 'END_015':part('END_015',operations=(('kindred',[random_cards(pool(card_type='MINION',mechanic='DEATHRATTLE'),cost_delta=-2)]),),death=(random_cards(pool(card_type='MINION',mechanic='DEATHRATTLE'),cost_delta=-2),)),
 'EDR_849':part('EDR_849',intrinsics=(('trigger',('other_friendly_minion_played',(('bonus_played',),))),)),
 'CORE_GIL_623':part('CORE_GIL_623',keywords=('TAUNT',),operations=(('self_enemy_hand_health',),)),
 'CORE_TRL_900':part('CORE_TRL_900',keywords=('RUSH',),operations=(('fill_hand','TRL_348t'),)),
})

# The final four combined Standard candidate identities have explicit behavior
# recipes too. Complete stage membership and their outcome contracts remain
# separate gates; adding a recipe does not supply a random distribution.
from .dark_gift_generators import request as gift_request,discover as gift_discover
PARTS.update({
 'TLC_827':part('TLC_827',intrinsics=(('end_zone_attack',1),('end_effects',(('buff_self',1,0),)))),
 'CORE_EDR_004_2026':part('CORE_EDR_004_2026',operations=(('rewindgen_gift',),),intrinsics=(('rewind',1),)),
 'END_013':part('END_013',operations=(gift_discover(gift_request(minimum=1,maximum=1)),)),
 'JAIL_EVENT_100':part('JAIL_EVENT_100',operations=(('suspicious_discover',),)),
})

# Historical consumers share behavior recipes, but retain separate complete
# stage membership contracts. No default offer pool is inferred.
from .zombeast_historical_parts import PARTS as HISTORICAL_PARTS
assert not (PARTS.keys() & HISTORICAL_PARTS.keys())
PARTS.update(HISTORICAL_PARTS)
