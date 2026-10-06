"""Reproducible deck populations. Playable subset and matches live in engine/."""
from collections import Counter
from pathlib import Path
import json
import random

ROOT = Path(__file__).resolve().parent
RUNES = ('blood', 'frost', 'unholy')
RUNE_PROFILES = [(b, f, 3-b-f) for b in range(4) for f in range(4-b)]


def load_cards():
    return json.loads((ROOT / 'data/core_pool.json').read_text())


def eligible(cards, profile):
    if len(profile) != 3 or any(type(n) is not int or n < 0 for n in profile) or sum(profile) != 3:
        raise ValueError('Choose three runes total: (blood, frost, unholy).')
    return [c for c in cards if all(c.get('runeCost', {}).get(r, 0) <= n
                                  for r, n in zip(RUNES, profile))]


def validate(deck, cards, profile):
    pool = {c['id']: c for c in eligible(cards, profile)}
    errors = []
    if len(deck) != 30:
        errors.append('Deck must contain 30 cards.')
    names = Counter()
    limits = {}
    for card_id in deck:
        if card_id not in pool:
            errors.append('Unavailable card or incompatible runes: ' + card_id)
            continue
        c = pool[card_id]
        names[c['name']] += 1
        limits[c['name']] = 1 if c['rarity'] == 'LEGENDARY' else 2
    errors.extend('Too many copies: ' + name for name, count in names.items() if count > limits[name])
    return errors


def random_deck(cards, profile, rng):
    # Sample card copies without replacement. This is reproducible, but is not
    # a uniform distribution over all possible deck multisets.
    pool = eligible(cards, profile)
    if len({c['name'] for c in pool}) != len(pool):
        raise ValueError('Pool must contain only one version of each named card.')
    slots = [c['id'] for c in pool for _ in range(1 if c['rarity'] == 'LEGENDARY' else 2)]
    if len(slots) < 30:
        raise ValueError('Insufficient cards for this rune profile.')
    deck = sorted(rng.sample(slots, 30))
    assert not validate(deck, cards, profile)
    return deck


def population(cards, per_profile=10, seed=42):
    if type(per_profile) is not int or per_profile < 1:
        raise ValueError('per_profile must be a positive integer.')
    rng = random.Random(seed)
    return [{'runes': dict(zip(RUNES, p)), 'cards': random_deck(cards, p, rng)}
            for p in RUNE_PROFILES for _ in range(per_profile)]


def describe(deck, cards):
    lookup = {c['id']: c for c in cards}
    counts = Counter(deck)
    return '\n'.join(f"{counts[c['id']]}x {c['name']} ({c['cost']} mana)"
                     for c in sorted((lookup[i] for i in counts), key=lambda c: (c['cost'], c['name'])))


def train(*args, **kwargs):
    raise NotImplementedError('Model training is not implemented yet. Use notebook 02 for random matches in the supported subset.')


if __name__ == '__main__':
    cards = load_cards()
    decks = population(cards)
    destination = ROOT / 'runs'
    destination.mkdir(exist_ok=True)
    (destination / 'generation_000.json').write_text(json.dumps({'seed': 42, 'status': 'untrained', 'decks': decks}, indent=2))
    print(f'Generated {len(decks)} untrained decks across {len(RUNE_PROFILES)} rune profiles.')
    print(describe(decks[0]['cards'], cards))
