"""CLI checks use fresh processes to keep candidate imports isolated."""
import json,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class SimulatorWorkflowTests(unittest.TestCase):
 def run_cli(self,*args):
  return subprocess.run([sys.executable,'tools/simulator_workflow.py',*args],cwd=ROOT,text=True,capture_output=True)
 def test_scope_does_not_claim_complete_support(self):
  r=self.run_cli('scope');self.assertEqual(r.returncode,0,r.stderr);d=json.loads(r.stdout)
  self.assertTrue(d['scope']['known_checks_passed']);self.assertFalse(d['scope']['full_support_certified']);self.assertFalse(d['training_executed']);self.assertTrue(d['source_unchanged'])
 def test_unsupported_deck_rejected_before_benchmark(self):
  good=json.loads(self.run_cli('scope').stdout)['decks'];good[0]['cards'][0]='CATA_470'
  with tempfile.TemporaryDirectory() as tmp:
   path=Path(tmp)/'decks.json';path.write_text(json.dumps(good));r=self.run_cli('benchmark','--decks',str(path))
  self.assertEqual(r.returncode,1,r.stderr);d=json.loads(r.stdout);self.assertFalse(d['scope']['known_checks_passed']);self.assertNotIn('results',d)
 def test_timing_is_bounded_and_reproducible(self):
  reports=[]
  for _ in range(2):
   r=self.run_cli('benchmark','--games','1','--max-actions','10','--seed','123');self.assertEqual(r.returncode,0,r.stderr);reports.append(json.loads(r.stdout))
  for d in reports:
   self.assertEqual(d['capped_games'],1);self.assertEqual(d['completed_games'],0);self.assertEqual(d['results'][0]['actions'],10);self.assertGreater(d['decisions_per_second'],0)
  self.assertEqual(reports[0]['decks'],reports[1]['decks']);self.assertEqual(reports[0]['results'][0]['winner'],reports[1]['results'][0]['winner'])
