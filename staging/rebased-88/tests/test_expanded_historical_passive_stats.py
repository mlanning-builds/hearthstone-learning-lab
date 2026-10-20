"""Live-zone passive contracts for explicit historical recipes."""
import gzip,json,unittest
from unittest.mock import patch
import test_expanded_generation as fixtures
from expanded import cards
from expanded.historical_passive_stats import HistoricalPassiveStats,RULES,AURAS,CONDITIONAL_ATTACK
class HistoricalPassiveTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with gzip.open('data/standard/all_cards.json.gz','rt') as f:cls.records={d['id']:d for d in json.load(f) if d['id'] in RULES}
 def setUp(self):
  self.fx=fixtures.GenerationTests();self.g=self.fx.game();self.g.cards.update(self.records);self.p,self.q=self.g.players
  for target,source in ((cards.RULES,RULES),(cards.AURAS,AURAS),(cards.CONDITIONAL_ATTACK,CONDITIONAL_ATTACK)):
   patcher=patch.dict(target,source);patcher.start();self.addCleanup(patcher.stop)
 def intrinsic(self,c):return HistoricalPassiveStats._historical_intrinsic_cost(self.g,c,0,self.g.cards[c.card_id]['cost'])
 def aura(self,c,cost):return HistoricalPassiveStats._historical_cost_aura(self.g,c,0,cost)
 def bonus(self,m):return HistoricalPassiveStats._historical_passive_aura_values(self.g,m)
 def test_board_aura_applies_and_silence_removes_source(self):
  target=self.g._summon(0,'CORE_EX1_162');before=target.attack
  source=self.g._summon(0,'CS2_122');self.assertEqual(target.attack,before+1)
  self.g._silence(source);self.assertEqual(target.attack,before)
 def test_conditional_damage_bonus_reversible(self):
  m=self.g._summon(0,'EX1_390');attack=m.attack;m.health-=1;self.g._refresh_auras();self.assertEqual(m.attack,attack+3)
  m.health=m.max_health;self.g._refresh_auras();self.assertEqual(m.attack,attack)
 def test_current_hand_discount_excludes_exact_physical_card(self):
  c=self.g._add(0,'EX1_105');self.g._add(0,'TOKEN_COIN')
  self.assertEqual(self.intrinsic(c),self.g.cards[c.card_id]['cost']-1)
  self.p.hand.remove(c);self.assertEqual(self.intrinsic(c),self.g.cards[c.card_id]['cost']-1)
 def test_self_counts_both_players_and_current_armor(self):
  c=self.g._add(0,'BRM_025');self.p.minions_died_turn=2;self.q.minions_died_turn=3
  self.assertEqual(self.intrinsic(c),self.g.cards[c.card_id]['cost']-5)
  c=self.g._add(0,'RLK_651');self.p.armor=4;self.assertEqual(self.intrinsic(c),self.g.cards[c.card_id]['cost']-4)
 def test_live_spell_tax_both_players_and_silence(self):
  c=self.g._add(0,'CORE_CS2_029');source=self.g._summon(1,'ICC_706')
  self.assertEqual(self.aura(c,6),8);self.g._silence(source);self.assertEqual(self.aura(c,6),6)
 def test_spell_reduction_floor_and_zero_cost_preservation(self):
  c=self.g._add(0,'CORE_CS2_029');self.g._summon(0,'EX1_608');self.g._summon(0,'EX1_608')
  self.assertEqual(self.aura(c,2),1);self.assertEqual(self.aura(c,0),0)
 def test_dynamic_dragons_and_other_beasts_update(self):
  raven=self.g._summon(0,'DRG_058');self.assertEqual(self.bonus(raven),(0,0))
  c=self.g._add(0,'CORE_EX1_162');self.g.cards[c.card_id]=dict(self.g.cards[c.card_id],races=['DRAGON'])
  self.assertEqual(self.bonus(raven),(2,0));self.p.hand.remove(c);self.assertEqual(self.bonus(raven),(0,0))
 def test_full_health_and_owner_turn_dynamic_bonus(self):
  m=self.g._summon(0,'BT_730');self.assertEqual(self.bonus(m),(2,0));m.health-=1;self.assertEqual(self.bonus(m),(0,0))
  m=self.g._summon(0,'TTN_713');self.assertEqual(self.bonus(m),(4,0));self.g.current=1;self.assertEqual(self.bonus(m),(0,0))
if __name__=='__main__':unittest.main()
