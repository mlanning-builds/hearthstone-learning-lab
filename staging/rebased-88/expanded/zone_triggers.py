"""Staged hero-bound resurrection and damage-triggered physical recruits.

The frozen archive is authoritative for card text. Timing and cross-zone edge
cases remain gated by the fidelity inventory before live registration.
"""
from engine.game import Card

DEATH_EFFECTS={'JAIL_398':[('area_damage','other_characters',3)]}
RULES={'JAIL_398':('none',[]),'TIME_618':('none',[('hero_eternal_life',)]),'JAIL_421':('none',[])}

class ZoneTriggers:
 def _zone_card_removed(self,owner,card,zone,cause):
  if zone not in ('hand','deck') or cause not in ('discard','destroy'):raise ValueError('Invalid zone destruction context')
  cid=self._card_data(card)['id']
  if cid!='JAIL_398':return
  self._rule_events.append(('captured_effects',dict(operations=tuple(DEATH_EFFECTS[cid]),context=dict(owner=owner,source=None,target=0,bonus=0,lifesteal=False)),[]))

 def _zone_trigger_effect(self,op,ctx):
  owner=ctx['owner'];p=self.players[owner]
  if op[0]=='hero_eternal_life':
   # Repeated Battlecries refresh one enchantment, rather than stacking lives.
   p.eternal_life=True
  elif op[0]=='zone_damage_recruit':
   card=op[1];zone_name=op[2];zone=getattr(p,zone_name)
   if not any(c is card for c in zone) or len(p.board)>=7:return True
   zone.remove(card)
   self._summon(owner,card.card_id,attack_bonus=card.attack_bonus,health_bonus=card.health_bonus,
    entry_origin='recruit',entry_site='zone_damage_recruit',entry_zone=zone_name,entry_source=card)
   self._refresh_auras()
  else:return False
  return True

 def _hero_resurrections(self):
  for owner,p in enumerate(self.players):
   if p.health>0 or not p.eternal_life:continue
   p.eternal_life=False
   amount=min(20,p.corpses)
   self._spend_corpses(owner,amount)
   if amount:
    p.health=min(p.max_health,amount)
    p.hero_health_changed_turn=True
    self._log('hero_resurrected',player=owner,health=p.health,card='TIME_618')

 def _zone_damage_trigger(self,target):
  owner=-target-1 if target<0 else self._find(target).owner
  if owner!=self.current:return
  p=self.players[owner];p.damaged_characters_turn.add(target)
  if len(p.damaged_characters_turn)<4:return
  # Capture physical cards: another effect moving/replacing a card before its
  # queued trigger resolves cannot summon its replacement or draw a copy.
  for name in ('hand','deck'):
   zone=getattr(p,name)
   for index,card in enumerate(zone):
    if self._card_data(card)['id']!='JAIL_421':continue
    if not isinstance(card,Card):card=Card(self._new_id(),card);zone[index]=card
    self._rule_events.append(('captured_effects',dict(operations=(('zone_damage_recruit',card,name),),
     context=dict(owner=owner,source=None,target=0,bonus=0,lifesteal=False)),[]))
