import unittest
import test_expanded_generation as fixtures
from expanded import cards
AURAS={'DS1_175': ('BEAST', 1, 0),
 'EX1_185': ('DEMON', 1, 0),
 'EX1_508': ('MURLOC', 1, 0),
 'GIL_119': ('ELEMENTAL', 2, 0),
 'GVG_021': ('DEMON', 2, 2),
 'LOOT_136': ('others', 1, 0)}

class StatAuraTests(unittest.TestCase):
 def game(self):
  return fixtures.GenerationTests().game()
 def paid(self,g,cid):
  c=g._add(0,cid);g.players[0].mana=10;g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid));g.assert_invariants();return next(m for m in g.players[0].minions if m.card_id==cid)
 def test_tribal_and_all_other_stat_auras_use_live_targets(self):
  targets={'BEAST':'CS2_120','DEMON':'BAR_327t','MURLOC':'CFM_310t','ELEMENTAL':'CS2_033','others':'CS2_182'}
  for cid,(group,a,h) in AURAS.items():
   g=self.game();friendly=g._summon(0,targets[group]);enemy=g._summon(1,targets[group]);before=(friendly.attack,friendly.max_health);enemy_before=(enemy.attack,enemy.max_health);source=self.paid(g,cid)
   self.assertEqual((friendly.attack,friendly.max_health),(before[0]+a,before[1]+h));self.assertEqual((enemy.attack,enemy.max_health),enemy_before);self.assertEqual((source.attack,source.max_health),(g.cards[cid]['attack'],g.cards[cid]['health']))
   g._silence(source);self.assertEqual((friendly.attack,friendly.max_health),before)
 def test_aura_stacks_and_removes_only_departing_providers_bonus(self):
  g=self.game();m=g._summon(0,'CS2_182');a=self.paid(g,'LOOT_136');b=self.paid(g,'LOOT_136');self.assertEqual(m.attack,6);a.health=0;g._settle();self.assertEqual(m.attack,5);g._silence(b);self.assertEqual(m.attack,4)
 def test_dormant_provider_gives_no_stats(self):
  g=self.game();m=g._summon(0,'CS2_182');g._summon(0,'LOOT_136',dormant_turns=2);self.assertEqual(m.attack,4)
 def test_malganis_blocks_hero_damage_until_silenced(self):
  g=self.game();source=self.paid(g,'GVG_021');self.assertEqual(g._damage(g.hero_id(0),5),0);self.assertEqual(g.players[0].health,30);g._silence(source);g._damage(g.hero_id(0),5);self.assertEqual(g.players[0].health,25)
 def test_malganis_health_aura_removal_preserves_remaining_damage_without_healing(self):
  g=self.game();m=g._summon(0,'BAR_327t');source=self.paid(g,'GVG_021');g._damage(m.uid,m.max_health-1);source.health=0;g._settle();self.assertIn(m,g.players[0].minions);self.assertEqual((m.health,m.max_health),(1,2))
 def test_robes_elusive_applies_to_self_and_others_and_does_not_copy_as_intrinsic(self):
  g=self.game();m=g._summon(0,'CS2_182');source=self.paid(g,'SCH_146');self.assertIn('ELUSIVE',g._effective_keywords(source));self.assertIn('ELUSIVE',g._effective_keywords(m));self.assertNotIn('ELUSIVE',m.keywords);copy=g._summon(1,m.card_id,copy_from=m);self.assertNotIn('ELUSIVE',g._effective_keywords(copy));g._silence(source);self.assertNotIn('ELUSIVE',g._effective_keywords(m))

if __name__=="__main__":unittest.main()
