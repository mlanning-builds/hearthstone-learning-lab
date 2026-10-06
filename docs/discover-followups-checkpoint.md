# Physical Discover results and deferred follow-ups

Internal progress in the **785 → 845** batch. The registry now contains **787 / 1185** collectible implementations, leaving **398 overall**. Two additions are connected in this batch; 58 remain before delivery.

## Changes

- Connected **Vault Breaker (`TLC_483`)** to selected physical cards. Duplicates in hand or deck are not substituted for the selected instance.
- Shared deferred continuations run after the enclosing play, triggered event, Deathrattle or turn-effect sequence. Further choices and Cost modifiers in that sequence resolve first.
- Multiple live Vault Breakers stack. A silenced, dead or removed listener does not apply its discount. Burned or replaced outcomes do not redirect the discount to another copy.
- Private result references participate in normal whole-game rollback and are not added to player observations. Existing Discover counters and feature schema v19 remain.
- Corrected **Cursed Catacombs (`TLC_451`)** to transfer its selected physical card into hand without firing successful-draw events or Casts/Summons When Drawn. It preserves the card's existing modifiers and makes it Temporary. An older test encoded the incorrect draw behavior and was replaced with the no-draw expectation and direct drawn-keyword regressions.

## Evidence and limits

The [official Vault Breaker entry](https://hearthstone.blizzard.com/en-us/cards/120582-vault-breaker/) specifies an after-Discover discount. [Blizzard's 33.2 patch notes](https://hearthstone.blizzard.com/en-gb/news/24223019/33-2-patch-notes) specify Cursed Catacombs' Discover-and-Temporary effect. These texts support the operation distinction but do not independently certify every timing edge case.

The enclosing-effect timing model is tested internally across all four continuation scopes. Independent client traces for multi-Discover ordering, listeners entering/leaving during an effect, and non-hand results remain required; `expanded/fidelity_gaps.json` records that limitation. Do not describe this as complete Standard certification.

## Validation

**1,962 / 1,962 checks pass**, zero failures/errors/skips, including 18 new focused follow-up checks. Final fingerprint: `191ce01ebabe2b43cd1497630bf6e0463639896dc87219e507d20d6cdd264cdd`.

Full receipt: `/Users/matthewlanning/Desktop/HearthStone AI /death-knight-lab/staging/rebased-88/runs/expanded_validation/validation-f345381ac8244eaa9593b3e2e782794c.json`.

**22 random games completed**, zero errors/caps; **2,567 feature decisions checked**. Random receipt: `/Users/matthewlanning/Desktop/HearthStone AI /death-knight-lab/staging/rebased-88/runs/random_validation/summary-336dc91f7dc3-a8dcbe80d57a4325af0c18ba7cd3228c.json`. The random run used fingerprint `336dc91f7dc3ce80549ad63e606ebc137b758d38e18f153861ce2d063f58a44f`; afterward only the old Frame Job test assertion was updated to compare physical card identity rather than require a string. Runtime source did not change after the random run.

The 60 staged random-generation declarations remain blocked outside the registry. Their [current candidate dependency report](engine-audit/generation-current.json) reflects 787 implementations; it is not a set of approved runtime pools.

No training or deck search ran. No Jupyter action is required for this internal checkpoint. The full objective and 60-card delivery remain unfinished.
