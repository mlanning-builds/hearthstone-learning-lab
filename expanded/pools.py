"""Explicit candidate-pool contracts. No text parsing or supported-only fallback.

A caller must supply reviewed membership and exclusions for its particular
card/patch. This module cannot infer Standard Discover eligibility from class
or collectible flags alone. Copies from a deck are not generation pools.
"""
from dataclasses import dataclass
from engine.cards import UnsupportedCard


@dataclass(frozen=True)
class GenerationPool:
    name: str
    card_ids: tuple
    source: str

    def __post_init__(self):
        if not self.name or not self.source:
            raise ValueError('A pool requires a name and membership provenance')
        if not isinstance(self.card_ids,tuple) or any(not isinstance(cid,str) or not cid for cid in self.card_ids):
            raise ValueError('Pool IDs must be a tuple of nonempty strings')
        if len(set(self.card_ids)) != len(self.card_ids):
            raise ValueError('Unique-card pools cannot contain duplicate IDs')

    def resolve(self, metadata, implemented, selector=None, exclude=()):
        excluded=set(exclude)
        # Validate membership against the complete supplied snapshot first.
        missing_metadata=sorted(set(self.card_ids)-metadata.keys())
        if missing_metadata:
            raise UnsupportedCard(self.name+': missing card data: '+', '.join(missing_metadata))
        candidates=tuple(cid for cid in self.card_ids if cid not in excluded and
                         (selector is None or selector.matches(metadata[cid])))
        unsupported=sorted(set(candidates)-set(implemented))
        if unsupported:
            raise UnsupportedCard(self.name+': eligible effects not implemented: '+', '.join(unsupported))
        return candidates

    def sample(self, metadata, implemented, rng, count=1, selector=None, exclude=()):
        if type(count) is not int or count<0:raise ValueError('Invalid sample count')
        candidates=self.resolve(metadata,implemented,selector,exclude)
        # Validation happens before RNG use, even for a zero-sized request.
        return rng.sample(list(candidates),min(count,len(candidates)))


def deck_choice_options(deck, metadata, count, rng):
    """Unique identities from the actual deck, retaining a physical index.

    This preserves existing Tracking selection semantics. It does not generate
    a card or substitute a global card pool for the player's deck.
    """
    if type(count) is not int or count<0:raise ValueError('Invalid choice count')
    representatives={}
    for index,value in enumerate(deck):
        cid=value.card_id if hasattr(value,'card_id') else value
        if cid not in metadata:raise UnsupportedCard('Deck choice missing card data: '+str(cid))
        representatives.setdefault(cid,index)
    sample=rng.sample(list(representatives),min(count,len(representatives)))
    return [dict(card_id=cid,index=representatives[cid]) for cid in sample]


def require_fixed_cards(card_ids, registry):
    """Validate explicit generated dependencies before any partial mutation."""
    missing=sorted(set(card_ids)-registry.keys())
    if missing:raise UnsupportedCard('Generated dependencies not implemented: '+', '.join(missing))
