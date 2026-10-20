"""Explicit historical self-scaling Battlecries from frozen printed records.

Counts are evaluated at Battlecry resolution, after physical hand removal and
board entry. No pools or probability assumptions are introduced.
"""
from .selectors import has_school,has_tribe
SPECS={
 'AT_047':('totems',1,1), 'BOT_226':('hero_damage',1,0),
 'BOT_413':('hand_spells',0,1), 'CS2_226':('other_friendly',1,1),
 'DAL_095':('hand_spells',1,0), 'DAL_560':('other_friendly',2,2),
 'DMF_121':('hand_spells',1,1), 'DRG_060':('enemy_hand',1,0),
 'GIL_507':('hand',0,1), 'GVG_097':('enemy_deathrattle',1,1),
 'ICC_450':('damaged',1,1), 'ICC_904':('deaths',1,1),
 'OG_320':('other_hand',1,0), 'RLK_110':('frost_hand',1,0),
 'TRL_071':('other_pirates',1,1), 'TSC_213':('spells_cast',1,1),
}
RULES={cid:('none',[('historical_self_scale',*spec)]) for cid,spec in SPECS.items()}
class HistoricalScaling:
 def _historical_scaling_effect(self,op,ctx):
  if op[0]!='historical_self_scale':return False
  source=ctx.get('source');owner=ctx['owner'];p=self.players[owner];enemy=self.players[1-owner]
  if source is None:return True
  kind,attack,health=op[1:];physical=ctx.get('physical_card')
  hand=[c for c in p.hand if c is not physical]
  friendly=[m for m in p.minions if m.health>0]
  if kind=='totems':count=sum(has_tribe(self._card_data(m),'TOTEM') for m in friendly)
  elif kind=='hero_damage':count=p.hero_damage_taken_turn
  elif kind=='hand_spells':count=sum(self.cards[c.card_id]['type']=='SPELL' for c in hand)
  elif kind=='other_friendly':count=sum(m.uid!=source.uid for m in friendly)
  elif kind=='enemy_hand':count=len(enemy.hand)
  elif kind in ('hand','other_hand'):count=len(hand)
  elif kind=='enemy_deathrattle':count=sum(bool(self._death_operations(m)) for m in enemy.minions if m.health>0)
  elif kind=='damaged':count=sum(0<m.health<m.max_health for player in self.players for m in player.minions)
  elif kind=='deaths':count=sum(player.minions_died_turn for player in self.players)
  elif kind=='frost_hand':count=sum(has_school(self.cards[c.card_id],'FROST') for c in hand)
  elif kind=='other_pirates':count=sum(m.uid!=source.uid and has_tribe(self._card_data(m),'PIRATE') for m in friendly)
  elif kind=='spells_cast':count=p.spells_cast_turn
  else:raise ValueError('Unknown historical scaling counter: '+str(kind))
  self._buff(source,count*attack,count*health)
  return True

GENERATED_IDS=frozenset(RULES)
