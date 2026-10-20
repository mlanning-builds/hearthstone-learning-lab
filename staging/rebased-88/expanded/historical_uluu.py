"""Uluu's physical held-card refresh, staged pending complete pool review.

The pair provider must implement the complete frozen format pool and exact
pair-selection policy. No implemented-only fallback or assumed distribution.
This module deliberately does not register GDB_854 in the production registry.
"""
from copy import deepcopy
from engine.cards import UnsupportedCard
from .physical_choices import install
from .effect_schema import validate_table

CARD_ID = 'GDB_854'
# Leo Robles Haub's original FAQ excludes whole self-transforming parents,
# not just their transforming branch. Ancient of Growth transforms other
# minions and is deliberately absent. Canonical comparison covers Core copies.
# https://x.com/mynty_phresh/status/1847706068899729845
EXCLUDED_PARENTS = frozenset((
    'AT_042', 'BRM_010', 'DED_001', 'EX1_165', 'GIL_188',
    'ICC_051', 'SCH_607', 'TRL_343', 'UNG_101', 'ICC_047',
))

def turn_entries(game, phase):
    if phase != 'start':
        return []
    return [dict(source=None, order=card.uid, card_id=CARD_ID,
                 operations=(('historical_uluu_refresh', card.uid),))
            for card in tuple(game.players[game.current].hand)
            if card.card_id == CARD_ID]

def checked_pair(game, owner, card):
    provider = getattr(game, 'historical_uluu_pair', None)
    if provider is None:
        raise UnsupportedCard('Uluu requires the complete frozen choice-pool and pair-selection contract')
    # Provider receives a detached snapshot; it cannot mutate the actual held
    # card before the entire selected pair has passed structural checks.
    pair = provider(game, owner, deepcopy(card))
    if not isinstance(pair, (tuple, list)) or len(pair) != 2:
        raise UnsupportedCard('Uluu requires exactly two choice definitions')
    branches = []
    identities = []
    from .cards import CHOICES
    from .identities import identity_resolver
    from standard.catalog import load_catalog
    # Frozen legal-format membership is separate from executable coverage.
    # The complete eligible subset and its pair distribution remain supplied
    # by the reviewed provider, never inferred from implemented branches.
    resolve=identity_resolver(game.cards)
    legal={resolve(data) for data in load_catalog()}
    excluded={resolve(game.cards[cid]) for cid in EXCLUDED_PARENTS
              if cid in game.cards}
    for option in pair:
        if not isinstance(option, dict):
            raise UnsupportedCard('Uluu choice requires a parent and branch index')
        parent,index=option.get('parent_id'),option.get('branch_index')
        if not isinstance(parent,str) or type(index) is not int:
            raise UnsupportedCard('Uluu choice source identity is missing')
        if parent not in game.cards or not game.cards[parent].get('collectible'):
            raise UnsupportedCard('Uluu choices must come from collectible parents')
        if resolve(game.cards[parent]) not in legal:
            raise UnsupportedCard('Uluu choice parent is outside the pinned Standard format')
        if resolve(game.cards[parent]) in excluded:
            raise UnsupportedCard('Uluu cannot gain choices from self-transforming parents or Fatespinner')
        if 'CHOOSE_ONE' not in game.cards[parent].get('mechanics',()):
            raise UnsupportedCard('Uluu source parent must have printed Choose One')
        choices=CHOICES.get(parent)
        if not choices or not 0<=index<len(choices):
            raise UnsupportedCard('Uluu choice branch is unavailable')
        branch=deepcopy(choices[index])
        # Programs are compiled from the actual source declaration. Providers
        # cannot attach an unrelated schema-valid program to a source label.
        if 'branch' in option and option['branch']!=branch:
            raise UnsupportedCard('Uluu provider program differs from source branch')
        validate_table('CHOICES', {CARD_ID: [branch]}, strict_unknown=True)
        identities.append((resolve(game.cards[parent]),index))
        branches.append(branch)
    if identities[0] == identities[1]:
        raise UnsupportedCard('Uluu requires two distinct choices')
    if all(branch[1] != 'none' for branch in branches):
        raise UnsupportedCard('Uluu cannot receive two targeted choices')
    return branches, tuple(identities)

def execute(game, op, ctx):
    if op[0] != 'historical_uluu_refresh':
        return False
    owner = ctx['owner']
    # Recheck actual zone and identity when the ordered trigger resolves.
    card = next((card for card in game.players[owner].hand
                 if card.uid == op[1] and card.card_id == CARD_ID), None)
    if card is None:
        return True
    branches, identities = checked_pair(game, owner, card)
    install(card, branches)
    # Replace the previous pair; never append choices from earlier turns.
    card.rule_state['historical_uluu_sources'] = identities
    game._refresh_auras()
    return True
