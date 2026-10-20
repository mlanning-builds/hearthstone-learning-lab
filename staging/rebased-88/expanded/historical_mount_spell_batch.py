"""Attached historical mounts and Twinspell programs; unvalidated."""

def op(name,*args):return ('historical_utility_mount_batch_'+name,)+args
TOKEN_RULES={
 'LOE_105':('minion',[('buff',1,1),op('attach',('add','LOE_105',1))]),
 'WON_022':('minion',[('buff',1,1),op('attach',('add','WON_022',1))]),
 'ONY_012':('minion',[('buff',1,2),('historical_event_spell_damage','target',1),op('attach',('summon','ONY_012t',1))]),
 'ONY_012t':('none',[]),
 'SW_316':('minion',[('buff',1,1),('keyword','DIVINE_SHIELD'),op('attach',('summon','SW_316t',1))]),
 'SW_316t':('none',[]),
 'SW_432':('minion',[('buff',4,2),('keyword','RUSH'),op('attach',('summon','SW_432t',1))]),
 'SW_432t':('none',[]),
 'SW_443':('minion',[('buff',4,7),('keyword','TAUNT'),op('attach',('summon','SW_443t',1))]),
 'SW_443t':('none',[]),
 'SW_458':('minion',[('buff',2,2),('keyword','IMMUNE_WHILE_ATTACKING'),op('attach',('summon','SW_458t',1))]),
 'SW_458t':('none',[]),
 'SW_087':('minion',[('buff',1,1),op('attach',('summon','SW_087t',1))]),
 'SW_087t':('none',[]),
 'WON_021':('none',[('summon','FP1_011',3)]),
 'ICC_244':('minion',[op('attach',op('resummon_one_health'))]),
 'YOD_005':('historic_beast',[('buff',2,2),('add','YOD_005ts',1)]),
 'YOD_005ts':('historic_beast',[('buff',2,2)]),
 'YOD_012':('none',[op('recruit'),op('recruit'),('add','YOD_012ts',1)]),
 'YOD_012ts':('none',[op('recruit'),op('recruit')]),
}
DEATH_EFFECTS={'SW_087t':[op('delayed_dreadsteed')]}
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

def execute(game,operation,ctx):
 name=operation[0];owner=ctx['owner']
 if name==op('attach')[0]:
  m=game._force_live(ctx.get('target'))
  if m is not None:m.attached_death_effects.append(operation[1]);m.keywords.add('DEATHRATTLE')
  return True
 if name==op('delayed_dreadsteed')[0]:
  game._schedule_turn_effect(game.current,'end',0,1,(('historical_copy_summon_owner',owner,'SW_087t'),),source_card_id='SW_087t')
  return True
 if name==op('resummon_one_health')[0]:
  source=ctx.get('source')
  if source is not None:
   card=game._fresh_replay_card(source)
   m=game._summon(owner,source.card_id,entry_source=card,entry_zone='hand',entry_origin='resurrection',entry_site='desperate_stand')
   if m is not None:m.health=1
  return True
 if name==op('recruit')[0]:
  game._summon(owner,'CS2_101t',entry_keywords=('TAUNT',),entry_origin='effect',entry_site='air_raid')
  return True
 return False
