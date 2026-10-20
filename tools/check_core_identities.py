"""Verify the explicit frozen alias ledger without building pools or playing games."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

FIELDS=('name','type','cardClass','classes','cost','attack','health','durability','mechanics','spellSchool','races','runeCost')
NON_ALIAS_COLLISIONS={'CORE_EDR_001':'EDR_001'}  # Bookcase and Dryad are different cards.


def record_hash(record):
    return hashlib.sha256(json.dumps(record,sort_keys=True).encode()).hexdigest()


def verify(manifest,records,catalog_ids):
    seen=set();database_ids=set()
    for pair in manifest['pairs']:
        cid=pair['core'];original=pair['original']
        if cid in seen or pair['core_dbf'] in database_ids:
            raise ValueError('Duplicate Core alias entry: '+cid)
        seen.add(cid);database_ids.add(pair['core_dbf'])
        if cid not in catalog_ids or cid.upper()!='CORE_'+original:
            raise ValueError('Alias must name its exact Standard Core original: '+cid)
        a,b=records[cid],records[original]
        if a.get('set')!='CORE' or not a.get('collectible') or not b.get('collectible'):
            raise ValueError('Alias records must be collectible Core and original cards: '+cid)
        for label,data in (('core',a),('original',b)):
            if pair[label+'_sha']!=record_hash(data) or pair[label+'_dbf']!=data['dbfId']:
                raise ValueError('Frozen alias hash/database mismatch: '+pair[label])
        for field in FIELDS:
            if a.get(field)!=b.get(field):raise ValueError('Alias gameplay field differs: '+cid+' '+field)
        # Formatting differences in serialized bold tags are not effect changes.
        if re.sub('<[^>]+>','',a.get('text',''))!=re.sub('<[^>]+>','',b.get('text','')):
            raise ValueError('Alias printed effect differs: '+cid)
    for cid,other in NON_ALIAS_COLLISIONS.items():
        if cid in catalog_ids and records[cid]['name']==records[other]['name']:
            raise ValueError('Re-review distinct ID collision: '+cid)
    expected={cid for cid in catalog_ids if cid.upper().startswith('CORE_') and cid[5:] in records
              and cid not in NON_ALIAS_COLLISIONS}
    if seen!=expected:
        raise ValueError('Explicit alias ledger is incomplete or unexpected: '+repr(sorted(seen^expected)))
    unpaired=sorted(cid for cid in catalog_ids if cid.upper().startswith('CORE_') and cid not in seen)
    tagged=[cid for cid in unpaired if records[cid].get('countAsCopyOfDbfId') is not None]
    return dict(verified_pairs=len(seen),explicit_tagged_unpaired=tagged,
                no_original_id=[cid for cid in unpaired if cid not in tagged and cid not in NON_ALIAS_COLLISIONS],
                distinct_id_collisions=[cid for cid in unpaired if cid in NON_ALIAS_COLLISIONS],
                pool_membership_approved=False)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--engine-root',type=Path,default=Path(__file__).resolve().parents[1]/'staging/rebased-88')
    args=parser.parse_args();root=args.engine_root.resolve();sys.path.insert(0,str(root))
    from standard.catalog import load_all_records,load_catalog
    records={d['id']:d for d in load_all_records()}
    manifest=json.loads((root/'expanded/core_identities.json').read_text())
    print(json.dumps(verify(manifest,records,{d['id'] for d in load_catalog()})))


if __name__=='__main__':main()
