# Discover state — internal batch checkpoint

Scope: the frozen regular Standard catalog; all-class simulation. This is an internal step in the **785 → 845** batch, not a completed delivery.

- Playable collectible implementations: **786 / 1185**; **399 remaining**.
- Newly connected: **TLC_365 — Storage Scuffle**. Its printed effect deals 3 damage to a minion. Its base Cost becomes 0 after its controller has Discovered this turn; existing Cost modifiers still apply.
- New shared state: per-player Discover count this turn and across the game. A choice increments the counts only after successful resolution, including selected cards burned by a full hand. Empty offers and invalid selections do not count.
- Existing Discover variants share this state: Tracking/Hellraiser, Temporary deck selection, enemy deck top selection, dead-Dragon resurrection, opponent-hand and deck copies, and deck selection that bottoms the rejected options. Staged generated Discover uses the same completion path.
- Dredge, fixed summon choices, and ordinary hand/Choose One choices are not classified as Discover.
- Counts are visible to both players; chosen identities are not added to public history or Discover log entries. Feature schema is now **v19**. Earlier feature-schema policy checkpoints are incompatible.

## Validation

**1,944 / 1,944 checks pass**, with zero failures, errors or skips, including 20 new Discover-history checks. Fingerprint remained unchanged: `6ab2b75a5bb80b0217ba66480f41fee7d3756bc17d9e1b823554a3b143da88c4`.

Full receipt: `/Users/matthewlanning/Desktop/HearthStone AI /death-knight-lab/staging/rebased-88/runs/expanded_validation/validation-e6458c3056b846f1a035d184810efc66.json`.

**22 random games completed**, zero errors/caps; **2,566 feature decisions checked** with the same fingerprint. Random receipt: `/Users/matthewlanning/Desktop/HearthStone AI /death-knight-lab/staging/rebased-88/runs/random_validation/summary-6ab2b75a5bb8-53ee7c1e79474f299b2602d0107a26bc.json`. These are internal regression checks, not independent certification of every interaction.

## Remaining work

This implements Discover occurrence, not the entire Discover interaction system. Vault Breaker still needs physical-result tracking and correctly timed after-Discover callbacks, including multi-choice effects, burned outcomes, non-hand outcomes and exact modifier ordering. Quest progress/rewards remain separate unfinished work. Do not count Vault Breaker or the 60 staged generator declarations as playable.

The official [Vault Breaker card entry](https://hearthstone.blizzard.com/en-us/cards/120582-vault-breaker/) confirms the printed after-Discover discount, but does not independently establish all timing interactions. Card effects are pinned to the checked-in snapshot; this checkpoint does not verify live legality.

[Current conservative generation dependency report](engine-audit/generation-current.json) reflects the 786-card registry. Its candidate sets are planning data, not approved production generation pools.

No training or deck search. No Jupyter action requested. The full 60-card delivery is **1 / 60 complete**, with 59 additions still needed.

Subsequent progress: [physical results and deferred follow-ups](discover-followups-checkpoint.md) connects Vault Breaker and corrects Cursed Catacombs. The earlier remaining-work description above records this checkpoint’s state, not the latest registry.
