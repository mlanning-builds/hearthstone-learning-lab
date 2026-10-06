"""Prepared scenarios for next-use Hero Power surcharges and Cult Neophyte."""
import unittest
from unittest.mock import patch
from expanded import Game, Action, random_deck
from expanded.game import Card


class PowerCostTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('WARRIOR',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
        for p in self.g.players:
            p.hand=[];p.deck=['CORE_CS2_029']*10;p.mana=p.max_mana=10

    def give(self,cid,owner=0):
        c=Card(self.g._new_id(),cid);self.g.players[owner].hand.append(c);return c

    def play(self,cid):
        c=self.give(cid);self.g.step(Action('play',c.uid,0,len(self.p.board)))

    def test_surcharge_controls_legality_and_exact_payment(self):
        self.play('CORE_DRG_403');self.g.step(Action('end'))
        self.q.mana=3;self.assertNotIn(Action('power'),self.g.legal_actions())
        self.q.mana=4;self.assertIn(Action('power'),self.g.legal_actions())
        self.g.step(Action('power'))
        self.assertEqual((self.q.mana,self.q.armor,self.q.next_power_increase),(0,2,0))
        self.assertNotIn(Action('power'),self.g.legal_actions())

    def test_persists_across_unused_turns_and_source_death(self):
        self.play('CORE_DRG_403');self.p.minions[0].health=0;self.g._settle()
        for _ in range(3):self.g.step(Action('end'))
        self.assertEqual(self.g._power_cost(1),4)
        self.g.step(Action('power'));self.assertEqual(self.g._power_cost(1),2)

    def test_two_saboteurs_stack_and_clear_together(self):
        self.play('CORE_DRG_403');self.play('CORE_DRG_403')
        self.g.step(Action('end'));self.assertEqual(self.g._power_cost(1),6)
        self.g.step(Action('power'))
        self.assertEqual(self.q.mana,4);self.assertEqual(self.g._power_cost(1),2)
        for _ in range(2):self.g.step(Action('end'))
        self.g.step(Action('power'));self.assertEqual(self.q.mana,8)

    def test_demon_hunter_uses_one_mana_base(self):
        self.q.hero_class='DEMONHUNTER'
        self.play('CORE_DRG_403');self.g.step(Action('end'))
        self.assertEqual(self.g._power_cost(1),3)
        self.g.step(Action('power'))
        self.assertEqual(self.q.mana,7);self.assertEqual(self.q.temporary_attack,1)
        self.assertEqual(self.g._power_cost(1),1)

    def test_full_board_does_not_consume_surcharge(self):
        self.q.hero_class='PALADIN'
        self.play('CORE_DRG_403');self.g.step(Action('end'))
        self.g._place_location(1,'CORE_REV_990')
        for _ in range(6):self.g._summon(1,'Core_CS2_200')
        self.assertNotIn(Action('power'),self.g.legal_actions())
        with self.assertRaises(ValueError):self.g.step(Action('power'))
        self.assertEqual(self.q.next_power_increase,2)
        self.q.minions[0].health=0;self.g._settle()
        self.g.step(Action('power'));self.assertEqual(self.q.next_power_increase,0)

    def test_failed_power_rolls_back_surcharge_mana_and_rng(self):
        self.q.hero_class='HUNTER'
        self.play('CORE_DRG_403');self.g.step(Action('end'))
        before=self.g.observe(1);rng=self.g.rng.getstate()
        with patch.object(Game,'_damage',side_effect=RuntimeError('fixture')):
            with self.assertRaisesRegex(RuntimeError,'fixture'):self.g.step(Action('power'))
        self.assertEqual(self.g.observe(1),before);self.assertEqual(self.g.rng.getstate(),rng)
        self.assertEqual(self.g.players[1].next_power_increase,2)

    def test_cost_is_public_and_does_not_expose_hand(self):
        self.give('CORE_CS2_029',1);self.play('CORE_DRG_403')
        for viewer in (0,1):
            view=self.g.observe(viewer)
            self.assertEqual(view['players'][1]['hero_power_cost'],4)
            self.assertEqual(view['players'][1]['next_power_increase'],2)
            self.assertNotIn('hand',view['players'][1-viewer])

    def test_neophyte_only_taxes_spells_for_one_turn(self):
        spell=self.give('CORE_CS2_029',1);minion=self.give('Core_CS2_200',1)
        self.play('CORE_SCH_713')
        self.assertEqual(self.g._cost(spell,1),4)
        self.g.step(Action('end'))
        self.assertEqual((self.g._cost(spell,1),self.g._cost(minion,1)),(5,6))
        self.assertEqual(self.g._power_cost(1),2)
        self.g.step(Action('end'));self.assertEqual(self.g._cost(spell,1),4)
