"""Complete pinned past membership, independent of executable coverage.

Policy: retired regular Constructed sets explicitly enumerated in PAST_SETS,
collectible records, valid hero/neutral classes, canonical Standard identities
excluded, unique canonical identities, and the source's printed selectors.
This is an explicit candidate policy, not independent client certification.
"""
from dataclasses import dataclass,field
from functools import lru_cache
import gzip,hashlib,json
from standard.catalog import DATA,CLASSES
from .generation_catalog import _freeze
from .generation import request_matches
from .pools import GenerationPool
from .identities import identity_resolver

@dataclass(frozen=True)
class HistoricalUniverse:
 digest:str
 records:object=field(compare=False,hash=False,repr=False)
 members:tuple
 def __deepcopy__(self,memo):return self

@lru_cache(maxsize=2)
def _verified_universe(archive,catalog,manifest_bytes):
 manifest=json.loads(manifest_bytes)
 for name,value in (('all_cards.json.gz',archive),('cards.json',catalog)):
  if hashlib.sha256(value).hexdigest()!=manifest['files_sha256'][name]:
   raise ValueError('Frozen historical catalog changed: '+name)
 records=json.loads(gzip.decompress(archive))
 if len(records)!=manifest['all_record_count'] or len({d['id'] for d in records})!=len(records):
  raise ValueError('Invalid frozen historical archive')
 metadata={d['id']:d for d in records}
 canonical=identity_resolver(metadata)
 standard={canonical(d) for d in json.loads(catalog)}
 from .historical_generation import PAST_SETS
 representatives={}
 for cid in sorted(metadata):
  d=metadata[cid]
  classes=d.get('classes') or (d.get('cardClass'),)
  if (not d.get('collectible') or d.get('set') not in PAST_SETS or
      d.get('type') not in ('MINION','SPELL','WEAPON','HERO','LOCATION') or
      not classes or any(k not in CLASSES+('NEUTRAL',) for k in classes)):
   continue
  identity=canonical(d)
  if identity not in standard:representatives.setdefault(identity,cid)
 return HistoricalUniverse(hashlib.sha256(archive).hexdigest(),_freeze(metadata),
                           tuple(sorted(representatives.values())))

def load_universe():
 return _verified_universe((DATA/'all_cards.json.gz').read_bytes(),
                          (DATA/'cards.json').read_bytes(),(DATA/'manifest.json').read_bytes())

@lru_cache(maxsize=2048)
def historical_contract(request,hero_class,universe):
 if request.era!='past' or request.family:return None
 ids=tuple(cid for cid in universe.members if request_matches(request,universe.records[cid],hero_class))
 return GenerationPool('pinned historical generation',ids,
  'Complete frozen archive; explicit retired Constructed sets, collectible records, canonical Standard exclusion and printed selector; no implemented-card filtering')
