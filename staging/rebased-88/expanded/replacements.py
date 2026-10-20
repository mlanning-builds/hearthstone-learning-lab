"""Staged summon, trigger and hero-damage replacements.

Consumers remain separate from live admission and client-conformance evidence.
"""
from engine.game import Card
from engine.cards import UnsupportedCard
from .imbue import IMBUE_POWERS
RULES={cid:('none',[]) for cid in ('CORE_DAL_575','TIME_064','JAIL_443')}

class Replacements:
 def _card_summon_repetitions(self,owner,origin):
  if origin in ('play','hero_power','unspecified'):return 1
  count=sum(m.card_id=='CORE_DAL_575' and not m.silenced and m.health>0 for m in self.players[owner].minions)
  return min(128,2**count)
 def _trigger_repetitions(self,owner):
  return 2 if self._active('TIME_064',owner) else 1
 def _battlecry_repetitions(self,owner):
  return max(self._trigger_repetitions(owner),2 if self._active('LOE_077',owner) or self._active('CORE_LOE_077',owner) or self._active('TRL_092',owner) or getattr(self.players[owner],'historical_double_battlecries',False) or getattr(self.players[owner],'historical_virnaal_turn',None)==self.turn else 1)
 def _replace_plague_damage(self,target,amount,source):
  if target>=0 or source is None or getattr(source,'card_id',None)!='JAIL_443' or getattr(source,'silenced',False):return False
  if 'JAIL_443t' not in self.cards:raise UnsupportedCard('Missing Blight dependency')
  victim=-target-1
  count=min(amount,max(0,99-len(self.players[victim].deck)))
  if count:
   cards=[Card(self._new_id(),'JAIL_443t') for _ in range(count)]
   self.players[victim].deck.extend(cards)
   self.rng.shuffle(self.players[victim].deck)
   self._record_deck_insertion(victim,source.owner,count,'shuffle',cards=cards)
  self._log('plague_damage_replaced',player=source.owner,target=target,count=amount)
  return True
 def _repeated_power_operations(self,owner):
  p=self.players[owner];power=p.primary_power
  if power:
   if 'upgraded_starting_class' in power:return self._genn_power_operations(owner)
   if 'basic_starting_class' in power:return self._basic_power_operations(power['basic_starting_class'])
   cid=power['card_id']
   if cid=='UNG_917t1':return (('buff',3,3),)
   from .historical_mad_genius import power_operations as boom_operations
   boom=boom_operations(self,owner)
   if boom is not None:return boom
   from .historical_brukan import power_operations as brukan_operations
   brukan=brukan_operations(self,owner)
   if brukan is not None:return brukan
   if cid=='AV_113p':return (('companions_random',),)
   if cid=='AV_207p':return (('historical_devout_heal',),)
   if cid=='AV_207p2':return (('historical_copy_power_hit','target',5),)
   if cid=='AV_200p2':return (('historical_arcane_burst',),)
   if cid=='TRL_065h':return (('historical_copy_power_hit','target',2),)
   if cid=='AV_203p':return (('historical_copy_coolant',),)
   if cid=='ICC_833h':return (('historical_jaina_touch',),)
   if cid=='ICC_830p':return (('historical_copy_power_hit','target',2),)
   if cid=='ICC_481p':return (('historical_copy_evolve_target',1),)
   if cid=='AV_205p':return (('historical_guff_random',),)
   if cid=='AV_206p':return (('historical_cariel_buff',),)
   if cid=='AV_316hp':return (('on_draw_shuffle','AV_316t4',1,0),('draw',1))
   if cid=='AV_202p':return (('historical_late_slam',),)
   if cid=='ICC_829p':return (('historical_ebon_horsemen',),)
   if cid=='ICC_834h':return (('historical_ebon_bladestorm',),)
   if cid=='ICC_831p':return (('historical_dark_siphon',),)
   if cid=='AV_204p':return (('hero_attack',2),)
   if cid=='ICC_832p':return (('historical_reckless_plague',),)
   if cid in ('TOY_400t6p','TOY_400t6p2','BT_429p','BT_429p2'):return (('damage',5),)
   if cid=='ICC_828p':return (('forge_zombeast_plain',),)
   from .historical_copy_batches import HISTORICAL_POWER_OPERATIONS
   if cid in HISTORICAL_POWER_OPERATIONS:return HISTORICAL_POWER_OPERATIONS[cid]
   from .historical_galakrond_batches import POWERS,power_operations
   if cid in POWERS:return tuple(power_operations(cid))
   if cid=='OG_006b':return (('power_summon','OG_006a',1,0,0),)
   if cid in IMBUE_POWERS.values():return tuple(self._imbue_power_operations(owner))
   if cid=='CATA_190p':return (('hero_attack',5),)
   if cid=='TLC_513hp':return (('origin_draw',False,False),)*2
   if cid=='EX1_tk33':return (('power_summon','EX1_tk34',1,0,0),)
   if cid in ('TLC_632t','TLC_632t2','JAIL_EVENT_101hp','UNG_934t2'):
    return (('damage_random_enemy',power.get('damage',2) if cid=='JAIL_EVENT_101hp' else 8),)
   raise UnsupportedCard('Repeated Hero Power body not implemented: '+cid)
  return self._basic_power_operations(p.hero_class)
 def _basic_power_operations(self,hero_class):
  return {
   'WARRIOR':(('armor',2),), 'HUNTER':(('damage_enemy_hero',2),),
   'MAGE':(('damage',1),), 'PRIEST':(('heal',2),),
   'DRUID':(('hero_attack',1),('armor',1)), 'DEMONHUNTER':(('hero_attack',1),),
   'WARLOCK':(('draw',1),('damage_own_hero',2)), 'ROGUE':(('equip','CS2_082'),),
   'PALADIN':(('power_summon','CS2_101t',1,0,0),),
   'DEATHKNIGHT':(('replacement_ghoul',),), 'SHAMAN':(('replacement_totem',),),
  }[hero_class]
 def _replacement_effect(self,op,ctx):
  owner=ctx['owner'];p=self.players[owner]
  if op[0]=='replacement_ghoul':self._summon(owner,'TOKEN_GHOUL',expires=True,entry_origin='hero_power',entry_site='repeated_power')
  elif op[0]=='replacement_totem':
   from .game import BASIC_TOTEM_POOL
   values=BASIC_TOTEM_POOL.resolve(self.cards,self.cards,exclude={m.card_id for m in p.minions})
   if values:self._summon(owner,self.rng.choice(values),entry_origin='hero_power',entry_site='repeated_power')
  elif op[0]=='replacement_power_consumed':
   power=p.primary_power
   if power and power.get('uid')==op[1] and power['card_id'] in ('TLC_632t','TLC_632t2'):
    power['remaining']-=1
    if power['remaining']==0:self._replace_primary_power(owner,power['restore'])
    else:power['card_id']='TLC_632t2'
  else:return False
  return True
