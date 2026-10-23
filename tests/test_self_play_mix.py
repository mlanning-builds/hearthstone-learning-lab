"""Configuration migration only; no games, inference or optimizer updates."""
import copy,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import torch
from tools import long_training_campaign as c
from hearthstone_sim.neural.checkpoints import SCHEMA,save,load
from tools.migrate_400_game_checkpoint import equal

class SelfPlayMixTests(unittest.TestCase):
    def test_new_mix_preserves_learned_state_and_other_settings(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);campaign=root/'campaign';campaign.mkdir()
            panel=root/'panel.json';panel.write_text('{}')
            compat=dict(engine=c.APPROVED_ENGINE,neural_code=c.APPROVED_CODE,decks_sha256='fixture-panel')
            settings=dict(seed=71,games_per_iteration=64,max_actions=1000,device='cpu',threads=6,collection_workers=4,
                self_play_fraction=.25,heuristic_fraction=.5,league_size=32,tactical_steps=128,
                checkpoint_every_iterations=1,failure_fraction=.02,failure_min_attempts=100,failure_repeats=5,
                retry_cap=20,trace_first=6,trace_every=4,ppo=dict(learning_rate=.0001,epochs=4,minibatch=64),
                evaluation=dict(every_iterations=16,games_per_opponent=128,seed=1000020000),evaluation_at=[],evaluate_at_start=True)
            prior=dict(schema=SCHEMA,kind='resume',compatibility=compat,settings=settings,
                migration=dict(kind='owner-authorized-all-class-campaign'),model={'w':torch.tensor([2.])},
                optimizer={'state':{'momentum':torch.tensor([.3])}},action_rng=torch.tensor([1]),
                shuffle_rng=torch.tensor([2]),league_rng=(3,4),global_game=100,iteration=2,
                tactical_state={'completed':128},safety={'attempted':100,'failed':2,'signatures':{'unrelated':2}},
                evaluation_safety={'attempted':10,'failed':0,'signatures':{}},league=[],evaluation_anchors={},evaluation_history=[])
            source=Path(save(root/'source.pt',prior)['path'])
            (campaign/'campaign.json').write_text(json.dumps(dict(start_global=0,target_games=10000,panel_sha256='fixture-panel')))
            with patch.object(c,'CAMPAIGN',campaign),patch.object(c,'PANEL',panel),patch.object(c,'latest_source',return_value=source),patch.object(c,'prepare',return_value=({},None,compat)),patch('hearthstone_sim.neural.deck_continuum.build_panel',return_value=panel):
                plan=c.prepare_campaign()
            result=load(plan['checkpoint']['path'],compat)
            self.assertEqual(result['settings']['self_play_fraction'],.6)
            self.assertEqual(result['settings']['heuristic_fraction'],.1)
            self.assertEqual(plan['opponent_mix'],dict(current=.6,older=.3,heuristic=.1))
            expected=copy.deepcopy(prior);expected['settings'].update(self_play_fraction=.6,heuristic_fraction=.1)
            for key in prior:
                if key!='migration':self.assertTrue(equal(expected[key],result[key]),key)
            command=plan['command']
            self.assertEqual(command[command.index('--self-play-fraction')+1],'0.6')
            self.assertEqual(command[command.index('--heuristic-fraction')+1],'0.1')
            self.assertEqual((plan['threads'],plan['collection_workers'],plan['session_seconds']),(6,4,7200))
            self.assertEqual(load(source,compat)['settings']['heuristic_fraction'],.5)

if __name__=='__main__':unittest.main()
