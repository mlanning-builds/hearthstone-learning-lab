# Colossal runtime implementation checkpoint — October 5, 2026

All eleven Colossal collectible bodies in the frozen Standard catalog now have staged runtime declarations, with their printed appendage abilities. This finishes the missing-body implementation pass; it does not certify client fidelity or admit these cards into training. Scope remains patch 36.6.0.251952, regular Constructed, all eleven classes.

## Connected behavior

| Body | Implementation |
|---|---|
| Wickerfang | Four Legs grow at end of turn; positive Attack/max-Health changes propagate to friendly active Wickerfang bodies. Shared buff, stat-setting and aura checkpoints distinguish stat gains from healing. |
| Ragnaros | Replays living friendly Deathrattles with each minion's source context. |
| Azshara | Grants a two-attack hero limit; appendages use the Herald attack system. |
| Al'Akir | Snapshots Attack for exact-cost generated minions; appendages share adjacent auras. |
| Sinestra | Repeats other-class spell effects through resumable spell frames; unsupported stacking remains explicit. |
| Arisen Onyxia | Replaces own-turn hero health loss, including health payments, with maximum/current Health gain. Armor is handled before health loss. Wings use Herald exact-cost generation and temporary health payment. |
| The Black Blood | Reacts to actual credited healing with forced attacks; three appendages heal damaged friendly characters. |
| Chromatus | Four head Deathrattles remove their matching keyword from friendly Chromatus bodies. |
| Vulcanos | End-turn damage and appendage Fire-spell generation. |
| Magmaw | Finite per-body queue of 99 appendages. Initial entry fills available space; later settlement replenishes after deaths or other board departures. Printed appendage Deathrattles grant random friendly Attack. |
| Cho'gall | Shared Arms/Soldiers replace friendly consumption with enemy-deck minion removal. |

Counts: **877 live registered / 308 staged; 233 staged runtime declarations / 75 without declarations**. These are definition counts, not a percentage of simulator correctness. No training or deck search ran.

## Evidence and explicit remaining gates

Frozen card text and identities come from `staging/rebased-88/data/standard/all_cards.json.gz` and the pinned Herald/Colossal inventory. [Official 35.0.3 patch notes](https://hearthstone.blizzard.com/en-us/news/24271854/35-0-3-patch-notes) establish Onyxia's exception allowing health-cost cards above current Health. This correction predates the frozen patch.

The following remain candidate semantics requiring independent client traces:

- Wickerfang: named-card rather than parent-only scope, aura/stat-setting gains, simultaneous recipients and negative Attack interactions.
- Chromatus: friendly named-card rather than parent-only scope, copied/stolen heads, external keyword auras and temporary grants.
- Onyxia: Armor/replacement/damage-event/Lifesteal ordering and exact max-Health behavior. The current implementation preserves missing Health and emits no healing callback for replacement.
- Magmaw: cycling the six frozen token identities, placement, refill priority relative to triggered effects/Deathrattles, and copied/control-changed bodies. The candidate refills after the current death wave completes; a fresh summoned copy starts a fresh budget. Silence clears the queue. A departed body cannot replenish.
- Cho'gall: uniform sampling of eligible physical deck slots and no-op on an empty eligible pool.
- Prior Sinestra stacking, dormant/silenced-copy Colossal entry, shared Herald timing/off-class rules, complete generated pools and all prior independent entry/trigger review gates remain.

No unsupported stacking or missing generation pool is silently approximated as playable support. Runtime-body completion must not be reported as all Colossals verified/enabled.

## Validation

Focused results: **97 Colossal body checks**, **21 entry checks**, **27 feature checks**. Feature schema v45 includes the public remaining-appendage counter through the existing rule-state encoder; internal parent/entity lists remain excluded. Full-suite and smoke receipts are recorded in the candidate `STATUS.md` when complete.

Validation provenance: the first full run was interrupted after stale v44 feature-version expectations failed. Those assertions now expect v45. The restarted full run is the only candidate for the final pass receipt. Final-source smoke games: 22/22 terminal, zero errors/caps, 2,463 feature decisions; fingerprint `defff313b91fc096bcb22f334f566db3f6add7e92d3589df0174526971a293bf`. Smoke receipt: `staging/rebased-88/runs/random_validation/summary-defff313b91f-869cec8c08c94c7cad1eb7d6bf399387.json`. Smoke decks use the live registry and therefore do not establish coverage of staged Colossals; the focused fixtures explicitly install those bodies and appendages.

Final regression result: **3,537/3,537 passed**, zero failures/errors/skips, source unchanged at the same `defff313b91f…` fingerprint. Receipt: `staging/rebased-88/runs/expanded_validation/validation-41529aab624c451a919ec0f0a17a9bbc.json`; full log: `staging/rebased-88/runs/expanded_validation/colossal-complete-full.log`. Separately, all 23 completion-queue checks passed.
