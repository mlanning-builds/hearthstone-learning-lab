"""Report the actual Amber Warden generation contract, without executing games."""
import argparse,json,sys
from pathlib import Path

def report(engine_root):
 sys.path.insert(0,str(engine_root.resolve()))
 from expanded.historical_generation import requests_for
 from expanded.historical_generation_catalog import load_universe,historical_contract
 from expanded.cards import registry,RULES
 from expanded.status import code_fingerprint
 from standard.catalog import CLASSES
 universe=load_universe();request,=requests_for('TIME_052')
 contracts=[historical_contract(request,hero_class,universe) for hero_class in CLASSES]
 contract=contracts[0]
 if any(value.card_ids!=contract.card_ids for value in contracts):
  raise ValueError('Amber Warden must have the same any-class pool for all eleven classes')
 written=set(registry())&set(RULES)
 missing=sorted(set(contract.card_ids)-written)
 return dict(scope='Actual normalized pinned TIME_052 request; explicit bindings counted, semantic and recursive closure unverified.',
  candidate_fingerprint=code_fingerprint(),request=repr(request),classes_checked=list(CLASSES),scope_classes='all 11 classes',eligible_minions=len(contract.card_ids),
  written_minions=len(set(contract.card_ids)&written),unwritten_minions=len(missing),
  excluded_mechanics=['COLOSSAL','TITAN'],eligibility_independently_certified=False,
  sources=['https://hearthstone.blizzard.com/en-us/blog/24245106/','https://hearthstone.blizzard.com/en-gb/expansions-adventures/titans'],
  cards=[dict(id=cid,name=universe.records[cid]['name'],text=universe.records[cid].get('text',''),mechanics=universe.records[cid].get('mechanics',[]),card_set=universe.records[cid].get('set')) for cid in missing])
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--engine-root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 result=report(a.engine_root);a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='cards'}))
