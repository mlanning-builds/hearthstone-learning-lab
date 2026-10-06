import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('candidate_status_receipts',ROOT/'staging/rebased-88/expanded/status.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

class ValidationReceiptTests(unittest.TestCase):
    def run_fixture(self, root, fingerprints, passing=True):
        result=unittest.TestResult()
        result.testsRun=1
        if not passing:
            result.failures.append(('fixture','failure'))
        with patch.object(module,'ROOT',root), patch.object(module,'code_fingerprint',side_effect=fingerprints), patch('unittest.defaultTestLoader.discover',return_value=unittest.TestSuite()), patch('unittest.TextTestRunner.run',return_value=result):
            return module.run_rule_fixtures()

    def test_change_during_passing_suite_cannot_certify_new_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);r=self.run_fixture(root,['before','after'])
            self.assertTrue(r['fixture_success'])
            self.assertFalse(r['success'])
            self.assertFalse(r['source_unchanged'])
            self.assertEqual(r['fingerprint'],'before')
            self.assertEqual(r['end_fingerprint'],'after')
            self.assertEqual(json.loads(Path(r['report_path']).read_text()),r)

    def test_repeated_runs_preserve_independent_receipts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            first=self.run_fixture(root,['same','same'])
            second=self.run_fixture(root,['same','same'],passing=False)
            self.assertTrue(first['success']);self.assertFalse(second['success'])
            self.assertNotEqual(first['report_path'],second['report_path'])
            self.assertEqual(json.loads(Path(first['report_path']).read_text()),first)
            self.assertEqual(json.loads((root/'runs/expanded_validation/validation.json').read_text()),second)
            self.assertFalse(list((root/'runs/expanded_validation').glob('*.tmp')))
