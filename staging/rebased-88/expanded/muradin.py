"""Staged Muradin family; attachment/copy edge cases remain admission gates.

Pinned TIME_209e describes a held weapon with its own return Deathrattle.
Avatar Form uses character damage, not spell damage; Blizzard 35.2 explicitly
fixed Poisonous propagation (https://hearthstone.blizzard.com/en-us/news/24271853).
"""
from engine.game import Card
from engine.cards import UnsupportedCard

HAMMER='TIME_209t'
RULES={'TIME_209':('none',[('muradin_take',)])}
TOKEN_RULES={HAMMER:('none',[]),'TIME_209t2':('friendly_character',[('avatar_form',)])}
DEATH_EFFECTS={HAMMER:[('hammer_shuffle',)]}

class Muradin:
 def _muradin_take(self,owner,source):
  if source is None or source not in self.players[owner].minions:return
  if hasattr(source,'_muradin_hammer'):
   # Repeated Battlecry cannot create a replacement for a held physical card.
   # How a second distinct Hammer replaces/joins one is not yet established.
   if any(self._card_data(c)['id']==HAMMER for zone in (self.players[owner].deck,self.players[owner].hand) for c in zone) or (self.players[owner].weapon or {}).get('card_id')==HAMMER:
    raise UnsupportedCard('Binding a second Hammer requires reviewed replacement semantics')
   return
  d=self.cards.get(HAMMER)
  if not d or d['type']!='WEAPON':raise UnsupportedCard('Missing High King Hammer metadata')
  p=self.players[owner];card=None;attack=durability=None
  # Recorded retrieval priority: deck, then hand, then equipped weapon.
  for zone in (p.deck,p.hand):
   options=[c for c in zone if self._card_data(c)['id']==HAMMER]
   if options:
    value=self.rng.choice(options) if len(options)>1 else options[0]
    zone.remove(value);card=value if isinstance(value,Card) else Card(self._new_id(),value)
    attack=max(0,d['attack']+card.attack_bonus)
    durability=(d.get('durability') or d['health'])+card.health_bonus
    break
  if card is None and p.weapon and p.weapon['card_id']==HAMMER:
   weapon=p.weapon;card=p.equipped_card
   if card is None:raise UnsupportedCard('Equipped Hammer has no physical identity')
   attack,durability=weapon['attack'],weapon['durability']
   card.attack_bonus=attack-d['attack']
   p.weapon=None;p.equipped_card=None
  if card is None:return
  source._muradin_hammer=dict(card=card,attack=attack,durability=durability)
  self._refresh_auras()
  self._log('muradin_holds_hammer',player=owner,entity=source.uid)

 def _muradin_death_operations(self,m):
  return (('muradin_return',),) if hasattr(m,'_muradin_hammer') else ()

 def _avatar_after_attack(self,owner,attacker,hero_keywords):
  entity=attacker if attacker is not None else self.players[owner]
  bindings=entity.rule_state.get('avatar_form',[]) if attacker is not None else entity.avatar_form
  for binding in tuple(bindings):
   if binding['turn']!=self.turn:continue
   context=dict(owner=owner,source=attacker,target=0,bonus=0,spell=False,
                lifesteal='LIFESTEAL' in hero_keywords,poisonous='POISONOUS' in hero_keywords)
   self._rule_events.append(('captured_effects',dict(
    operations=(('avatar_wave',binding['uid']),),context=context),[]))

 def _muradin_effect(self,op,ctx):
  name=op[0];owner=ctx['owner'];p=self.players[owner];source=ctx.get('source')
  if name=='muradin_take':self._muradin_take(owner,source)
  elif name=='muradin_return':
   held=getattr(source,'_muradin_hammer',None)
   if held is not None:
    del source._muradin_hammer
    self._enter_hand(owner,held['card'])
  elif name=='hammer_shuffle':
   weapon=ctx.get('broken_weapon');card=ctx.get('broken_weapon_card')
   if weapon is None or card is None or card.card_id!=HAMMER:
    raise UnsupportedCard('Hammer shuffle requires its broken physical card')
   if weapon.get('_hammer_shuffled'):return True
   weapon['_hammer_shuffled']=True
   card.attack_bonus=weapon['attack']-self.cards[HAMMER]['attack']+2
   # Return the same card. Damage to equipped durability is not a permanent
   # enchantment; retained printed/held durability bonuses remain on the card.
   p.deck.insert(self.rng.randrange(len(p.deck)+1),card)
   self._record_deck_insertion(owner,owner,1,'shuffle')
   self._log('hammer_shuffled',player=owner,attack=self.cards[HAMMER]['attack']+card.attack_bonus)
  elif name=='avatar_form':
   target=ctx.get('target',0)
   if target<0:
    if -target-1!=owner:return True
    p.temporary_attack+=2;bindings=p.avatar_form
   else:
    m=next((m for m in p.minions if m.uid==target),None)
    if m is None:return True
    self._adjust_minion_attack(m,2);m.temporary_attack+=2
    bindings=m.rule_state.setdefault('avatar_form',[])
   bindings.append(dict(uid=self._new_id(),turn=self.turn))
  elif name=='avatar_wave':
   if source is not None:
    if source not in self.players[source.owner].minions:return True
    bindings=source.rule_state.get('avatar_form',[])
    owner=source.owner
   else:bindings=p.avatar_form
   if not any(b['uid']==op[1] and b['turn']==self.turn for b in bindings):return True
   damage_ctx=dict(ctx,owner=owner,spell=False,bonus=0)
   targets=[self.hero_id(1-owner)]+[m.uid for m in self.players[1-owner].minions]
   with self._damage_batch():
    for target in targets:self._deal_effect(target,2,damage_ctx)
  else:return False
  return True
