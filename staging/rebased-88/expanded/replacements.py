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
 def _replace_plague_damage(self,target,amount,source):
  if target>=0 or source is None or getattr(source,'card_id',None)!='JAIL_443' or getattr(source,'silenced',False):return False
  if 'JAIL_443t' not in self.cards:raise UnsupportedCard('Missing Blight dependency')
  victim=-target-1
  count=min(amount,max(0,99-len(self.players[victim].deck)))
  self.players[victim].deck.extend(Card(self._new_id(),'JAIL_443t') for _ in range(count))
  self.rng.shuffle(self.players[victim].deck)
  self._record_deck_insertion(victim,source.owner,count,'shuffle')
  self._log('plague_damage_replaced',player=source.owner,target=target,count=amount)
  return True
 def _repeated_power_operations(self,owner):
  p=self.players[owner];power=p.primary_power
  if power:
   if 'upgraded_starting_class' in power:return self._genn_power_operations(owner)
   cid=power['card_id']
   if cid in IMBUE_POWERS.values():return tuple(self._imbue_power_operations(owner))
   if cid=='CATA_190p':return (('hero_attack',5),)
   if cid=='TLC_513hp':return (('origin_draw',False,False),)*2
   if cid=='EX1_tk33':return (('power_summon','EX1_tk34',1,0,0),)
   if cid in ('TLC_632t','TLC_632t2','JAIL_EVENT_101hp','UNG_934t2'):
    return (('damage_random_enemy',power.get('damage',2) if cid=='JAIL_EVENT_101hp' else 8),)
   raise UnsupportedCard('Repeated Hero Power body not implemented: '+cid)
  return {
   'WARRIOR':(('armor',2),), 'HUNTER':(('damage_enemy_hero',2),),
   'MAGE':(('damage',1),), 'PRIEST':(('heal',2),),
   'DRUID':(('hero_attack',1),('armor',1)), 'DEMONHUNTER':(('hero_attack',1),),
   'WARLOCK':(('draw',1),('damage_own_hero',2)), 'ROGUE':(('equip','CS2_082'),),
   'PALADIN':(('power_summon','CS2_101t',1,0,0),),
   'DEATHKNIGHT':(('replacement_ghoul',),), 'SHAMAN':(('replacement_totem',),),
  }[p.hero_class]
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
