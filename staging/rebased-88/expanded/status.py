"""Readiness checks distinguish written code, user-run fixtures, and full coverage."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
HERE=Path(__file__).resolve().parent


def code_fingerprint():
    h=hashlib.sha256()
    paths=sorted(HERE.glob('*.py'))+sorted(HERE.glob('*.json'))+sorted((ROOT/'engine').glob('*.py'))+[ROOT/'data/standard/manifest.json',ROOT/'standard/catalog.py']+sorted((ROOT/'tests').glob('test_expanded*.py'))
    for path in paths:
        h.update(str(path.relative_to(ROOT)).encode());h.update(path.read_bytes())
    return h.hexdigest()


def readiness():
    from standard.catalog import load_catalog
    catalog=load_catalog()
    index=json.loads((HERE/'implementation_index.json').read_text())
    ids=set(index['implemented_card_ids'])
    # A written implementation is not equivalent to externally verified behavior.
    missing=[dict(id=c['id'],name=c['name'],card_set=c['set'],classes=c.get('classes') or [c.get('cardClass')],text=c.get('text','')) for c in catalog if c['id'] not in ids]
    validation=ROOT/'runs/expanded_validation/validation.json'
    receipt=json.loads(validation.read_text()) if validation.exists() else None
    gaps=json.loads((HERE/'fidelity_gaps.json').read_text())
    from .dependencies import current_dependency_report
    dependencies=current_dependency_report()
    current=code_fingerprint()
    fixtures_passed=bool(receipt and receipt.get('fingerprint')==current and receipt.get('success'))
    return dict(engine=index['engine'],catalog_cards=len(catalog),effects_written=len(ids),missing_cards=missing,
                base_hero_powers_written=index['base_hero_power_classes'],
                fixtures_passed_for_current_code=fixtures_passed,fixture_receipt=receipt,
                full_standard_ready=False,known_fidelity_gaps=gaps,
                generated_dependency_report=dependencies,
                remaining=['Implement '+str(len(missing))+' remaining card effects and all required interaction systems.',
                           'Validate complete game behavior against an independent reference.',
                           'Verify live legality, exceptional deck construction, and generated-card pools.',
                           'Extend and validate the experimental learning policy across the complete Standard engine.'],
                fingerprint=current)


def require_full_standard():
    state=readiness()
    raise RuntimeError('Full Standard is not ready: '+str(len(state['missing_cards']))+' card effects remain, plus interaction validation and complete training coverage. The experimental Game is available only for explicitly implemented decks.')


RULE_EXCLUSIONS=frozenset(('test_expanded_training','test_expanded_learning_core'))

def _run_rule_group(case_ids,progress=False):
    """Execute only explicit rule cases in a fresh worker; no experiment entrypoint."""
    import io,unittest,sys,signal,time
    from contextlib import redirect_stdout,redirect_stderr
    for case_id in case_ids:
        module=case_id.split('.')[0]
        if module in RULE_EXCLUSIONS or not module.startswith('test_expanded'):
            raise ValueError('Not an allowed rule case: '+case_id)
    output=io.StringIO();started=[]
    timed=hasattr(signal,'SIGALRM')
    active_result=[None]
    def case_timeout(*unused):
        if active_result[0] is not None:
            active_result[0]._deadline_stop=True;active_result[0].failfast=True
        raise TimeoutError('Rule case exceeded 180 seconds')
    if timed:
        previous_timer=signal.setitimer(signal.ITIMER_REAL,0)
        previous_handler=signal.signal(signal.SIGALRM,case_timeout)
        timer_started=time.monotonic()
    class ObservedResult(unittest.TextTestResult):
        def startTest(self,test):
            active_result[0]=self
            started.append(test.id());super().startTest(test)
            if progress:print('Rule start: '+test.id(),file=sys.__stderr__,flush=True)
            if timed:signal.alarm(180)
        def addSubTest(self,test,subtest,err):
            if err is not None and isinstance(err[1],TimeoutError):
                # unittest normally swallows a subtest error and continues the
                # same loop. Abort that case, then allow the next case to run.
                self._deadline_stop=True;self.failfast=True
            super().addSubTest(test,subtest,err)
        def stopTest(self,test):
            if timed:signal.alarm(0)
            if getattr(self,'_deadline_stop',False):
                self.failfast=False;self.shouldStop=False;self._deadline_stop=False
            super().stopTest(test)
            if progress:
                prior_failures,prior_errors=getattr(self,'_reported_counts',(0,0))
                for failed,trace in self.failures[prior_failures:]+self.errors[prior_errors:]:
                    print('Rule failure: '+failed.id()+'\n'+trace,file=sys.__stderr__,flush=True)
                self._reported_counts=(len(self.failures),len(self.errors))
                if self.testsRun%100==0:
                    print(f'Worker rule checks: {self.testsRun}/{len(case_ids)}; failures={len(self.failures)}; errors={len(self.errors)}',file=sys.__stderr__,flush=True)
    try:
        with redirect_stdout(output),redirect_stderr(output):
            suite=unittest.defaultTestLoader.loadTestsFromNames(case_ids)
            result=unittest.TextTestRunner(stream=output,verbosity=2,resultclass=ObservedResult).run(suite)
    finally:
        if timed:
            signal.alarm(0);signal.signal(signal.SIGALRM,previous_handler)
            if previous_timer[0]>0:
                signal.setitimer(signal.ITIMER_REAL,max(0.001,previous_timer[0]-(time.monotonic()-timer_started)),previous_timer[1])
    return dict(tests_run=result.testsRun,started_ids=started,
        failures=[(test.id(),trace) for test,trace in result.failures],
        errors=[(test.id(),trace) for test,trace in result.errors],
        skipped=[(test.id(),reason) for test,reason in result.skipped],
        expected_failures=[(test.id(),trace) for test,trace in result.expectedFailures],
        unexpected_successes=[test.id() for test in result.unexpectedSuccesses],output=output.getvalue())

def _parallel_rule_results(case_ids,workers,progress=None):
    import unittest,sys
    from collections import Counter
    from concurrent.futures import ProcessPoolExecutor,as_completed
    from multiprocessing import get_context
    result=unittest.TestResult();started=[];outputs={}
    groups=[case_ids[index::workers] for index in range(workers)]
    with ProcessPoolExecutor(max_workers=workers,mp_context=get_context('spawn')) as executor:
        futures={executor.submit(_run_rule_group,group,progress is not None):index for index,group in enumerate(groups) if group}
        for future in as_completed(futures):
            group=future.result();outputs[futures[future]]=group['output']
            result.testsRun+=group['tests_run'];started.extend(group['started_ids'])
            result.failures.extend(group['failures']);result.errors.extend(group['errors']);result.skipped.extend(group['skipped'])
            result.expectedFailures.extend(group['expected_failures']);result.unexpectedSuccesses.extend(group['unexpected_successes'])
            if progress:progress(result.testsRun,len(case_ids),len(result.failures),len(result.errors))
    for index in sorted(outputs):sys.stderr.write(outputs[index])
    # Count duplicates too: imported fixture classes can appear more than once.
    if Counter(started)!=Counter(case_ids) or result.testsRun!=len(case_ids):
        result.errors.append(('rule_case_coverage','Worker execution does not match the exact discovered rule case inventory'))
    return result

def run_rule_fixtures(progress=None,workers=1):
    """Run explicitly from a notebook or validation command; never at import."""
    import unittest
    import uuid
    from datetime import datetime,timezone
    if type(workers) is not int or not 1<=workers<=8:raise ValueError("Rule workers must be an integer from one to eight")
    start_fingerprint=code_fingerprint()
    discovered=unittest.defaultTestLoader.discover(str(ROOT/'tests'),pattern='test_expanded*.py')
    excluded_modules=RULE_EXCLUSIONS
    def rule_cases(items):
        for item in items:
            if isinstance(item,unittest.TestSuite):
                yield from rule_cases(item)
            elif item.__class__.__module__.split('.')[-1] not in excluded_modules:
                yield item
    suite=unittest.TestSuite(rule_cases(discovered))
    total=suite.countTestCases()
    class ProgressResult(unittest.TextTestResult):
        def stopTest(self,test):
            super().stopTest(test)
            if progress:
                progress(self.testsRun,total,len(self.failures),len(self.errors))
    result=(_parallel_rule_results([case.id() for case in suite],workers,progress) if workers>1 else
            unittest.TextTestRunner(verbosity=2,resultclass=ProgressResult).run(suite))
    end_fingerprint=code_fingerprint()
    unchanged=start_fingerprint==end_fingerprint
    report=dict(fingerprint=start_fingerprint,end_fingerprint=end_fingerprint,
                source_unchanged=unchanged,fixture_success=result.wasSuccessful(),
                success=result.wasSuccessful() and unchanged,tests_run=result.testsRun,
                failures=len(result.failures),errors=len(result.errors),skipped=len(result.skipped),unexpected_successes=len(result.unexpectedSuccesses),
                completed_at=datetime.now(timezone.utc).isoformat(),
                excluded_modules=sorted(excluded_modules),rule_workers=workers,
                scope='Non-training engine fixtures only; learning integration and policy-update scenarios excluded. Not full Standard certification.')
    folder=ROOT/'runs/expanded_validation';folder.mkdir(parents=True,exist_ok=True)
    run_id=uuid.uuid4().hex
    report['run_id']=run_id
    archive=folder/('validation-'+run_id+'.json')
    report['report_path']=str(archive)
    payload=json.dumps(report,indent=2)+'\n'
    with archive.open('x') as stream:
        stream.write(payload)
    # Owner-requested immutable audit: retain every pre-existing receipt.
    import os
    if os.environ.get('HS_VALIDATION_ARCHIVE_ONLY')=='1':return report
    path=folder/'validation.json';temp=folder/('.validation-'+run_id+'.tmp')
    try:
        with temp.open('x') as stream:
            stream.write(payload)
        temp.replace(path)
    finally:
        if temp.exists():
            temp.unlink()
    return report
