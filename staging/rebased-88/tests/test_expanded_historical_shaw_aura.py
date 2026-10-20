import unittest
import test_expanded_generation as fixtures
from expanded import cards

class ShawAuraTests(unittest.TestCase):
 def game(self):
  return fixtures.GenerationTests().game()
 def paid(self,g,cid):
  c=g._add(0,cid);g.players[0].mana=10;g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid));g.assert_invariants();return next(m for m in reversed(g.players[0].minions) if m.card_id==cid)
 def test_other_minion_can_attack_minions_on_entry_but_source_cannot(self):
  g=self.game();enemy=g._summon(1,'CS2_182');other=self.paid(g,'CS2_182');source=self.paid(g,'GIL_650')
  acts=[a for a in g.legal_actions() if a.kind=='attack' and a.source==other.uid];self.assertTrue(any(a.target==enemy.uid for a in acts));self.assertFalse(any(a.target==g.hero_id(1) for a in acts));self.assertFalse(any(a.kind=='attack' and a.source==source.uid for a in g.legal_actions()));self.assertNotIn('RUSH',other.keywords)
 def test_two_sources_grant_rush_to_each_other_and_silence_removes_only_provider(self):
  g=self.game();a=g._summon(0,'GIL_650');b=g._summon(0,'GIL_650');self.assertIn('RUSH',g._effective_keywords(a));self.assertIn('RUSH',g._effective_keywords(b));g._silence(a);self.assertIn('RUSH',g._effective_keywords(a));self.assertNotIn('RUSH',g._effective_keywords(b))
 def test_dormant_and_enemy_sources_do_not_grant_rush(self):
  g=self.game();other=g._summon(0,'CS2_182');g._summon(0,'GIL_650',dormant_turns=2);g._summon(1,'GIL_650');self.assertNotIn('RUSH',g._effective_keywords(other))
 def test_enemy_copy_does_not_embed_derived_rush_and_source_death_removes_it(self):
  g=self.game();source=g._summon(0,'GIL_650');other=g._summon(0,'CS2_182');copied=g._summon(1,other.card_id,copy_from=other);self.assertIn('RUSH',g._effective_keywords(other));self.assertNotIn('RUSH',g._effective_keywords(copied));source.health=0;g._settle();self.assertNotIn('RUSH',g._effective_keywords(other))

if __name__=="__main__":unittest.main()
