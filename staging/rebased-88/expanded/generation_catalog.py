"""Full pinned Standard generation membership, independent of written coverage.

Membership never uses the playable registry. Past-era and exceptional named
families retain separate contracts. Missing executable outcomes fail closed.
"""
from dataclasses import dataclass,field
from functools import lru_cache
from types import MappingProxyType
import hashlib,json
from standard.catalog import DATA,CLASSES
from .generation import request_matches
from .pools import GenerationPool

def _freeze(value):
    if isinstance(value,dict):return MappingProxyType({k:_freeze(v) for k,v in value.items()})
    if isinstance(value,list):return tuple(_freeze(v) for v in value)
    return value

@dataclass(frozen=True)
class StandardUniverse:
    digest:str
    records:object=field(compare=False,hash=False,repr=False)
    def __deepcopy__(self,memo):return self  # Recursively immutable metadata.

@lru_cache(maxsize=2)
def _verified_universe(snapshot,manifest_snapshot):
    manifest=json.loads(manifest_snapshot);digest=hashlib.sha256(snapshot).hexdigest()
    if digest!=manifest['files_sha256']['cards.json']:raise ValueError('Frozen generation catalog changed')
    records=json.loads(snapshot)
    if len(records)!=manifest['standard_catalog_count'] or len({c['id'] for c in records})!=len(records):
        raise ValueError('Invalid frozen generation catalog count or identities')
    for c in records:
        values=c.get('classes') or [c.get('cardClass')]
        if any(k not in CLASSES+('NEUTRAL',) for k in values):raise ValueError('Invalid generation class: '+c['id'])
    return StandardUniverse(digest,_freeze({c['id']:c for c in records}))

def load_universe():
    return _verified_universe((DATA/'cards.json').read_bytes(),(DATA/'manifest.json').read_bytes())

@lru_cache(maxsize=512)
def standard_contract(request,hero_class,universe):
    if request.era or request.family:return None
    ids=tuple(sorted(cid for cid,c in universe.records.items() if request_matches(request,c,hero_class)))
    return GenerationPool('pinned Standard generation',ids,
        'Complete patch 36.6.0.251952 catalog; Fabled, regular Quest, triple-Rune and request-specific exclusions; playable registry is not a membership input')
