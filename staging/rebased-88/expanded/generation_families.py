"""Explicit Constructed families in the frozen 36.6.0.251952 catalog.

Membership is reviewed against the pinned collectible records; names are not
parsed at runtime. These small closed families have no staged outcome cards.
"""
FAMILIES={
    'mask':('DINO_402','DINO_403','DINO_428','DINO_429','DINO_432'),
    'paladin_aura':('CATA_480','END_011','JAIL_327','TIME_700','TTN_851'),
}

def reviewed_contract(request, hero_class):
    from .generation_cards import pool
    from .pools import GenerationPool
    # Only these exact requests have approved defaults. A family name cannot
    # authorize arbitrary extra filters, historical cards or broad pools.
    expected={'mask':pool(card_type='SPELL',family='mask',classes='other'),
              'paladin_aura':pool(card_type='SPELL',family='paladin_aura',classes='PALADIN')}
    if request.family not in expected or request!=expected[request.family]:return None
    ids=FAMILIES[request.family]
    if request.family=='mask':
        mask_classes={'DINO_402':'WARLOCK','DINO_403':'HUNTER','DINO_428':'PRIEST','DINO_429':'MAGE','DINO_432':'DRUID'}
        ids=tuple(cid for cid in ids if mask_classes[cid]!=hero_class)
    return GenerationPool('pinned '+request.family,ids,'Explicit frozen Constructed family, patch 36.6.0.251952')
