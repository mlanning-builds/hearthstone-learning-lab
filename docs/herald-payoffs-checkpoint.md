# Herald payoff checkpoint — October 5, 2026

Deathwing, Worldbreaker and Ultraxion now have staged runtime bodies. All fifteen frozen Herald-family collectibles have runtime declarations, alongside all eleven Colossals. Overall: **235/308 staged declarations, 73 without; 877 live registered**. These two additions are not admitted for training.

Ultraxion snapshots `prior Herald count + 1`, resolves one Herald through the existing army machinery, then adds a persistent owner discount. The discount applies to an explicit set of Deathwing character cards, including future copies; cosmetic heroes and Spawn of Deathwing are excluded. It is public state and follows the existing cost pipeline. Independent confirmation of amount, timing, identity scope and cost-setting precedence remains required.

Deathwing preserves the player's Health and class, adds printed Armor, installs Ruthless (+5 hero Attack this turn), and snapshots one/two/four Cataclysm selections according to Herald progression. Four explicit operations summon Progeny, destroy a highest-current-Health enemy minion, damage enemy minions, or shuffle five one-cost Legendary Dragons. Complete pool contracts remain mandatory. Effects execute as Battlecry operations, not paid spells or Discover events.

The earlier distinct-only choice plan had no sufficient evidence. The candidate now permits repeated selections, retains their order across pauses and copies, and queues selected effects after the final selection. Repeat eligibility, select-all versus immediate effect timing, random tie behavior and replacement details remain fidelity gates. This is an explicit candidate policy, not claimed client conformance.

Public feature schema v46 includes the Deathwing discount. Only the choosing player sees pending Cataclysm selections and remaining choices; both are encoded for that player's next decision. The opponent sees only that a choice is pending.

Sources: frozen `all_cards.json.gz`, pinned XML (Ultraxion base script value 1), and [Blizzard's expansion overview](https://hearthstone.blizzard.com/en-us/expansions-adventures/CATACLYSM). The official overview supports the broad effects and Herald progression; it does not settle all timing details above.

Validation covers 26 new scenarios plus affected Herald, Colossal, hero replacement, cost, choice, resolution and feature systems. Current receipts and the distinction between targeted and full-suite validation are in candidate `STATUS.md`. No training or deck search ran.

Validation completed: **466/466 targeted checks**, zero failures/errors/skips; separately **23/23 queue checks**. Source unchanged at `a251e59e5434894cc9bfc2ae99b94433fd2c9e6077929289948f5ac58abf2910`. Receipt: `staging/rebased-88/runs/expanded_validation/herald-payoffs-effd8c57b95141a0998f4dbf1499a4f6.json`. The full suite and smoke games were not rerun; the prior 3,537-test receipt applies only to its earlier fingerprint.
