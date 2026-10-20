"""Import checks run in fresh interpreters to preserve original engine state."""
import subprocess,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class ActivePackageTests(unittest.TestCase):
 def run_code(self,code):return subprocess.run([sys.executable,'-c',code],cwd=ROOT,text=True,capture_output=True)
 def test_active_package_selects_candidate_from_project_root(self):
  r=self.run_code("from hearthstone_sim import Game; import inspect; assert 'staging/rebased-88' in inspect.getfile(Game)")
  self.assertEqual(r.returncode,0,r.stderr)
 def test_original_engine_is_preserved_and_mixed_import_rejected(self):
  r=self.run_code("import engine,inspect; original=engine.Game; assert 'staging/rebased-88' not in inspect.getfile(original); from hearthstone_sim import Game")
  self.assertNotEqual(r.returncode,0);self.assertIn('already loaded from another simulator',r.stderr)
 def test_smoke_command_runs_no_training(self):
  r=subprocess.run([sys.executable,'tools/smoke_simulator.py'],cwd=ROOT,text=True,capture_output=True)
  self.assertEqual(r.returncode,0,r.stderr);self.assertIn('"training_executed": false',r.stdout)
