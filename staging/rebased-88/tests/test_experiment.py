import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from lab import population
from engine.cards import supported_pool
from engine.experiment import play_game, replay_game, run_experiment


class ExperimentTests(unittest.TestCase):
    def test_random_games_all_runes_finish_and_reproduce(self):
        decks=population(supported_pool(),1,12)
        for i,d in enumerate(decks):
            opponent=decks[(i+1)%len(decks)]
            cards=[d['cards'],opponent['cards']]
            profiles=[tuple(d['runes'].values()),tuple(opponent['runes'].values())]
            result=play_game(cards,profiles,seed=i,first_player=i%2,record=True)
            replay=replay_game(result['replay'])
            self.assertEqual(result['winner'],replay.winner)
            self.assertEqual(result['health'],[p.health for p in replay.players])
            self.assertLessEqual(result['turns'],89)

    def test_balanced_schedule_resume_and_save(self):
        with tempfile.TemporaryDirectory() as directory:
            states=[]
            result=run_experiment(4,1,7,directory,states.append)
            self.assertEqual(len(result['results']),4)
            self.assertEqual([r['first_player'] for r in result['results']],[0,1,0,1])
            for i in (0,2):
                a,b=result['results'][i:i+2]
                self.assertEqual(a['deck_indices'],b['deck_indices'])
                self.assertEqual(a['seed'],b['seed'])
            resumed=run_experiment(4,1,7,directory,states.append)
            self.assertEqual(result['results'],resumed['results'])
            self.assertEqual(states[-1]['resumed'],4)
            self.assertTrue(Path(result['directory'],'summary.json').exists())

    def test_interruption_resumes_without_replaying_completed_games(self):
        with tempfile.TemporaryDirectory() as directory:
            def interrupt(state):
                if state['completed']==2 and state['status']=='running':
                    raise KeyboardInterrupt()
            with self.assertRaises(KeyboardInterrupt):
                run_experiment(4,1,9,directory,interrupt)
            resumed=run_experiment(4,1,9,directory)
            with tempfile.TemporaryDirectory() as other:
                fresh=run_experiment(4,1,9,other)
            self.assertEqual(resumed['results'],fresh['results'])

    def test_errors_are_not_counted_as_losses(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch('engine.experiment.play_game',side_effect=RuntimeError('test failure')):
                with self.assertRaises(RuntimeError): run_experiment(2,1,3,directory)
            saved=json.loads(next(Path(directory).glob('*/checkpoint.json')).read_text())
            self.assertEqual(saved['status'],'failed')
            self.assertEqual(saved['results'],[])

    def test_replay_rejects_changed_rules(self):
        decks=population(supported_pool(),1,12)[:2]
        result=play_game([d['cards'] for d in decks],[tuple(d['runes'].values()) for d in decks],record=True)
        result['replay']['engine_fingerprint']='wrong'
        with self.assertRaises(ValueError): replay_game(result['replay'])

    def test_odd_or_invalid_batch_rejected(self):
        for games in (0,1,3,-2):
            with self.assertRaises(ValueError): run_experiment(games=games)

if __name__=='__main__': unittest.main()
