# Historical keyword and draw primitives

Sixteen frozen historical card bodies use explicit existing operations, not runtime printed-text parsing. They remain generated dependencies, excluded from Standard decks. This does not approve any historical outcome pool.

Seventeen draft checks passed before registry changes. Ordinary checks cover paid mana, both controllers, silence before damage and buffs, Divine Shield consumption, Rush combat restrictions, draw counts and fatigue, printed Overload, and battlecry damage independent of Spell Damage. Source-bound full regression is required after applying these declarations.

- `AT_053` — Ancestral Knowledge: `('none', [('draw', 2)])`.
- `AT_069` — Sparring Partner: `('minion', [('keyword', 'TAUNT')])`.
- `AT_084` — Lance Carrier: `('friendly_minion', [('buff', 2, 0)])`.
- `AV_266` — Windchill: `('minion', [('freeze',), ('draw', 1)])`.
- `BAR_750` — Earth Revenant: `('none', [('area_damage', 'enemy_minions', 1)])`.
- `BOT_067` — Rocket Boots: `('minion', [('keyword', 'RUSH'), ('draw', 1)])`.
- `BOT_246` — Beakered Lightning: `('none', [('area_damage', 'all_minions', 1)])`.
- `CS3_027` — Focused Will: `('minion', [('silence',), ('buff', 0, 3)])`.
- `EX1_245` — Earth Shock: `('minion', [('silence',), ('damage', 1)])`.
- `EX1_332` — Silence: `('minion', [('silence',)])`.
- `EX1_371` — Hand of Protection: `('minion', [('keyword', 'DIVINE_SHIELD')])`.
- `RLK_922` — Seal of Blood: `('minion', [('buff', 3, 3), ('keyword', 'DIVINE_SHIELD'), ('damage_own_hero', 3)])`.
- `WON_048` — Lay on Hands: `('character', [('heal', 8), ('draw', 3)])`.
- `WORK_009` — Imployee of the Month: `('friendly_minion', [('keyword', 'LIFESTEAL')])`.
- `WW_410` — Triple Sevens: `('minion', [('damage', 7), ('draw', 7)])`.
- `YOP_033` — Backfire: `('none', [('draw', 3), ('damage_own_hero', 3)])`.

After application, 57 focused checks passed against the actual registry, including historical numeric, fixed child, nested/opponent Deathrattle and continuous aura scenarios. All 41 project-tool checks passed. The corrected full source regression is running; no training or notebook cells have been executed.
