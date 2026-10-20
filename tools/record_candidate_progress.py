"""Record derived candidate progress only when its local rule suite is current.

No simulation or training is executed. Original overlay code remains untouched.
"""
import argparse
import json
from pathlib import Path
import sys



def milestone_status(added,target,missing):
    """Card-count progress never implies semantic or release readiness."""
    if any(type(value) is not int or value<0 for value in (added,target,missing)):
        raise ValueError('Progress counts must be nonnegative integers')
    remaining=max(0,target-added)
    next_work=['Review candidate semantics and interactions against independent evidence.']
    if remaining:next_work.append(f'Implement the remaining {remaining} milestone additions and dependencies.')
    next_work.extend([f'Implement the full Standard remainder: {missing} card effects and generated dependencies.',
                      'Validate shared interactions, full-class learning and reproducibility before release.'])
    return dict(remaining_in_milestone=remaining,implementation_target_reached=remaining==0,
                remaining_standard_cards=missing,release_ready=False,milestone_complete=False,
                stage=(f'{added} additional candidate cards; implementation target reached, semantic review remains'
                       if not remaining else f'{added} additional candidate cards; semantic review and {remaining} additions remain'),
                next_work=next_work)


def record(root,candidate):
    sys.path.insert(0,str(candidate))
    from expanded.cards import COLLECTIBLE_IDS,registry,TOKEN_IDS,RULES
    from expanded.status import code_fingerprint
    records=registry()  # Check the pinned metadata hashes too.
    index=json.loads((candidate/'expanded/implementation_index.json').read_text())
    ids=set(index['implemented_card_ids'])
    if ids!=COLLECTIBLE_IDS or len(ids)!=index['effect_implementations_written']:
        raise ValueError('Candidate registry/index mismatch')
    receipt=json.loads((candidate/'runs/expanded_validation/validation.json').read_text())
    if not receipt['success'] or receipt['fingerprint']!=code_fingerprint():
        raise ValueError('Candidate needs a passing rule-suite receipt for current source')
    active=set(json.loads((root/'expanded/implementation_index.json').read_text())['implemented_card_ids'])
    catalog={c['id'] for c in json.loads((root/'data/standard/cards.json').read_text())}
    if not active<=ids<=catalog:raise ValueError('Invalid active/candidate/catalog relationship')
    historical=set(index.get('generated_historical_card_ids',()))
    if (len(historical)!=index.get('generated_historical_effects_written',0)
            or historical&catalog or not historical<=set(records)&TOKEN_IDS&set(RULES)):
        raise ValueError('Invalid separate historical dependency inventory')
    # Keep the required historical outcome backlog separate from the three
    # remaining Standard registrations in every generated progress summary.
    import importlib.util
    spec=importlib.util.spec_from_file_location('_progress_amber_audit',root/'tools/audit_amber_remainder.py')
    audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)
    historical_audit=audit.report(candidate)
    historical_scope={key:historical_audit[key] for key in ('eligible_minions','written_minions','unwritten_minions','eligibility_independently_certified')}
    added=ids-active
    path=root/'staging/standard-200/progress.json';progress=json.loads(path.read_text())
    progress.update(milestone_status(len(added),progress['target_additional_cards'],len(catalog-ids)))
    remaining=progress['remaining_in_milestone']
    progress.update(staged_cards=sorted(added),active_engine_cards=len(active),
                    staged_overlay_cards=len(ids),baseline_cards=len(active),
                    runtime_checks=f"{receipt['tests_run']} candidate checks passed")
    progress['generated_historical_effects_written']=len(historical)
    progress['required_historical_minion_outcomes']=historical_scope
    public_receipt=dict(receipt)
    if public_receipt.get('report_path'):
        report_path=Path(public_receipt['report_path'])
        if report_path.is_absolute():
            try:
                relative_report=report_path.relative_to(root)
            except ValueError:
                # A workspace rename preserves the immutable receipt and archive.
                # Accept the relocated archive only if its exact receipt matches.
                relocated=candidate/'runs/expanded_validation'/report_path.name
                if not relocated.is_file() or json.loads(relocated.read_text())!=receipt:
                    raise ValueError('Validation archive is outside this project')
                relative_report=relocated.relative_to(root)
            public_receipt['report_path']=str(relative_report)
    progress['rebased_candidate']=dict(path=str(candidate.relative_to(root)),version=index['engine'],validation=public_receipt,active=False)
    path.write_text(json.dumps(progress,indent=2)+'\n')
    text=f'''# Current candidate status

Generated by `tools/record_candidate_progress.py`. Counts describe written implementations, not full game fidelity.

- Active notebook: {len(active)} collectible cards.
- Candidate: {len(ids)} collectible cards ({len(added)} additional).
- Pinned catalog: {len(catalog)} collectible cards; {len(catalog-ids)} still lack candidate implementations.
- Generated historical dependencies: {len(historical)} explicit bodies, excluded from Standard decks; historical generation membership remains unfinished.
- Broad historical minion pool: {historical_scope['written_minions']} of {historical_scope['eligible_minions']} explicit bindings; {historical_scope['unwritten_minions']} outcomes remain unwritten under the candidate pool policy. Recursive behavior closure is unverified.
- Remaining cards in the original count milestone: {remaining}; this historical target does not mean full Standard completion.
- Current rule regression suite: {receipt['tests_run']} passed; fingerprint `{receipt['fingerprint']}`.
- Regression scope: {receipt.get('scope','Targeted engine fixtures only').rstrip('.')}.
- Full Standard certification: incomplete.
- Candidate integrated into active notebook 08: no. Candidate notebooks 09–12 use the isolated candidate.

Next gates: semantic review, generated dependency closure, interaction validation, remaining cards, full-class policy and deck search, reproducibility. No training is started by this command.
'''
    (candidate/'STATUS.md').write_text(text)
    print(json.dumps(dict(candidate_cards=len(ids),additional_cards=len(added),remaining_in_milestone=remaining,tests_passed=receipt['tests_run'])))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--candidate',default='staging/rebased-88')
    args=p.parse_args();root=Path(__file__).resolve().parents[1]
    record(root,(root/args.candidate).resolve())
