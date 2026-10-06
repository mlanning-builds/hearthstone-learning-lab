"""Physical binding and combat checkpoints for generated attack groups."""
import unittest
import test_expanded_generation as fixtures
from expanded.generation_extensions import requests_for,DEATH_EFFECTS
from expanded.generation import request_matches
from engine.cards import UnsupportedCard

class GeneratedAttackTests(unittest.TestCase):
    def setUp(self):
        self.helper=fixtures.GenerationTests();self.g=self.helper.game()
        self.request=next(iter(requests_for('DINO_422')))
        self.cid=next(cid for cid,d in self.g.cards.items() if request_matches(self.request,d,'MAGE'))
    def install(self):self.helper.install(self.g,self.request,[self.cid])
    def run_body(self):self.helper.run_ops(self.g,DEATH_EFFECTS['DINO_422'])
    def test_empty_enemy_board_attacks_hero(self):
        self.install();self.run_body()
        minions=self.g.players[0].minions
        self.assertEqual(len(minions),2)
        self.assertEqual(self.g.players[1].health,30-sum(m.attack for m in minions))
        self.assertEqual([m.attacks for m in minions],[0,0])
    def test_full_board_does_not_attack_with_existing_minions(self):
        self.install()
        for _ in range(7):self.g._summon(0,'EX1_tk34')
        self.run_body();self.assertEqual(self.g.players[1].health,30)
    def test_one_slot_only_successful_summon_attacks(self):
        self.install()
        for _ in range(6):self.g._summon(0,'EDR_851t')
        self.run_body();new=self.g.players[0].minions[-1]
        self.assertEqual(self.g.players[1].health,30-new.attack)
    def test_missing_pool_does_not_summon_or_consume_rng(self):
        rng=self.g.rng.getstate()
        with self.assertRaisesRegex(UnsupportedCard,'no reviewed membership'):self.run_body()
        self.assertEqual(self.g.rng.getstate(),rng);self.assertFalse(self.g.players[0].minions)
    def test_dead_bound_attacker_does_not_choose_another(self):
        self.g._summon(0,'EX1_tk34');rng=self.g.rng.getstate()
        self.helper.run_ops(self.g,[('force_group_one',999999,'random_enemy_character')])
        self.assertEqual(self.g.rng.getstate(),rng);self.assertEqual(self.g.players[1].health,30)
    def test_attack_secret_can_remove_first_generated_attacker(self):
        self.install();self.g._place_secret(1,'CORE_EX1_611');self.run_body()
        self.assertEqual(len(self.g.players[0].hand),1)
        self.assertEqual(len(self.g.players[0].minions),1)
        self.assertEqual(self.g.players[1].health,30-self.g.players[0].minions[0].attack)
    def test_controller_change_changes_enemy_side(self):
        m=self.g._summon(0,'EX1_tk34');self.g.players[0].board.remove(m)
        m.owner=1;self.g.players[1].board.append(m)
        self.helper.run_ops(self.g,[('force_group_one',m.uid,'random_enemy_character')])
        self.assertEqual(self.g.players[0].health,24);self.assertEqual(self.g.players[1].health,30)
