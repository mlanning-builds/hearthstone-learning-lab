import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class DodoTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('DRUID',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p=self.g.players[0];self.p.hand=[];self.p.mana=self.p.max_mana=10
    def play(self,health,armor=0,attack_buff=0):
        self.p.health=health;self.p.armor=armor
        c=Card(self.g._new_id(),'TIME_703');c.attack_bonus=attack_buff;self.p.hand.append(c)
        self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid))
        return [m for m in self.p.minions if m.card_id=='TIME_703']
    def test_exact_ten_health_activates(self):
        copies=self.play(10);self.assertEqual([(m.attack,m.health) for m in copies],[(10,10),(10,10)])
        self.assertTrue(all('TAUNT' in m.keywords for m in copies))
    def test_eleven_health_does_not_activate(self):
        copies=self.play(11);self.assertEqual([(m.attack,m.health) for m in copies],[(5,5)])
    def test_armor_does_not_prevent_activation(self):
        self.assertEqual(len(self.play(9,armor=20)),2)
    def test_opponent_health_does_not_activate(self):
        self.g.players[1].health=1;self.assertEqual(len(self.play(30)),1)
    def test_hand_buff_is_copied_after_battlecry_buff(self):
        self.assertEqual([m.attack for m in self.play(5,attack_buff=2)],[12,12])
    def test_full_board_still_buffs_original(self):
        for _ in range(6):self.g._summon(0,'CORE_EX1_506')
        copies=self.play(10);self.assertEqual(len(copies),1);self.assertEqual(copies[0].attack,10)
