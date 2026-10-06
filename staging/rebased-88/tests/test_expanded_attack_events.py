"""Synthetic listeners test the shared combat boundary, not card certification."""
import unittest
from unittest.mock import patch
from expanded import Game, Action, random_deck
from expanded.cards import TRIGGERS

class AttackEventTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('WARRIOR',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
        self.p.hand=[];self.p.deck=['CORE_CS2_029']*5
        self.m=self.g._summon(0,'CORE_EX1_506')
        self.m.summoned_turn=-1

    def attack(self,target=-2):
        self.g.step(Action('attack',self.m.uid,target))

    def test_self_listener_draws_once(self):
        with patch.dict(TRIGGERS,{'CORE_EX1_506':('attacked_self',[('draw',1)])}):
            self.g._summon(0,'CORE_EX1_506')
            self.attack()
        self.assertEqual(len(self.p.hand),1)

    def test_mortally_wounded_attacker_triggers_before_removal(self):
        enemy=self.g._summon(1,'CORE_EX1_506');enemy.attack=10
        with patch.dict(TRIGGERS,{'CORE_EX1_506':('attacked_self',[('draw',1)])}):
            self.attack(enemy.uid)
        self.assertEqual(len(self.p.hand),1)
        self.assertNotIn(self.m,self.p.board)

    def test_silenced_listener_does_not_trigger(self):
        self.g._silence(self.m)
        with patch.dict(TRIGGERS,{'CORE_EX1_506':('attacked_self',[('draw',1)])}):self.attack()
        self.assertEqual(self.p.hand,[])

    def test_zero_damage_still_triggers(self):
        enemy=self.g._summon(1,'CORE_EX1_506');enemy.keywords.add('DIVINE_SHIELD');enemy.attack=0
        with patch.dict(TRIGGERS,{'CORE_EX1_506':('attacked_self',[('draw',1)])}):self.attack(enemy.uid)
        self.assertEqual(len(self.p.hand),1)

    def test_fatigue_after_lethal_attack_can_make_draw(self):
        self.p.health=1;self.p.deck=[];self.q.health=1
        with patch.dict(TRIGGERS,{'CORE_EX1_506':('attacked_self',[('draw',1)])}):self.attack()
        self.assertTrue(self.g.terminal)
        self.assertIsNone(self.g.winner)
        self.assertEqual(self.g._combat_sequence_depth,0)

    def test_cancelled_attack_has_no_after_event(self):
        with patch.dict(TRIGGERS,{'CORE_EX1_506':('attacked_self',[('draw',1)])}), patch.object(self.g,'_secret_event',return_value=True):self.attack()
        self.assertEqual(self.p.hand,[])

    def test_new_listener_during_proposed_attack_is_not_eligible(self):
        def proposed(*args,**kwargs):
            self.g._summon(0,'CORE_EX1_506')
            return False
        with patch.dict(TRIGGERS,{'CORE_EX1_506':('hero_attack',[('draw',1)])}), patch.object(self.g,'_secret_event',side_effect=proposed):
            self.p.temporary_attack=1
            self.g.step(Action('attack',-1,-2))
        self.assertEqual(len(self.p.hand),1)
