"""Complete production Fel pools with physical follow-up and Health payment."""
import unittest
from expanded import Action
from expanded.health_generation import FEL
import test_expanded_imbue_azure_admission as fixtures

class FelGenerationAdmissionTests(unittest.TestCase):
 def test_whispering_stone_death_generates_two_health_payment_spells(self):
  helper=fixtures.ImbueAzureAdmissionTests();g=helper.game('WARLOCK','TLC_467')
  helper.play(g,'TLC_467');m=next(m for m in g.players[0].minions if m.card_id=='TLC_467');m.health=0;g._settle()
  self.assertEqual(len(g.players[0].hand),2)
  for c in g.players[0].hand:
   self.assertIn(c.card_id,g._generation_candidates(FEL,0));self.assertEqual(g._payment_kind(c,0),'health')
  g.step(Action('end'));g.step(Action('end'))
  self.assertTrue(all(g._payment_kind(c,0)=='health' for c in g.players[0].hand))
 def test_map_paid_selected_spell_offers_an_unchosen_spell(self):
  helper=fixtures.ImbueAzureAdmissionTests();g=helper.game('DEMONHUNTER','TLC_900')
  g.players[0].health=30;helper.play(g,'TLC_900');self.assertEqual(g.pending_choice['kind'],'map_discover')
  offered={o['card_id'] for o in g.pending_choice['options']};g.step(Action('choose',choices=(0,)))
  c=g.players[0].hand[-1];g.players[0].mana=10
  g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid))
  self.assertEqual(g.pending_choice['kind'],'map_follow');self.assertNotIn(c.card_id,{o['card_id'] for o in g.pending_choice['options']})
  g.step(Action('choose',choices=(0,)));self.assertIn(g.players[0].hand[-1].card_id,offered)
