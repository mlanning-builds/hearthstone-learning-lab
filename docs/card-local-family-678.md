# Bounded-zone choices and Cannoneers: 666 → 678

This is the first integrated block from the September 30 remaining-card inventory, not a completed 60-card delivery. It adds 12 collectible implementations and four fixed generated tokens. The candidate now has 678 of 1,185 pinned collectible implementations; 507 remain. Scope remains regular Standard for the frozen September 18 catalog, not live legality or Mercenaries.

## Implemented cards

| Shared behavior | Cards |
| --- | --- |
| Cannoneer generation, owner-end shots, extra-shot aura, weapon firing | Land Ho! (CAP_102), Cannonmaster (CAP_107), Hand Cannon (CAP_103), Captain Crowley (CAP_106) |
| Bounded deck and graveyard choices | Frame Job (CAP_403), Succumb to Madness (EDR_455), Hellraiser (JAIL_734) |
| Damage survival and remembered deathrattle rewards | Destructive Blaze (CATA_586), Grove Shaper (EDR_271), Hungering Ancient (EDR_494) |
| Opponent token summons and existing deck recruitment | Time Adm'ral Hooktail (TIME_713), Gladiatorial Combat (TIME_870) |

Generated dependencies: Cannoneer, Treant of Life, Timeless Chest, Coliseum Tiger. They do not count as collectible progress. Coins use the existing reviewed Coin implementation.

Effects reuse the existing physical deck choices, event listeners, resumable effect frames, recruitment, and attached deathrattles. Choices use actual deck/graveyard contents, never an artificially restricted global generation pool. New fixed-token operation arguments are also covered by the literal dependency audit.

## Evidence and limits

Printed definitions come from the pinned `data/standard/all_cards.json.gz` records, hash-checked by the registry. The [Hellraiser reference](https://hearthstone.wiki.gg/wiki/Hellraiser) corroborates the current Taunt/empty-deck wording. No independent game-client comparison was run.

46 new scenarios cover each card, full boards/hands, silence, physical deck modifiers, owner-only firing, stacked Crowley bonuses, last weapon durability, living targets between shots, stored spell rewards, copy/resurrection, choice privacy and deterministic suspended-choice replay. Full suite: **1,469 passed**, zero failures/errors; current-source receipt `validation-d86dc9501f204974b2a6970d9246c11e.json`. Literal dependency audit: no missing IDs. See candidate STATUS.md for the full receipt path and fingerprint.

Remaining fidelity questions are recorded in `expanded/fidelity_gaps.json`: duplicate choice weighting, reset of consumed deck enchantments, and deathrattle/Reborn timing between weapon-triggered shots require independent traces. The shared event scheduler still has its previously documented limitations. Written implementations and passing internal scenarios are not full Standard certification.

## Inventory update

Ten of the twelve initially lower-risk cards are now implemented, alongside the two other Cannoneer-family cards. Destructive Phoenix and Inspector Murloc Holmes remain unsupported: delayed physical hand-card tracking, copy timing and expiry need a reviewed contract before connecting them. The original 519-card inventory remains a baseline snapshot; it is not the current backlog count.

Remaining baseline categories after removing this block: 2 lower-risk candidates pending timing review, 127 generation-dependent definitions, 206 shared-rule extensions, and 172 larger-system/unusual/scope cases = 507. These remain planning estimates.

No training or deck search ran. No JupyterLab reload or validation run is required from the user for this block. Notebook 13 remains the candidate validation entry point; notebook 08 retains the older engine.
