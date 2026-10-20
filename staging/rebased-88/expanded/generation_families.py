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
    if request.excluded_mechanic=='COLOSSAL':
        from dataclasses import replace
        request=replace(request,excluded_mechanic='')
    if request==pool(card_type='MINION',mechanic='COLOSSAL',era='past'):
        from pathlib import Path
        import json
        manifest=json.loads(Path(__file__).with_name('historical_colossal_pool.json').read_text())
        ids=tuple(member['id'] for member in manifest['members'])
        expected=('NX2_037','TID_711','TID_712','TSC_026','TSC_029','TSC_030',
                  'TSC_216','TSC_219','TSC_639','TSC_660','TSC_937','TSC_950','TSC_962')
        if ids!=expected or manifest['count']!=len(expected):
            raise ValueError('Reviewed past Colossal membership changed')
        return GenerationPool('pinned past collectible Colossals',ids,
            'Complete thirteen-identity frozen historical Colossal manifest; canonical Standard copies excluded; all classes')
    if request==pool(card_type='MINION',rarity='LEGENDARY',mechanic='WILD_GOD'):
        from .imbue_consumers import WILD_GODS
        return GenerationPool('pinned legendary Wild Gods',tuple(sorted(WILD_GODS)),
                              'Complete eleven-card frozen Wild God family, patch 36.6.0.251952; cross-class Malorne offers')
    if request==pool(card_type='MINION',tribe='MURLOC'):
        from .murloc_generation import MURLOC_IDS
        return GenerationPool('pinned Standard random Murlocs',MURLOC_IDS,
                              'Complete explicit frozen collectible Murloc membership, patch 36.6.0.251952; All-type included')
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
