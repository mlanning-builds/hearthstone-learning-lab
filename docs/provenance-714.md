# Physical card origin and hand-entry delivery

October 1, 2026. Candidate: `staging/rebased-88`. Scope: pinned regular Standard catalog, patch 36.6.0.251952; all 11 classes, excluding Mercenaries and Battlegrounds.

## Delivered mechanic

Starting cards now have physical identities before the opening draw. The engine records their original owner and canonical starting identity, explicit opponent-copy ancestry, and the turn of each hand entry. Draws, mulligans, generation, copying, recruitment, returns, trades, shuffles and transfers use this state. A generated copy of a starting card does not become an original merely because its name matches. Transferring an opponent's card is distinct from copying it.

The mechanic includes per-player nonstarting-card play counts and held-card progress for playing an opponent copy. Draw effects retain resolution checkpoints; Dreamwarden buffs its surviving source after the draw resolves. Origin fields remain private engine state; the owner receives explicit predicates in the observation. Feature schema v15 makes this state available to learning and invalidates older policy checkpoints.

## All ten directly assigned cards connected

| Card | Shared behavior |
| --- | --- |
| Steamcleaner | Remove nonstarting cards from both decks |
| Techysaurus | Discount from nonstarting cards played |
| Dragonscale Armaments | Draw an original spell and a nonstarting spell |
| Dreamwarden | Conditional nonstarting draw and self-buff |
| Rat Burglar | Transfer cards entering the opponent's hand during this turn |
| Smuggled Shovel | Deathrattle draws a nonstarting spell |
| Mind Sweeper | Held opponent-copy progress enables enemy-board damage |
| Unshackle Soul | Held opponent-copy progress enables its cheaper cost |
| Enthralled Shade | Discount held cards copied from the opponent |
| Story of the Waygate | Discount nonstarting cards in hand |

Coverage advances from 704 to **714 / 1,185** written collectible implementations, leaving **471**. These are all ten primary assignments in the roadmap's origin/hand-entry family. Other mechanics can reuse the tracking; no additional cards are counted until their own dependencies are implemented.

## Verification and limits

The focused suite contains 44 scenarios covering original/generated identity, copies versus transfers, mulligans, recruitment and returns, shuffle reset, hand-entry timing, full-hand behavior, conditional discounts, damage, theft, draw selection, hidden information, features and rollback. The designated full candidate suite passed **1641 checks**, with zero failures, errors or skips. The random validation completed **22 games**, zero errors or caps, with **2,781 feature decisions checked**. Both runs used unchanged fingerprint `13b4e9701945514bdbc526cfc95d916663d7c4b0c510e6186314acccfb3fd2e7`.

- [Full-suite receipt](../staging/rebased-88/runs/expanded_validation/validation-95d957356ad34ea6a8eba4eaa8cdcc08.json)
- [Full-suite log](../staging/rebased-88/runs/expanded_validation/provenance-714.log)
- [Random validation](../staging/rebased-88/runs/random_validation/summary-13b4e9701945-05ceefb5637842b0a5c767ba62a5e29f.json)

Independent reference verification remains pending. The declared model treats transformed identity as nonstarting, retains inherited opponent-copy ancestry, and counts a countered card as played. Core aliases, transformation/copy edge cases and full-hand theft need independent client traces. These are explicitly tracked in `expanded/fidelity_gaps.json`; internal passing checks do not certify game fidelity.

An exploratory unfiltered test discovery also included legacy benchmark and learning tests whose `benchmarks` and `learner` packages are absent from this isolated candidate. That invocation reported two import errors. The designated candidate suite is `expanded.status.run_rule_fixtures`, which selects `test_expanded*.py`; its result below is the candidate regression gate.

## Next mechanic

Complete the **seven held upgrades and turn-counter cards**, then the **ten temporary-card and attached-hand-effect cards**, using this physical-state foundation. Continue delivering by completed mechanic without a card-count cap. No Jupyter reload or training run is required for this development checkpoint.
