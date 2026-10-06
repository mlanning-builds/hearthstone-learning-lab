"""Staged held parity and all eleven upgraded starting Hero Powers."""
from engine.cards import UnsupportedCard
CLASSES=('WARRIOR','SHAMAN','ROGUE','PALADIN','HUNTER','DRUID','WARLOCK','MAGE','PRIEST','DEMONHUNTER','DEATHKNIGHT')
POWERS={name:'HERO_%02dbp2'%(i+1) for i,name in enumerate(CLASSES)}
RULES={'CATA_615':('none',[])}
TOKEN_RULES={'CATA_615t':('none',[('genn_upgrade',)])}
class Genn:
 def _genn_checkpoint(self):
  for owner,p in enumerate(self.players):
   for c in p.hand:
    if c.card_id!='CATA_615':continue
    parities={self._cost(other,owner)%2 for other in p.hand if other is not c}
    if len(parities)<=1:
     if 'CATA_615t' not in self.cards:raise UnsupportedCard('Missing Worgen King')
     self._b60_transform_card(c,'CATA_615t');return True
  return False
 def _genn_power_operations(self,owner):
  power=self.players[owner].primary_power;k=power['upgraded_starting_class']
  return {
   'WARRIOR':(('armor',4),), 'HUNTER':(('damage_enemy_hero',3),),
   'MAGE':(('damage',2),), 'PRIEST':(('heal',4),),
   'DRUID':(('hero_attack',2),('armor',2)), 'DEMONHUNTER':(('hero_attack',2),),
   'WARLOCK':(('draw',1),), 'ROGUE':(('equip','AT_132_ROGUEt'),),
   'PALADIN':(('power_summon','CS2_101t',2,0,0),),
   'DEATHKNIGHT':(('genn_ghoul',),), 'SHAMAN':(('genn_totem',),),
  }[k]
 def _genn_effect(self,op,ctx):
  owner=ctx['owner'];p=self.players[owner]
  if op[0]=='genn_upgrade':
   k=getattr(p,'starting_hero_class',p.hero_class);cid=POWERS[k]
   if cid not in self.cards:raise UnsupportedCard('Missing upgraded starting power: '+cid)
   self._replace_primary_power(owner,dict(card_id=cid,upgraded_starting_class=k,cost=1))
  elif op[0]=='genn_ghoul':self._summon(owner,'TOKEN_GHOUL',attack_bonus=1,expires=True,entry_origin='hero_power',entry_site='genn_power')
  elif op[0]=='genn_totem':
   from .game import BASIC_TOTEM_POOL
   choices=BASIC_TOTEM_POOL.resolve(self.cards,self.cards)
   if choices and len(p.board)<7:
    self.pending_choice=dict(owner=owner,kind='genn_totem',options=[dict(card_id=cid) for cid in choices]);self.phase='choice'
  else:return False
  return True
 def _genn_choice(self,choice,selected):
  if choice['kind']!='genn_totem':return False
  self._summon(choice['owner'],selected['card_id'],entry_origin='hero_power',entry_site='genn_totem')
  return True
