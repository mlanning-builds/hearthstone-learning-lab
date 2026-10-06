"""Bounded runner integration: capped games cannot update model weights."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]

class TrainingResumeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.output=Path(self.tmp.name)
    def run_training(self,episodes,resume=None,seed=71):
        args=[sys.executable,str(ROOT/'tools/train_candidate.py'),'--engine-root',str(ROOT/'staging/rebased-88'),
              '--episodes',str(episodes),'--max-actions','2','--seed',str(seed),
              '--learning-rate','0.001','--output',str(self.output),'--experimental']
        if resume:args+=['--resume-receipt',str(resume)]
        return subprocess.run(args,cwd=ROOT,text=True,capture_output=True,timeout=30)
    def manifest(self,result):
        self.assertEqual(result.returncode,0,result.stderr)
        event=json.loads(result.stdout.splitlines()[-1])
        return json.loads(Path(event['manifest']).read_text())
    def test_split_run_matches_uninterrupted_sampling_and_schedule(self):
        full=self.manifest(self.run_training(3))
        first=self.manifest(self.run_training(1))
        resumed=self.manifest(self.run_training(2,first['episode_receipts'][-1]))
        self.assertEqual(Path(full['final_checkpoint']['path']).read_bytes(),
                         Path(resumed['final_checkpoint']['path']).read_bytes())
        for left,right in zip(full['episode_receipts'][1:],resumed['episode_receipts']):
            a=json.loads(Path(left).read_text());b=json.loads(Path(right).read_text())
            for key in ('episode','seed','first_player','replay_only_decks','result'):
                self.assertEqual(a[key],b[key])
            self.assertFalse(b['result']['updated'])
        self.assertEqual(resumed['config']['starting_episode'],1)
    def test_changed_seed_rejected_before_new_run_folder(self):
        first=self.manifest(self.run_training(1));folders=list(self.output.iterdir())
        result=self.run_training(1,first['episode_receipts'][0],seed=72)
        self.assertNotEqual(result.returncode,0)
        self.assertIn('Resume configuration mismatch: seed',result.stderr)
        self.assertEqual(list(self.output.iterdir()),folders)
