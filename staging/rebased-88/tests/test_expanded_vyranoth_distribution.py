"""Designer-confirmed even allocations; undefined remainders fail before mutation."""
import unittest
from copy import deepcopy
from engine.game import Card
from engine.cards import UnsupportedCard
import test_expanded_generation as fixtures
class VyranothDistributionTests(unittest.TestCase):
 def game(self):
  g=fixtures.GenerationTests().game();g.players[0].starting_deck=['TIME_064']*10
  g.cards['TIME_064']=dict(g.cards['TIME_064'],cost=10);return g
 def apply(self,g):g._effect(('vyranoth_stats',),dict(owner=0,source=None,target=0,bonus=0,lifesteal=False))
 def test_even_allocations_without_random_rolls(self):
  for count in (1,2,5,10,25,50):
   with self.subTest(count=count):
    g=self.game();p=g.players[0];p.deck=[Card(g._new_id(),'CORE_EX1_162') for _ in range(count)];state=g.rng.getstate()
    self.apply(g);self.assertEqual({(c.attack_bonus,c.health_bonus) for c in p.deck},{(50//count,50//count)})
    self.assertEqual(g.rng.getstate(),state)
 def test_nonminions_untouched_and_physical_modifiers_retained(self):
  g=self.game();p=g.players[0];c=Card(g._new_id(),'CORE_EX1_162');c.attack_bonus=3;c.health_bonus=1
  p.deck=['CORE_CS2_029',c];self.apply(g);self.assertIs(p.deck[1],c)
  self.assertEqual(p.deck[0],'CORE_CS2_029');self.assertEqual((c.attack_bonus,c.health_bonus),(53,51))
 def test_approximated_remainder_conserves_exact_attack_and_health_budgets(self):
  g=self.game();p=g.players[0];p.deck=['CORE_EX1_162']*3
  self.apply(g)
  self.assertEqual(sum(c.attack_bonus for c in p.deck),50)
  self.assertEqual(sum(c.health_bonus for c in p.deck),50)
  self.assertTrue(all(c.attack_bonus in (16,17) and c.health_bonus in (16,17) for c in p.deck))
