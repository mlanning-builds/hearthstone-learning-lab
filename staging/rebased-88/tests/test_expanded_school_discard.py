import unittest
from unittest.mock import patch
from expanded import Game,Action,random_deck
from expanded.game import Card
from expanded.cards import TRIGGERS

class SchoolDiscardTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('MAGE',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
        for p in self.g.players:p.hand=[];p.deck=[];p.mana=p.max_mana=10
    def give(self,cid):
        c=Card(self.g._new_id(),cid);self.p.hand.append(c);return c
    def play(self,cid,target=0):
        c=self.give(cid);self.g.step(Action('play',c.uid,target))
    def test_overheat_single_buff_without_nature(self):
        m=self.g._summon(0,'CORE_EX1_506');base=(m.attack,m.health)
        fire=self.give('CORE_CS2_029');self.play('FIR_906')
        self.assertEqual((m.attack,m.health),(base[0]+1,base[1]+1));self.assertIn(fire,self.p.hand)
    def test_overheat_extra_buff_only_friendly_board(self):
        m=self.g._summon(0,'CORE_EX1_506');enemy=self.g._summon(1,'CORE_EX1_506')
        base=(m.attack,m.health);self.give('CORE_EX1_154');self.play('FIR_906')
        self.assertEqual((m.attack,m.health),(base[0]+2,base[1]+2))
        self.assertEqual((enemy.attack,enemy.health),base)
        self.assertEqual(self.p.discard_history,['CORE_EX1_154'])
    def test_overheat_empty_board_still_discards(self):
        self.give('CORE_EX1_154');self.play('FIR_906');self.assertFalse(self.p.hand)
        self.assertEqual(len(self.p.discard_history),1)
    def test_winds_does_not_discard_itself(self):
        self.play('FIR_910',-2);self.assertEqual(self.q.health,27)
        self.assertEqual(self.p.discard_history,[])
    def test_winds_fire_discard_doubles_damage(self):
        self.give('CORE_CS2_029');self.play('FIR_910',-2)
        self.assertEqual(self.q.health,24);self.assertEqual(self.p.discard_history,['CORE_CS2_029'])
    def test_winds_other_school_not_discarded(self):
        c=self.give('CORE_EX1_154');self.play('FIR_910',-2)
        self.assertEqual(self.q.health,27);self.assertIn(c,self.p.hand)
    def test_winds_spell_damage_applies_to_each_hit(self):
        self.g._summon(0,'CORE_EX1_012');self.give('CORE_CS2_029');self.play('FIR_910',-2)
        self.assertEqual(self.q.health,22)
    def test_dead_target_does_not_redirect_second_hit(self):
        m=self.g._summon(1,'CORE_EX1_506');self.give('CORE_CS2_029');self.play('FIR_910',m.uid)
        self.assertFalse(self.q.minions);self.assertEqual(self.q.health,30)
        self.assertEqual(len(self.p.discard_history),1)
    def test_discard_choice_resumes_before_bonus(self):
        with patch.dict(TRIGGERS,{'CORE_EX1_506':('friendly_discard',[('choose_fixed_summon',('NEW1_034',))])}):
            self.g._summon(0,'CORE_EX1_506');self.give('CORE_CS2_029');self.play('FIR_910',-2)
            self.assertEqual(self.q.health,27);self.assertEqual(self.g.phase,'choice')
            self.g.step(Action('choose',choices=(0,)))
            self.assertEqual(self.q.health,24);self.assertIsNone(self.g.pending_frame)
