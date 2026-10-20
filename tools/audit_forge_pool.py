"""Audit observed forge membership without narrowing or activating runtime pools."""
import argparse
import gzip
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def audit(manifest, metadata, implemented, recipes=()):
    if manifest.get('schema') != 1 or manifest.get('card_id') != 'CATA_470':
        raise ValueError('Unsupported forge manifest')
    if manifest.get('approved_for_runtime') is not False or not manifest.get('source'):
        raise ValueError('Observed manifests require an explicit runtime prohibition and source')
    stages = manifest.get('stages', {})
    if set(stages) != {'dragon', 'undead'}:
        raise ValueError('Expected Dragon and Undead stages')
    for stage, ids in stages.items():
        if not isinstance(ids, list) or not ids or any(not isinstance(cid, str) or not cid for cid in ids):
            raise ValueError('Invalid component identities: ' + stage)
        if len(set(ids)) != len(ids):
            raise ValueError('Duplicate component identities: ' + stage)
    rows = []
    for cid in sorted(set(stages['dragon']) | set(stages['undead'])):
        record = metadata.get(cid)
        if record is None or record.get('type') != 'MINION':
            raise ValueError('Missing minion metadata: ' + cid)
        if any(type(record.get(key)) is not int or record[key] < 0 for key in ('cost', 'attack', 'health')):
            raise ValueError('Invalid component statistics: ' + cid)
        rows.append(dict(card_id=cid, name=record['name'], cost=record['cost'],
                         stages=[stage for stage, ids in stages.items() if cid in ids],
                         standalone_registered=cid in implemented,
                         composite_recipe_declared=cid in recipes,
                         composite_behavior_reviewed=False))
    pairs = [(first, second) for first in stages['dragon'] for second in stages['undead']
             if metadata[first]['cost'] + metadata[second]['cost'] <= 10]
    return dict(card_id=manifest['card_id'], source=manifest['source'],
                stage_counts={stage: len(ids) for stage, ids in stages.items()},
                distinct_components=len(rows), components=rows,
                composite_recipes_declared=sum(row['composite_recipe_declared'] for row in rows),
                missing_standalone_ids=[row['card_id'] for row in rows if not row['standalone_registered']],
                affordable_ordered_pairs=len(pairs),
                first_parts_without_completion=[cid for cid in stages['dragon'] if not any(a == cid for a, b in pairs)],
                full_support_certified=False, runtime_activated=False,
                limitations=manifest['limitations'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, default=ROOT/'data/review/nefarius-components.json')
    parser.add_argument('--output', type=Path, default=ROOT/'docs/engine-audit/nefarius-component-coverage.json')
    args = parser.parse_args()
    sys.path.insert(0, str(ROOT))
    from hearthstone_sim._bootstrap import activate
    activate()
    from expanded.cards import registry
    from expanded.status import code_fingerprint
    fingerprint = code_fingerprint()
    snapshot = ROOT/'staging/rebased-88/data/standard/all_cards.json.gz'
    with gzip.open(snapshot, 'rt') as stream:
        metadata = {card['id']: card for card in json.load(stream)}
    raw = args.manifest.read_bytes()
    from expanded.nefarius_parts import PARTS
    report = audit(json.loads(raw), metadata, registry(), PARTS)
    from expanded.generation import GenerationEffects
    from expanded.generation_cards import PoolRequest
    from expanded.selectors import HERO_CLASSES
    from engine.cards import UnsupportedCard
    from types import SimpleNamespace
    from dataclasses import asdict
    class Probe(GenerationEffects):
        pass
    probe=Probe();probe.cards=registry()
    def requests(value):
        if isinstance(value,PoolRequest):yield value
        elif isinstance(value,(tuple,list)):
            for child in value:yield from requests(child)
    downstream=[]
    for cid,part in sorted(PARTS.items()):
        for request in sorted(set(requests((part.operations,part.death_operations,part.intrinsics))),key=repr):
            for hero_class in sorted(HERO_CLASSES):
                probe.players=[SimpleNamespace(hero_class=hero_class)]
                row=dict(component=cid,hero_class=hero_class,request=asdict(request))
                try:
                    row.update(eligible_registered_outcomes=len(probe._generation_candidates(request,0)),known_membership_checks_passed=True)
                except UnsupportedCard as exc:
                    row.update(known_membership_checks_passed=False,blocker=str(exc))
                downstream.append(row)
    report['downstream_generation']=downstream
    report['downstream_checks_passed']=all(row['known_membership_checks_passed'] for row in downstream)
    report.update(engine_fingerprint=fingerprint, manifest_sha256=hashlib.sha256(raw).hexdigest(),
                  metadata_sha256=hashlib.sha256(snapshot.read_bytes()).hexdigest())
    if code_fingerprint() != fingerprint:
        raise RuntimeError('Engine source changed during audit')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({key: report[key] for key in ('stage_counts', 'distinct_components', 'composite_recipes_declared', 'missing_standalone_ids', 'affordable_ordered_pairs', 'downstream_checks_passed', 'runtime_activated')}))


if __name__ == '__main__':
    main()
