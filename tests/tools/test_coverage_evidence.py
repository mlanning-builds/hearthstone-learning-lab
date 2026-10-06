import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('coverage_tool',ROOT/'tools/build_coverage.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

class CoverageEvidenceTests(unittest.TestCase):
    def fixture(self,root):
        for name,text in [('expanded/rules.py','RULE=1'),('data/standard/manifest.json','{}'),('standard/catalog.py','CATALOG=1')]:
            path=root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text)
    def receipt(self,root,success=True):
        path=root/'runs/expanded_validation/validation.json';path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(dict(success=success,fingerprint=module.fingerprint(root),tests_run=7)))
    def test_missing_receipt_is_not_a_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);self.fixture(root)
            self.assertFalse(module.validation_evidence(root)['suite_receipt_matches_current_code'])
    def test_source_change_invalidates_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);self.fixture(root);self.receipt(root)
            self.assertTrue(module.validation_evidence(root)['suite_receipt_matches_current_code'])
            (root/'expanded/rules.py').write_text('RULE=2')
            self.assertFalse(module.validation_evidence(root)['suite_receipt_matches_current_code'])
    def test_failed_suite_is_not_a_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);self.fixture(root);self.receipt(root,False)
            self.assertFalse(module.validation_evidence(root)['suite_receipt_matches_current_code'])
    def test_active_receipt_does_not_certify_candidate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);candidate=root/'staging/rebased-88'
            self.fixture(root);self.fixture(candidate);self.receipt(root)
            self.assertTrue(module.validation_evidence(root)['suite_receipt_matches_current_code'])
            self.assertFalse(module.validation_evidence(candidate)['suite_receipt_matches_current_code'])
