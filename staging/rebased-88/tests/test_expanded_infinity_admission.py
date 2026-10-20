"""Production-registry Infinity actions and Secret battlefield-entry ordering."""
import unittest
from unittest.mock import patch
from expanded import Action,cards,infinity
import test_expanded_imbue_azure_admission as fixtures

class InfinityAdmissionTests(unittest.TestCase):
 def game(self,cid):
  fx=fixtures.ImbueAzureAdmissionTests()
  return fx,fx.game('MAGE' if cards.registry()[cid]['cardClass']=='NEUTRAL' else cards.registry()[cid]['cardClass'],cid)
 def test_paid_weapon_infinite_attack_expires_at_turn_end(self):
  fx,g=self.game('END_012');fx.play(g,'END_012')
  self.assertEqual(g.players[0].weapon['attack'],infinity.INFINITY)
  g.step(Action('end'));self.assertEqual(g.players[0].weapon['attack'],4)
 def test_paid_acolyte_restores_exact_physical_hand_cost_on_death(self):
  fx,g=self.game('END_018');c=g._add(0,'CORE_CS2_029');c.cost_delta=-1
  before=g._cost(c,0);fx.play(g,'END_018');self.assertEqual(g._cost(c,0),infinity.INFINITY-1)
  g.players[0].minions[-1].health=0;g._settle();self.assertEqual(g._cost(c,0),before)
 def test_paid_murozond_activates_on_next_owner_turn(self):
  fx,g=self.game('TIME_024');fx.play(g,'TIME_024');m=g.players[0].minions[-1]
  self.assertEqual(m.attack,8);g.step(Action('end'));self.assertEqual(m.attack,8)
  g.step(Action('end'));self.assertEqual(m.attack,infinity.INFINITY)
 def test_secret_order_uses_placement_time_not_hand_creation_time(self):
  fx,g=self.game('END_024');c=g._add(0,'END_024')
  low=g._summon(1,'CORE_CS2_188');high=g._summon(1,'CORE_EX1_162');high.health=high.max_health=10
  g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid))
  with patch.dict(cards.END_EFFECTS,{'CORE_CS2_188':[('buff_self',0,20)]}):
   g.step(Action('end'));g.step(Action('end'))
  self.assertNotIn(low,g.players[1].minions);self.assertIn(high,g.players[1].minions)
 def test_secret_before_later_minion_runs_before_its_end_buff(self):
  fx,g=self.game('END_024');fx.play(g,'END_024')
  low=g._summon(1,'CORE_CS2_188');high=g._summon(1,'CORE_EX1_162');high.health=high.max_health=10
  with patch.dict(cards.END_EFFECTS,{'CORE_CS2_188':[('buff_self',0,20)]}):
   g.step(Action('end'));g.step(Action('end'))
  self.assertIn(low,g.players[1].minions);self.assertNotIn(high,g.players[1].minions)
 def test_empty_board_retains_secret_and_shield_prevents_infinite_damage(self):
  fx,g=self.game('END_024');fx.play(g,'END_024');g.step(Action('end'));g.step(Action('end'))
  self.assertEqual(len(g.players[0].secrets),1)
  m=g._summon(1,'CORE_CS2_188');m.keywords.add('DIVINE_SHIELD')
  g.step(Action('end'));g.step(Action('end'))
  self.assertIn(m,g.players[1].minions);self.assertNotIn('DIVINE_SHIELD',m.keywords)
  self.assertFalse(g.players[0].secrets);g.assert_invariants()
