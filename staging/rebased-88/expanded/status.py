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


def run_rule_fixtures(progress=None):
    """Run explicitly from a notebook or validation command; never at import."""
    import unittest
    import uuid
    from datetime import datetime,timezone
    start_fingerprint=code_fingerprint()
    discovered=unittest.defaultTestLoader.discover(str(ROOT/'tests'),pattern='test_expanded*.py')
    excluded_modules={'test_expanded_training','test_expanded_learning_core'}
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
    result=unittest.TextTestRunner(verbosity=2,resultclass=ProgressResult).run(suite)
    end_fingerprint=code_fingerprint()
    unchanged=start_fingerprint==end_fingerprint
    report=dict(fingerprint=start_fingerprint,end_fingerprint=end_fingerprint,
                source_unchanged=unchanged,fixture_success=result.wasSuccessful(),
                success=result.wasSuccessful() and unchanged,tests_run=result.testsRun,
                failures=len(result.failures),errors=len(result.errors),skipped=len(result.skipped),
                completed_at=datetime.now(timezone.utc).isoformat(),
                excluded_modules=sorted(excluded_modules),
                scope='Non-training engine fixtures only; learning integration and policy-update scenarios excluded. Not full Standard certification.')
    folder=ROOT/'runs/expanded_validation';folder.mkdir(parents=True,exist_ok=True)
    run_id=uuid.uuid4().hex
    report['run_id']=run_id
    archive=folder/('validation-'+run_id+'.json')
    report['report_path']=str(archive)
    payload=json.dumps(report,indent=2)+'\n'
    with archive.open('x') as stream:
        stream.write(payload)
    path=folder/'validation.json';temp=folder/('.validation-'+run_id+'.tmp')
    try:
        with temp.open('x') as stream:
            stream.write(payload)
        temp.replace(path)
    finally:
        if temp.exists():
            temp.unlink()
    return report
