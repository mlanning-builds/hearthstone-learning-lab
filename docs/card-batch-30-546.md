# Thirty-card batch: conditions, history, generation, and hand/deck effects

Scope: the pinned regular Hearthstone Standard snapshot, all classes; not Mercenaries or Battlegrounds. This batch adds 30 collectible implementations using shared operations. Generated dependencies are additional and do not count toward the 30.

Candidate coverage: **516 → 546 of 1,185** collectible implementations; **639 remain**. These are written implementations with internal regression coverage, not independent client certification. Full Standard readiness remains false.

## Validation

- Full suite: **1253 checks; 0 failures; 0 errors**.
- New batch scenarios: 37, including one or more per collectible.
- Receipt: `/Users/matthewlanning/Desktop/HearthStone AI /death-knight-lab/staging/rebased-88/runs/expanded_validation/validation-b246580da142419a911d9bdc258faac5.json`.
- Fingerprint: `023f4f40da8e3d4a9700132f64464b9c3b10ade2552438491c0e9769085817d7`.
- Literal generated-dependency audit: no missing IDs; dynamic pools and semantic completeness remain separate work.
- No training was run.

Shared behavior added includes last-turn minion history, conditional effects, history-scaled damage, hand-stat equalization, cost resets, copying deck spells, fixed bottom/shuffle insertions, current-turn death copies, and health-limited control. Spirit Bond resumes its summon after death-triggered choices; conditional multiple summons use existing resumable checkpoints. Wisp and fixed generated-card records are pinned explicitly.

Observation features advance to v10 because minion-play history is now public state. Older feature-schema checkpoints are incompatible. Full-game fidelity remains limited by the existing fidelity-gap ledger, including modifier ordering, generated pools, and independent timing verification.

## Added collectibles

| Card ID | Card |
| --- | --- |
| `TIME_447` | Power Word: Barrier |
| `TIME_449` | Lasting Legacy |
| `FIR_777` | Spirit of the Kaldorei |
| `FIR_908` | Charred Chameleon |
| `MEND_041` | Wizened Wildspeaker |
| `MEND_043` | Heartroot Stones |
| `EDR_941` | Starsurge |
| `TLC_517` | Knockback |
| `EDR_940` | Merry Moonkin |
| `FIR_958` | Tindral Sageswift |
| `TIME_019` | Manifested Timeways |
| `TIME_429` | Divine Augur |
| `TIME_057` | Wizened Truthseeker |
| `JAIL_882` | R4T-C4TCH3R |
| `JAIL_399` | Imp Gang Stooge |
| `JAIL_447` | Reckless Detective |
| `TIME_017` | Tankgineer |
| `TIME_EVENT_300` | Dark Iron Harbinger |
| `EDR_263` | Grace of the Greatwolf |
| `EDR_262` | Spirit Bond |
| `EDR_490` | Sleep Paralysis |
| `EDR_523` | Web of Deception |
| `EDR_804` | Divination |
| `TLC_826` | Story of Carnassa |
| `TLC_820` | Glade Ecologist |
| `MEND_805` | Charity |
| `TIME_435` | Eternus |
| `JAIL_035` | Vigilant Sentry |
| `EDR_978` | Meadowstrider |
| `JAIL_436` | Widow's Bite |

## Jupyter

Use `notebooks/13_shared_rules_checks.ipynb` for the isolated candidate. Restart the kernel and Run All to reproduce validation. This does not start training. Notebook 08 remains the older engine.

Future delivery batches target 30 newly implemented collectibles, grouped around reusable mechanics. Do not count generated tokens or unresolved partial implementations toward that target.
