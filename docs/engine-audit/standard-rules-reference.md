# Standard rules reference and implementation checklist

Reviewed 2026-09-22. Research and source inspection only. No simulator imports, tests, games, training, or notebook cells were run.

## Scope and evidence

Target: regular Hearthstone Standard, all 11 classes. Exclude Mercenaries roles, abilities, equipment, and combat; exclude Battlegrounds tavern, economy, triples, and combat rules. A shared word does not establish shared behavior across modes.

The local catalog is already pinned by `data/standard/manifest.json` to patch **36.6.0.251952**, build **251952**, with legality cutoff **2026-09-18**, containing **1,185 collectible records**. These are existing local manifest values, not a new certification of live legality. `release_rules.json` explicitly leaves live bans unverified. Preserve this snapshot while building; do not silently mix it with newer wiki card lists. Generated tokens and explicit special pools require separate dependency coverage.

The wiki is community documentation. Its historical examples explain mechanics but do not make their cards Standard-legal. Some pages contain old statements or contradictory timing descriptions. Direct requests frequently returned HTTP 403; accessible search-indexed text was used. This is a partial reference review, not a claim to have read every recursive link or verified current-client behavior.

## Architecture implied by the reference

[Card properties](https://hearthstone.wiki.gg/wiki/Category:Card_properties) is an organizing taxonomy. [Ability](https://hearthstone.wiki.gg/wiki/Ability) distinguishes named abilities, unnamed operations, and broad effect categories. Implement these layers explicitly:

1. Imported identity: card ID, base stats, class, type, tribes, school, set and patch.
2. Shared rules: events, target selectors, operations, modifiers, duration and zone transitions.
3. Card definitions: compose those rules with specific amounts, conditions, targets and generated dependencies.
4. Exceptional behavior: explicit reviewed definitions where composition is insufficient.
5. Coverage: distinguish imported, implemented, dependency-complete and user-validated.

Keyword/text matching may help search the catalog. It must not authorize executable behavior or mark a card supported.

## Documented contracts and acceptance scenarios

These scenarios are specifications for future checks, not executed or passing tests.

| Rule family | Documented contract | Acceptance scenario |
| --- | --- | --- |
| Play versus summon | Playing a minion from hand and summoning it through an effect are distinct events. Ordinary effect summons do not activate Battlecry. | Compare playing a Battlecry minion with summoning the same minion; only the first runs its Battlecry. Both follow eligible summon hooks. |
| Transformation | Transformation replaces an existing entity; it must not acquire ordinary summon triggers simply because implementation reuses a summon helper. | Transform a minion while a summon listener is present; verify no summon reward. |
| Ongoing auras | An external aura remains when its recipient is silenced. Neutralizing its source removes the aura. | Damage a 1/1 buffed to 2/2 by an aura, then silence the recipient: it stays damaged, at 2/1. |
| One-time effects | Track consumption per effect instance; multiple separately granted effects need independent state. | Consume one of two different granted one-time triggers; the other remains available. |
| Draw versus generate | A successful ordinary draw can activate an on-draw effect; generating a copy in hand does not. Overdraw does not activate ordinary on-draw behavior. | Compare draw, generated copy, and full-hand burn of the same on-draw card. |
| Discard versus removal | Ordinary on-discard effects require discard from hand. Burning/removing a deck card is different; explicit card exceptions need their own definitions. | Discard a card with an on-discard effect, then separately remove it from deck; only the discard activates that effect. |
| Resurrection | Eligibility is based on recorded qualifying deaths, not a set of distinct card IDs. Ordinary resurrection creates a fresh base copy. | Record two deaths of one card and one of another; preserve three eligible death entries. Resurrection does not consume a death entry. |
| Reborn | Ordinary Reborn summons a fresh copy at one health with Reborn consumed; enchantments do not carry over. Deathrattles precede Reborn. | Resolve a Deathrattle that fills the last board slot before the Reborn summon attempt. |
| Poisonous | Requires actual damage to a minion; damage blocked by Divine Shield cannot poison it. | First hit removes the shield without destroying the target through Poisonous. |
| Discover | Pool criteria, current hero class, offered choices and destination are separate concerns. Discovering from deck can draw; discovering a copy creates one. | Check class restrictions, explicit cross-class pools, copy-versus-draw behavior, and hidden choice visibility. |
| Tradeable | Trading is not playing or an ordinary shuffle; enchantments and the relative ordering of other deck cards must survive. | Trade a buffed card with a known deck order; check preserved modifiers, distinct drawn card, and no play/shuffle trigger. Exact internal timing remains unresolved below. |

Sources for the table:

- [Game terms](https://hearthstone.wiki.gg/wiki/Game_terms), [Summon](https://hearthstone.wiki.gg/wiki/Summon)
- [Ongoing effect](https://hearthstone.wiki.gg/wiki/Ongoing_effect), [One-time effect](https://hearthstone.wiki.gg/wiki/One-time_effect)
- [On-draw effect](https://hearthstone.wiki.gg/wiki/On-draw_effect), [On-discard effect](https://hearthstone.wiki.gg/wiki/On-discard_effect)
- [Resurrection effect](https://hearthstone.wiki.gg/wiki/Resurrection_effect), [Reborn](https://hearthstone.wiki.gg/wiki/Reborn)
- [Poisonous](https://hearthstone.wiki.gg/wiki/Poison), [Discover](https://hearthstone.wiki.gg/wiki/Discover), [Tradeable](https://hearthstone.wiki.gg/wiki/Tradeable)

## Findings from current source inspection

These are static findings, not runtime results. No engine changes accompany this document.

- `expanded/systems.py::_silence` resets aura bookkeeping and clamps current health to base maximum before refreshing auras. For the documented 2/1 aura-buffed example, the written arithmetic would re-add a health point and produce 2/2. This conflicts with the reference scenario. Repair must preserve external aura contributions without accidentally preserving removable enchantments.
- `expanded/systems.py::_transform` delegates to `_summon`. Audit the entire helper chain before asserting a trigger bug; transformation needs a distinct event contract even if entity creation is shared.
- Tribe selectors in `expanded/systems.py` and `expanded/game.py` use direct membership checks. Centralize tribe matching before registering ALL-type cards; keyword flags and tribe membership are separate dimensions.
- `expanded/resolution.py` explicitly says its frames are not a complete Hearthstone scheduler. Existing per-operation settling is not proof of correct nested trigger, death, aura or choice timing.
- Existing Tradeable code preserves a Card instance and other deck ordering. Do not replace it with a generic shuffle. Exact insertion timing still needs resolution.

## Unresolved details and next implementation order

[Advanced rulebook](https://hearthstone.wiki.gg/wiki/Advanced_rulebook) describes nested sequences, phases, event resolution, aura updates and death processing. Its historical examples and the wiki's own warning about patch drift mean it is a research reference, not a current executable oracle. Do not reduce the scheduler to a universal FIFO or a universal end-of-card death sweep.

Tradeable's notes describe drawing then inserting, whereas its quoted 22.2 patch note describes insertion then drawing a different card. Preserve the established broad contract; verify observable timing with draw-trigger interactions before choosing a detailed algorithm.

Discover's historical rune restrictions, current generation exclusions, special pools and exceptions need patch-specific verification. Do not silently restrict random pools to the implemented subset: that changes the game being learned.

Next work:

1. Repair aura/silence accounting with explicit modifier semantics and prepared user-run scenarios.
2. Specify event phases and distinguish play, summon, transform, draw, generate, discard and remove operations.
3. Audit shared selectors and generated pools against the frozen catalog.
4. Attach card definitions only to reviewed rules and dependencies; leave unsupported effects explicit.
5. Complete the staged milestone under these contracts, then let the user run checks locally.

Remaining reference review includes detailed combat/targeting keywords, costs and enchantment ordering, hero/location/weapon lifecycles, Death Knight resources and deck restrictions, and expansion-specific mechanics used by the frozen catalog. Category listings already inspected are an index for this work, not evidence that every underlying mechanic has been reviewed.

## Implementation follow-up: 0.10.1

The silence/aura arithmetic issue above is now patched in the active engine and mirrored into the unfinished overlay. Six regression scenarios were added to `tests/test_expanded_systems.py`. Source syntax was inspected without imports. Runtime results are pending the user running notebook 08 after a kernel restart. This is a focused fix, not a complete ordered-enchantment or event-scheduler implementation. The staged milestone requires rebasing onto this version before installation.

## Implementation follow-up: 0.11

User reported all 185 checks passing for 0.10.1 (53.682 seconds). This does not validate the following new changes.

The event dispatcher now uses transient generator frames on an explicit stack. Child events produced by each effect operation finish before the next parent operation/listener or previously queued sibling. Listener snapshots are retained and eligibility is checked when dispatched. Nested settle calls remain deferred until the outer checkpoint. Frames are local to dispatch, never stored in observations or persistent game state.

Re-entrant triggers and choices inside triggers raise UnsupportedCard rather than silently applying unsupported timing. Public Game.step retains its existing rollback boundary. Full phase scheduling, self-trigger compensation, special Battlecry transformations, and damage batching inside individual complex operations remain unfinished. This is operation-boundary dispatch, not a claim of complete phase conformance.

Minion allocation is separated into _create_minion. Ordinary summon keeps its public summon event. Transform creates a fresh exhausted entity at the same position without reporting a summon/death or copying old buffs/readiness. Charge/Rush continue through existing legality rules. Historical special Battlecry transformation phases need separate implementation.

Eight new user-run scenarios cover child-before-parent/sibling ordering, removed/late listeners, deferred deaths, explicit unsupported cases and transformation identity/readiness. Notebook 08 expects 0.11 and discovers 193 test methods. Static parsing only; execution remains the user's responsibility. The unfinished 200-card overlay must be rebased before release.

References: [Advanced rulebook](https://hearthstone.wiki.gg/wiki/Advanced_rulebook), [Transform](https://hearthstone.wiki.gg/wiki/Transform-related).

## Implementation follow-up: 0.12

User reported all 193 checks passing for 0.11 (55.564 seconds). New runtime validation remains pending.

Event frames now contain copyable data rather than generators: listener snapshot/index, selected operations/index, context, active trigger identity, post-operation checkpoint, and choice permission. The stack is private game state and participates in Game.step rollback. Choices at top-level card-operation checkpoints and after-play event dispatch suspend both listeners and remaining card operations; choice resolution finishes suspended events before resuming the card. A second choice suspends again without replaying the previous operation. Terminal cleanup removes pending continuations.

Ten new user-run scenarios cover operation/listener order, consecutive choices, empty pools, invalid choices, rollback on failed resumption, cloned-state replay, hidden options, lethal effects, hand overflow, and a trigger choice halfway through a card. The eight 0.11 event checks remain included. Source AST parsing only; 203 prepared methods, none executed by the assistant.

This provides continuation infrastructure, not newly certified card definitions. Re-entrant trigger compensation is still unsupported. Choices at nonresumable event boundaries (including current death/turn pipelines and internal checkpoints inside complex operations) remain rejected. Exact game timing for particular Discover/Battlecry interactions still needs rule-specific review. The unfinished 200-card overlay remains blocked on rebase and validation.

## Shared-engine block in progress: 0.13-dev selectors

Shared Constructed identity selectors now handle dual tribes, ALL, untyped minions, spell schools and class membership. Composable CardSelector uses explicit AND conditions and printed cost bounds. Candidate order and duplicate entries survive selection; this does not authorize a generation pool or establish deck legality. Imported metadata is not parsed as executable text. Invalid selector domains fail explicitly; ALL is not a wildcard for keywords or arbitrary categories.

Integrated into active tribal targets, auras, filtered draws, Murloc buffs, Beast checks, Dragon-in-hand conditions, Elemental-play triggers, tribal discounts, school effects and ordinary class eligibility. Silence keeps printed tribe identity; transform changes identity via its replacement card. Distinct-type history counting and special generation exclusions remain separate unfinished contracts. Known tribe and school identifiers were compared to the frozen catalog by reading JSON only.

Twelve prepared scenarios include dual/ALL matching, school/class boundaries, combined filters, invalid inputs, aura/silence/transform interactions, and instance-preserving tribal draws. Syntax parsed, no runtime execution. Total prepared methods: 215. This is a development checkpoint, not a completed consolidated release; no new user run requested yet. Latest user-validated release remains 0.12 with 203 checks.

Sources: [All](https://hearthstone.wiki.gg/wiki/All), [Minion types](https://hearthstone.wiki.gg/wiki/Minion#Minion_types), [Multi-type minions](https://hearthstone.wiki.gg/wiki/Dual-type), [Spell schools](https://hearthstone.wiki.gg/wiki/Spell#Spell_schools). Only Constructed semantics are used; the Mercenaries school variants are excluded.

## Consolidated 0.13 continuation release

Persistent death-wave state captures removed entities, positions and written Deathrattle operations, then tracks operation and Reborn cursors. Each removal records a corpse once; choice resolution resumes remaining effects before Reborn. Persistent turn state captures sources and operations, then performs normal draw or end cleanup once. Decision resolution resumes events/deaths, then the turn, then a parent card continuation. These frames are copied with game state and hidden from policy observations. Reentrant settle calls are guarded; terminal resolution clears outstanding frames.

Sixteen new prepared lifecycle cases plus twelve selector cases yield 231 prepared methods. No tests, games or training were executed. AST parsing covers the expanded source and fixture files. Latest proven user-run baseline remains 0.12 (203 checks).

Limits: this preserves an experimental wave-based death model; it is not certification of nested death-phase exceptions. Self-trigger compensation, ordered enchantment records, special Battlecry transformation phases, full hero-card lifecycles and all generated pools remain unfinished. Arbitrary effect helpers with internal loops still need explicit continuation boundaries before they can safely introduce choices. Existing staged card overrides must be rebased against the new Lifecycle mixin rather than copied over active methods.

Next integration priorities are ordered modifiers and explicit generation dependencies, followed by re-entrancy mechanics once source-specific compensation behavior is established. Full Standard remains blocked, and the 291 active definitions have not increased merely because shared systems were added.

## Pool contracts: 0.14

GenerationPool takes explicit unique IDs and provenance, validates complete metadata, applies explicit selectors/exclusions, then checks implementation coverage before RNG use. It never manufactures a pool from the supported subset. This is a reusable enforcement contract, not a completed collection of Standard Discover rules. Callers remain responsible for reviewed patch-specific membership, self-generation exclusions, class/rune exceptions and dependencies; weighted instance sampling is a different contract.

The existing basic Shaman hero power uses its same four explicit totem IDs through this contract. Discover-from-deck uses a separate helper preserving unique identity offers and a physical deck index, including enchanted Card instances. Ordinary explicit summon effects validate fixed dependencies before their loop. No new card definitions or broad generation pools were enabled.

Ten new prepared checks cover missing effects/data, unchanged RNG on failure, deliberate filters/exclusions, ALL-type matching, sample size/uniqueness, empty pools, invalid configurations and deck-instance preservation. 241 prepared methods total. Runtime remains pending for both 0.13 and 0.14; no simulator execution by the assistant.

## Assistant-run validation baseline

User explicitly authorized local validation and requested a tracked full-project goal. The first import exposed Python 3.9 incompatibility in selector type annotations; postponed annotation evaluation fixed it. The complete 0.14 suite then passed: 241 tests, 59.623 seconds, zero failures/errors/skips. Receipt: runs/expanded_validation/validation.json. This validates prepared scenarios only; all remaining coverage limits above still apply. No training was launched.

### Combat after-attack boundary (candidate implementation)

Reference: https://hearthstone.wiki.gg/wiki/Advanced_rulebook#After_Attack_Event
(reviewed 2026-09-22). The documented Constructed combat sequence places the
After Attack event in the same phase as combat damage, before death processing;
it also restricts eligibility to triggers present at sequence start. This is a
community rules reference, not proof that every interaction in the frozen patch
has been reproduced. Candidate synthetic fixtures verify listener snapshots,
zero damage, silence, cancellation, mortally wounded listeners and simultaneous
hero defeat through after-attack fatigue. No Mercenaries or Battlegrounds timing
was imported. SI:7 Supplier is registered with six card-specific regression fixtures.
