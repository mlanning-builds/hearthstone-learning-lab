"""Resurrection selects compiled costs/types and restores fresh definitions."""
import unittest
import test_expanded_forge_types as type_fixtures
from expanded.death_definitions import definitions,cost
from expanded.selectors import has_tribe


class ForgeResurrectionTests(unittest.TestCase):
    def setUp(self):
        self.fixture=type_fixtures.ForgeTypeTests();self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups);self.game=self.fixture.game
        self.context=dict(owner=0,source=None,target=0,bonus=0,spell=False,lifesteal=False)

    def dead_creation(self):
        card=self.fixture.craft();self.compiled_cost=card.set_cost
        m=self.fixture.fixture.play(card);self.base=(m.attack,m.max_health)
        self.game._buff(m,8,8);self.game._silence(m)
        m.health=0;self.game._settle(allow_event_choices=True)
        return m

    def test_highest_beast_uses_creation_cost_and_all_type(self):
        dead=self.dead_creation();self.game.players[0].death_history.append('EDR_851t')
        self.game._effect(('resurrect_highest','BEAST'),self.context)
        m=self.game.players[0].minions[-1]
        self.assertNotEqual(m.uid,dead.uid)
        self.assertEqual((m.attack,m.max_health),self.base)
        self.assertTrue(has_tribe(self.game._card_data(m),'MURLOC'))
        self.assertFalse(m.silenced)

    def test_cost_slot_restores_creation_and_grants_reborn(self):
        self.dead_creation()
        self.game._effect(('resurrect_costs_reborn',(self.compiled_cost,)),self.context)
        m=self.game.players[0].minions[-1]
        self.assertEqual((m.attack,m.max_health),self.base)
        self.assertIn('REBORN',self.game._effective_keywords(m))
        self.assertTrue(has_tribe(self.game._card_data(m),'DEMON'))

    def test_created_definition_is_weighted_per_death_record(self):
        self.dead_creation();value=list(definitions(self.game,0))[0]
        self.assertEqual(cost(self.game,value),self.compiled_cost)
        # Each real subsequent death adds one eligible outcome, preserving
        # ordinary resurrection weighting rather than deduplicating token IDs.
        self.game._effect(('resurrect_highest',None),self.context)
        m=self.game.players[0].minions[-1];m.health=0;self.game._settle(allow_event_choices=True)
        values=list(definitions(self.game,0));self.assertEqual(len(values),2)
        self.assertTrue(all(cost(self.game,v)==self.compiled_cost for v in values))

    def test_plain_history_fixture_preserves_ordinary_card_behavior(self):
        self.game.players[0].death_history=['EDR_851t']
        self.game._effect(('resurrect_highest',None),self.context)
        self.assertEqual(self.game.players[0].minions[-1].card_id,'EDR_851t')

    def dead_deathrattle_creation(self,built_in=True):
        from expanded.minion_forge import ForgePart
        first=ForgePart('DINO_435',death_operations=(('draw',1),) if built_in else (),source='explicit deathrattle fixture')
        second=ForgePart('EDR_851t',source='explicit deathrattle fixture')
        self.game._forge_choice(dict(kind='forge_part',forge_kind='dragon',owner=0,discount=0,first=first,parts=[second]),dict(card_id=second.card_id))
        card=self.game.players[0].hand[-1];self.compiled_cost=card.set_cost
        m=self.fixture.fixture.play(card);self.base=(m.attack,m.max_health)
        m.attached_death_effects.append(('armor',7))
        if built_in:self.game._silence(m)
        m.health=0;self.game._settle(allow_event_choices=True)
        return m

    def test_deathrattle_resurrection_recognizes_silenced_intrinsic_recipe(self):
        self.dead_deathrattle_creation()
        self.game._effect(('resurrect_deathrattle_copies',self.compiled_cost,100,False),self.context)
        copies=self.game.players[0].minions
        self.assertEqual(len(copies),2);self.assertNotEqual(copies[0].uid,copies[1].uid)
        for m in copies:
            self.assertEqual((m.attack,m.max_health),self.base)
            self.assertEqual(m.attached_death_effects,[('draw',1)])
        copies[0].attached_death_effects.append(('armor',1))
        self.assertEqual(copies[1].attached_death_effects,[('draw',1)])

    def test_granted_deathrattle_does_not_change_printed_eligibility(self):
        self.dead_deathrattle_creation(False)
        self.game._effect(('resurrect_deathrattle_copies',0,100,False),self.context)
        self.assertEqual(self.game.players[0].minions,[])

    def test_deathrattle_resurrection_uses_compiled_cost_not_token_zero(self):
        self.dead_deathrattle_creation()
        self.assertGreater(self.compiled_cost,4)
        self.game._effect(('resurrect_deathrattle_copies',0,4,False),self.context)
        self.assertEqual(self.game.players[0].minions,[])

    def test_oathstone_restores_each_compiled_dragon_death(self):
        self.dead_deathrattle_creation()
        self.game._effect(('resurrect_highest',None),self.context)
        m=self.game.players[0].minions[-1];m.health=0;self.game._settle(allow_event_choices=True)
        self.game._start_play_effects([('fabled_resurrect_dragons',)],dict(self.context))
        self.game._settle(allow_event_choices=True)
        copies=self.game.players[0].minions
        self.assertEqual(len(copies),2)
        for m in copies:
            self.assertEqual((m.attack,m.max_health),self.base)
            self.assertEqual(m.attached_death_effects,[('draw',1)])
