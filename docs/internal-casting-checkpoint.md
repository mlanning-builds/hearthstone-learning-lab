# Internal spell casting foundation

Internal progress toward the unfinished 785 → 845 delivery: **809/1185** implementations, **376 remaining**, **24/60** in the batch. The fixed spell dependencies are not counted as new collectibles.

## Connected effects

- Opu the Unseen: Battlecry, eligible Combo and Deathrattle cast Fan of Knives separately. Deaths settle between casts; each cast damages enemy minions and draws. Silence removes the Deathrattle.
- Captured Archmage: counts four other owner Archmage deaths, excluding its own recorded entity. This also works when its Deathrattle is triggered while alive. The resulting Fireball chooses an eligible enemy.
- Shadow Rounds: a confirmed target death schedules another cast with a newly selected enemy minion. Reborn and Deathrattle summons resolve before the next target selection. A surviving/shielded/transformed target does not count as a killed target. Recasts do not consume additional mana or increment ordinary hand-play counters.

The shared dispatcher embeds spell operations in existing replay continuations, avoiding a competing global pending frame. Spell attribution is separate from the minion caster: the caster's Poisonous and Lifesteal are not inherited. Internal spells use Spell Damage, target legality and direct damage accounting. Parent effects, choice interruptions, terminal outcomes and Game.step rollback retain their existing boundaries.

This dispatcher currently admits only the fixed spell definitions required by these cards. Automatic effect-choice selection now has a shared scheduler; pre-cast Choose One branches and arbitrary dynamic spells remain unsupported. A chain deeper than 256 fails explicitly; this is an engine guard, not a claimed Hearthstone repeat limit.

## Validation

33 new focused checks pass. **2317 checks passed**, zero failures/errors/skips. **22 terminal random games**, zero errors/caps. Both runs used fingerprint `7576a7c12255c1e5bebf183c93c59c18a77b108f72082e8b99f08b5f107dea5b`.

Receipts under the candidate:
- `runs/expanded_validation/validation-7ba3ed7408ee49449a247139bdca29d3.json`
- `runs/random_validation/summary-7576a7c12255-9af902e8d0414b19a8fa4ca0767436f0.json` No training.

## Reference evidence and remaining gaps

[Blizzard 34.0 patch notes](https://hearthstone.blizzard.com/en-us/news/24243857) explicitly fix Opu death resolution between Battlecry and Combo. [Official 36.0.2 hotfix](https://us.forums.blizzard.com/en/hearthstone/t/3602-hotfix-patch/163357) confirms Captured Archmage's four-other-death condition when triggered by another card.

A [July 2026 firsthand report](https://us.forums.blizzard.com/en/hearthstone/t/captured-archmage-sometimes-targeting-elusive-minions/162984) reports Archmage hitting an Elusive minion. The candidate currently uses ordinary spell eligibility; reproducing that exception in the pinned client remains necessary. General caster attribution, automatic targets, exact spell-version identity, repeat limits and event/death phase ordering still require independent traces. Passing fixtures do not establish complete client parity.

## Continue the larger family

18 primary nested-casting cards remain, plus other mechanics that reuse the dispatcher. Before connecting arbitrary hand/deck casters, implement explicit automatic-choice policy without auto-selecting unrelated choices created by draw/death triggers. Preserve physical spell state, controller versus caster, alternate branches, overload, targets and per-cast history. Larger random generators must retain complete pools; never filter them down to implemented spells to claim completion.

## Automatic choice scheduler follow-up

The operation dispatcher tags each newly opened choice with its innermost effect's policy. Scheduler checkpoints select tagged automatic choices with the game's seeded RNG, applying each selection without resuming the parent frame. A nested manual effect retains a manual choice even when an automatic spell is its caller. Single-option choices consume no RNG. The same checkpoint path is used for card, event, death, and turn effects. Selected options can create further choices without erasing them.

Twelve targeted scheduler checks cover repeated choices, no-extra-RNG single options, ordinary manual play, nested manual triggers, replay contexts, choices that open choices, physical deck Discover, and Deathrattle spell casts. Tests substitute operation lists where needed; they do not represent newly supported collectible cards. The earlier fixed-spell admission guard remains in place.

A [firsthand 2023 Oh My Yogg report](https://us.forums.blizzard.com/en/hearthstone/t/oh-my-yogg-and-discover-spells/112600) describes both Twisted Knowledge discoveries being selected automatically. This supports automatic selection; it does not establish pinned-patch Discover counter/listener attribution, nested-trigger behavior, or Choose One target order. Those remain explicit fidelity gaps. No supported-only random spell pools were introduced.

Validation of the automatic-choice follow-up: **2334 tests passed**, zero failures/errors/skips, and **22 random games completed**, zero errors/caps. Both used fingerprint `55df0a06a66873e9dd4639d18f1358674d500531ec8f9006d0510336df09363e`. Receipts: `runs/expanded_validation/validation-524733fecbd449c799bae14628c5b9f1.json` and `runs/random_validation/summary-55df0a06a668-d64cc7dabb174acf98e94bee26b4926d.json`. These supersede the earlier validation figures above; coverage stays **809**.

## Physical spells and operation-family admission

The same internal casting path now accepts a detached physical Card or an exact entity UID from the owner's hand/deck. Zone casting removes that object without draw, discard, hand-play, payment or replacement-draw events. Its stored `rule_state`, ancestry and spell-damage bonus survive. A stale UID does nothing; an unsupported spell fails before removal. A selected spell that cannot target is consumed and fizzles. Whole-action rollback restores consumption and RNG if resolution fails.

Admission now uses declared target modes and shared executable operation families rather than adding a per-card casting handler: 179 spell definitions, including 95 already-counted collectible spells, have a casting path. This is **not new collectible coverage**. It is not a generation pool: no consumer may restrict its random results to this admitted subset. Empty/unplayable Shadow of Demise is not inferred to be an ordinary vanilla spell.

Existing Choose One spells select a branch before targeting. Own active Fandral combines their effects with the established special handling for Wrath and Power of the Wild. Enemy-only targeting leaves untargeted spells valid; prefer-source targeting uses the source only when legal, otherwise selects another legal target. A [firsthand Macaw/Morbid Swarm report](https://us.forums.blizzard.com/en/hearthstone/t/zombeast-piece-chatty-macaw-and-morbid-swarm/154791) records a caster-specific targeting exception; it does not certify the generic branch policy. Failed branches, Corpse eligibility and consumer-specific target exceptions remain explicit reference gaps.

The focused checks include both branches of all 12 existing Choose One spells; all 179 admitted paths; exact physical-card retention and real held-age damage; duplicate copies, stale references, fizzle consumption, no ordinary draw/play/discard side effects; combined effects and rollback. The all-path check establishes executable integration, not complete effect or client fidelity. Generic Combo/Outcast/Kindred cast attribution and arbitrary remaining spell families still require work before full dynamic consumers can be claimed.

Physical casting and family-admission validation: **2361 tests passed**, zero failures/errors/skips, and **22 random games completed**, zero errors/caps, using fingerprint `5caa5ad69423d2acb0664cba4cb5129cf96518d9a705fb00d7869c2179929008`. Receipts: `runs/expanded_validation/validation-fea975b393f543aa80a9753f6d35cc9b.json` and `runs/random_validation/summary-5caa5ad69423-30bfd6c4c2f046ad98718911b2eb871b.json`. Exact admission inventory: [internal casting audit](engine-audit/internal-casting-current.json). No training or new collectible additions.

## State-changing and delayed spell families

Internal casting admission now covers **220 spell definitions**, including **134 already-counted collectible spells**. New shared families cover Secrets, nested delayed turn operations, stat setting, cost modifiers, shuffled dependencies, zone choices and missiles. Scheduled admission recursively rejects unhandled child operations; this is still not a generation-pool filter.

Secret placement now enforces duplicate and five combined Secret/Quest slots at resolution, including automatic casts. A rejected automatic placement still completes that cast and does not replace an existing Secret. Actual hand/deck spell identity moves into the Secret zone. Owner observations retain identity and opponents see only the existing count. A [firsthand May 2026 Fyrakk report](https://us.forums.blizzard.com/en/hearthstone/t/fyrakk-the-blazing-can-cast-the-same-secret/161253) observes two consecutive attempts to cast the same Secret with only one ending up in play; this supports duplicate placement failure without excluding that spell from random selection.

Missiles now expand into one-hit continuations. Total shots capture Spell Damage once, each hit deals one damage, and choices/deaths settle before the next hit. The existing direct-effect fallback remains for helpers outside operation frames; this does not resolve every broader event scheduler gap.

Twenty targeted interaction checks cover all seven current Secrets, physical identity, hidden observations, duplicate/full/Quest slots, subsequent Counterspell activation, owner-turn delays and expiry, current-board Spell Damage at delayed resolution, unknown nested operation rejection, shuffled on-draw cards, zone-copy choices, discounts, stat resets, and missile choice/death/terminal boundaries. Scheduled effects still preserve source card ID rather than full physical spell state; enchantment carryover and later-choice attribution require further work and pinned-client evidence.

State-family validation: **2381 tests passed**, zero failures/errors/skips, and **22 random games completed**, zero errors/caps, with fingerprint `0b8aef5f0ade280e4361fb835dcae786f2f58753871b5d97fee311b87d99cc05`. Receipts: `runs/expanded_validation/validation-7612f33319114f3fb20d82ab275b55ac.json` and `runs/random_validation/summary-0b8aef5f0ade-b393e14ec1da4053ae942daa2655a311.json`. Inventory now lists 220 admitted paths, including 134 already-counted collectible spells, with 137 implemented collectible spells still outside internal-cast admission. Coverage remains **809/1185** and **24/60** in the unfinished batch.

## Conditional, modifier and draw families

Admission now covers **280 definitions / 194 existing collectible spells**, adding 60 collectible casting paths without changing the 809 collectible implementation total. This group includes explicit hand/state branches, weapon/friendly/legendary/Wisp target requirements, draw choices and modifiers, transformations, stat and zone buffs, fixed insertion, attached Deathrattles and established persistent modifiers. Recursive admission checks every alternative of a hand condition, even if the current hand would select a different branch. Conditional child operations use the same resumable splitter.

Damage followed by conditional draw, fresh summon, random buff or healing now snapshots the existing immediate damage outcome and queues the follow-up at the next operation checkpoint. A child choice suspends before the follow-up, and multi-card draws retain their ordinary per-draw continuations. The change also fixes normal hand plays. It deliberately does not claim new client evidence for kill attribution or prevention/transformation timing; those are recorded separately.

Twenty targeted checks cover Mortal Coil, Slam, Nascent Bolt, Initiation, Synchronized Spark, Purifying Breath, ordinary hand-play interruption, hand-empty and holding-cost conditions, prior-turn state, weapon requirements, friendly-only healing, Far Sight physical identity/discounts, Hex without Deathrattle, and fixed generated insertion counts. The all-admitted-path integration check also passes for the expanded family set. Combo/Outcast/Kindred attribution and other unreviewed operation families remain excluded pending their own work.

Conditional/modifier/draw validation: **2401 tests passed**, zero failures/errors/skips; **22 random games completed**, zero errors/caps. Matching fingerprint `a863f885dc5212bbbe18d6f9ad401eca60256c4d64f3cf578dab2d7ae5155f3f`; receipts `runs/expanded_validation/validation-4562c9853954440c875d3d34488ba0d2.json` and `runs/random_validation/summary-a863f885dc52-3eaf25d0beec4fbd998be5de0db0f732.json`. Admission audit: 280 definitions / 194 existing collectible spells, with 77 existing collectible spells still unadmitted. The 785 → 845 delivery remains 24/60, with no new collectible additions in this infrastructure checkpoint.

## Resource payments and resumable board-damage waves

Current delivery scope is all 1,185 collectibles and the full simulator objective. Previous batch counters above are historical, not stopping conditions.

Shared casting admission now covers 292 definitions / 206 already implemented collectible spells; 65 existing collectible spells remain unadmitted. Added families use existing Corpse, effect-mana, board-count and destruction helpers. Repeated descending and armor-funded damage now advances through operation continuations, preserving choice interruption and death settlement between waves. Armor is spent once before the first wave. Twelve focused checks exercise resource thresholds, limited board slots, effect-mana payment, Spell Damage on each wave, and a Deathrattle summon hit by later waves.

These checks establish candidate behavior, not independent client conformance. The direct-effect fallback remains for operations outside resumable frames; broader death/event timing and casting attribution gaps remain open. No new collectible coverage or training is claimed.

Validation: **2413 tests passed**, zero failures/errors/skips; **22 random games completed**, zero errors/caps. Matching fingerprint `fe6940760dee32c374f56e74d0d57987a6b7398b365db56132d555480b2367ec`. Receipts: `runs/expanded_validation/validation-eda8eb18555248ecaaaf1d5ce3401921.json` and `runs/random_validation/summary-fe6940760dee-f5b530c5728b4aa8ba22a474d9beb187.json`. Full log: `runs/expanded_validation/resource-waves-full.log`.

## History, resurrection and recruitment casting

Shared admission now covers 299 definitions / 213 existing collectible spells, leaving 58 implemented collectible spells unadmitted. Added families include highest-cost resurrection, separate-cost Reborn resurrection, played-one-cost summons, shield recruits, bottom-deck Demon recruitment and tribal buffs/damage. This does not increase the 809 collectible implementation count or permit filtering random pools.

History summons snapshot eligible played records before child events; each summon has a continuation checkpoint. Separate-cost resurrection similarly pauses between cost groups. Checks exercise interruption and resumption, snapshot stability, paid-cost history, spell exclusion, empty history, Undead eligibility, Reborn, shield grants, bottom-three recruitment and cross-board tribal damage. These preserve existing candidate selection semantics; independent client timing validation remains outstanding.

Verification at fingerprint `8cf53ec73e9209d303b61339823ae540cd3f54c425cde4f5b80bc75ee9a78d30`: eight new history-group tests, all 27 physical casting tests (including traversal of admitted paths), and 125 related history/dormancy/persistent tests passed: **160 total**. Full-suite and random-game receipts above predate these changes and are not represented as current full validation. No training run. Full-coverage goal remains active.

## Post-draw, provenance and discard casting

Admission reaches 305 definitions / 219 already implemented collectible spells; 52 existing collectible spells remain unadmitted. Origin-selected draws and nonstarting-card discounts use physical card provenance. Discard conditions recursively check their child operations and use the same resumable splitter.

Barnabus and Searing Reflection now capture the drawn card and queue their follow-up at a separate operation checkpoint, so a child choice can suspend before the buff/armor or summon. Existing burn distinctions remain: Barnabus requires a successful draw; Reflection preserves burned identity for its fresh fixed-stat summon. These changes also apply to hand plays. Exact client trigger ordering and card-movement edge cases remain reference gaps, not independently certified behavior.

Nine new checks cover interrupted draw follow-ups, attack threshold, burn handling, retained hand identity, fresh summon stats, original/generated spell draws, selective discounts, eligible/absent discards, and recursive rejection of unknown child effects. Another 136 physical-casting, draw-event, provenance and discard checks passed. **145 targeted/related tests passed**, fingerprint `642b034335f06dbf1f467a7f57652b9f6bc6a859c18d148b46500f4755494f54`. Full suite/random receipts above predate this change. Collectible coverage remains 809/1185. No training.

## Forced combat, copies and consolidated validation

Automatic spells now enter the existing controller-aware forced-combat frames for summon-and-attack groups and enemy attacks into a chosen minion. Bat Mask's board-copy loop now retains its chosen object and original slot count in a continuation, pausing for child choices between copies and respecting board capacity at each summon. This also improves ordinary hand play. The candidate preserves existing copy-selection semantics; independent client event ordering and target mutation cases still need reference validation. Outcast-dependent Horn of Feasting remains unadmitted.

Seven focused checks cover empty/nonempty minion decks, forced attacks without spending normal attacks, target death during a summon group, friendly attack targets, enemy target controller, interrupted copy groups, and absent-target fizzle. Admission now covers **310 definitions / 224 already implemented collectible spells**; **47 existing collectible spells** remain unadmitted. No eligible random pool may be restricted to this list.

Consolidated validation for the history, draw, discard and forced-combat extensions: **2437 tests passed**, zero failures/errors/skips; **22 random games completed**, zero errors/caps. Matching fingerprint `4eded83e319dd5b84c0469891088a22c07844bb97c10b3a1161b5151e91af224`. Receipts `runs/expanded_validation/validation-f5488c54b1754b0abee84b07eb97d9e1.json` and `runs/random_validation/summary-4eded83e319d-aecb4d2946fd464ea2f0c78057626406.json`; log `runs/expanded_validation/casting-consolidated-full.log`. This supersedes the targeted-only checkpoints above. Collectible coverage is still **809/1185**, with 376 missing. No training or full Standard certification claimed.

## Damage outcomes and held spell state

Shared admission reaches 323 definitions / 237 existing collectible spells, leaving 34 implemented collectible spells unadmitted. Added families cover held armor/Stealth state, health-setting with automatic secondary choices, excess damage, distinct/secondary targets, neighbor freeze/destruction and confirmed-death shuffling. Physical state uses the actual cast card; fresh generated casts receive fresh state. No random pool is narrowed to supported cards.

Damage-dependent owner draws, damage-count summons and excess rewards now capture the immediate damage result and continue after the operation checkpoint. The victim's owner is captured before death. Torch keeps its pinned Spell Damage exclusion and physical damage payload. Bone Flurry expands through per-missile continuations. These changes also apply to normal hand plays. Existing damage accounting is preserved; exact client outcome timing, modifier interactions and observer attribution still require independent verification.

**145 targeted/related tests passed**, including 12 new damage-amount checks plus physical casting, batch60, school discard and earlier internal-follow-up regressions. Fingerprint `e8122ac6af51b79738edba050810fce395206f086ae1c54cab318f15908fa112`. The new tests initially exposed a test assumption that absent cost_delta was stored as zero; the assertion now handles the existing optional field. Full-suite/random receipts above predate this extension. Collectible coverage remains **809/1185**, with 376 missing; no training run.

## Persistent state, closed Dreams and replay integration

Internal casting admission now covers **344 definitions / 252 existing collectible spells**, with **19 existing collectible spells** still unadmitted. The remaining set comprises Follow, Combo/Outcast/Kindred, hand position, repeated targeting, Quests and unplayable Shadow of Demise. This inventory only describes already implemented spells; the 376 missing collectible implementations and additional dependencies remain outside it.

Connected existing Hero Power changes/refresh, Dormant, Judgment, Bonus Effects, physical deck/death-history choices, replayed Deathrattles, board shuffling, attached effects, and Dreams. Attached operation admission recursively rejects unknown children. All generated Dream spells now have admitted paths; the closed reward pool remains complete. Physical Shaladrassil state selects ordinary or Corrupted Dreams. Opponent multi-summons now pause between entries. Existing replay contexts retain their trigger/choice ownership; no broader automatic-choice policy or independent client parity is asserted.

**275 targeted/related checks passed**: 15 new integration cases, 210 physical-casting/Dream/Dormant/replay/local/Prepare/Bonus checks, and 50 replacement-power regressions. Fingerprint `fc9ddcb8175695b0ef5fb240b7073ea4c25f29f8212a8e03175887c8e6840235`. Full-suite and random-game receipts above predate this and the damage extension. No new collectible additions or training.

## Quest placement and played-history targeting

Quest placement now enforces the same existing capacity rule at effect resolution as at hand-play legality: an active Quest or five Secrets prevents placement. Rejection preserves prior progress and emits a Quest-fizzle record; physical internal casts remain consumed. Automatic placement uses the generic internal-cast attribution policy and does not increment the ordinary hand-play Quest counter. Existing progress and reward systems remain in use. Repeated-copy targeting reads the controller's played history and automatic casts do not add ordinary plays.

Admission: **350 definitions / 258 existing collectible spells**, with **13 existing collectible spells** still unadmitted (Follow, Combo/Outcast/Kindred, hand-center effects and the unplayable Shadow of Demise placeholder). The earlier unsupported-spell tests now use that placeholder instead of a supported Quest.

**114 targeted/related checks passed**, consisting of 10 new cases and 104 Quest, physical-casting, fixed-casting, state-casting and Secret checks. Fingerprint `c80db75da81f1f1a39c2b8374954fd5da047ef16d947a50c19be68d917102292`. These tests cover placement capacity, no progress reset, physical consumption, Corpse reward, same-turn board progress and own/opponent played-history distinctions. Independent client cast attribution remains a reference gap. Full-suite/random receipts above predate this extension. Coverage remains **809/1185**; no training.

## Owner-scoped Follow and consolidated validation

Normal hand-action generation and Follow eligibility now share an owner-parameterized helper. Follow no longer implicitly asks the current player's legal actions or loses all eligible cards merely because another choice is pending. The helper retains existing mana/payment, locks, capacity, target and branch rules; it does not switch current player or grant the opponent actions in the current player's public legal list. Existing turn-scoped Follow expiry remains unchanged; independent off-turn expiry/reference behavior remains to verify.

The three existing Follow spells are now internally castable. Nine new tests cover casting for the noncurrent owner, preserved choice state, owner costs/locks, missing targets, full board, Pirate-only attachment, Evidence's opponent-deck insertion, and after-play execution. The Evidence fixture initially checked the wrong deck; it now verifies the operation's explicit enemy-deck destination.

Admission is **353 definitions / 261 existing collectible spells**; **10 existing collectible spells** remain unadmitted: Combo/Outcast/Kindred, hand-center behavior and unplayable Shadow of Demise. This remains distinct from missing collectible coverage.

Consolidated validation across damage, persistent/replay, Quest and Follow changes: **2483 tests passed**, zero failures/errors/skips; **22 random games completed**, zero errors/caps. Matching fingerprint `2be0a37afb409eaa0688e84009dfa1e638b24386985d9b151ddd4106e2394532`. Receipts `runs/expanded_validation/validation-34ea5967e3e04ed5a3d6770d58eb2b1d.json` and `runs/random_validation/summary-2be0a37afb40-883ebdad03d747d3b575c7b749b91c31.json`; log `runs/expanded_validation/follow-consolidated-full.log`. This supersedes the earlier targeted-only evidence. Coverage remains **809/1185**, with 376 missing. No training run or full Standard certification.

## Outcast bodies and play/cast distinction

[Blizzard's Demon Hunter introduction](https://news.blizzard.com/en-us/article/23305788/introducing-the-demon-hunter) defines Outcast in terms of playing a card from a hand edge. The candidate's internal cast is a separate action and keeps its existing false Outcast flag; generated, detached, hand-zone and deck-zone casts now support Spectral Sight, Flash Flood and Horn of Feasting base effects. Ordinary hand plays still calculate their own Outcast position. This is an implementation of the documented play/cast distinction, not independent verification of every consumer or spell-replacement exception.

Outcast child operations are recursively admitted and split through the shared continuation mechanism. Six new tests cover four casting origins for each spell, normal edge/middle plays, and rejection of unknown child effects. Another 101 physical-casting, forced-combat, attack-window and composed-effect checks passed: **107 total**. Fingerprint `26fb0b1a76e54a97bf6718b9ceab6b6a64c5a0c7a81ff78eafd5d889b3b98b39`. Full-suite/random receipts above predate this extension.

Admission is **356 definitions / 264 already implemented collectible spells**, with **7 remaining unadmitted**. Collectible coverage remains **809/1185**. The status page now presents current evidence separately from the last full-suite result; its previous contents are preserved in `status-history-before-outcast.md`. No training.

## Kindred history and continuations

[Blizzard's Lost City announcement](https://hearthstone.blizzard.com/en-us/news/24204896) defines Kindred using a matching minion type or spell school on the owner's previous turn. The candidate applies that general condition to internal spell casts. **This automatic-cast application is an inference, not a separately observed client trace.** Consumer-specific exceptions and off-turn behavior need independent reference verification.

On the owner's turn, the cast snapshots previous_schools. Off-turn, it reads the owner's played_schools, which still represents the just-finished own turn until their next turn-start rollover. This avoids using older history or the opponent's history. Automatic casts do not publish ordinary played-school/history entries. Conditional child operations recursively validate and split; Hybridization draws one cost group per checkpoint while retaining the original Kindred snapshot. This also improves ordinary card resolution.

**160 targeted/related checks passed**: 11 new cases and 149 physical-casting, Kindred, draw-event and forced-combat checks. Fingerprint `e4feafd4f243bad0d11e8ad23a7c4b01b21c1c81b71b6c833879661e4d841b1b`. Admission reaches **360 definitions / 268 existing collectible spells**, with three unadmitted: Deadly Bribe, Precise Shot and the unplayable Shadow of Demise placeholder. Full-suite/random receipts above predate the Outcast and Kindred extensions. Coverage stays **809/1185**; no training.

## Remaining conditions, generated dependencies and consolidated validation

Precise Shot captures the actual spell's exact middle hand position before zone consumption; generated/deck/detached spells do not inherit the caster's hand position. A [firsthand March 2026 Nagaling report](https://us.forums.blizzard.com/en/hearthstone/t/nagaling-precise-shot/158373) supports the generated-cast distinction; it does not independently certify every hand-consuming effect. Combo uses the initiating context snapshot when present, otherwise completed plays in the owner's current turn. This avoids counting the root play merely because its frame paused. Generic Combo consumer attribution remains to verify against independent traces.

Added the five remaining already-defined noncollectible spell bodies: Blight, Shred of Time, The Sacred Cave, Underfel Rift and Purifying Vines. No new collectible coverage is claimed. Admission reaches **367 definitions / 270 existing collectible spells**. Untransformed Shadow of Demise is the sole existing collectible spell intentionally unadmitted. This is executable integration of existing rules, not completion of missing catalog cards or certification of full pools.

Fourteen new tests cover Combo true/false snapshots, off-turn counters, no auto-cast play history, spell-owned hand position, generated/deck/detached casts, self-damage owner, Murloc reward, permanent capacity and relation-based health. Consolidated results including Outcast and Kindred: **2514 tests passed**, zero failures/errors/skips; **22 random games completed**, zero errors/caps. Fingerprint `c7c485ecac56b1df2a36a04be4fd9078a780c7baeb22bef7f0741f4d31772c85`. Receipts `runs/expanded_validation/validation-d9d8ed6a9fe04bcf83760faf4137d791.json` and `runs/random_validation/summary-c7c485ecac56-67b0462eec6c420a80c5b56459cd7553.json`; log `runs/expanded_validation/existing-spell-casting-full.log`.

Next: connect physical spell selection/storage and deck consumers (Crackling Cloudstrider, Violet Treasuregill), then shared spell repetition (Tyrande, Niri). Pinned text confirms these consume existing physical cards/history rather than requiring a global random spell pool. Their own semantics still require reviewed implementation and tests. Overall coverage remains **809/1185**, with 376 missing; goal active, no training.

## Spell repetition: evidence and implementation boundary

Scope remains all 1,185 frozen Standard collectibles. This checkpoint does not impose a card-count limit.

A [firsthand Tyrande/healing report](https://www.reddit.com/r/hearthstone/comments/1t0tekl/why_tyrande_moonwell_behave_differently_than/) describes a minion falling to zero health on the first repeated healing-to-damage effect and recovering on the next effect before death. Another commenter reports the same for a hero. These are observed reports, not independently reproduced pinned-client traces. They contradict treating every repetition as a fresh random cast with an ordinary death checkpoint between copies. Thread speculation about universal rules is not accepted as specification.

A [Niri/Rogue Imbue bug report](https://us.forums.blizzard.com/en/hearthstone/t/niri-the-crater-and-rogue-imbue/157586) reports a one-cost hero power being doubled. Its existence does not establish intended or current patch behavior; keep hero-power attribution separate from spell repetition until verified. Neither Mercenaries abilities nor Battlegrounds repetition belongs to this scope.

Current code boundary: `expanded/resolution.py::_resume_play_effects` settles after each operation. `expanded/spell_casting.py::_cast_spell_split` creates an automatic target/branch selection and separate cast completion. Reusing either unchanged for Tyrande can lose the player's target/branch and settle deaths too early. The existing lexical `_damage_batch` also aggregates Lifesteal, so it must not be reused blindly as a suspendable repetition lifetime.

Next implementation requirements:

- Retain the original spell's physical identity, target, selected branch and condition snapshot in a resumable repetition frame; distinguish effect repetition from a new play or a fresh random cast.
- Separate death/winner settlement suppression from damage/Lifesteal batching. Preserve the boundary across Discover suspension and rollback, release it exactly once at completion, and do not suppress required intermediate draw/summon triggers indiscriminately.
- Define original-target invalidation and target-death behavior from evidence, including a zero-health target awaiting settlement. Never silently retarget a selected spell.
- Track Tyrande charges on the player independently of its minion; establish countered-spell consumption and stacking from traces. Keep Niri's live aura, paid/current one-cost condition, minion doubling and internal-cast eligibility distinct.
- Validate one payment/play-history publication, repeated randomness and choices, Overload/cast-event attribution, overlapping doubling providers, silence/removal, child effects and nested rollback. Add independent trace cases for lethal damage followed by healing and hero recovery before claiming fidelity.

These requirements are unfinished; Tyrande/Niri are not counted as written support by this investigation.

## Physical consumer consolidated validation

Cloudstrider and Treasuregill additions: **2528 tests passed**, zero failures/errors/skips; **22 bounded random games terminal**, no errors/caps. Fingerprint `513a6ac6eb74f69fe96d8090f0c75d09a2294fa97fd37cb2cca94bc214c178cc`. Receipts `runs/expanded_validation/validation-08f060d20f7c4dfa8e72b34d2aa8fb4d.json` and `runs/random_validation/summary-513a6ac6eb74-be2cc4ab5eb54c699d2fb8cd1b25bae8.json`; persistent log `runs/expanded_validation/spell-consumers-full.log`. Admission remains 367 spell definitions / 270 existing collectible spells.

Registry definitions: 811/1185, including two provisional consumers; saved implementation index: 811, explicitly flagging those two as provisional. Do not equate either written count with independently verified support. Shadow of Demise and repeated Battlecry absorption binding remain open. Full objective active; no training or deck search.

## Shared repetition frame implemented

`repeat_spell_effects` captures the selected operation body and context, creates separate mutable bodies per copy, preserves physical identity and the selected target, and uses balanced begin/end operations to defer death and winner settlement. Its depth is retained through manual or automatic choices and normal action rollback. Child events still drain between operations; Lifesteal healing is not combined across repetitions. Removed original targets cause later copies to fizzle rather than select a different target.

Fourteen focused behavioral tests pass: same target, minion/hero recovery from lethal damage, eventual lethal completion, manual and automatic Discover, a mortally wounded target across decisions, nesting, no extra play/payment publication, removed targets, failed-action rollback, separate Lifesteal, damage listeners and a single deathrattle after repeated hits. These are constructed scenarios, not independent pinned-client trace certification. The shared frame is not connected to Tyrande/Niri yet; their charge/cost/event semantics and finer target/death timing remain explicit gaps. Coverage stays 811 written definitions with two provisional consumers, 374 missing definitions. Prior full validation (2528 tests) predates this new frame.

Related regression run: 133 tests passed in 8.766 seconds, zero failures/errors. Includes the 14 new cases plus resolution, lifecycle and lifecycle choices, trigger choices, power sequences, event handling, damage batches, continuation, automatic choices and existing spell-consumer checks. The full suite has not been rerun for this revision.

## Tyrande and Niri provisional connections

Tyrande grants a player-owned three-spell repetition counter, consumed by hand spell plays. Niri doubles one-cost hand spells by paid cost, internal spells by physical card cost, and buffs played one-cost minions through the existing minion-play listener. Target/Choose One context and manual choices are retained. Both doubling providers currently overlap without multiplying spell copies; Tyrande regrant uses the greater remaining counter. These and countered-charge consumption, Niri self-play exclusion, cast-event/Overload attribution and detailed timing are explicitly provisional rather than externally proven rules. No Mercenaries or Battlegrounds behavior is imported.

Fifteen new consumer tests pass alongside fourteen shared-frame tests. Visible charges use feature schema v28, invalidating older policy schemas. Registry/index/catalog audit agree at 813 written definitions, 372 missing; four recent consumers remain flagged provisional. Full revision validation is pending. No training or deck search ran.

Consolidated repetition validation: **2557 tests passed**, zero failures/errors/skips; **22 random games terminal**, no errors/caps; feature schema v28. Fingerprint `943879692d00e2c4bfd8e2292164b890147210d540e8b36b7627e1376c7fe76b`. Receipts `runs/expanded_validation/validation-923fd3c8d397438386c7dfa094e4d697.json` and `runs/random_validation/summary-943879692d00-c1746adb706e4c19a4d5077b2531bbf2.json`; persistent log `runs/expanded_validation/spell-repetition-full.log`. Current written coverage remains 813/1185, including four provisional consumers, with 372 missing definitions. No full fidelity or training completion claim.

## Stored physical spells and Ursol's Aura

The turn scheduler now accepts a retained physical spell, exposes a controlled public view, and carries the stored reference into its resumable turn context. Each tick casts an independent copy with current Spell Damage and fresh target/branch selection. Ursol selects the highest current hand cost, removes the exact physical card without payment/discard/draw, and casts the generated `EDR_259e1` Aura token with payload and duration. Its explicit declaration dependency is included in the dependency report. Empty unbound tokens fail rather than inventing their contents. Five recent consumers remain provisional; this does not certify all casting attribution or enchantment semantics.

A [firsthand Ursol report](https://www.reddit.com/r/hearthstone/comments/1jwwt9d/fyi_about_ursols_inner_workings/) supports immediate hand removal and later repeated spell results, including different randomly selected branches on separate turns. A [survival report](https://us.forums.blizzard.com/en/hearthstone/t/still-dont-get-why-ursols-spell-effect-is-an-aura/150420) supports persistence after minion removal. Neither establishes all physical-enchantment behavior. The [Chronological Aura report](https://us.forums.blizzard.com/en/hearthstone/t/interaction-between-ursol-and-chronological-aura/164111) remains a patch-sensitive timing case requiring an independent trace.

Seventeen focused tests cover physical selection/current cost/ties, no immediate cast/discard, exactly three owner ends, silence/removal, independent schedules, current Spell Damage, automatic Discover, explicit unsupported-selection rollback, public JSON isolation, generated dependency admission and candidate Niri interaction. Consolidated: **2574 tests passed**, zero failures/errors/skips; **22 random games terminal**, no errors/caps. Fingerprint `dba32825d00e6fcad5cede034281391a5bd9e68f64f62ccbe18b27e9b6f7a38c`; receipts `runs/expanded_validation/validation-0bf15b89003240e19b2d18315777dae8.json` and `runs/random_validation/summary-dba32825d00e-bac32de1407c4fa5b4a400ceff921f8a.json`; log `runs/expanded_validation/stored-spell-aura-full.log`. Schema v29; coverage **814 written / 371 missing**, including five provisional definitions. No training or deck search.
