"""Reconcile derived coverage ledgers with the pinned, explicit runtime registry.

This never registers cards, changes effects, approves generation membership or
rewrites reviewed metadata hashes. Default mode detects drift without writing.
"""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys
import uuid


def reconcile(index,audit,live,catalog_ids,historical_ids=None):
    live=set(live);catalog_ids=set(catalog_ids)
    rows=audit['cards'];row_ids=[row['id'] for row in rows]
    if len(row_ids)!=len(set(row_ids)) or set(row_ids)!=catalog_ids:
        raise ValueError('Audit rows must account for every catalog identity exactly once')
    if not live<=catalog_ids:
        raise ValueError('Runtime collectible identities are outside the pinned catalog')
    if index['catalog_size']!=len(catalog_ids) or audit['total']!=len(catalog_ids):
        raise ValueError('Catalog totals disagree; do not repair provenance by changing counts')
    if not set(index.get('provisional_card_ids',()))<=live:
        raise ValueError('Provisional identities must be live registered collectibles')
    new_index=deepcopy(index);new_audit=deepcopy(audit)
    new_index['implemented_card_ids']=sorted(live)
    new_index['effect_implementations_written']=len(live)
    if historical_ids is not None:
        historical_ids=set(historical_ids)
        if historical_ids&catalog_ids:raise ValueError('Generated historical identities must stay outside Standard catalog entries')
        new_index['generated_historical_card_ids']=sorted(historical_ids)
        new_index['generated_historical_effects_written']=len(historical_ids)
    new_audit['written']=len(live);new_audit['missing']=len(catalog_ids-live)
    for row in new_audit['cards']:
        row['implementation']='written_unverified' if row['id'] in live else 'missing'
    return new_index,new_audit


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--engine-root',type=Path,required=True)
    p.add_argument('--write',action='store_true',help='Update the two derived ledgers after validating the registry')
    args=p.parse_args();root=args.engine_root.resolve();sys.path.insert(0,str(root))
    from expanded.cards import registry,COLLECTIBLE_IDS,TOKEN_IDS,RULES
    from standard.catalog import load_catalog
    records=registry()  # Validate every existing reviewed hash first.
    import importlib
    historical_ids=set()
    for name in ('historical_vanilla','historical_simple','historical_numeric'):
        if (root/'expanded'/f'{name}.py').exists():
            historical_ids.update(importlib.import_module('expanded.'+name).GENERATED_IDS)
    if not historical_ids<=set(records)&TOKEN_IDS&set(RULES):
        raise ValueError('Historical inventory requires registered metadata and explicit generated bodies')
    paths=[root/'expanded/implementation_index.json',root/'expanded/catalog_audit.json']
    old=[json.loads(path.read_text()) for path in paths]
    new=reconcile(*old,COLLECTIBLE_IDS,{row['id'] for row in load_catalog()},historical_ids)
    changed=[path for path,before,after in zip(paths,old,new) if before!=after]
    if args.write:
        # Encode both outputs before publishing either derived document.
        encoded=[json.dumps(value,indent=2)+'\n' for value in new]
        for path,value in zip(paths,encoded):
            if path not in changed:continue
            temp=path.with_name(path.name+'.inventory-'+uuid.uuid4().hex+'.tmp')
            try:
                with temp.open('x') as stream:stream.write(value)
                temp.replace(path)
            finally:
                if temp.exists():temp.unlink()
    print(json.dumps(dict(consistent=not changed or args.write,
                          drifted_files=[str(path) for path in changed],
                          live_collectibles=len(COLLECTIBLE_IDS),
                          generated_historical_effects=len(historical_ids),
                          writes_performed=args.write and bool(changed))))
    return int(bool(changed) and not args.write)


if __name__=='__main__':raise SystemExit(main())
