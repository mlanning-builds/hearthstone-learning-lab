"""Private physical ancestry for copies; never match originals by name alone.

This is infrastructure only. Harvester event/zone consumers remain unwritten.
UIDs identify physical entities within a game; replayed/resurrected cards receive
new identities. Ordinary same-identity zone movement preserves ancestry.
"""
_FIELDS = ('_historical_entity_lineage', '_historical_copy_source')


def carry(source, target, *, copied=False, source_owner=None):
    if target is None or source is target:
        return
    source_id = getattr(source, 'card_id', None)
    same_identity = source_id is not None and source_id == getattr(target, 'card_id', None)
    lineage = getattr(source, '_historical_entity_lineage', None)
    copy_source = getattr(source, '_historical_copy_source', None)
    for field in _FIELDS:
        if hasattr(target, field):
            delattr(target, field)
    if not same_identity:
        return
    if not copied:
        if lineage is not None:
            target._historical_entity_lineage = lineage
        if copy_source is not None:
            target._historical_copy_source = copy_source
        return
    source_uid = getattr(source, 'uid', None)
    target_uid = getattr(target, 'uid', None)
    if source_uid is None or target_uid is None or source_uid == target_uid:
        return
    if lineage is None:
        lineage = source_uid
        source._historical_entity_lineage = lineage
    target._historical_entity_lineage = target_uid
    if source_owner in (0, 1):
        target._historical_copy_source = (source_owner, lineage, source_id)
    elif copy_source is not None:
        target._historical_copy_source = copy_source


def matches_original(entity, reference):
    """Identity changes break the link even if a physical UID survives."""
    if not isinstance(reference, tuple) or len(reference) != 3:
        return False
    _, lineage, card_id = reference
    return (getattr(entity, 'card_id', None) == card_id
            and getattr(entity, '_historical_entity_lineage', None) == lineage)
