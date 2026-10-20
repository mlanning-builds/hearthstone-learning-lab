"""Physical Choose One programs; pool selection is a separate contract.

No card is admitted to a generation pool by this module. In particular this
infrastructure does not claim a complete Uluu choice pool.
"""
from copy import deepcopy
from .effect_schema import validate_table
from engine.cards import UnsupportedCard

KEY = 'physical_choose_one'

def branches(card, static):
    state = getattr(card, 'rule_state', {})
    if KEY not in state:
        return static.get(card.card_id)
    value = state[KEY]
    if not isinstance(value, (tuple, list)) or len(value) != 2:
        raise UnsupportedCard('Physical Choose One requires two branches')
    validate_table('CHOICES', {card.card_id: value}, strict_unknown=True)
    return value

def install(card, choices):
    """Attach two explicit branch programs without modifying shared card rules."""
    value = deepcopy(choices)
    if not isinstance(value, (tuple, list)) or len(value) != 2:
        raise UnsupportedCard('Physical Choose One requires two branches')
    validate_table('CHOICES', {card.card_id: value}, strict_unknown=True)
    state = getattr(card, 'rule_state', None)
    if state is None:
        card.rule_state = state = {}
    state[KEY] = value
    # A physical minion's selected program is a repeatable Battlecry program.
    state['crafted_target'] = 'none'
    state['crafted_ops'] = []

def combined_targets(game, owner, card, choices):
    """A single selected target must satisfy every targeted branch."""
    modes = [branch[1] for branch in choices if branch[1] != 'none']
    if not modes:
        return [0]
    targets = list(game._targets_for(card.card_id, owner, modes[0]))
    for mode in modes[1:]:
        allowed = set(game._targets_for(card.card_id, owner, mode))
        targets = [target for target in targets if target in allowed]
    return targets
