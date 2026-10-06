import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class WeaponsmithTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('WARRIOR',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p=self.g.players[0];self.p.hand=[];self.p.mana=self.p.max_mana=10
    def give(self,cid):
        c=Card(self.g._new_id(),cid);self.p.hand.append(c);return c
    def play(self,c):
        self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid))
    def smith(self):self.play(self.give('END_021'))
    def test_buffs_minions_and_weapons_only(self):
        m=self.give('CORE_EX1_506');w=self.give('EDR_457t');s=self.give('CORE_CS2_029')
        self.smith();self.assertEqual((m.attack_bonus,w.attack_bonus,s.attack_bonus),(2,2,0))
        self.assertEqual(self.p.minions[0].attack,2)
    def test_weapon_bonus_survives_equip_and_attack(self):
        w=self.give('EDR_457t');self.smith();self.play(w)
        self.assertEqual((self.p.weapon['attack'],self.p.weapon['durability']),(4,2))
        self.g.step(Action('attack',-1,-2));self.assertEqual(self.g.players[1].health,26)
        self.assertEqual(self.p.weapon['durability'],1)
    def test_multiple_buffs_stack_on_weapon(self):
        w=self.give('EDR_457t');self.smith();self.smith();self.play(w)
        self.assertEqual(self.p.weapon['attack'],6)
    def test_minion_bonus_survives_play(self):
        m=self.give('CORE_EX1_506');self.smith();self.play(m)
        self.assertEqual(next(m for m in self.p.minions if m.card_id=='CORE_EX1_506').attack,4)
    def test_equipped_weapon_does_not_receive_hand_buff(self):
        self.g._equip(0,'EDR_457t');self.smith();self.assertEqual(self.p.weapon['attack'],2)
    def test_replacement_weapon_does_not_inherit_bonus(self):
        w=self.give('EDR_457t');self.smith();self.play(w)
        self.g._equip(0,'EDR_457t');self.assertEqual(self.p.weapon['attack'],2)
