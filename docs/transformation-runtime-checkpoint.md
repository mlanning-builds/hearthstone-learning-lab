# Shared transformation runtime — October 5, 2026

Coverage remains **868 live registrations and 317 staged recipes**. No card was promoted by this checkpoint. Eleven of the fourteen pending transformation cards now have staged runtime declarations in `expanded/transformations.py`, with three exceptions explicitly tracked. This continues the all-card completion queue without reinstating a fixed card-count batch.

| Cards | Shared runtime |
| --- | --- |
| Ascendance | Exact-cost board transformation and attached original-identity deathrattles |
| Conjuration Specialist; Bootleg Alchemist | Private physical hand selection and exact-cost spell replacement |
| Alara'shi | Hand minion transformation with retained stats and cost enchantments |
| Plucky Podling | Replacement at intended result cost plus two, including held and Tribute copy paths |
| Envoy of the Glade | Neutral deck-entry conversion with preserved order |
| Desperate Bribe | Summons for both players followed by friendly board transformation |
| Dangerous Variant; Unknown Voyager | Start-turn and surviving-damage transformation hooks |
| Anomalize | Bound summons and permutation of their four attack/health values |
| Life Cycle | Capture owner/cost/position, destroy, process deaths, then summon replacement |

Pool contracts remain mandatory. Missing or ineligible outcomes are rejected instead of narrowing to implemented cards. Group transforms check their currently known member pools before changing the first member. Dynamic failures during paid play use the engine's state rollback. Fixture-only registrations exercise the staged declarations and event hooks without changing production card admission.

## Exceptions still requiring bodies

- Genn, Cursed King: held parity changes and all starting Hero Power upgrades.
- Divergence: physical split, rounding, enchantments and full-hand behavior.
- Alternate Reality: complete historical Choose One membership and executable outcomes.

## Validation and limits

46 focused checks passed, including paid-play rollback, original-identity deathrattles, full-board transforms, private choices, silenced triggers, Podling replacement, JSON observations, and Life Cycle deathrattles filling the board before replacement. Ten completion-queue checks passed. Consolidated regression: **2,999/2,999 tests passed**, zero failures/errors/skips. All **22 smoke games finished**, zero errors/caps, with 2,508 feature decisions checked. Both runs used unchanged fingerprint `167b7711e4af6357874a62458e6c4c47be4ff160353332a7cdce15e8fa201e28`. Receipts are recorded in the [candidate status](../staging/rebased-88/STATUS.md).

The frozen catalog supplies printed effects. The [official Conjuration Specialist listing](https://hearthstone.blizzard.com/en-us/cards/123848/) confirms its selection and split text. [Anomalize's reference notes](https://hearthstone.wiki.gg/wiki/Anomalize) describe permutation of four stat values; [the dormant interaction report](https://us.forums.blizzard.com/en/hearthstone/t/anomalize-is-bugged-when-it-summons-a-dormant-minion/155884) is limited community evidence, not an independent conformance trace.

Do not admit these eleven cards merely because controlled tests pass. Production membership and outcome support remain unresolved. Independent review is still needed for hand-cost layering and split enchantments, Podling's replacement interactions, Bribe summon ordering, dormant/full-board stat scrambling, and transformation timing. These gaps and the three missing bodies are recorded in `expanded/fidelity_gaps.json`.

The regenerated [all-card queue](engine-audit/completion-queue.md) includes these runtime declarations and static selectors. Dynamic selectors remain visible blockers; their missing graph edges do not prove closure. The next ordinary family is Rewind, alongside resolution of the three transformation exceptions and cross-family outcome dependencies. No training ran.
