"""Staged positive-stat gain reaction and original-deck stat distribution."""
from .historical_saidan import add as _saidan_add
from engine.game import Card
from engine.cards import UnsupportedCard
RULES={'JAIL_330':('none',[]),'CATA_213':('none',[('vyranoth_stats',)])}
class StatRules:
 def _champion_checkpoint(self):
  for p in self.players:
   for c in p.hand+p.deck:
    if not isinstance(c,Card) or c.card_id!='JAIL_330':continue
    current=(c.attack_bonus,c.health_bonus);old=getattr(c,'_champion_stats',(0,0))
    if current[0]>old[0] or current[1]>old[1]:_saidan_add(c,'attack_bonus',1);_saidan_add(c,'health_bonus',1)
    c._champion_stats=(c.attack_bonus,c.health_bonus)
   for m in p.all_minions:
    if m.card_id!='JAIL_330':continue
    current=(m.attack-m.aura_attack,m.max_health-m.aura_health)
    old=getattr(m,'_champion_stats',current)
    if not m.silenced and not m.dormant and (current[0]>old[0] or current[1]>old[1]):
     self._adjust_minion_attack(m,1);m.max_health+=1;m.health+=1
    m._champion_stats=(m.attack-m.aura_attack,m.max_health-m.aura_health)
 def _stat_rule_effect(self,op,ctx):
  if op[0]!='vyranoth_stats':return False
  owner=ctx['owner'];p=self.players[owner]
  total=sum(self._starting_card_data(owner,cid)['cost'] for cid in p.starting_deck if self._starting_card_data(owner,cid)['type']=='MINION')
  if total!=100:return True
  indices=[i for i,c in enumerate(p.deck) if self._card_data(c)['type']=='MINION']
  if not indices:return True
  amount,remainder=divmod(50,len(indices))
  extra_attack=extra_health=set()
  if remainder:
   from .approximation_policy import mark
   mark(self,'vyranoth')
   extra_attack=set(self.rng.sample(indices,remainder));extra_health=set(self.rng.sample(indices,remainder))
  # Designer clarification specifies even +50/+50, not fifty independent rolls.
  for i in indices:
   c=p.deck[i]
   if not isinstance(c,Card):c=Card(self._new_id(),c);p.deck[i]=c
   _saidan_add(c,'attack_bonus',amount+int(i in extra_attack));_saidan_add(c,'health_bonus',amount+int(i in extra_health))
  self._champion_checkpoint()
  return True
