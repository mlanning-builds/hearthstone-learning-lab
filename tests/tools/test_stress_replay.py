"""Exercise the saved replay path, including failure location reporting."""
from dataclasses import asdict
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
CANDIDATE=ROOT/'staging/rebased-88'
sys.path.insert(0,str(CANDIDATE))
from expanded import Action,random_deck
from expanded.status import code_fingerprint

class StressReplayTests(unittest.TestCase):
    def replay(self,actions):
        case=dict(fingerprint=code_fingerprint(),game_seed=71,
                  decks=[asdict(random_deck('WARRIOR',31)),asdict(random_deck('MAGE',53))],
                  actions=[asdict(a) for a in actions])
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'case.json';path.write_text(json.dumps(case))
            return subprocess.run([sys.executable,str(ROOT/'tools/stress_candidate.py'),
                                   '--engine-root',str(CANDIDATE),'--replay',str(path)],
                                  capture_output=True,text=True,timeout=30)
    def test_saved_choices_replay_as_legal_actions(self):
        result=self.replay([Action('mulligan'),Action('mulligan'),Action('end')])
        self.assertEqual(result.returncode,0,result.stderr+result.stdout)
    def test_replay_reports_the_exact_failing_action(self):
        result=self.replay([Action('mulligan'),Action('end')])
        self.assertEqual(result.returncode,1,result.stderr+result.stdout)
        failure=json.loads(result.stdout)
        self.assertEqual(failure['action'],1);self.assertEqual(failure['error'],'ValueError')
