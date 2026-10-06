# Closed Dream rewards — internal batch checkpoint

The candidate remains pinned to regular Standard snapshot 36.6.0.251952. Hopeful Dryad and Shaladrassil are now connected, including all five ordinary and five corrupted Dream rewards. This brings written coverage to **796/1185**, leaving **389**. Tokens do not count as collectible additions. The current 785 → 845 batch is **11/60**; **49 additions remain**. No training or Jupyter run is requested.

## Shared behavior

The Dream pool is explicit and closed. Missing reward metadata rejects generation before RNG use; there is no supported-only subset. Hopeful Dryad picks one reward, while Shaladrassil inserts all five in a seeded random order through the capped-hand boundary. Ordinary and corrupted pools remain separate.

Shaladrassil keeps its upgrade on the physical held card. It compares the played card's paid cost to that held card's current cost after shared one-use discounts have been consumed, before the played effect can discount or draw a copy. Opponent plays and prior plays do not upgrade it. Copies preserve the held state independently. Countered plays currently qualify; exact event timing remains a reference-validation item.

Nightmare gives +5/+5 and attaches a caster-turn destruction timer. The timer follows control changes and minion copies; Silence, transformation and returning to hand remove the ordinary enchantment. Corrupted Nightmare instead grants Immunity through the current turn and keeps its stats afterward.

Dream returns either side's minion to its owner's hand. Corrupted Dream removes a minion from the battlefield and shuffles a clean physical card into its owner's deck, preserving starting-deck lineage without triggering death. Shuffle history records the actor and destination separately.

Corrupted Laughing Sister gives its controller's hero a live Elusive aura. Spells and Hero Powers cannot target that hero from either side; attacks, Battlecries, location effects and untargeted damage remain available. Silence, death and control changes update the aura. The hero's public observation and feature schema v22 expose this state.

Ordinary Ysera Awakens damages characters other than explicitly identified Ysera minions. Corrupted Awakening destroys Ysera minions before enemy damage. Ysera's own unimplemented Start of Game mechanic is not registered by adding this target exception.

## Source evidence and remaining fidelity work

Raw values and effects use the reviewed local token records. Blizzard's [known-issues notice](https://us.forums.blizzard.com/en/hearthstone/t/316-known-issues/142174) identifies nonrandom Shaladrassil reward order as a bug. The [32.0.2 hotfix](https://us.forums.blizzard.com/en/hearthstone/t/3202-hotfix-patch/143615/1) confirms discounted-cost comparisons and prevents a card from activating Shaladrassil merely by discounting it during its effect. [32.0.3](https://hearthstone.blizzard.com/en-us/news/24191047/32-0-3-patch-notes) fixes activation by an opponent's play. [31.6.1](https://us.forums.blizzard.com/en/hearthstone/t/3161-patch-notes/142347) confirms Emerald Aspect's exemption from ordinary Ysera Awakens while hero portraits still take damage.

These sources do not certify all cost-consumption timing, countered/nested plays, enchantment-copy deadlines or corrupted-Awakening ordering. Those remain explicitly listed in `expanded/fidelity_gaps.json`. Internal fixtures prove candidate behavior, not independent client conformance.

Focused validation: **35 checks passed**, including every reward family, complete-pool rejection and rollback, overflow, cost comparisons, physical copies, timer removal/control changes, Elusive and both Awakening variants. Broader receipts are recorded in the candidate STATUS file when complete.

## Consolidated validation

Full suite: **2081 passed**, no failures/errors/skips. Receipt: `staging/rebased-88/runs/expanded_validation/validation-d19c15b2b0d7429285f934b58cdc8544.json`.

Random legal play: **22 terminal games**, no errors/caps, **2637 feature decisions**. Receipt: `staging/rebased-88/runs/random_validation/summary-f23f1ff30a47-647cc11c138d4a47ae596265a3247a8f.json`.

Both used fingerprint `f23f1ff30a47af19d4c6e832c83b82afc32355331dc56d046cb83f277ee07701`. This validates candidate behavior; it is not full Standard conformance or evidence of optimal play. The 60-card delivery and overarching goal remain unfinished.
