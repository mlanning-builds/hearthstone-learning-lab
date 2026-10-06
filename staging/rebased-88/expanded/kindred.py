"""Pinned Kindred membership; no runtime parsing of card text.

The September 18 Standard records omit KINDRED tags on many actual Kindred
cards. References to Kindred (Torga and Primalfin Challenger) are not members.
"""
from .selectors import shares_tribe, SCHOOLS

KINDRED_IDS = frozenset('''
CORE_EDR_004_2026 DINO_138 DINO_404 DINO_413 DINO_435 END_015 TLC_107
TLC_223 TLC_226 TLC_236 TLC_243 TLC_366 TLC_428 TLC_429 TLC_432 TLC_440
TLC_447 TLC_454 TLC_463 TLC_482 TLC_519 TLC_600 TLC_815 TLC_816 TLC_825
TLC_829 TLC_903
'''.split())


def activates_kindred(kindred, partner):
    """Whether playing partner on the prior turn can activate kindred."""
    if kindred.get('id') not in KINDRED_IDS:
        return False
    if kindred.get('type') == 'MINION':
        return shares_tribe(kindred, partner)
    school = kindred.get('spellSchool')
    return (kindred.get('type') == partner.get('type') == 'SPELL'
            and school in SCHOOLS and partner.get('spellSchool') == school)

RULES={'TLC_251':('none',[('kindred_twice_next',)])}

def repetitions(game,owner,cid,active):
    return 2 if active and cid in KINDRED_IDS and getattr(game.players[owner],'kindred_twice',False) else 1

def consume_repetition(game,owner,cid,active):
    count=repetitions(game,owner,cid,active)
    if count>1:game.players[owner].kindred_twice=False
    return count
