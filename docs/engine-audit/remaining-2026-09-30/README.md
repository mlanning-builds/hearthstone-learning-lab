# Remaining Standard cards: implementation classification

**Historical baseline:** This inventory records 519 missing cards at 666 implementations. The [subsequent local-family block](../../card-local-family-678.md) adds 12, leaving 507. Keep this snapshot distinct from current candidate STATUS.md.

Baseline: **666 written / 1,185 collectible cards; 519 remaining**, pinned snapshot 36.6.0.251952. Regular Standard only; no Mercenaries or Battlegrounds.

Every remaining ID has one primary category. Counts are exact for this inventory; difficulty assignments are conservative planning estimates. This is a first-pass engineering review, not 519 completed card specifications or a guarantee that generated dependencies are closed.

| Category | Cards | Meaning |
| --- | ---: | --- |
| A: Lower-risk local additions | 12 | Mostly existing helpers; limited glue, fixed tokens and tests. |
| C: Main effect familiar; generation dependencies block completion | 127 | Often short definitions, but eligible generated results include missing behavior. |
| B: Needs a shared-rule extension | 208 | Build or extend a shared mechanic, then attach and test the family. |
| D: Larger systems, unusual effects, or scope decisions | 172 | Substantial lifecycle/action work, bespoke state, complex dependencies; includes 2 scope decisions. |

**Do not describe A + C as “139 easy cards ready now.”** The 127 generation-dependent cards are not currently completeable by swapping in a reduced pool. Some also need local glue. A pool service alone does not unlock them: every eligible generated effect and nested dependency must work.

## Lower-risk candidates

| Card | Why it is a candidate |
| --- | --- |
| Land Ho! (`CAP_102`) | Requires CAP_107t Cannoneer, including its end-turn shot; token does not count as another collectible. |
| Cannonmaster (`CAP_107`) | Pinned CAP_107t is a 1/1 with an end-turn random-enemy shot; existing summon/end-turn primitives cover it. |
| Frame Job (`CAP_403`) | Selection is from the actual enemy deck, not a global generated pool; implement private options and deck reorder. |
| Destructive Blaze (`CATA_586`) | Self-summoning dependency forms a cycle, not an unknown random pool; verify trigger/death ordering. |
| Destructive Phoenix (`CATA_EVENT_001`) | Reuse held-card timers/private selection; distinguish discard from destruction and preserve the correct summoned-copy payload. |
| Grove Shaper (`EDR_271`) | Capture the cast Nature spell identity in the generated Treant deathrattle; no random global card pool. |
| Succumb to Madness (`EDR_455`) | Discover from recorded friendly Dragon deaths; check duplicates and fresh resurrection semantics. |
| Hungering Ancient (`EDR_494`) | Choose from the actual deck, retain consumed identities and add them on death; no global pool. |
| Hellraiser (`JAIL_734`) | Existing deck-choice and self-buff helpers cover the two branches; verify what counts as an empty deck. |
| Inspector Murloc Holmes (`JAIL_851`) | Reuse private enemy-hand choice; add the named-card next-turn watch and fixed Coin reward. |
| Time Adm'ral Hooktail (`TIME_713`) | Pinned TIME_713t is a 0/8 Chest whose deathrattle fills its opponent’s hand with Coins; owner semantics matter. |
| Gladiatorial Combat (`TIME_870`) | Recruit from the actual deck and create a fixed enemy Stealth Tiger; include the exact token. |

## Shared families, largest first

These are exclusive primary-family counts, not additive estimates of everything each engine feature touches. A card can have several secondary dependencies. The generation, custom-state and setup groups are broad buckets, not single reusable mechanics.

| Family | Primary cards | Category | Work needed |
| --- | ---: | --- | --- |
| Global generation/Discover pool dependencies | 127 | C | Main effect often uses familiar operations, but exact pool eligibility and every possible generated card must work. No supported-only pool substitution. Additional card-specific conditions may still need local glue. |
| Custom or unusual persistent systems | 36 | D | Needs a dedicated state/action contract and generated effects; research/implementation effort is not established by a short card description. |
| Forced attacks and combat interruption | 24 | D | Need an owner-correct resumable combat API, precombat interruption, retaliation, kill attribution and death/choice checkpoints. |
| Setup, deckbuilding and hero replacement | 22 | D | Touches deck legality, initial state, starting hands/hero powers or attached special cards; cannot be implemented as a normal Battlecry. |
| Bounded state/choice extensions | 22 | B | A local feature extension is needed beyond composing current opcodes; inspect the card-specific explanation and generated dependencies. |
| Casting/replaying cards inside effects | 21 | D | Need nested play frames, legal/random targets, counter/trigger timing and resumable repeated effects; damage-only substitutions are insufficient. |
| Dark Gifts | 19 | B | Implement the complete Dark Gift effect pool and attached-state behavior; Discover variants also depend on generated-card pools. |
| Imbue and upgraded hero powers | 19 | B | Implement all affected hero-power upgrades and Imbue progress plus generated dependencies. |
| Prepare | 19 | B | Implement shared Prepare action, discount/progress state and associated triggers; complex reward effects remain separate dependencies. |
| Dormant and awakening | 18 | B | Add inactive board entities, targeting/trigger suppression, wake timing and conditional awakening. |
| Rewind and alternate outcomes | 17 | D | Rollback/counterfactual outcomes, RNG and hidden-information handling need a shared contract. |
| Casts/Summons When Drawn | 16 | D | Need a resumable draw pipeline, automatic effect resolution/replacement draw, burned-card rules and correct summon controller. |
| Herald and Deathwing upgrades | 15 | B | Implement Herald progress, Soldier generation and Deathwing upgrade dependencies together. |
| Damage, healing, costs and temporary control | 14 | B | Extend source-aware damage/healing replacement or ordered modifiers; existing flat buffs alone do not cover the rule. |
| Colossal and appendages | 12 | D | Implement appendage placement, lifecycle and component-specific effects; some also require forced attacks or spell repetition. |
| Mostly existing mechanics | 12 | A | Existing draw, summon, choice, history, payload and trigger helpers cover the main behavior; add bounded glue and fixed dependencies, then validate. |
| Quests and rewards | 12 | D | Add quest slots/progress, event conditions and complete reward effects; each reward needs separate review. |
| Card origin and hand-entry tracking | 10 | B | Track physical starting-deck origin, copied-from-opponent identity and hand-entry time through every draw, copy, shuffle and control transition. |
| Shatter and Advance | 10 | D | Split/recombined card identity and Advance transformations need new hand/deck/action semantics. |
| Temporary cards and attached hand effects | 10 | B | Add temporary generated-card expiry and playable-hand-card grant semantics; generated pools remain separate dependencies. |
| Discover history and delayed rewards | 7 | B | Add Discover-specific events/counters and follow-up choice ownership; ordinary choices must not count as Discover. |
| Held upgrades and turn counters | 7 | B | Extend physical-card progress and expiry hooks; verify threshold and turn-boundary semantics before reuse. |
| Leyline scaling and persistent upgrades | 7 | B | Implement the three related Leylines and shared upgrade/cost/repetition state; random-minion Leyline also needs pool closure. |
| Health/Corpse payment | 7 | B | Add alternate payment to legal actions and resolution, including prevention, lethal payment and modifier interactions. |
| Random Bonus Effects | 6 | B | Define the exact keyword pool, exclusions, stacking and steal/transfer rules; shared by multiple cards. |
| Play onto either board | 5 | B | Extend action encoding, board-space legality and controller-dependent Battlecries/deathrattles. |
| Type matching and Kindred selectors | 5 | B | Extend multi-type matching, distinct selection and Kindred partner eligibility; verify ALL-type and overlapping-type cases. |
| Animal Companion replacement and count | 4 | B | Centralize Companion generation and persistent substitutions/counts; replacement Beast pools must also be complete. |
| Void Soul generation and upgrades | 4 | B | Review and implement the fixed Void Soul dependency plus persistent upgrade state; a random-generator member also needs its full pool. |
| Recorded deathrattle replay | 3 | B | Reuse captured death records but add nested resumable effect replay and listener/death ordering. |
| Leech health stealing | 3 | B | Implement the fixed Leech token and player-level steal amount; include lowest-health ties and hero/minion health semantics. |
| Cannoneer shared firing rules | 2 | B | Add a shared firing operation and permanent extra-shot modifier; include fixed Cannoneer token behavior. |
| Draw listeners | 2 | B | Add draw-event publication with burn, fatigue, copy and continuation semantics. |
| Noncombat simulation scope decisions | 2 | D | Decide explicitly whether emote/timer behavior is modeled or intentionally omitted in this ML simulator; do not silently count it as implemented. |

## Practical development order

1. Finish the 12 local candidates and their fixed tokens; they are the shortest bounded queue, not a complete 60-card batch by themselves.
2. Extend the relatively contained shared systems: held upgrades (7), type selection (5), physical origin tracking (10), and fixed Cannoneer/Leech families (2 + 3). Verify timing and generated tokens before counting each card.
3. Build family releases for Dormant (18), Imbue (19), Prepare (19), and Herald (15). Dark Gifts (19) also has strong reuse, but its full effect pool and Discover dependencies raise the completion risk.
4. Build forced combat (24), nested casting/replay (21), and draw-trigger resolution (16) as engine projects with interaction fixtures. These remove foundations blocking both simple-looking and complex cards.
5. Use exact generation-pool dependency inventories to prioritize missing results; progressively clear the 127 generation-dependent definitions as their dependencies become complete. Rewind, Shatter, custom builders, special deck setup and complex rewards remain separate work.

This ordering aims for bounded progress and reuse. It is not a promise that each family alone yields its full count or that future releases must stop at a particular number. Continue consolidated deliveries and local validation; no Jupyter run is needed just to use this inventory.

## Evidence and boundaries

- Reviewed current `expanded/catalog_audit.json`, `implementation_index.json`, explicit rule tables and shared `game.py`, `systems.py`, `batch_effects.py`, `batch60.py`, `lifecycle.py`, `resolution.py`, `pools.py` and recorded fidelity gaps.
- `GenerationPool.resolve` refuses missing eligible effects. The engine has deck/private choices, but that is not a complete global Discover implementation.
- Nested card-effect frames are explicitly rejected. General Dormant, Prepare, Rewind, Imbue and Herald lifecycle support is not present in the current candidate.
- Spot-reviewed generated records in the pinned card archive; examples include the Cannoneer, Leech, Genn’s upgraded form, Dragon Egg and Coin Chest. Full token-chain review is still required for the complete backlog.
- No simulator code, implementation counts or validation receipts were changed. No training or engine checks were needed for this inventory.

[All 519 cards, grouped](cards.md) · [Machine-readable classification](classification.json) · [Reproducible classifier](classify.py)
