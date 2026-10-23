"""Public selector serialization; no games or optimizer updates."""
import copy
from dataclasses import asdict
import unittest
from test_neural_ppo import fixture
from hearthstone_sim.neural.runner import prepare
from hearthstone_sim.neural.encoding import VisibleEncoder

class PoolEncodingTests(unittest.TestCase):
    def test_nested_selector_matches_plain_mapping(self):
        prepare()
        from expanded.generation_cards import PoolRequest
        request=PoolRequest(card_type='MINION',classes='own')
        decision=fixture()
        decision['observation']['players'][0]['board']=[dict(uid=8,card_id='VISIBLE',deathrattles=[['generate',request]])]
        plain=copy.deepcopy(decision)
        plain['observation']['players'][0]['board'][0]['deathrattles'][0][1]=asdict(request)
        encoder=VisibleEncoder()
        self.assertEqual(encoder.encode(decision),encoder.encode(plain))
        decision['observation']['players'][0]['board'][0]['deathrattles'][0][1]=object()
        with self.assertRaisesRegex(ValueError,'not plain JSON'):encoder.encode(decision)
