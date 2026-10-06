# Quest infrastructure checkpoint — unfinished 60-card delivery

Candidate: `staging/rebased-88`, pinned regular Standard snapshot 36.6.0.251952. No live legality refresh, training, or deck search.

The 785 → 845 delivery remains unfinished. This group adds Restore the Wild, Reanimate the Terror and Questing Assistant. Written coverage is 794/1185, with 391 remaining; current batch progress is 9/60. The three reward records do not count as collectible additions. Other Quests remain rejected until their complete reward dependencies are supported.

## Connected behavior

- Quest cards reserve an opening-hand slot and retain their physical starting-deck lineage. They can be mulliganed away. Playing a Quest starts public progress; previously performed actions do not retroactively contribute.
- One active Quest per player, sharing the five secret/Quest slots. Quest-play history persists after completion and includes a countered Quest for Questing Assistant's condition.
- All candidate Corpse deductions now pass through one validated payment function, independent of event recording. This includes Blood Tap, Grave Strength, summon-response damage, alternative payment, secondary Hero Powers, conditional effects and choices. Resource gains are not spending.
- Reanimate the Terror tracks 15 Corpses and awards Tyrax through the normal hand-cap boundary. Tyrax's Deathrattle creates Terror's Grave, with targeted 4-damage activations and a Deathrattle that returns Tyrax. Both final-charge removal and destruction use the shared location-removal hook.
- Restore the Wild counts seven occupied friendly board slots once on each own turn. The Everbloom has its pinned 2 Attack/5 durability and grants friendly minions +2/+2 after hero attacks.
- Questing Assistant targets an enemy minion for 3 damage only after a Quest was played.
- Observation and feature schema v21 expose active progress and Quest-play history. Private deck and reward-in-hand identities remain hidden from opponents.

## Evidence and limits

Printed effects and values use the reviewed local snapshot. Blizzard's [Quest design article](https://hearthstone.blizzard.com/en-us/news/20567342) establishes opening-hand reservation, the need to play a Quest and public progress. The [Lost City expansion page](https://hearthstone.blizzard.com/en-us/expansions-adventures/the-lost-city-of-ungoro) confirms the returning opening-hand mechanic.

Internal fixtures exercise setup, mulligan, progress boundaries, overpayment, recording disabled, capped-hand rewards, invalid payments, countering, occupied slots, reward effects, location destruction and feature visibility. These do not certify client timing. Independent pinned-patch traces remain needed for full-board edge cases (Dormant minions/locations, an already-full board at turn start), rewards within compound effects, countered-play history and mixed location/minion death ordering. See `expanded/fidelity_gaps.json`.

No Jupyter action is needed for this internal checkpoint. Continue toward 60 additions before delivering the batch.

## Validation result

Final full suite: **2046 passed**, zero failures/errors/skips. Receipt: `staging/rebased-88/runs/expanded_validation/validation-8f1038f5957342c4b5eafdce4d50d45d.json`; fingerprint `4a5c76b4769838b0b5d0c147406adcde61e6fe05996d16cbb7984bb3c9463b7d` remained stable during the run. The initial run found one stale v20 assertion in a provenance test; it was updated for v21 and the full suite rerun.

Random validation completed **22/22 games**, zero errors/caps and **2267 feature decisions** on the same runtime source. Its receipt is `staging/rebased-88/runs/random_validation/summary-210108f7a658-6ddfa55fe518421f9543f219b8c25787.json`; the later test-assertion edit accounts for its different overall fingerprint.
