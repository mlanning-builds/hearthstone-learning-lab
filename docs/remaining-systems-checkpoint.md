# Remaining systems checkpoint — October 5, 2026

Twelve additional frozen Standard collectibles have staged runtime declarations. The completion queue now has **247/308 staged runtime declarations, 61 without declarations across 21 categories**, alongside **877 live registered collectibles**. No card is newly admitted for training at this checkpoint. Runtime declaration presence is not complete, verified support.

## Implemented behavior

| Shared system | Collectibles | Behavior |
| --- | --- | --- |
| Evolving locations | Past Gnomeregan, Past Conflux, Past Silvermoon | Physical locations advance through three archived identities, retaining durability and cooldown. Discover pauses resume the same activation. |
| Location upgrades and reopening | Amirdrassil, Nespirah | Per-use upgrades, Fel reopening, final-charge removal, freed Nespirah and a non-Colossal Naga selector. |
| Damage replacement | Stormrook | Friendly Nature spell damage is replaced by a random five-cost summon without consuming Divine Shield. |
| Physical zone transformations | Divergence, Alternate Reality | Halved physical hand cards; complete hand/deck replacement from a historical Choose One contract. |
| Opening-deck overdraw effect | Godfrey | Physical burned draws are retained, discounted and recovered when space becomes available. Generated cards burned at full hand are not overdraws. |
| Temporary control | Cursed Chains | Original-controller deadline, cast-turn attack prohibition, silence/transform persistence and full-board return handling. Overlapping temporary-control enchantments explicitly reject pending ordering review. |
| Hero-bound resurrection | Husk, Eternal Reaper | One nonstacking, consumed enchantment; spend up to twenty Corpses on lethal and restore current Health without a healing event. |
| Damage-triggered zone summons | Warptooth | Count distinct friendly characters damaged on the owner's turn; capture and recruit actual hand/deck cards, retaining hand buffs and avoiding paid-play or draw events. |

All changes are restricted to regular Constructed mechanics in frozen patch **36.6.0.251952**, not Mercenaries or Battlegrounds. Feature schema v47 adds relevant public state and owner-only overdraw-cache contents. It remains a deliberately lossy baseline rather than proof of sufficient ML state representation.

## Remaining gates

Generated pools are still explicit, complete membership contracts. No unsupported outcomes are silently removed. Historical Choose One results and new location/Stormrook generation are not admitted through reduced fixture pools. Amirdrassil's reachable costs require individual contracts, not merely the broad planning inventory.

`expanded/fidelity_gaps.json` records independent timing and interaction review still needed: split enchantments and rounding, overdraw recovery timing, location destruction/order, damage replacement order, resurrection interactions, Warptooth full-board retries, and temporary control overlap. Tests establish candidate behavior, not independent game-client conformance.

Primary printed source: the project's frozen card archive. Additional interaction notes consulted: [Husk](https://hearthstone.wiki.gg/wiki/Husk%2C_Eternal_Reaper) for nonstacking and hero-replacement persistence, and [Warptooth](https://hearthstone.wiki.gg/wiki/Warptooth) for the distinct-character requirement. These are secondary notes; the client-evidence gates remain open.

## Remaining runtime categories

| Category | Cards without a runtime declaration |
| --- | ---: |
| Fabled | 9 |
| Quests | 8 |
| Replacement effects | 7 |
| Starting/setup effects | 6 |
| Custom creation | 3 |
| Automatic play | 3 |
| Infinity | 3 |
| Deck construction | 3 |
| Stored spells | 3 |
| Persistent effects | 2 |
| Automatic casting | 2 |
| Stored cards | 2 |
| Hidden choices | 2 |
| Transformation, Secret, Rewind, Deathrattle, custom choice, hidden state, location, conditional aura | 1 each |

This is a runtime inventory only. All 308 staged collectibles additionally require integration, dependency closure and review before the full frozen card pool is playable. The machine-readable [completion queue](engine-audit/completion-queue.json) lists each identity and its outstanding gates.

Validation receipts are recorded in the candidate's [STATUS.md](../staging/rebased-88/STATUS.md). No training or deck search ran.

Final validation: **3,612/3,612 full engine checks**, **24/24 queue checks**, **22/22 smoke games** without errors or caps, and **2,463 feature decisions** checked. The code stayed unchanged at `b9b247e49986888d2d193aa4a639a1a92484f727fa136ef7cf2f6f6335dfa368`. The full-suite receipt is `staging/rebased-88/runs/expanded_validation/validation-5158115815a542c982a5ea1cc7f73430.json`. The 49 added focused fixtures are included in the full count. The first run found seven synthetic event-compatibility errors, fixed before the passing rerun.
