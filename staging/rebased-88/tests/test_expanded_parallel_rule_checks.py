"""Parallel validation executes the exact case multiset and excludes training."""
import unittest,signal
from unittest.mock import patch
from expanded.status import _run_rule_group,_parallel_rule_results
class WorkerFixture(unittest.TestCase):
 def run_pass(self):self.assertTrue(True)
 def run_fail(self):self.fail('deliberate worker failure')
 def run_error(self):raise ValueError('deliberate worker error')
 def run_timeout_subtest(self):
  with self.subTest(part='deadline'):signal.raise_signal(signal.SIGALRM)
  self.fail('Timed-out subtest continued its loop')
 def run_skip(self):self.skipTest('deliberate worker skip')
 @unittest.expectedFailure
 def run_known_failure(self):self.fail('expected worker failure')
 @unittest.expectedFailure
 def run_unexpected_success(self):self.assertTrue(True)
PREFIX=__name__+'.WorkerFixture.'
class ParallelRuleCheckTests(unittest.TestCase):
 def test_duplicate_case_ids_are_preserved(self):
  ids=[PREFIX+'run_pass']*2;r=_run_rule_group(ids)
  self.assertEqual(r['started_ids'],ids);self.assertEqual(r['tests_run'],2);self.assertFalse(r['failures'] or r['errors'])
 def test_failures_errors_and_skips_are_retained(self):
  ids=[PREFIX+method for method in ('run_pass','run_fail','run_error','run_skip')];r=_run_rule_group(ids)
  self.assertEqual(r['started_ids'],ids);self.assertEqual(r['tests_run'],4)
  self.assertEqual((len(r['failures']),len(r['errors']),len(r['skipped'])),(1,1,1))
 def test_training_and_arbitrary_modules_rejected_before_loading(self):
  for name in ('test_expanded_training.X.test_a','test_expanded_learning_core.X.test_a','other_module.X.test_a'):
   with patch('unittest.defaultTestLoader.loadTestsFromNames') as load:
    with self.assertRaises(ValueError):_run_rule_group([name])
    load.assert_not_called()
 def test_fresh_processes_execute_the_exact_duplicate_inventory(self):
  ids=[PREFIX+'run_pass']*3;r=_parallel_rule_results(ids,2)
  self.assertTrue(r.wasSuccessful());self.assertEqual(r.testsRun,3)

 def test_parallel_unexpected_success_cannot_be_reported_as_pass(self):
  ids=[PREFIX+'run_known_failure',PREFIX+'run_unexpected_success'];r=_parallel_rule_results(ids,2)
  self.assertFalse(r.wasSuccessful());self.assertEqual(r.testsRun,2)
  self.assertEqual((len(r.expectedFailures),len(r.unexpectedSuccesses)),(1,1))

 @unittest.skipUnless(hasattr(signal,'SIGALRM'),'POSIX case deadline')
 def test_timed_out_subtest_aborts_case_but_preserves_next_case(self):
  ids=[PREFIX+'run_timeout_subtest',PREFIX+'run_pass'];r=_run_rule_group(ids)
  self.assertEqual(r['started_ids'],ids);self.assertEqual(r['tests_run'],2)
  self.assertEqual(len(r['errors']),1);self.assertFalse(r['failures'])

 @unittest.skipUnless(hasattr(signal,'SIGALRM'),'POSIX case deadline')
 def test_nested_group_restores_its_callers_deadline_handler(self):
  handler=signal.getsignal(signal.SIGALRM)
  _run_rule_group([PREFIX+'run_pass'])
  self.assertIs(signal.getsignal(signal.SIGALRM),handler)
