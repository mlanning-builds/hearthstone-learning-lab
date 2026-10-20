"""Copied Deathrattles retain private effect memories and fresh self references."""
from copy import deepcopy
import json
import unittest
from unittest.mock import patch
import test_expanded_generation as fixtures
from expanded import Action
from engine.game import Card
from engine.cards import UnsupportedCard


class InheritedMemoryTests(unittest.TestCase):
    def setUp(self):
        self.game=fixtures.GenerationTests().game()
        self.devourer=self.game._summon(0,'RLK_538')
        self.player=self.game.players[0]

    def kill(self,minion):
        minion.health=0;self.game._settle(allow_event_choices=True)

    def jar(self,cid='CORE_EX1_162'):
        donor=self.game._summon(0,'TLC_841t')
        card=Card(self.game._new_id(),cid);card.attack_bonus=3;card.health_bonus=2
        card._hidden_fixture='secret payload marker'
        donor._bound_card=card
        return donor,card

    def test_bound_card_snapshot_keeps_enchantments_after_donor_changes(self):
        donor,card=self.jar();self.kill(donor)
        card.attack_bonus=1000;donor._bound_card=None
        self.kill(self.devourer)
        copies=[m for m in self.player.minions if m.card_id=='CORE_EX1_162']
        self.assertEqual(len(copies),2)
        # Its aura buffs the other copy, independently of the copied +3/+2.
        self.assertTrue(all(m.attack-m.aura_attack==5 and m.max_health==4 for m in copies))

    def test_bound_minion_egg_uses_death_time_snapshot(self):
        donor=self.game._summon(0,'EDR_454t')
        model=self.game._summon(0,'EDR_851t');self.game._buff(model,4,5)
        donor._bound_minion=deepcopy(model)
        self.kill(donor);donor._bound_minion.attack=1000
        self.kill(self.devourer)
        copies=[m for m in self.player.minions if m.card_id=='EDR_851t']
        self.assertEqual(len(copies),3)
        self.assertTrue(all(m.attack==5 and m.max_health==6 for m in copies))

    def test_copied_definition_survives_game_clone(self):
        donor,_=self.jar();self.kill(donor)
        clone=deepcopy(self.game)
        self.kill(self.devourer)
        copied=next(m for m in clone.players[0].minions if m.uid==self.devourer.uid)
        copied.health=0;clone._settle(allow_event_choices=True)
        self.assertEqual(self.game.observe(0),clone.observe(0))

    def test_repeated_trigger_does_not_consume_or_mutate_definition(self):
        donor,_=self.jar();self.kill(donor)
        definitions=deepcopy(self.game._inherited_death_definitions)
        with patch.object(self.game,'_trigger_repetitions',return_value=2):self.kill(self.devourer)
        self.assertEqual(self.game._inherited_death_definitions,definitions)
        self.assertEqual(sum(m.card_id=='CORE_EX1_162' for m in self.player.minions),3)
        self.game.assert_invariants()

    def test_private_payload_is_not_in_either_observation(self):
        donor,_=self.jar();self.kill(donor)
        for viewer in (0,1):
            visible=json.dumps(self.game.observe(viewer))
            self.assertNotIn('secret payload marker',visible)
            self.assertNotIn('_inherited_death_definitions',visible)

    def test_devoured_card_batch_returns_independent_copies(self):
        donor=self.game._summon(0,'EDR_851t')
        card=Card(self.game._new_id(),'CORE_CS2_029');card.cost_delta=-2
        donor._devoured_cards=[(1,card)]
        donor.attached_death_effects.append(('stored_return_devoured',))
        self.kill(donor)
        self.assertEqual(len(self.game.players[1].hand),1)
        self.kill(self.devourer)
        hand=self.game.players[1].hand
        self.assertEqual(len(hand),2);self.assertEqual([c.cost_delta for c in hand],[-2,-2])
        self.assertNotEqual(hand[0].uid,hand[1].uid)

    def test_remembered_discards_and_secret_uid_bindings_are_independent(self):
        donor=self.game._summon(0,'EDR_851t')
        donor.remembered_discards=['CORE_CS2_029']
        donor.attached_death_effects.append(('return_remembered_discards',2))
        self.kill(donor);donor.remembered_discards.clear()
        self.kill(self.devourer)
        self.assertEqual([c.card_id for c in self.player.hand],['CORE_CS2_029']*2)
        self.assertEqual([c.cost_delta for c in self.player.hand],[-2,-2])

    def test_scalar_egg_memory_is_frozen_at_inheritance(self):
        donor=self.game._summon(0,'CATA_210');donor.rule_state['egg_bonus']=4
        self.kill(donor);donor.rule_state['egg_bonus']=1000
        self.kill(self.devourer)
        whelps=[m for m in self.player.minions if m.card_id=='CATA_210t']
        self.assertEqual(len(whelps),2)
        base=self.game.cards['CATA_210t']
        self.assertTrue(all(m.attack==base['attack']+4 and m.max_health==base['health']+4 for m in whelps))

    def test_unsupported_physical_relationship_keeps_action_rollback(self):
        donor=self.game._summon(0,'EDR_851t')
        donor._muradin_hammer=dict(card=Card(self.game._new_id(),'TIME_209t'),attack=4,durability=2)
        donor.health=1
        self.game._start_play_effects([('choose_fixed_summon',('EDR_851t',)),('destroy',)],
            dict(owner=0,source=None,target=donor.uid,bonus=0,lifesteal=False))
        self.devourer.health=self.devourer.max_health=3
        before=deepcopy(self.game.observe(0));rng=self.game.rng.getstate()
        with patch('expanded.death_inheritance.PHYSICAL_REVIEW',frozenset(('muradin_return',))), self.assertRaisesRegex(UnsupportedCard,'physical-card relationship'):
            self.game.step(Action('choose',choices=(0,)))
        self.assertEqual(self.game.observe(0),before);self.assertEqual(self.game.rng.getstate(),rng)

    def test_replication_killer_is_the_new_bearers_killer(self):
        donor=self.game._summon(0,'CATA_185');self.kill(donor)
        killer=self.game._summon(1,'CORE_CS2_179')
        self.game._damage(self.devourer.uid,10,damage_source=killer,damage_owner=1)
        self.game._settle(allow_event_choices=True)
        self.assertEqual([m.card_id for m in self.game.players[1].minions],['CATA_185'])

    def test_attack_history_belongs_to_recipient_even_before_inheritance(self):
        self.game._buff(self.devourer,5,5);self.devourer.summoned_turn=-1
        victim=self.game._summon(1,'EDR_851t')
        self.game.step(Action('attack',self.devourer.uid,victim.uid))
        donor=self.game._summon(0,'EDR_819')
        donor.rule_state['combat_kills']=['CORE_CS2_179']
        self.kill(donor)
        # Donor's own resurrection adds its recorded victim. The inherited
        # effect later resurrects the recipient's earlier victim instead.
        before=sum(m.card_id=='EDR_851t' for m in self.player.minions)
        self.kill(self.devourer)
        self.assertEqual(sum(m.card_id=='EDR_851t' for m in self.player.minions),before+1)

    def test_malformed_bound_memory_rejects_without_partial_inheritance(self):
        donor=self.game._summon(0,'TLC_841t');donor._bound_card='not a physical card'
        before=deepcopy(self.devourer.attached_death_effects)
        with self.assertRaisesRegex(UnsupportedCard,'Invalid inherited Deathrattle memory'):self.kill(donor)
        self.assertEqual(self.devourer.attached_death_effects,before)

    def test_absorbed_spell_reference_survives_source_state_changes(self):
        donor=self.game._summon(0,'CATA_563');donor.rule_state['absorbed_spell_id']='CORE_CS2_023'
        self.kill(donor)
        self.assertEqual(len(self.player.hand),2)
        donor.rule_state['absorbed_spell_id']='CORE_CS2_029'
        self.kill(self.devourer)
        self.assertEqual(len(self.player.hand),4)

    def test_nellie_crew_and_gigafin_bindings_use_separate_memories(self):
        crew=self.game._summon(0,'EDR_851t');crew._nellie_crew=['CORE_EX1_162']
        crew.attached_death_effects.append(('historic_nellie_return',))
        self.kill(crew);crew._nellie_crew.clear()
        devour=self.game._summon(0,'EDR_851t');devour._devoured_cards=['EDR_851t']
        devour.attached_death_effects.append(('historic_gigafin_return',))
        self.kill(devour)
        self.assertEqual(devour._devoured_cards,[])
        self.kill(self.devourer)
        self.assertEqual(len(self.player.hand),2)
        self.assertTrue(all(c.set_cost==1 for c in self.player.hand))
        self.assertEqual([m.card_id for m in self.game.players[1].minions],['EDR_851t']*2)

    def test_discarded_secret_target_does_not_retarget_an_identical_card(self):
        enemy=self.game.players[1]
        selected=Card(self.game._new_id(),'CORE_CS2_029')
        other=Card(self.game._new_id(),'CORE_CS2_029')
        enemy.hand=[selected,other]
        donor=self.game._summon(0,'EDR_851t');donor.secret_discard=(1,selected.uid)
        donor.attached_death_effects.append(('b60_discard_secret',))
        self.kill(donor);self.assertEqual(enemy.hand,[other])
        donor.secret_discard=(1,other.uid)
        self.kill(self.devourer)
        self.assertEqual(enemy.hand,[other])

    def test_remembered_draw_target_does_not_retarget_a_new_physical_copy(self):
        selected=self.game._enter_hand(0,Card(self.game._new_id(),'CORE_CS2_029'))
        donor=self.game._summon(0,'EDR_851t');donor.remembered_draw=selected.uid
        donor.attached_death_effects.append(('b60_discard_remembered',))
        self.kill(donor);self.assertFalse(self.player.hand)
        other=self.game._enter_hand(0,Card(self.game._new_id(),'CORE_CS2_029'))
        donor.remembered_draw=other.uid
        self.kill(self.devourer)
        self.assertEqual(self.player.hand,[other])

    def test_dormant_release_keeps_the_bound_entity_reference(self):
        target=self.game._summon(1,'CORE_CS2_179')
        self.game._sleep_minion(target,10000)
        donor=self.game._summon(0,'EDR_851t');donor.rule_state['imprisoned_entity']=target.uid
        donor.attached_death_effects.append(('dormant_release',))
        self.kill(donor);self.assertEqual(target.dormant,0)
        self.game._sleep_minion(target,10000);donor.rule_state['imprisoned_entity']=0
        self.kill(self.devourer)
        self.assertEqual(target.dormant,0)

    def test_infinity_receipt_restores_only_its_original_layer(self):
        card=self.game._enter_hand(0,Card(self.game._new_id(),'CORE_CS2_029'))
        card._infinity_cost_layers=[101]
        donor=self.game._summon(0,'EDR_851t');donor._infinity_cost_receipts=[(card.uid,101)]
        donor.attached_death_effects.append(('infinity_restore_cost',))
        self.kill(donor);self.assertFalse(card._infinity_cost_layers)
        card._infinity_cost_layers=[101,102];donor._infinity_cost_receipts.clear()
        self.kill(self.devourer)
        self.assertEqual(card._infinity_cost_layers,[102])
