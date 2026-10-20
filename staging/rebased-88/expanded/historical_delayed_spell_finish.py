"""Historical delayed spells, attached deaths and on-draw obligations."""
from engine.game import Card
from .generation_cards import random_cards
from .transformations import evolve_pool

def op(name,*args):return ('historical_utility_delayed_finish_'+name,)+args
TOKEN_RULES={
 'EX1_137':('none',[('damage_enemy_hero',2),('historical_if_combo',('schedule_turn_effect','start',1,1,(('add','EX1_137',1),)))]),
 'LOE_111':('none',[('area_damage','all_minions',3),('on_draw_shuffle','LOE_111',1,1)]),
 'ICC_849':('enemy_minion',[op('embrace')]),
 'DRG_302':('minion',[op('attach',op('resummon_twice'))]),
 'LOOT_344':('none',[op('talismans')]),
 'TRL_082':('friendly_minion',[op('attach',op('voodoo'))]),
 'VAC_416':('enemy_minion',[op('death_roll')]),
 'VAC_417':('enemy_minion',[op('sensory')]),
 'LEG_RLK_039':('none',[('gain_corpses',4),('on_draw_shuffle','RLK_039t',4,0)]),
 'RLK_039t':('none',[('summon','RLK_070t',1)]),
 'ONY_034':('none',[('on_draw_shuffle','ONY_034t',3,1)]),
 'ONY_034t':('none',[op('agony')]),
 'LOE_007':('none',[op('curse_enemy')]),
 'LOE_007t':('none',[]),
}
CAST_EFFECTS={'RLK_039t':(('summon','RLK_070t',1),),'ONY_034t':(op('agony'),)}
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

def sequence(game,ctx,operations):
 operations=tuple(operations)
 if not operations:return ('batch30_noop',),()
 first,tail=game._split_fixed_summon(operations[0],ctx)
 return first,tuple(tail)+operations[1:]

def split(game,operation,ctx):
 name=operation[0];owner=ctx['owner'];p=game.players[owner]
 if name==op('resummon_twice')[0]:
  source=ctx.get('source')
  if source is None:return ('batch30_noop',),()
  card=game._fresh_replay_card(source)
  return sequence(game,ctx,(op('summon_card',card),op('summon_card',card)))
 if name==op('voodoo')[0]:
  source=ctx.get('source')
  if source is None:return ('batch30_noop',),()
  return game._split_fixed_summon(random_cards(evolve_pool(game._card_stat(source,'cost',owner),1),destination='board'),ctx)
 if name==op('death_roll')[0]:
  target=game._force_live(ctx.get('target'))
  if target is None:return ('batch30_noop',),()
  amount=target.attack
  return ('destroy',),(('missiles','enemies',amount),)
 if name==op('sensory')[0]:
  target=game._force_live(ctx.get('target'))
  if target is None:return ('batch30_noop',),()
  from copy import deepcopy
  return op('copy',deepcopy(target)),(op('sensory_after',target.uid),)
 return None

def turn_entries(game,phase):
 if phase!='start':return []
 return [dict(source=None,order=c.uid,card_id='LOE_007t',operations=(op('held_curse_damage'),)) for c in game.players[game.current].hand if c.card_id=='LOE_007t']

def execute(game,operation,ctx):
 prefix='historical_utility_delayed_finish_'
 if not operation[0].startswith(prefix):return False
 name=operation[0][len(prefix):];owner=ctx['owner'];p=game.players[owner];target=game._force_live(ctx.get('target'))
 if name=='held_curse_damage':game._damage(game.hero_id(owner),2,damage_source=None,damage_owner=owner,damage_cause='held_curse')
 elif name=='curse_enemy':game._add(1-owner,'LOE_007t')
 elif name=='embrace':
  if target is not None:
   key=game._new_id();target.rule_state.setdefault('historical_embrace_darkness',[]).append(key)
   game._schedule_turn_effect(owner,'start',1,1,(op('control',target.uid,key),),source_card_id='ICC_849')
 elif name=='control':
  m=game._force_live(operation[1])
  if m is not None and operation[2] in m.rule_state.get('historical_embrace_darkness',()):
   m.rule_state['historical_embrace_darkness'].remove(operation[2])
   if m.owner!=owner:
    if len(p.board)>=7:m.health=0
    else:
     game.players[m.owner].board.remove(m);m.owner=owner;p.board.append(m);m.summoned_turn=game.turn;m.attacks=0;game._refresh_auras()
 elif name=='attach':
  if target is not None:target.attached_death_effects.append(operation[1]);target.keywords.add('DEATHRATTLE')
 elif name=='talismans':
  for m in p.minions:m.attached_death_effects.append(('historical_family_basic_totem',));m.keywords.add('DEATHRATTLE')
 elif name=='summon_card':
  card=operation[1];game._summon(owner,card.card_id,entry_source=card,entry_zone='hand',entry_origin='resurrection',entry_site='grave_rune')
 elif name=='copy':game._summon(owner,operation[1].card_id,copy_from=operation[1],entry_origin='copy',entry_site='sensory_deprivation')
 elif name=='sensory_after':
  victim=game._force_live(operation[1])
  if victim is not None and p.health<=20:victim.health=0
 elif name=='agony':
  p.fatigue+=1;game._damage(game.hero_id(owner),p.fatigue,damage_source=None,damage_cause='fatigue')
 else:return False
 return True
