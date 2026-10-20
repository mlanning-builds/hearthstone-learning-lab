"""Continuous historical rules run through production play and draw paths."""
import unittest
import test_expanded_generation as fixtures
class HistoricalPassiveProductionTests(unittest.TestCase):
 def game(self):return fixtures.GenerationTests().game()
 def test_draw_and_play_refresh_dragon_hand_attack(self):
  g=self.game();p=g.players[0];raven=g._summon(0,'DRG_058');base=raven.attack
  p.deck=['CORE_EX1_043'];g._draw(0);g._settle();self.assertEqual(raven.attack,base+2)
  dragon=p.hand[0];p.mana=10;g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==dragon.uid))
  self.assertEqual(raven.attack,base)
 def test_live_cost_changes_with_armor_and_silenced_tax(self):
  g=self.game();c=g._add(0,'RLK_651');before=g._cost(c,0);g.players[0].armor=4;self.assertEqual(g._cost(c,0),before-4)
  spell=g._add(0,'CORE_CS2_029');before=g._cost(spell,0);tax=g._summon(1,'ICC_706');self.assertEqual(g._cost(spell,0),before+2)
  g._silence(tax);self.assertEqual(g._cost(spell,0),before)
 def test_kirin_tor_tricaster_spell_damage_and_cost_are_live(self):
  g=self.game();spell=g._add(0,'CORE_CS2_029');before=g._cost(spell,0);source=g._summon(0,'DAL_576')
  self.assertEqual(g._cost(spell,0),before+1);self.assertEqual(g._spell_damage(0),3)
  g._silence(source);self.assertEqual(g._cost(spell,0),before);self.assertEqual(g._spell_damage(0),0)
if __name__=='__main__':unittest.main()
