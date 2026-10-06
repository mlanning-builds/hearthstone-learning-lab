import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class FixedSummonTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('WARRIOR',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
        for p in self.g.players:p.hand=[];p.deck=['CORE_CS2_029']*30;p.mana=p.max_mana=10
    def give(self,cid):
        c=Card(self.g._new_id(),cid);self.p.hand.append(c);return c
    def play(self,cid,target=0):
        c=self.give(cid);self.g.step(Action('play',c.uid,target));return c
    def test_mirror_summons_one_without_dragon(self):
        self.play('TIME_006');self.assertEqual(len(self.p.minions),1)
        m=self.p.minions[0];self.assertEqual((m.attack,m.health),(0,4));self.assertIn('TAUNT',m.keywords)
    def test_mirror_all_type_hand_card_activates_second_summon(self):
        self.give('DINO_435');self.play('TIME_006')
        self.assertEqual([m.card_id for m in self.p.minions],['TIME_006t1']*2)
    def test_mirror_respects_single_free_board_slot(self):
        for _ in range(6):self.g._summon(0,'Core_CS2_200')
        self.give('DINO_435');self.play('TIME_006');self.assertEqual(len(self.p.board),7)
    def test_security_gains_attack_per_hit_not_per_damage(self):
        self.play('TLC_622');a,b=self.p.minions
        self.g._damage(a.uid,2);self.g._settle();self.assertEqual(a.attack,1)
        self.g._damage(a.uid,1);self.g._settle();self.assertEqual(a.attack,2)
        self.assertEqual(b.attack,0);self.g._silence(a)
        self.g._damage(a.uid,1);self.g._settle();self.assertEqual(a.attack,0)
    def test_brilliance_discount_uses_spell_damage_and_resets_next_turn(self):
        c=self.give('CATA_452');base=self.g._cost(c,0)
        self.play('CORE_CS2_029',self.g.hero_id(1))
        self.assertEqual(self.g._cost(c,0),max(0,base-6))
        self.p.mana=10;self.g.step(Action('play',c.uid))
        m=self.p.minions[-1];self.assertEqual((m.card_id,m.attack,m.health),('CATA_452t',6,6))
        self.g.step(Action('end'));self.g.step(Action('end'))
        other=self.give('CATA_452');self.assertEqual(self.g._cost(other,0),base)
