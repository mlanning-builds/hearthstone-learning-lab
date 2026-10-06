"""Staged Noggenfogger target replacement at action resolution boundaries.

Printed type restrictions and client immunity/Stealth ordering still require
independent review; this is not an admitted targeting contract.
"""
from dataclasses import replace
RULES={'CORE_CFM_670':('none',[])}
class RandomTargets:
 def _noggenfogger_active(self):return any(self._active('CORE_CFM_670',owner) for owner in (0,1))
 def _random_action_target(self,action):
  if not action.target or not self._noggenfogger_active():return action
  owner=self.current
  if action.kind=='play':
   card=next(c for c in self.players[owner].hand if c.uid==action.source)
   from .cards import RULES,CHOICES
   rule=self._crafted_rule(card) or RULES.get(card.card_id,('none',()))
   mode=rule[0]
   if card.card_id in CHOICES and action.choices and action.choices[0]>=0:mode=CHOICES[card.card_id][action.choices[0]][1]
   if mode in ('none','weapon_required'):return action
   if 'location' in mode:targets=[x.uid for p in self.players for x in p.locations]
   else:
    characters=self._visible_targets(owner,magic=self.cards[card.card_id]['type']=='SPELL')
    targets=characters if 'character' in mode else [uid for uid in characters if uid>0]
  elif action.kind=='power':
   targets=self._visible_targets(owner,magic=True)
   if action.choices==(1,):targets=[uid for uid in targets if uid>0]
  else:return action
  return replace(action,target=self.rng.choice(targets)) if targets else action
 def _random_attack_target(self,source,target):
  if not self._noggenfogger_active():return target
  targets=[self.hero_id(i) for i,p in enumerate(self.players) if not self._hero_immune(i)]
  targets.extend(m.uid for p in self.players for m in p.minions if m.health>0 and 'STEALTH' not in self._effective_keywords(m) and 'IMMUNE' not in self._effective_keywords(m))
  targets=[uid for uid in targets if uid!=source]
  return self.rng.choice(targets) if targets else target
