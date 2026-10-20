"""Explicit generated damage/healing programs and post-damage continuations."""
from .generation_cards import pool,discover
from .selectors import has_tribe

def follow(amount,condition,*operations):return ('historical_damage_then',amount,condition,tuple(operations))
def finale(*operations):return ('historical_play_finale',tuple(operations))
TOKEN_RULES={
 'DEEP_011':('minion',[follow(2,'alive',('hero_attack',3))]),
 'ETC_082':('character',[follow(3,'dead',('historical_copy_recruit_one','deck',(('tribe','eq','DEMON'),),None,None))]),
 'ETC_369':('character',[('heal',8),finale(('summon','ETC_369t',1))]),
 'ETC_369t':('none',[]),
 'ETC_394':('minion',[('damage',2),finale(discover(pool(card_type='SPELL',school='FEL',classes='own_or_neutral')))]),
 'NX2_012':('minion',[('hero_attack',2),('historical_damage_hero_attack',)]),
 'NX2_017':('none',[('historical_damage_discard_area',)]),
 'NX2_019':('minion',[follow(2,'dead',('damage_enemy_hero',3))]),
 'RLK_208':('character',[('damage',4),('historical_damage_warband',)]),
 'RLK_209':('none',[('historical_damage_unleash',)]),
 'RLK_534':('none',[('missiles','enemies',5)]),
 'RLK_605':('minion',[('historical_damage_blazing',)]),
 'RLK_815':('none',[('historical_damage_undeath',)]),
 'RLK_818':('none',[('historical_damage_ricochet',)]),
 'TID_075':('none',[('historical_damage_descend',3)]),
 'JAM_002':('none',[('historical_damage_descend',5)]),
 'TOY_377':('character',[follow(3,'dead',('summon','CS2_033',1))]),
 'TOY_500':('none',[('missiles','all_minions',10)]),
 'TOY_714':('none',[('historical_damage_shelves',)]),
 'TOY_826':('none',[('historical_damage_threads',)]),
 'TSC_056':('minion',[('historical_damage_volcano_bind',)]),
 'WW_352':('character',[('damage',3),('historical_excavate_dig',False)]),
 'WW_354':('minion',[('historical_damage_corpses',)]),
 'WW_378':('minion',[follow(1,'dead',('historical_excavate_dig',False))]),
 'WW_380':('damaged_enemy_minion',[('destroy',),('historical_excavate_dig',False)]),
 'YOG_508':('character',[('historical_damage_twilight',)]),
 'YOG_509':('friendly_minion',[('buff',2,2),('historical_damage_keeper',)]),
 'YOG_526':('character',[('damage',3),('historical_if_combo',('add','YOG_514',1))]),
}
DISCARD_EFFECTS={'RLK_534':[('missiles','enemies',5)]}
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)


def victim(game,target):
 if target<0:return game.players[-target-1]
 return next((m for player in game.players for m in player.minions if m.uid==target and m.health>0),None)


def split(game,op,ctx):
 owner=ctx['owner'];p=game.players[owner];name=op[0]
 if name=='historical_damage_then':
  state={}
  return ('historical_damage_capture',op[1],state),(('historical_damage_follow',op[2],state,op[3]),)
 if name=='historical_damage_follow':
  target=op[2].get('victim')
  passed=target is not None and (target.health<=0 if op[1]=='dead' else target.health>0)
  if not passed or not op[3]:return ('batch30_noop',),()
  first,tail=game._split_fixed_summon(op[3][0],ctx)
  return first,tuple(tail)+tuple(op[3][1:])
 if name=='historical_damage_descend':
  if op[1]<1:return ('batch30_noop',),()
  return ('damage_random_enemy_minion',op[1]),((('historical_damage_descend',op[1]-1),) if op[1]>1 else ())
 if name=='historical_damage_warband':
  if any(game._card_data(card)['type']=='MINION' for card in p.deck):return ('batch30_noop',),()
  return game._split_fixed_summon(('summon','BT_036t',4),ctx)
 if name=='historical_damage_unleash':
  context=dict(ctx,lifesteal=bool(ctx.get('lifesteal') or p.max_mana>=6))
  return game._split_fixed_summon(('replay_context',(('area_damage','enemies',1),),context),ctx)
 if name=='historical_damage_undeath':return ('area_damage','enemies',4 if game._choicegen_undead_died(owner) else 2),()
 if name=='historical_damage_shelves':
  count=1+sum(has_tribe(game._card_data(card),'DRAGON') for card in p.hand)
  return ('area_damage','enemy_minions',1),tuple(('area_damage','enemy_minions',1) for _ in range(count-1))
 if name=='historical_damage_ricochet':
  targets=[m.uid for m in game.players[1-owner].minions if m.health>0]+[game.hero_id(1-owner)]
  selected=game.rng.sample(targets,min(3,len(targets)))
  operations=tuple(('replay_context',(('damage',1),),dict(ctx,target=uid)) for uid in selected)
  if not operations:return ('batch30_noop',),()
  first,tail=game._split_fixed_summon(operations[0],ctx)
  return first,tuple(tail)+operations[1:]
 return None


def execute(game,op,ctx):
 name=op[0];owner=ctx['owner'];p=game.players[owner];target=victim(game,ctx.get('target',0))
 if name=='historical_damage_capture':
  op[2]['victim']=target
  game._deal_effect(ctx.get('target',0),op[1],ctx)
 elif name=='historical_damage_hero_attack':game._deal_effect(ctx.get('target',0),game._hero_attack(owner),ctx)
 elif name=='historical_damage_discard_area':game._effect(('area_damage','all_minions',3 if getattr(p,'historical_discard_cards',()) else 2),ctx)
 elif name=='historical_damage_blazing':
  count=1+sum(m.health<m.max_health for m in p.minions)+int(p.health<p.max_health)
  if target is not None:game._buff(target,count,count)
 elif name=='historical_damage_threads':
  for player in game.players:
   for minion in player.minions:minion.attached_death_effects.append(('area_damage','all_minions',1))
 elif name=='historical_damage_volcano_bind':
  if target is not None:target.attached_death_effects.append(('area_damage','all_minions',3))
 elif name=='historical_damage_corpses':game._deal_effect(ctx.get('target',0),p.corpses,ctx)
 elif name=='historical_damage_twilight':
  uid=ctx.get('target',0);friendly=(uid==game.hero_id(owner) or uid>0 and target is not None and target.owner==owner)
  if friendly:game._heal(uid,6,healer=owner,spell=ctx.get('spell',False))
  else:game._deal_effect(uid,3,ctx)
 elif name=='historical_damage_keeper':
  if target is not None:
   amount=target.attack
   with game._damage_batch():
    for player in game.players:
     for minion in tuple(player.minions):
      if minion is not target:game._deal_effect(minion.uid,amount,ctx)
 else:return False
 return True
