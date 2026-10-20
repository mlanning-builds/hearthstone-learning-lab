"""Explicit generated attack weapons and the physical Banana depletion chain."""
TOKEN_RULES={cid:('none',[]) for cid in ('TTN_467','TTN_725','TTN_088','DEEP_016','JAM_011','RLK_012','TOY_522','TOY_522t')}
TOKEN_RULES.update({
 'ETC_201':('minion',[('buff',1,1),('add','ETC_201t',1)]),
 'ETC_201t':('minion',[('buff',1,1),('add','ETC_201t2',1)]),
 'ETC_201t2':('minion',[('buff',1,1)]),
})
TOKEN_RULES.update({
 'ETC_207':('none',[('summon','CS2_127',1),('add','ETC_207t',1)]),
 'ETC_207t':('none',[('summon','CS2_127',1),('add','ETC_207t2',1)]),
 'ETC_207t2':('none',[('summon','CS2_127',1)]),
})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)
WEAPON_TRIGGERS={
 'TTN_725':[('historical_attack_weapon_tempest',)],
 'RLK_012':[('historical_attack_weapon_soulbreaker',)],
 'TOY_522':[('historical_attack_weapon_watercannon',)],
}


def before_hero_attack(game,owner,target):
 weapon=game.players[owner].weapon
 if weapon is None:return
 cid=weapon['card_id']
 if cid in ('ONY_005ta3','VAC_464t4') and target>0:
  minion=game._force_live(target)
  if minion is not None:game._silence(minion)
 if cid=='MIS_101' and game.players[owner].corpses>=3:
  game._spend_corpses(owner,3);game._buff_weapon(owner,0,1)
 elif cid=='TTN_467':game._effect(('armor',4),dict(owner=owner,source=None,target=0,bonus=0,lifesteal=False,card_id=cid))
 elif cid=='JAM_011' and target>0 and game._force_live(target) is not None:
  game._effect(('set_target_stats',3,3),dict(owner=owner,source=None,target=target,bonus=0,lifesteal=False,card_id=cid))


def split(game,op,ctx):
 if op[0]!='historical_attack_weapon_water_group':return None
 state=dict(summoned=[],mode='random_enemy_character')
 return ('historical_attack_weapon_water_summon',state),(('force_group_attacks',state),)


def execute(game,op,ctx):
 owner=ctx['owner'];p=game.players[owner];name=op[0]
 if name=='historical_attack_weapon_phaoris':
  if ctx.get('attack_killed'):game._buff_weapon(owner,2,1)
 elif name=='historical_attack_weapon_tempest':
  values=[(game.hero_id(1-owner),game.players[1-owner].health)]+[(m.uid,m.health) for m in game.players[1-owner].minions if m.health>0]
  lowest=min(health for _,health in values)
  game._deal_effect(game.rng.choice([uid for uid,health in values if health==lowest]),3,ctx)
 elif name=='historical_attack_weapon_soulbreaker':
  if ctx.get('attack_killed'):game._gain_corpses(owner,2)
 elif name=='historical_attack_weapon_watercannon':
  game._rule_events.append(('captured_effects',dict(operations=(('historical_attack_weapon_water_group',),),context=dict(ctx)),[]))
 elif name=='historical_attack_weapon_water_summon':
  before={m.uid for m in p.minions}
  game._summon(owner,'TOY_522t',entry_origin='effect',entry_site='watercannon')
  op[1]['summoned'].extend(m.uid for m in p.minions if m.uid not in before and m.card_id=='TOY_522t')
 else:return False
 return True

WEAPON_TRIGGERS.update({'ONY_005tb6':[('historical_attack_weapon_phaoris',)],'ONY_005tc7':[('area_damage','enemies',4)]})
