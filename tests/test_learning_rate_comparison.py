"""No games, policy evaluations or optimizer steps."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import torch
from tools import learning_rate_comparison as pilot
from hearthstone_sim.neural.checkpoints import SCHEMA, save, load, code_digest
from tools.migrate_400_game_checkpoint import equal


class PilotChecks(unittest.TestCase):
    def test_copies_preserve_state_and_share_only_lr_difference(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            compat = {'fixture': 'no-game'}
            opponent = save(root/'opponent.pt', dict(schema=SCHEMA, compatibility=compat, model={'w': torch.tensor([3.])}))
            descriptor = dict(name='opponent.pt', sha256=opponent['sha256'])
            original = dict(schema=SCHEMA, compatibility=compat, model={'w': torch.tensor([2.])},
                optimizer=dict(state={0: {'exp_avg': torch.tensor([.4])}},param_groups=[dict(lr=.0001)]),
                action_rng=torch.tensor([1]), shuffle_rng=torch.tensor([2]), league_rng=(3,4),
                global_game=12000, iteration=400, tactical_state={'completed':128},
                settings={'ppo': {'learning_rate':.0001}, 'heuristic_fraction':.5},
                league=[descriptor], evaluation_anchors={'anchor':descriptor})
            source = Path(save(root/'source.pt', original)['path'])
            frozen = copy.deepcopy(original)
            a = pilot.clone_arm(original, source, root/'a', .0001)
            b = pilot.clone_arm(original, source, root/'b', .00005)
            self.assertTrue(equal(original, frozen))
            first, second = [load(cp['path'], compat) for cp in (a,b)]
            self.assertEqual(second['optimizer']['param_groups'][0]['lr'], .00005)
            for value in (first,second):
                value['settings']['ppo']['learning_rate'] = 0
                value['optimizer']['param_groups'][0]['lr'] = 0
                value['migration']['learning_rate'] = 0
            self.assertTrue(equal(first,second))
            self.assertTrue(source.exists())

    def test_start_rejects_active_run_before_any_mutation(self):
        with patch.object(pilot,'preflight',return_value={}), patch.object(pilot,'active_training',return_value=['active']), patch('sys.argv',['pilot','--train']), patch.object(pilot,'execute') as execute:
            with self.assertRaisesRegex(RuntimeError,'still active'):
                pilot.main()
            execute.assert_not_called()

    def test_notebook_is_clean_and_python_parses(self):
        nb = json.loads((pilot.ROOT/'notebooks/20_learning_rate_comparison.ipynb').read_text())
        for cell in nb['cells']:
            if cell['cell_type']=='code':
                self.assertIsNone(cell['execution_count'])
                self.assertEqual(cell['outputs'],[])
                compile(''.join(cell['source']),'<notebook>','exec')

    def test_active_neural_fingerprint_untouched(self):
        from tools.long_training_campaign import APPROVED_CODE
        self.assertEqual(code_digest(), APPROVED_CODE)

if __name__=='__main__':
    unittest.main()
