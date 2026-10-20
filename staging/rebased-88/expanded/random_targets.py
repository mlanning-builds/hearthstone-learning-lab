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
   targets=[uid for uid in self._targets_for(card.card_id,owner,mode_override=mode) if uid]
  elif action.kind=='power':
   if action.choices==(1,):targets=[uid for uid in self._visible_targets(owner,magic=True) if uid>0]
   elif self.players[owner].primary_power is not None:targets=[uid for uid in self._replacement_power_targets(owner) if uid]
   else:targets=self._visible_targets(owner,magic=True)
  else:return action
  return replace(action,target=self.rng.choice(targets)) if targets else action
 def _random_attack_target(self,source,target):
  if not self._noggenfogger_active():return target
  owner=self._find(source).owner if source>0 else -source-1
  opponent=1-owner
  targets=[] if self._hero_immune(opponent) or self._hero_stealth(opponent) else [self.hero_id(opponent)]
  targets.extend(m.uid for m in self.players[opponent].minions if m.health>0 and 'STEALTH' not in self._effective_keywords(m) and 'IMMUNE' not in self._effective_keywords(m))
  return self.rng.choice(targets) if targets else target
