import copy
import random
import unittest
from benchmarks.suite import RulesPolicy, match
from engine.cards import supported_pool
from engine.game import Game
from lab import population
from learner.policy import Policy

class BenchmarkTests(unittest.TestCase):
    def test_legal_observation_only_and_no_mutation(self):
        decks=population(supported_pool(),per_profile=1,seed=91)[:2]
        for style in ('aggressive','trading'):
            game=Game([d['cards'] for d in decks],[tuple(d['runes'].values()) for d in decks],seed=31,record=False)
            bot=RulesPolicy(style); rng=random.Random(33)
            while not game.terminal:
                obs=game.observe(game.current,include_events=False); before=copy.deepcopy(obs)
                action=bot.choose(obs,rng)[0]
                self.assertEqual(obs,before)
                self.assertIn(action,game.legal_actions())
                game.step(action)
    def test_frozen_model_reproducible(self):
        pair=population(supported_pool(),per_profile=1,seed=22)[:2]
        p=Policy(); before=p.export()
        a=match(p,RulesPolicy('trading'),pair,32,0)
        b=match(p,RulesPolicy('trading'),pair,32,0)
        self.assertEqual(a,b); self.assertEqual(before,p.export())
    def test_bad_style(self):
        with self.assertRaises(ValueError): RulesPolicy('expert')
