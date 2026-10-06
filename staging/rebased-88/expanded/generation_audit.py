"""Conservative dependency planning, never a runtime eligibility oracle.

Run with python -m expanded.generation_audit --output PATH. No matches, training,
network requests, or registration changes occur. The snapshot is hash-verified.
"""
from collections import Counter
from dataclasses import asdict
import argparse
import hashlib
import json
from pathlib import Path
from .generation import request_matches
from .generation_cards import RULES, requests_for
from .selectors import classes, HERO_CLASSES


def build_report(catalog, implemented, card_ids=None):
    metadata = {card['id']: card for card in catalog}
    implemented = set(implemented)
    impact = Counter()
    rows = []
    from . import generation_extensions as extensions
    selected=set(RULES) if card_ids is None else set(card_ids)
    for cid in sorted(selected):
        card = metadata[cid]
        owners = sorted(HERO_CLASSES) if card_ids is not None else sorted((classes(card) & HERO_CLASSES) or HERO_CLASSES)
        contexts = []
        card_missing = set()
        for owner in owners:
            for request in sorted(requests_for(cid) | extensions.requests_for(cid), key=repr):
                ids = sorted(k for k, value in metadata.items() if request_matches(request, value, owner))
                missing = sorted(set(ids) - implemented)
                card_missing.update(missing)
                contexts.append(dict(hero_class=owner, request=asdict(request),
                                     candidate_ids=ids, missing_ids=missing,
                                     membership_reviewed=False))
        impact.update(card_missing)
        rows.append(dict(card_id=cid, name=card['name'],
                         record_sha256=hashlib.sha256(json.dumps(card, sort_keys=True).encode()).hexdigest(),
                         status='live_registered' if cid in implemented else 'staged_not_playable',
                         engine_body_written=cid in RULES or cid in extensions.RULES,
                         dynamic_pool_review_required=cid in {'CATA_EVENT_400','CORE_BOT_256','CORE_CATA_006','CORE_WW_374'},
                         historical_pool_review_required=cid=='CATA_EVENT_000',
                         pool_contexts=contexts,
                         missing_candidate_count=len(card_missing), missing_candidate_ids=sorted(card_missing)))
    return dict(schema=1, scope='Pinned regular Standard catalog only; no Mercenaries/Battlegrounds',
                staged_cards=len(rows), newly_playable_cards=0,
                catalog_cards=len(metadata), playable_catalog_cards=len(set(metadata) & implemented),
                membership_reviewed=False,
                limitation='Metadata matches are conservative planning candidates, NOT approved generation pools. Self-generation exclusions, canonical copies, special eligibility and per-class rules still require review. A zero missing count does not authorize registration.',
                cards=rows,
                blockers_by_affected_generators=[dict(card_id=cid, name=metadata[cid]['name'], affected_generators=count)
                                                for cid, count in sorted(impact.items(), key=lambda item: (-item[1], item[0]))])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--batch-ledger',type=Path)
    args = parser.parse_args()
    from standard.catalog import load_catalog
    from .cards import COLLECTIBLE_IDS
    selected=None
    if args.batch_ledger:selected=[r['card_id'] for r in json.loads(args.batch_ledger.read_text())['cards']]
    report = build_report(load_catalog(), COLLECTIBLE_IDS,selected)
    if selected:
        report['batch_cards']=len(selected)
        report['batch_live_registered']=len(set(selected)&COLLECTIBLE_IDS)
        report['newly_playable_cards']=report['batch_live_registered']
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({k: report[k] for k in ('staged_cards', 'newly_playable_cards', 'playable_catalog_cards')}))


if __name__ == '__main__':
    main()
