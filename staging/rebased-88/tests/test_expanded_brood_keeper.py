import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class BroodKeeperTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('WARRIOR',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p=self.g.players[0];self.p.hand=[];self.p.mana=self.p.max_mana=10
    def give(self,cid):
        c=Card(self.g._new_id(),cid);self.p.hand.append(c);return c
    def play(self,cid):
        c=self.give(cid);self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid))
    def test_no_dragon_does_not_equip(self):
        self.play('EDR_457');self.assertIsNone(self.p.weapon)
    def test_held_dragon_equips_two_two(self):
        self.give('TIME_856');self.play('EDR_457')
        self.assertEqual(self.p.weapon,dict(card_id='EDR_457t',attack=2,durability=2))
        self.assertEqual(self.p.mana,8)
    def test_board_dragon_does_not_count(self):
        self.g._summon(0,'TIME_856');self.play('EDR_457');self.assertIsNone(self.p.weapon)
    def test_replaces_weapon_without_refreshing_hero_attack(self):
        self.g._equip(0,'EDR_457t');self.g.step(Action('attack',-1,-2))
        self.give('TIME_856');self.play('EDR_457')
        self.assertEqual(self.p.weapon['durability'],2)
        self.assertFalse(any(a.kind=='attack' and a.source==-1 for a in self.g.legal_actions()))
    def test_generated_weapon_can_be_played_from_hand(self):
        self.play('EDR_457t');self.assertEqual(self.p.weapon['durability'],2)
        self.g.step(Action('attack',-1,-2));self.assertEqual(self.p.weapon['durability'],1)
    def test_battlecry_not_repeated_by_summon(self):
        self.give('TIME_856');self.g._summon(0,'EDR_457');self.assertIsNone(self.p.weapon)
