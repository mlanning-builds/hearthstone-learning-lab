"""Frozen identity aliases, separate from executable rules and eligible pools."""
from functools import lru_cache
import hashlib
import json
from pathlib import Path
from engine.cards import UnsupportedCard


@lru_cache(maxsize=1)
def core_aliases():
    from standard.catalog import load_all_records
    records = {d['id']: d for d in load_all_records()}
    manifest = json.loads(Path(__file__).with_name('core_identities.json').read_text())
    aliases = {}
    for pair in manifest['pairs']:
        for label in ('core', 'original'):
            record = records[pair[label]]
            digest = hashlib.sha256(json.dumps(record, sort_keys=True).encode()).hexdigest()
            if digest != pair[label + '_sha'] or record['dbfId'] != pair[label + '_dbf']:
                raise UnsupportedCard('Frozen identity record changed: ' + pair[label])
        if pair['core_dbf'] in aliases:
            raise UnsupportedCard('Duplicate frozen Core identity')
        aliases[pair['core_dbf']] = pair['original_dbf']
    return aliases


def identity_resolver(metadata):
    """Snapshot the lookup once when grouping a pool or validating a deck."""
    by_dbf = {d['dbfId']: d for d in metadata.values() if 'dbfId' in d}
    aliases = core_aliases()
    return lambda data: _resolve(data, by_dbf, aliases)


def canonical_identity(data, metadata):
    """Resolve explicit copy tags and reviewed Core pairs, never printed names.

    Synthetic explicit tags remain usable in controlled fixtures. Resolving a
    relationship does not admit the related record or approve any pool.
    """
    aliases = core_aliases()
    if data.get('countAsCopyOfDbfId') is None and data.get('dbfId') not in aliases:
        return data.get('dbfId', data['id'])
    by_dbf = {d['dbfId']: d for d in metadata.values() if 'dbfId' in d}
    return _resolve(data, by_dbf, aliases)


def _resolve(data, by_dbf, aliases):
    value = data.get('dbfId', data['id'])
    explicit = data.get('countAsCopyOfDbfId')
    if explicit is not None:
        value = explicit
    seen = {data.get('dbfId', data['id'])} if explicit is not None else set()
    while True:
        if value in seen:
            raise UnsupportedCard('Cyclic canonical card identity')
        seen.add(value)
        record = by_dbf.get(value, {})
        following = record.get('countAsCopyOfDbfId')
        if following is None:
            following = aliases.get(value)
        if following is None:
            return value
        value = following
