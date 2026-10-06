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
    current=code_fingerprint()
    fixtures_passed=bool(receipt and receipt.get('fingerprint')==current and receipt.get('success'))
    return dict(engine=index['engine'],catalog_cards=len(catalog),effects_written=len(ids),missing_cards=missing,
                base_hero_powers_written=index['base_hero_power_classes'],
                fixtures_passed_for_current_code=fixtures_passed,fixture_receipt=receipt,
                full_standard_ready=False,
                remaining=['Implement '+str(len(missing))+' remaining card effects and all required interaction systems.',
                           'Validate complete game behavior against an independent reference.',
                           'Verify live legality, exceptional deck construction, and generated-card pools.',
                           'Connect an all-card, all-class learning policy; the old model is subset-specific.'],
                fingerprint=current)


def require_full_standard():
    state=readiness()
    raise RuntimeError('Full Standard is not ready: '+str(len(state['missing_cards']))+' card effects remain, plus interaction validation and the expanded training interface. The experimental Game is available only for explicitly implemented decks.')


def run_rule_fixtures(progress=None):
    """Called only by the user-run notebook. No automatic execution at import."""
    import unittest
    from datetime import datetime,timezone
    suite=unittest.defaultTestLoader.discover(str(ROOT/'tests'),pattern='test_expanded*.py')
    total=suite.countTestCases()
    class ProgressResult(unittest.TextTestResult):
        def stopTest(self,test):
            super().stopTest(test)
            if progress:
                progress(self.testsRun,total,len(self.failures),len(self.errors))
    result=unittest.TextTestRunner(verbosity=2,resultclass=ProgressResult).run(suite)
    report=dict(fingerprint=code_fingerprint(),success=result.wasSuccessful(),tests_run=result.testsRun,
                failures=len(result.failures),errors=len(result.errors),skipped=len(result.skipped),
                completed_at=datetime.now(timezone.utc).isoformat(),
                scope='Targeted engine fixtures only; not full Standard certification or training.')
    folder=ROOT/'runs/expanded_validation';folder.mkdir(parents=True,exist_ok=True)
    path=folder/'validation.json';temp=path.with_suffix('.tmp');temp.write_text(json.dumps(report,indent=2)+'\n');temp.replace(path)
    return report
