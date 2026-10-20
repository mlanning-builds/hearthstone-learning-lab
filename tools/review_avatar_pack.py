"""Resolve reviewed acquisition exceptions without inventing Avatar pack odds."""
import gzip,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]


def record_hash(record):return hashlib.sha256(json.dumps(record,sort_keys=True).encode()).hexdigest()


def resolve(candidates,review,metadata):
    expected={row['id'] for row in candidates['special_acquisition_requires_review']}
    rows=review['cards'];seen=set();excluded=[];restrictions={}
    for row in rows:
        cid=row['id']
        if cid not in expected or cid in seen:raise ValueError('Unexpected or duplicate acquisition review: '+cid)
        seen.add(cid)
        if not row.get('source') or row.get('record_sha256')!=record_hash(metadata[cid]):
            raise ValueError('Unbound acquisition evidence: '+cid)
        qualities=row.get('pack_qualities')
        if not isinstance(qualities,list) or len(qualities)!=len(set(qualities)) or not set(qualities)<={'REGULAR','GOLDEN','SIGNATURE','DIAMOND'}:
            raise ValueError('Invalid pack qualities: '+cid)
        if not qualities:excluded.append(cid)
        else:restrictions[cid]=qualities
    if seen!=expected:raise ValueError('Incomplete acquisition review: '+str(sorted(expected-seen)))
    remaining=sorted(set(candidates['set_filtered_candidate_ids'])-set(excluded))
    return dict(acquisition_cases_reviewed=len(seen),excluded_special_ids=sorted(excluded),
                special_quality_restrictions=restrictions,identity_candidate_count=len(remaining),identity_candidate_ids=remaining,
                runtime_activated=False,distribution_established=False,full_support_certified=False,
                limitations=['Special-acquisition exceptions are reviewed; other membership and release eligibility remain subject to pinned-patch conformance.','Identity eligibility does not establish rarity/quality weights or ordered joint pack distribution.','Ysera Golden-only acquisition must not be collapsed into a blanket free-card exclusion.'])


def main():
    candidates=json.loads((ROOT/'docs/engine-audit/avatar-pack-candidates.json').read_text())
    review=json.loads((ROOT/'data/review/avatar-pack-acquisition.json').read_text())
    snapshot=ROOT/'staging/rebased-88/data/standard/all_cards.json.gz'
    with gzip.open(snapshot,'rt') as stream:metadata={r['id']:r for r in json.load(stream)}
    report=resolve(candidates,review,metadata)
    report.update(patch=review['patch'],observed_on=review['observed_on'],sources=[r['source'] for r in review['cards']],
                  snapshot_sha256=hashlib.sha256(snapshot.read_bytes()).hexdigest())
    (ROOT/'docs/engine-audit/avatar-pack-acquisition-review.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ('identity_candidate_ids','sources')}))


if __name__=='__main__':main()
