"""Explicit on-draw identities from the pinned Constructed archive."""
IMP='CAP_400t2t'
SHRED='TIME_025t'
RULES={
 'CAP_400':('none',[]),
 'CAP_401':('none',[('on_draw_top_imp',)]),
 'CAP_404':('none',[('opponent_next_turn_cost','MINION',2),('on_draw_shuffle',IMP,2,1)]),
 'CAP_406':('none',[('on_draw_imp_upgrade',)]),
 'CORE_SW_439':('none',[]),
 'EDR_260':('none',[]),
 'JAIL_386':('none',[('armor',2),('on_draw_shuffle','JAIL_386t',5,0)]),
 'JAIL_881':('none',[('missiles','enemies',4),('on_draw_shuffle','JAIL_881t',2,0)]),
 'TIME_025':('none',[('on_draw_shuffle',SHRED,2,0)]),
 'TIME_026':('none',[('board_buff',1,1),('on_draw_shuffle',SHRED,2,0)]),
 'TIME_027':('none',[('missiles','enemies',6),('on_draw_shuffle',SHRED,2,0)]),
 'TIME_028':('none',[('on_draw_consume_shred','buff')]),
 'TIME_029':('none',[('on_draw_consume_shred','copy')]),
 'TLC_518':('none',[('on_draw_shuffle','TLC_513t2',3,0)]),
}
DEATH_EFFECTS={
 'CAP_400':[('on_draw_shuffle',IMP,2,1)],
 'CORE_SW_439':[('on_draw_shuffle','SW_439t',4,0)],
 'EDR_260':[('on_draw_shuffle','EDR_260t',2,0)],
}
CAST_EFFECTS={
 'EDR_445pt3':(('imbue_portal',),),
 'SW_439t':(('summon','SW_439t2',1),),
 'JAIL_386t':(('armor',2),),
 'JAIL_881t':(('missiles','enemies',4),),
 'JAIL_443t':(('on_draw_hurt_owner',2),),
 SHRED:(('on_draw_hurt_owner',3),),
}
SUMMON_DRAW={'EDR_260t':0,'TLC_513t2':0,IMP:1}
TOKEN_IDS=set(CAST_EFFECTS)|set(SUMMON_DRAW)|{'SW_439t2'}
TOKEN_RULES={cid:('none',list(CAST_EFFECTS.get(cid,()))) for cid in TOKEN_IDS}

from . import historical_drawn_batches
CAST_EFFECTS.update(historical_drawn_batches.CAST_EFFECTS)
SUMMON_DRAW.update(historical_drawn_batches.SUMMON_DRAW)

CAST_EFFECTS['LOOT_526t']=(('historical_sleep_candle',),)

CAST_EFFECTS['WW_372t']=tuple(('historical_copy_tnt_zone',zone) for zone in ('hand','deck','board'))

from .generation_cards import random_cards,pool
_TIME_EPOCH_RULES={'WON_041t':('none',[random_cards(pool(card_type='MINION',rarity='LEGENDARY'),2)]),'WON_041t2':('none',[('board_buff',2,2)]),'WON_041t3':('none',[random_cards(pool(card_type='SPELL'),2)]),'WON_041t4':('none',[('area_damage','enemies',2)])}
CAST_EFFECTS.update({cid:tuple(recipe[1]) for cid,recipe in _TIME_EPOCH_RULES.items()})

# Fel Rift resolves through the existing automatic cast and replacement draw.
CAST_EFFECTS['AV_316t4']=(('summon','AV_316t',1),)
TOKEN_IDS.update(('AV_316t4','AV_316t'))
TOKEN_RULES['AV_316t4']=('none',list(CAST_EFFECTS['AV_316t4']))
TOKEN_RULES['AV_316t']=('none',[])

from .historical_summoning_spells import CAST_EFFECTS as SUMMONING_CAST_EFFECTS
CAST_EFFECTS.update(SUMMONING_CAST_EFFECTS)

CAST_EFFECTS['TOY_829t']=[('historical_utility_horseman_head',)]

CAST_EFFECTS['LOOT_106t']=(('autocast_random',pool(card_type='SPELL'),1),)

from .historical_spell_archive_batch import CAST_EFFECTS as ARCHIVE_CAST_EFFECTS
CAST_EFFECTS.update(ARCHIVE_CAST_EFFECTS)

from .historical_delayed_spell_finish import CAST_EFFECTS as DELAYED_FINISH_CASTS
CAST_EFFECTS.update(DELAYED_FINISH_CASTS)

from .historical_final_combat_spells import CAST_EFFECTS as FINAL_COMBAT_CASTS
CAST_EFFECTS.update(FINAL_COMBAT_CASTS)

from .historical_obligation_spells import CAST_EFFECTS as OBLIGATION_CASTS
CAST_EFFECTS.update(OBLIGATION_CASTS)
