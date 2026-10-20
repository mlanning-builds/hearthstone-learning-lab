"""Rule checks for the final historical combat spell family."""
from copy import deepcopy
import unittest
from expanded import Game,Action,random_deck

class FinalCombatSpellTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  g=Game([random_deck('MAGE',31),random_deck('MAGE',53)],seed=71)
  g.step(Action('mulligan'));g.step(Action('mulligan'))
  for p in g.players:p.hand=[];p.board=[];p.deck=[];p.mana=p.max_mana=10;p.health=30;p.armor=0
  cls.prototype=g
 def game(self):return deepcopy(self.prototype)
 def play(self,g,cid,target=0):
  card=g._add(0,cid)
  g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==card.uid and a.target==target))
 def test_shadowform_uses_modern_two_damage_power(self):
  g=self.game();self.play(g,'EX1_625');self.assertEqual(g.players[0].primary_power['card_id'],'EX1_625t')
  self.play(g,'EX1_625');self.assertEqual(g.players[0].primary_power['card_id'],'EX1_625t')
 def test_garrote_and_drawn_bleeds_gain_spell_damage(self):
  g=self.game();g._summon(0,'CS2_052');self.play(g,'SW_311')
  self.assertEqual(g.players[1].health,27);self.assertEqual([g._card_data(c)['id'] for c in g.players[0].deck],['SW_311t']*3)
  g._draw(0);g._settle();self.assertEqual(g.players[1].health,18)
 def test_sweeping_strikes_hits_both_neighbors(self):
  g=self.game();m=g._summon(0,'CS2_182');enemies=[g._summon(1,'CS2_182') for _ in range(3)]
  self.play(g,'DAL_062',m.uid);g._attack(m.uid,enemies[1].uid,forced=True);g._settle()
  self.assertEqual([x.health for x in enemies],[1,1,1])
 def test_hit_it_very_hard_limits_attacks_to_minions(self):
  g=self.game();enemy=g._summon(1,'CS2_182');self.play(g,'ONY_023')
  self.assertEqual(g._attack_targets(),[enemy.uid]);self.assertEqual(g._hero_attack(0),10)
  g.turn+=1;self.assertIn(g.hero_id(1),g._attack_targets())
 def test_punch_card_hero_cleave_without_weapon(self):
  g=self.game();enemies=[g._summon(1,'CS2_182') for _ in range(3)];self.play(g,'WORK_022')
  g._attack(g.hero_id(0),enemies[1].uid,forced=True);g._settle()
  self.assertEqual([x.health for x in enemies],[2,2,2])
