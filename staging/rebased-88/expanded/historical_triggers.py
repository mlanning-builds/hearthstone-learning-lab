"""Generated historical triggers expressed through reviewed existing event operations.

Printed identities come from the pinned all-card snapshot. Trigger registration
is explicit even when that snapshot omits TRIGGER_VISUAL; this tag is not an
eligibility gate. No curated generation pool is inferred here.
"""
TRIGGERS={
 'RLK_538':('b60_friendly_death',[('inherit_friendly_deathrattle',)]),
 'EX1_007':('damaged_self',[('draw',1)]),
 'EX1_095':('spell_cast',[('draw',1)]),
 'EX1_399':('damaged_self',[('buff_self',3,0)]),
 'EX1_604':('damaged_minion',[('buff_self',1,0)]),
 'NEW1_012':('spell_cast',[('buff_self',1,0)]),
 'CFM_060':('spell_cast',[('buff_self',2,0)]),
 'EX1_187':('spell_cast',[('buff_self',2,2)]),
 'KAR_036':('spell_cast',[('buff_self',0,1)]),
 'KAR_035':('spell_cast',[('heal_own_hero',3)]),
 'NEW1_020':('spell_cast',[('area_damage','all_minions',1)]),
 'BRM_002':('spell_cast',[('missiles','enemies',2)]),
 'ONY_007':('spell_cast',[('missiles','enemies',4)]),
 'DAL_182':('spell_cast',[('damage_random_enemy_minion',1)]),
 'CFM_807':('spell_cast',[('refresh_power',)]),
 'BOT_059':('damaged_self',[('armor',2)]),
 'BRM_016':('damaged_self',[('damage_enemy_hero',2)]),
 'WON_338':('damaged_self',[('damage_enemy_hero',2)]),
 'WON_357':('damaged_self',[('draw',1)]),
 'BRM_006':('damaged_self',[('summon','BRM_006t',1)]),
 'BRM_022':('damaged_self',[('summon','BRM_022t',1)]),
 'AV_129':('damaged_self',[('board_buff',1,0)]),
 'AV_401':('spell_cast',[('buff_random_hand_minion','friendly',1,1)]),
 'UNG_087':('damaged_self',[('damage_own_hero',3)]),
 'UNG_079':('attacked_self',[('freeze_self',)]),
 'RLK_117':('attacked_self',[('destroy_self',)]),
 'NX2_002':('spell_cast',[('area_damage','enemy_minions',1)]),
 'SW_459':('attacked_self',[('tribe_board_buff','BEAST',1,1)]),
 'EX1_559':('spell_cast',[('add','CS2_029',1)]),
 'NEW1_026':('spell_cast',[('summon','NEW1_026t',1)]),
 'TRL_131':('spell_cast',[('summon','TRL_131t',1)]),
 'BAR_035':('spell_cast',[('summon','BAR_035t',1)]),
}
RULES={cid:('none',[]) for cid in TRIGGERS}
GENERATED_IDS=frozenset(RULES)
TOKEN_RULES={cid:('none',[]) for cid in ('BRM_006t','BRM_022t','NEW1_026t','TRL_131t','BAR_035t')}
TOKEN_IDS=set(TOKEN_RULES)
SOURCE='data/standard/all_cards.json.gz pinned English printed card definitions'
