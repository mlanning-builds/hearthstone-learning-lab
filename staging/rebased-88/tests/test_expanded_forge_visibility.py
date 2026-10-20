"""Composite rules cross the visible ML boundary as ordinary serializable data."""
import json,unittest
from copy import deepcopy
import test_expanded_forge_types as fixtures
from expanded.minion_forge import ForgePart
from expanded.generation_cards import pool,random_cards,PoolRequest
from expanded.features import encode_decision,SCHEMA


class VisibleForgeTests(unittest.TestCase):
    def setUp(self):
        self.fixture=fixtures.ForgeTypeTests();self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups);self.game=self.fixture.game

    def craft(self,minimum=4):
        self.request=pool(card_type='MINION',minimum=minimum,maximum=minimum)
        first=ForgePart('DINO_435',operations=(random_cards(self.request),),source='explicit visibility fixture')
        second=ForgePart('EDR_851t',source='explicit visibility fixture')
        self.game._forge_choice(dict(kind='forge_part',forge_kind='dragon',owner=0,discount=0,first=first,parts=[second]),dict(card_id=second.card_id))
        return self.game.players[0].hand[-1]

    def rows(self,view):return encode_decision(dict(observation=view,actor=view['viewer'],actions=view['legal_actions']))

    def test_generated_recipe_is_json_serializable_and_encodable(self):
        card=self.craft();view=self.game.observe(0)
        json.dumps(view);rows=self.rows(view)
        self.assertTrue(rows);self.assertEqual(SCHEMA,'visible-action-features-v62')
        self.assertTrue(any('minimum' in key for row in rows for key in row))
        self.assertIsInstance(card.rule_state['crafted_ops'][0][1],PoolRequest)

    def test_visible_rules_are_detached_from_runtime_definition(self):
        card=self.craft();view=self.game.observe(0)
        shown=next(c for c in view['players'][0]['hand'] if c['uid']==card.uid)
        shown['rule_state']['crafted_ops'][0][1]['minimum']=999
        self.assertEqual(card.rule_state['crafted_ops'][0][1].minimum,4)

    def test_opponent_cannot_see_private_held_recipe(self):
        card=self.craft();view=self.game.observe(1)
        self.assertNotIn('hand',view['players'][0])
        self.assertNotIn(card.card_id,json.dumps(view))

    def test_silenced_creation_types_are_public_for_both_viewers(self):
        card=self.craft();m=self.game._summon(0,card.card_id,entry_source=card)
        self.game._silence(m)
        for viewer in (0,1):
            view=self.game.observe(viewer);shown=next(e for e in view['players'][0]['board'] if e['uid']==m.uid)
            self.assertEqual(shown['races'],['ALL']);json.dumps(view)
        self.assertTrue(any('races' in key and 'ALL' in key for row in self.rows(self.game.observe(0)) for key in row))

    def test_generation_bounds_change_visible_features(self):
        self.craft(4);first=self.rows(self.game.observe(0))
        self.game.players[0].hand=[];self.craft(7);second=self.rows(self.game.observe(0))
        self.assertNotEqual(first,second)
