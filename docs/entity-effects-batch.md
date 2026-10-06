# Physical entity effects

Frozen regular Standard patch 36.6.0.251952. No training or deck search ran.

Six additional collectible implementations bring the candidate to **868 live definitions and 317 staged recipes**. They are dependencies outside the existing fixed 60-card membership; that batch remains 2/60 complete.

| Card | Runtime behavior |
| --- | --- |
| Faceless Replicator (`CATA_185`) | Combat, retaliation and minion-effect damage identify the killing minion. Destruction operations also capture their minion source. Its Deathrattle transforms a surviving killer without summoning it or replaying a Battlecry. |
| Tribute Dance (`DINO_414`) | A second minion selection transforms the first into a copy, preserving the first target's controller and position. Uses the shared board-copy rules for buffs, damage and enchantments. |
| Bloodthistle Illusionist (`EDR_780`) | Copies the actual source, then privately marks one as fragile. Both display the same possible-illusion marker; neither observation exposes the selected identity. Silence removes the enchantment, shields prevent its damage condition, and subsequent copies retain it. |
| Alarm-o-Matic (`JAIL_502`) | At owner turn start, swaps with an actual opposing held minion. Incoming hand buffs survive, no Battlecry plays, and the returning minion resets battlefield enchantments. |
| Ido of the Threshfleet (`TLC_241`) | Active sources provide their bound `TLC_241t` spell, replenish it after use, and remove it when the source dies, sleeps or is silenced. Spell replacement and removal are neither draw nor discard events. |
| Aviana, Elune's Chosen (`EDR_895`) | A player-bound timer matures after three owner turn starts, then applies a permanent card-cost setting. Source death does not cancel the timer. |

Shared code: `expanded/entity_effects.py`. The module plugs into copy/silence handling, effect continuations, damage attribution and stabilization checkpoints. Token metadata uses the pinned archive and reviewed hashes. Feature schema is **visible-action-features-v33**, including full-moon state; public board observations include possible-illusion markers but keep the true fragile flag private.

45 focused checks cover actual play and turn transitions, copying and privacy, full hands/boards, hand buffs, source silence/death, damage attribution, spell replenishment and delayed cost changes. Full regression and smoke-game receipts are linked in the candidate STATUS.md after completion.

## Evidence and limits

Printed identities, text, stats and types come from the frozen catalog. References consulted:

- [Bloodthistle Illusionist](https://hearthstone.wiki.gg/wiki/Bloodthistle_Illusionist)
- [Copy effects](https://hearthstone.wiki.gg/wiki/Copy_effect)
- [Transform effects](https://hearthstone.wiki.gg/wiki/Transform-related)
- [Aviana reveal discussion and turn sequence](https://www.reddit.com/r/hearthstone/comments/1ism3g6)

These are candidate engine contracts, not independently captured client traces. Open conformance work includes second-target restrictions during automatic spell casts, full-board Illusionist behavior, source-bound spells copied or moved across zones, simultaneous copy/death ordering, and competing cost-setting enchantments. Global random transforms remain staged; no random outcome pool has been narrowed to the implemented subset.
