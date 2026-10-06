import importlib.util
from pathlib import Path
import unittest
spec=importlib.util.spec_from_file_location('candidate_progress',Path(__file__).resolve().parents[2]/'tools/record_candidate_progress.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

class MilestoneProgressTests(unittest.TestCase):
    def test_target_reached_does_not_imply_release(self):
        d=module.milestone_status(200,200,694)
        self.assertTrue(d['implementation_target_reached'])
        self.assertFalse(d['release_ready']);self.assertFalse(d['milestone_complete'])
        self.assertEqual(d['remaining_standard_cards'],694)
        self.assertFalse(any('remaining 0 milestone' in x for x in d['next_work']))
    def test_beyond_target_retains_full_standard_scope(self):
        d=module.milestone_status(210,200,684)
        self.assertEqual(d['remaining_in_milestone'],0)
        self.assertTrue(any('684' in x for x in d['next_work']))
        self.assertFalse(d['release_ready'])
    def test_before_target_still_lists_remaining_additions(self):
        d=module.milestone_status(197,200,697)
        self.assertFalse(d['implementation_target_reached']);self.assertEqual(d['remaining_in_milestone'],3)
        self.assertTrue(any('remaining 3 milestone' in x for x in d['next_work']))
    def test_even_full_card_count_does_not_certify_semantics(self):
        d=module.milestone_status(894,200,0)
        self.assertFalse(d['release_ready']);self.assertFalse(d['milestone_complete'])
    def test_invalid_counts_rejected(self):
        for values in ((-1,200,694),(200,True,694),(200,200,1.5)):
            with self.assertRaises(ValueError):module.milestone_status(*values)
