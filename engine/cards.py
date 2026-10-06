"""Explicit closed card pool. No interpreting card text as executable behavior."""
import hashlib
import json
from pathlib import Path
from lab import load_cards

SUPPORTED = {
    'CORE_CS2_179', 'CORE_CS2_189', 'Core_CS2_200', 'CORE_EX1_011',
    'CORE_EX1_096', 'CORE_EX1_110', 'CORE_EX1_506', 'CORE_GIL_558',
    'CORE_GIL_622', 'CORE_GVG_085', 'CORE_LOOT_137', 'CORE_LOOT_413',
    'CORE_NEW1_023', 'CORE_SW_068', 'CORE_ULD_191', 'CORE_ULD_271',
    'CORE_ULD_723', 'CORE_UNG_084', 'CS3_038',
    'RLK_503', 'RLK_708', 'RLK_958', 'CORE_RLK_087', 'CORE_EDR_002',
    'RLK_048', 'RLK_707', 'RLK_709', 'CORE_RLK_712', 'RLK_067',
    'RLK_024', 'CORE_RLK_505', 'CORE_RLK_062', 'RLK_511',
}
# Local token identifiers, deliberately distinct from Blizzard card IDs.
TOKENS = {
    'TOKEN_GHOUL': dict(name='Frail Ghoul', cost=1, attack=1, health=1,
                       races=['UNDEAD'], mechanics=['CHARGE']),
    'TOKEN_SCOUT': dict(name='Murloc Scout', cost=1, attack=1, health=1, races=['MURLOC']),
    'TOKEN_BAINE': dict(name='Baine Bloodhoof', cost=4, attack=5, health=5),
    'TOKEN_COIN': dict(name='The Coin', cost=0, type='SPELL'),
}
for cid, card in TOKENS.items():
    card.update(id=cid, type=card.get('type', 'MINION'), collectible=False)


class UnsupportedCard(ValueError):
    pass


def registry():
    manifest = json.loads((Path(__file__).parent / 'reviewed_cards.json').read_text())
    chosen = {c['id']: c for c in load_cards() if c['id'] in SUPPORTED}
    if chosen.keys() != SUPPORTED or manifest.keys() != SUPPORTED:
        raise RuntimeError('Supported pool and reviewed manifest disagree.')
    for cid, card in chosen.items():
        digest = hashlib.sha256(json.dumps(card, sort_keys=True).encode()).hexdigest()
        if digest != manifest[cid]:
            raise RuntimeError('Card data changed; review implementation: ' + cid)
    return {**chosen, **TOKENS}


def supported_pool():
    return [c for cid, c in registry().items() if cid in SUPPORTED]


def coverage():
    return [{'id': c['id'], 'name': c['name'], 'supported': c['id'] in SUPPORTED}
            for c in load_cards()]
