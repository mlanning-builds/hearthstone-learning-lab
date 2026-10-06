"""Reconstruct the frozen catalog selection; no downloads or legality certification."""
from datetime import date
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]

def audit_selection(records,catalog,rules):
    cutoff=date.fromisoformat(rules['as_of'])
    exceptions={cid for cid,rule in rules['included_exceptions'].items()
                if date.fromisoformat(rule['available_from'])<=cutoff}
    future={cid for cid,release in rules['excluded_future_cards'].items()
            if date.fromisoformat(release)>cutoff}
    expired_exclusions=sorted(set(rules['excluded_future_cards'])-future)
    expected={c['id']:c for c in records if c.get('collectible') and
              (c.get('set') in rules['included_sets'] or c['id'] in exceptions) and
              c['id'] not in future and c['id'] not in rules['banned_ids']}
    actual={c['id']:c for c in catalog}
    missing=sorted(set(expected)-set(actual));extra=sorted(set(actual)-set(expected))
    changed=sorted(cid for cid in set(expected)&set(actual) if expected[cid]!=actual[cid])
    duplicate_ids=len(actual)!=len(catalog)
    return dict(as_of=rules['as_of'],expected_count=len(expected),catalog_count=len(catalog),
                missing=missing,extra=extra,changed_records=changed,duplicate_ids=duplicate_ids,
                expired_exclusions=expired_exclusions,
                selection_consistent=not(missing or extra or changed or duplicate_ids or expired_exclusions),
                legality_certified=False,
                scope='Internal selection consistency only. Source set membership, bans, release rules and exceptional deck construction require independent verification.')

def main():
    sys.path.insert(0,str(ROOT))
    from standard.catalog import load_catalog,load_all_records,verify_data
    manifest=verify_data();rules=json.loads((ROOT/'data/standard/release_rules.json').read_text())
    report=audit_selection(load_all_records(),load_catalog(),rules)
    report['patch']=manifest['patch'];report['manifest_date_matches_rules']=manifest['as_of']==rules['as_of']
    report['selection_consistent'] &= report['manifest_date_matches_rules']
    path=ROOT/'docs/engine-audit/catalog-selection.json'
    path.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))
    return int(not report['selection_consistent'])

if __name__=='__main__':raise SystemExit(main())
