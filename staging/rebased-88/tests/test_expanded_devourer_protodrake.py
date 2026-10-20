"""Required component bodies preserve death-time snapshots and complete pools."""
from copy import deepcopy
import unittest
from unittest.mock import patch
import test_expanded_generation as fixtures
from engine.cards import UnsupportedCard
from expanded import Action
from expanded.cards import RULES, DEATH_EFFECTS
from expanded.generation_cards import requests_for


class DevourerProtodrakeTests(unittest.TestCase):
    def setUp(self):
        self.fixture=fixtures.GenerationTests();self.game=self.fixture.game()
        self.devourer=self.game._summon(0,'RLK_538')

    def kill(self,minion):
        minion.health=0;self.game._settle(allow_event_choices=True)

    def test_inherits_printed_deathrattle_and_executes_it(self):
        donor=self.game._summon(0,'CORE_EX1_012')
        self.kill(donor)
        self.assertEqual(self.devourer.attached_death_effects,[('draw',1)])
        count=len(self.game.players[0].hand)
        self.kill(self.devourer)
        self.assertEqual(len(self.game.players[0].hand),count+1)

    def test_granted_operations_are_snapshotted_and_enemy_is_ignored(self):
        donor=self.game._summon(0,'EDR_851t')
        donor.attached_death_effects.append(('armor',3))
        self.kill(donor);donor.attached_death_effects.clear()
        self.kill(self.game._summon(1,'CORE_EX1_012'))
        self.assertEqual(self.devourer.attached_death_effects,[('armor',3)])

    def test_silenced_donor_does_not_transfer_printed_deathrattle(self):
        donor=self.game._summon(0,'CORE_EX1_012');self.game._silence(donor)
        self.kill(donor)
        self.assertFalse(self.devourer.attached_death_effects)

    def test_simultaneously_dead_listener_does_not_inherit(self):
        donor=self.game._summon(0,'CORE_EX1_012')
        self.devourer.health=0;donor.health=0;self.game._settle()
        self.assertFalse(self.devourer.attached_death_effects)

    def test_inherited_effects_are_removed_by_silence(self):
        self.kill(self.game._summon(0,'CORE_EX1_012'))
        self.game._silence(self.devourer)
        self.assertFalse(self.devourer.attached_death_effects)

    def test_deathrattle_multiplier_is_not_stored_in_copied_operations(self):
        donor=self.game._summon(0,'CORE_EX1_012')
        with patch.object(self.game,'_trigger_repetitions',return_value=2):
            self.kill(donor)
        self.assertEqual(self.devourer.attached_death_effects,[('draw',1)])

    def test_unrelated_donor_state_does_not_block_inheritance(self):
        donor=self.game._summon(0,'CORE_EX1_012');donor.rule_state['stored_fixture']=1
        self.kill(donor)
        self.assertEqual(self.devourer.attached_death_effects,[('draw',1)])

    def test_protodrake_declares_complete_standard_seven_cost_board_request(self):
        request,=requests_for('SCH_711')
        self.assertEqual((request.minimum,request.maximum,request.card_type),(7,7,'MINION'))
        self.assertEqual(request.excluded_mechanic,'COLOSSAL')
        outcomes=self.game._generation_candidates(request,0)
        self.assertTrue(outcomes)
        self.assertTrue(all(self.game.cards[cid]['cost']==7 for cid in outcomes))
        self.assertTrue(all('COLOSSAL' not in self.game.cards[cid].get('mechanics',()) for cid in outcomes))

    def test_protodrake_death_summons_one_outcome_without_battlecry(self):
        request,=requests_for('SCH_711')
        self.fixture.install(self.game,request,['CATA_723'])
        with patch.dict(RULES,{'CATA_723':('none',[('armor',100)])}):
            drake=self.game._summon(0,'SCH_711');self.kill(drake)
        self.assertEqual(self.game.players[0].armor,0)
        self.assertEqual([m.card_id for m in self.game.players[0].minions],['RLK_538','CATA_723'])
