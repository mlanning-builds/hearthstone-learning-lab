"""Compare a live pool observation with pinned metadata; never admit a pool."""
import gzip
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def compare(observation,metadata,standard_ids):
    if observation.get('approved_for_runtime') is not False:
        raise ValueError('Observation must explicitly prohibit runtime activation')
    rows=[]
    for title in observation['visible_candidates']:
        core=title.endswith(' (Core)')
        name=title[:-7] if core else title
        matches=[r for r in metadata if r.get('name')==name and r.get('type')=='MINION'
                 and bool(r.get('id','').startswith('CORE_'))==core and r.get('collectible')]
        rows.append(dict(observed_title=title,pinned_matches=[r['id'] for r in matches],
                         pinned_standard_matches=[r['id'] for r in matches if r['id'] in standard_ids],
                         resolved_unambiguously=len(matches)==1))
    return dict(rows=rows,unmapped_titles=[r['observed_title'] for r in rows if not r['pinned_matches']],
                ambiguous_titles=[r['observed_title'] for r in rows if len(r['pinned_matches'])>1],
                runtime_activated=False,stage_membership_established=False,full_support_certified=False,
                limitation='Live combined query is not a pinned first/second-stage pool; no text/keyword heuristic or supported-only filter is applied.')


def main():
    source=ROOT/'data/review/storm-pool-observation.json'
    snapshot=ROOT/'staging/rebased-88/data/standard/all_cards.json.gz'
    with gzip.open(snapshot,'rt') as stream:metadata=json.load(stream)
    standard={r['id'] for r in json.loads((ROOT/'data/standard/cards.json').read_text())}
    observation=json.loads(source.read_text());report=compare(observation,metadata,standard)
    report.update(source=observation['source'],observed_on=observation['observed_on'],
                  observation_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                  metadata_sha256=hashlib.sha256(snapshot.read_bytes()).hexdigest())
    (ROOT/'docs/engine-audit/storm-pool-observation-coverage.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='rows'}))


if __name__=='__main__':main()
