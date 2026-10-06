import sys,json,hashlib,dataclasses
from pathlib import Path
from collections import Counter
import argparse
parser=argparse.ArgumentParser(description='Audit staged definitions without enabling them for play.')
parser.add_argument('--engine-root',type=Path,required=True)
args=parser.parse_args()
r=args.engine_root.resolve();sys.path.insert(0,str(r))
from expanded.pending_definitions import DEFINITIONS,require_integrated
from expanded.cards import COLLECTIBLE_IDS
from standard.catalog import load_catalog
from engine.cards import UnsupportedCard
catalog={c['id']:c for c in load_catalog()};missing=set(catalog)-COLLECTIBLE_IDS
assert set(DEFINITIONS)<=missing, sorted(set(DEFINITIONS)-missing)
for cid,d in DEFINITIONS.items():
 assert d['hooks'] and d['family'] and d['status']=='defined_pending_integration'
 try: require_integrated(cid)
 except UnsupportedCard:pass
 else:raise AssertionError(cid+' allowed execution')
rows=[]
for cid,d in sorted(DEFINITIONS.items()):
 rows.append(dict(card_id=cid,name=catalog[cid]['name'],source_sha256=hashlib.sha256(json.dumps(catalog[cid],sort_keys=True).encode()).hexdigest(),**d))
report=dict(scope='Frozen regular Standard 36.6.0.251952; explicit staged effect definitions, NOT playable support',catalog_size=len(catalog),live_definitions=len(set(catalog)&COLLECTIBLE_IDS),pending_definitions=len(DEFINITIONS),without_any_definition=len(missing-set(DEFINITIONS)),families=dict(Counter(d['family'] for d in DEFINITIONS.values())),remaining_ids=sorted(missing-set(DEFINITIONS)),definitions=rows)
p=r/'../../docs/engine-audit/pending-definitions.json';p.write_text(json.dumps(report,indent=2,default=lambda x:dataclasses.asdict(x) if dataclasses.is_dataclass(x) else str(x))+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ('definitions','remaining_ids')}))
