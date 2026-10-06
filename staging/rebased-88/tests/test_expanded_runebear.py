import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class RunebearTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('HUNTER',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p=self.g.players[0];self.p.hand=[];self.p.mana=self.p.max_mana=10
    def play(self,attack=0,health=0):
        c=Card(self.g._new_id(),'EDR_481');c.attack_bonus=attack;c.health_bonus=health;self.p.hand.append(c)
        self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid))
        return [m for m in self.p.minions if m.card_id=='EDR_481']
    def test_unbuffed_does_not_copy(self):
        bears=self.play();self.assertEqual(len(bears),1);self.assertIn('TAUNT',bears[0].keywords)
    def test_exact_threshold_copies_hand_buffs(self):
        bears=self.play(1,2);self.assertEqual(len(bears),2)
        self.assertEqual([(m.attack,m.health) for m in bears],[(4,6),(4,6)])
        self.assertNotEqual(bears[0].uid,bears[1].uid)
    def test_health_buff_alone_does_not_activate(self):
        self.assertEqual(len(self.play(0,4)),1)
    def test_aura_counts_without_being_double_copied(self):
        aura=self.g._summon(0,'CORE_CS2_122')
        bears=self.play();self.assertEqual(len(bears),2)
        self.assertEqual([m.attack for m in bears],[4,4])
        self.g._silence(aura);self.assertEqual([m.attack for m in bears],[3,3])
    def test_full_board_cannot_fit_copy(self):
        for _ in range(6):self.g._summon(0,'CORE_EX1_506')
        self.assertEqual(len(self.play(1)),1);self.assertEqual(len(self.p.board),7)
    def test_summoning_does_not_activate_battlecry(self):
        self.g._summon(0,'EDR_481',attack_bonus=2)
        self.assertEqual(len(self.p.minions),1)
