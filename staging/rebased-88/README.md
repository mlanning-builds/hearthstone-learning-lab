# Rebased Standard card candidate

Regular Hearthstone Standard only; excludes Mercenaries and Battlegrounds.

This isolated candidate merges the original `../standard-200` card work onto the active 0.14 lifecycle, selectors and generation-pool engine. It is still incomplete. See [current derived status](STATUS.md) for card counts, validation and remaining work. The original overlay and active notebook engine remain unchanged.

## Validation

The [current status](STATUS.md) is generated only after a passing full-suite receipt matches the source fingerprint. The receipt lives in `runs/expanded_validation/validation.json`. A bounded eleven-game all-class training experiment and frozen-policy construction comparison are recorded in the root README. Passing checks is not independent Hearthstone conformance certification.

The merge retains resumable death/turn phases, shared ALL/dual-tribe matching, generation dependency checks and current summon/transform handling. Added staged history, Kindred, cost and card-effect handlers were adapted to these interfaces. Persistent end-of-turn damage now hits only the opposing hero, with an explicit regression.

Six inherited fixture failures were corrected using the frozen card metadata: untyped Egg/Redeemer/Wrangler fixtures were incorrectly used for tribe-dependent scenarios, and two weapons were treated as minions. Resurrection now uses the actual Undead Chillfallen Baron. These corrections do not establish complete card semantics.

## Remaining gates

Review card semantics and cross-system timing independently, especially play/counter history, nested effect choices and event reentrancy. Complete generated dependency closure and legality review. The requested 200-additional-card milestone remains unfinished; see STATUS.md for the derived remainder. Do not install the original `standard-200` engine files over the active engine.

This directory has a local data symlink to the frozen root catalog; it is not a standalone distributable package. Run validation from this directory using the root virtual environment. The active Jupyter notebook continues to use the root engine until an integrated release is prepared.

## Filter validation follow-up

Card-effect filters now reject unknown fields, unsupported operators, malformed numeric values and invalid Constructed tribe/type names before inspecting candidate cards. Empty decks and early nonmatches no longer conceal broken declarations. Missing stats do not count as zero. Held-card conditions use the same declaration validation.

Six additional regression scenarios cover those failures plus enchanted instance stats, ALL tribes, physical duplicate deck copies and unchanged random state when no draw is possible. This validates the internal filter contract; it does not supply independent reference outcomes for every card using it.

## Stat-setting spell extension

Added DINO_403 (Devilsaur Mask), DINO_432 (Panther Mask), and EDR_252 (Mark of Ursol) from the pinned Standard snapshot. Shared target stat-setting replaces previous stat changes, preserves external aura contributions and prevents overwritten temporary attack from being subtracted at turn end. Five scenarios cover attack readiness, damaged targets, drawing, owner-dependent stats, silence/aura interaction and temporary expiration.

Sources: frozen `data/standard/cards.json` records and hashes; [official Panther Mask card library](https://hearthstone.blizzard.com/es-es/cards/118712-panther-mask/), [Mark of Ursol](https://hearthstone.wiki.gg/wiki/Mark_of_Ursol), and [advanced rulebook enchantment ordering](https://hearthstone.wiki.gg/wiki/Advanced_rulebook). General ordered enchantment recalculation and dynamic conditional modifiers remain separate engine review work; these scenarios are not blanket certification of all interactions.

## Trigger/card-copy extension

Added DINO_435 (Crater Experiment), EDR_853 (Broll Bearmantle), and JAIL_440 (Tower of Ghouls) using existing explicit Kindred, spell-completion and damage triggers. The fixed companion pool and Frail Ghoul dependency were already registered. Six scenarios check copied hand buffs, Kindred tribe requirements, spell completion, a killed listener, Ghoul expiry, Divine Shield and Silence. Dynamic replacement of future Animal Companions remains unimplemented alongside the corresponding unsupported replacement cards.

Evidence: exact pinned Standard metadata and [Crater Experiment reference](https://hearthstone.wiki.gg/wiki/Crater_Experiment). Card-specific scenarios are not independent whole-game conformance evidence.

### Reviewed spell-damage discrepancy

TIME_856 (Algeth'ar Instructor) is now implemented with an explicit +2 value in `SPELL_DAMAGE_VALUES`. The raw snapshot remains unchanged: its numeric `spellDamage` field is 1, while its printed text and [official card library](https://hearthstone.blizzard.com/en-gb/cards/119632/) specify +2. Three scenarios cover actual spell damage, stacking, Silence, removal and ownership. Future metadata conflicts require explicit review; no text-parsing fallback was added.

## Hero Power completion event

Added END_008 (Enduring Roach), EDR_470 (Barkshield Sentinel) and CORE_DRG_256 (Dragonbane) through the shared `hero_power_used` event. Base power effects and death processing precede its listener snapshot. Owner and Silence filtering use the existing trigger dispatcher. Refreshing mana respects locked crystals and does not refresh the power itself.

Hero victory checks are deferred until the complete power sequence finishes, including after-use effects. Evidence: the [advanced rulebook](https://hearthstone.wiki.gg/wiki/Advanced_rulebook) describes Inspire-phase effects preceding the sequence's win/loss check. Eight scenarios cover temporary mana preservation, ownership, Silence, dead listeners, health changes, random damage with one target, mana limits and lethal timing. This does not certify every phase exception elsewhere in the engine. Choice-producing callbacks at unsupported power boundaries still raise and roll back rather than skipping their effects.

## Bounded random-game validation

`tools/stress_candidate.py --engine-root staging/rebased-88 --seeds 10 --max-actions 500` completed 110 random legal-action games across all 11 classes in 76.963 seconds: 110 terminal, zero capped, zero exceptions. The exact source fingerprint and per-game outcomes are saved in `runs/random_validation/summary.json`. This checks execution and invariants on implemented decks, not card-rule correctness or playing strength. It does not train or rank decks.

Failures save initial decks, game seed and selected actions. Pass a failure JSON path with `--replay` to replay it against the same source fingerprint. Five tool checks passed, including valid replay and exact failing-action reporting.

User entry point: `notebooks/09_candidate_random_validation.ipynb`. Its default is 11 games with a 500-action cap and visible progress. The notebook targets this candidate explicitly and leaves notebook 08 unchanged. Its cells were syntax-checked; the underlying runner was executed directly for the results above.

## Secret-history observation privacy

Opponent play history and current/previous spell lists now use `SECRET` placeholders for Secret identities. Public spell-school history contains only schools from identified spells and carries an explicit `_hidden` flag when its true contents are incomplete. Owner observations and internal rule histories retain the actual identities. Secret-reveal events remain public; historical placeholders are conservative even after a reveal.

Four regression scenarios cover two distinct same-cost Secrets producing identical opponent views, owner access, previous-turn history and nonmutation. This closes a demonstrated information leak; it is not a complete audit of all hidden-information inference channels. Any training adapter must retain this visibility boundary rather than reading Game internals.

## Policy interface foundation

`expanded.environment.PolicyEnvironment` exposes a turn-based, two-player decision interface: actor-visible observation, variable-length legal action candidates, an all-valid mask over those candidates, per-player terminal rewards, and separate termination/truncation flags. A policy scores the returned candidates; action indices are local to that decision, not a fixed global action vocabulary. Revisions reject stale decisions across actions and resets. Reset requires an explicit action cap and seed.

Default construction invokes the full-Standard readiness gate, which currently rejects use. `PolicyEnvironment(experimental=True)` explicitly enables candidate-only validation. This does not implement training, an encoder, policy checkpoints or deck optimization. Those remain required for the full goal. Six scenarios verify deterministic action sequences, actor switches, hidden hands, stale/invalid actions, truncation and observation-copy isolation.

```python
from expanded.environment import PolicyEnvironment
from expanded import random_deck

env = PolicyEnvironment(experimental=True)
decision = env.reset([random_deck('MAGE', 31), random_deck('DEATHKNIGHT', 53)],
                     seed=13, max_actions=300)
# A future policy chooses among decision['actions'] using its observation.
# Do not treat an action-cap truncation as a terminal draw during learning.
```

## Either-player end-turn listeners

Added TIME_054 (Time Skipper) and JAIL_883 (Activated Golem) through `END_EVERY_EFFECTS`. The turn frame gathers either-player listeners together with owner-only listeners and retains resumable operation boundaries. Time Skipper's Coin goes to the ending player, regardless of the minion's owner. Ordinary owner-only effects remain restricted; Silence and removed listeners are skipped.

Six scenarios cover both turns, opposing copies, Reborn, Silence, owner-only isolation and a listener killed by an earlier effect. Rules text comes from the frozen catalog; see [Activated Golem](https://hearthstone.wiki.gg/wiki/Activated_Golem). The candidate orders ordinary captured minion listeners by entity creation order. The [advanced rulebook](https://hearthstone.wiki.gg/wiki/Advanced_rulebook) documents trigger priorities and historical dominant-player exceptions; reproducing all such patch-specific exceptions remains unresolved. These checks do not certify complete cross-player timing fidelity.

## Paired policy evaluation

`expanded.evaluation.evaluate_pair` runs two fixed decks/policies twice per supplied seed, changing which player starts while retaining deck identities. Policies receive actor-visible decisions only. Reports retain each game, source fingerprint, exact decks, seeds, action budget and terminal reasons. Capped episodes are excluded from wins/draws/losses and reported separately; a completed-game score is absent if no games finish. Truncation may bias that score and no best-deck claim is made.

Callers must explicitly supply seeds, action cap and policies. Duplicate seeds and invalid actions are rejected. Policy randomness is caller-controlled; matching game seeds does not imply identical event streams after different actions. Full Standard remains gated by default. Four checks cover starting hands/Coin assignment, paired scheduling, truncation, invalid inputs and complete fatigue-ended games. No optimization or training was executed.

## Conditional combat values

Added END_022 (Time-Twisted Seer) and JAIL_202 (Spiderling) from the pinned catalog. Explicit conditional registries supply damaged-only Spell Damage and owner-turn hero Attack. Values are calculated when queried, so healing, Silence, removal and turn changes do not leave cached bonuses behind. Four scenarios cover state transitions, stacking, actual spell damage, hero attacks and opposing turns.

TIME_606 (Quel'dorei Fletcher) remains unsupported pending review of its zero-cost Hero Power aura's ordering against cost increases. No assumed ordering was added merely to increase card counts.

## Frozen token parsing cache

Token parsing is cached by actual compressed snapshot bytes plus the requested token IDs (bounded to two entries). Every registry call still reads current files and checks reviewed record hashes. Returned registry data is deep-copied, including legacy/local token records, so a caller cannot alter another game's metadata.

Four checks cover changed file contents, changed requested IDs, mutable-record isolation and reuse of identical parses. A local ten-iteration sample measured registry loading at 0.7278 seconds before versus 0.1447 after including the first cold parse; ten game constructions measured 0.7162 versus 0.0787 seconds. These are small local startup benchmarks, not training-throughput guarantees. No training was run.

## Incoming-damage modifiers

Added TIME_060 (Quantum Destabilizer) and CATA_208 (Selfless Protector) using an explicit incoming-damage registry, based on their frozen card records. Positive damage is modified before the existing prevention/damage event path; zero damage stays zero, Immune and Divine Shield prevent damage, and Silence disables the printed modifier. Spell bonuses are included before incoming multiplication.

Six scenarios cover distinct double/extra values, zero damage, prevention, Silence, spell scaling and simultaneous combat retaliation. Other source/target modifier families and their relative priority still need implementation and independent review; this is not a claim that all Hearthstone damage-layer interactions are complete.

## Shared-type and hand tribal buffs

Added TLC_441 (Ready the Fleet) and MEND_305 (Nurturing Nature) from the pinned Standard records. The shared-type effect includes its explicit target even if untyped; other friendly minions must share a printed type through the shared ALL/dual-type selector. Random hand buffs select actual eligible card instances, including ALL-type minions, without touching noneligible cards.

Five scenarios cover untyped targets, dual/ALL matching, enemy exclusion, hand/board buffs and friendly-Beast target availability. This reuses existing target legality and persistent hand-stat bonuses; it adds no inferred rules-text execution.

## Fixed-summon spell extension

Added CATA_452 (Spellweaver's Brilliance), TIME_006 (Mirror Dimension), and TLC_622 (City Defenses). Their generated cards CATA_452t, TIME_006t1 and TLC_622t are explicitly registered, hash-pinned and playable when moved to hand. Steadfast Security uses the existing damage trigger dispatcher; Mirror Dimension uses the shared ALL-aware tribe selector; Brilliance uses the existing per-turn spell-damage counter.

Five scenarios cover base/conditional summoning, a one-slot board, per-hit Security attack growth, Silence and discount reset. Records come from the frozen patch snapshot. These tests do not independently certify global damage-counting, trigger compensation or summon timing exceptions.

## Resource-spending summons

Added CATA_135 (Mossbinding) and CATA_465 (Chow Down), with hash-pinned CATA_135t and CATA_465t dependencies. Shared operations retain the actual summoned entities so existing copies cannot accidentally receive the buff or keyword. Mossbinding spends remaining mana after payment; Chow Down spends eight Corpses once when the threshold and a summoned recipient exist.

Five scenarios cover payment versus effect spending, no extra mana, one free board slot, old/new recipient separation and insufficient Corpses. Text and token stats come from the frozen snapshot. Full-board cast legality, global mana-spend triggers, nested summon-event choices and exceptional Corpse interactions remain part of the broader engine review; these fixtures do not certify those unfinished systems.

## Random validation after resource-summon additions

The 402-card candidate (fingerprint `ecbd9b91096ced7b44b5bfa7c6f29868401550461b2699ee4a13a5d5b3aa3ab2`) completed 110 seeded random games in 55.760 seconds: zero exceptions, zero capped games. Separate archived reports preserve this evidence when later runs update `summary.json`.

The runner now records per-game and aggregate played/summoned card IDs, unseen implemented collectibles, and its own source hash. An additional 11-game coverage run completed without errors: 168 distinct played IDs, 138 summoned IDs (including tokens), and 236 of 402 implemented collectibles not observed in either category. The aggregate sets were checked against the per-game sets; all eight tool tests passed. Seeing a card is not proof its conditions or interactions were exercised. Use these counts to identify missing validation cases, not as full-card correctness certification.

### Shared after-attack boundary

Combat now snapshots trigger listeners before the proposed attack, queues the
`minion_attack` / `attacked_self` event after simultaneous damage, and resolves
combat events before removing mortally wounded minions. Hero defeat is deferred
until that combat sequence finishes, allowing after-attack fatigue to produce a
draw. Cancelled attacks produce no after-attack event. Seven synthetic fixtures
cover these boundaries, silence, zero damage, and listener eligibility. They do
not certify a new collectible card. Attack redirection, nested choices, forced
attacks and all card-specific survival conditions still require separate review.

### SI:7 Supplier

CAP_003 now uses the shared self-attack trigger to draw one card. Six card
fixtures exercise a legal play, mana cost, Stealth, summoning sickness, attacking,
lethal retaliation, defending, Silence and a full hand. Its printed definition
is hash-pinned to the local catalog. This adds one implementation, not a claim
that the full combat system or Standard pool is certified.

### Defender and damage-triggered cards

Wrathspike Brute uses a shared `defended_self` event filter for hero and minion
attacks; taking spell damage alone does not activate it. Gorishi Tunneler uses
`attacked_self` to damage the opposing hero. Tortolla composes the existing
damage event with armor and self-buff operations. Nine focused fixtures cover
combat targets, lethal retaliation, lethal defense, silence, repeated damage and
Divine Shield prevention. These definitions use the frozen Standard catalog and
share the documented combat scheduler limitations.

### Random validation: bounced basic totems

The 110-game run at fingerprint `2dc6f1fe1d33` found two errors (108 games
completed, zero capped): a returned NEW1_009 could not be replayed. All four
basic totems are now explicitly playable from hand. A regression fixture covers
each one; both original failing action prefixes replay successfully against the
repair. Original failure files remain unchanged, with the cross-version repair
receipt in `runs/random_validation/totem-fix-replay.json`. The earlier random
run observed 365 of 406 implementations, which is not effect coverage. A complete
post-fix random run remains separate from these prefix replays.

### Generated minion hand-play audit

A systematic return-to-hand check found 16 additional registered minions missing
from the explicit playable-token list. Those reviewed tokens now use normal
minion play dispatch. The regression iterates every registered noncollectible
minion, summons it, returns it to hand, and legally plays it again. This proves
that path for the registered pool; it does not prove that every generated card
in Standard is registered, nor that every token's other interactions are correct.
It does not increase collectible coverage.

Post-repair validation at `2f75ffb841c7`: all 110 random games completed,
zero errors or action caps. The suite passed 430 tests, including the
return-to-hand path for all 54 registered noncollectible minions.

### Lowest-Health enemy damage

Lava Flow and Renewing Flames share one lowest-Health selector, with each hit
represented as a separate resumable operation. Each hit reselects from the enemy
hero and minions; Armor does not contribute to Health, and ties use the seeded
RNG. Existing damage handling supplies Spell Damage, shields and Lifesteal.
Six fixtures cover reselection after deaths, hero Armor, Lifesteal, shields,
Spell Damage and tied candidates. Full immunity/redirect priority and all nested
interaction combinations remain part of the wider fidelity audit.

### Call of the Wild (Core)

CORE_OG_211 uses three ordered fixed summons: Huffer, Leokk, then Misha. All
three dependencies were already registered. Four fixtures check summon order,
printed cost, aura-adjusted stats, Charge, seeded RNG stability, one/two free
board slots and Silence removing Leokk's aura. This implements the pinned Core
record, not the original Wild collectible or adventure-specific extra summons.
Order reference: https://hearthstone.wiki.gg/wiki/Template:Call_of_the_Wild_notes
The broad summon-event scheduler and full-board spell legality audit remain
separate from these concrete fixtures.

### Hand-position and held-card conditions

Precise Shot snapshots whether it occupies the unique center of the hand before
it is removed; even-sized hands have no exact center. Darkscale Broodmother
uses an explicit held-Dragon condition after leaving the hand, so it cannot count
itself. Its mana refresh reuses the existing locked-crystal-aware operation.
Seven fixtures cover these distinctions and Spell Damage. The generic held-card
operation currently uses the existing explicit filter semantics; current-cost
conditions and while-held histories need separate implementation and review.

### Held-card cost evaluation

Held-card filter calls now explicitly pass the hand owner and use the engine's
current payable cost, including active discounts and timed increases. Deck
filters retain their separate stored-card cost behavior. Five regression cases
cover reductions, increases, expiration, combined adjustments and ensuring deck
queries do not inherit hand effects. This fixes an existing threshold inconsistency
for FIR_961. Full ordered cost-enchantment behavior is still under review;
sharing `_cost` ensures consistency, not complete cost-system certification.

### Precursory Strike and Flames of the Firelord

These spells compose existing damage, filtered drawing and current held-cost
checks. The shared conditional operation now permits a single alternative effect.
Eight focused cases cover qualifying card types, discounted thresholds, missing
minions in the deck, base/bonus damage and Spell Damage. Full ordered cost effects,
targeting exceptions and nested trigger interactions remain wider audit items.

### Held-condition targeting and Weaver of the Cycle

A declarative held-target map now gates target choices through the same held-card
predicate used during effect resolution. Weaver of the Cycle uses it to require
a character target only with a qualifying held spell. Six fixtures cover inactive
play, card types, current-cost reduction, target requirements, Stealth/Elusive and
Battlecry exclusion from Spell Damage. Future conditions involving the played
card's own type or while-held history require explicit exclusion/timing review;
this first map entry checks spells for a played minion.

### Brood Keeper and Nightmare Slicer

Brood Keeper composes held-Dragon evaluation with weapon equipping. Its generated
Nightmare Slicer is imported from the pinned all-card snapshot, hash-reviewed and
registered for play from hand as well as direct equip. Six fixtures cover missing
and held Dragons, board-only Dragons, cost, weapon replacement after attacking,
token hand play, and summon versus Battlecry. The raw token record stores usable
durability in its Health field; the existing weapon normalization handles this.

### Thassarian and Disciple of the Dove

Thassarian reuses random enemy damage for Battlecry and Deathrattle, with existing
Reborn resolution. Disciple of the Dove composes minion-filtered draw followed by
a hand Health buff. Six fixtures cover successive Deathrattles around Reborn,
Silence, direct summon, draw-before-buff ordering, absent deck matches and retaining
the buff when the held minion is played. Full simultaneous-death and nested-event
conformance remains subject to the broader scheduler audit.

### Dimensional Weaponsmith and weapon hand buffs

A shared hand Attack operation supports minions and weapons. Playing a weapon now
passes its stored Attack bonus into equip; generated direct equips default to
printed Attack. Six fixtures cover eligible types, stacking, minion play, weapon
combat, existing equipment exclusion and replacement reset. This addresses Attack
bonuses only; a general weapon enchantment stack and all copying/replacement
interactions still require review.

### Skittish Saucier and hand adjacency

Play context records the two neighboring card identities before removing the
played card. Skittish Saucier discounts only those identities still present in
hand. Six fixtures cover interior and edge positions, no neighbors, eligible
card types and direct summons not firing Battlecries. General hand rearrangement
and simultaneous hand-trigger semantics remain separate audit items.

Random validation at `661d0f51cf57`: 110 completed games, zero errors and
zero caps; 36 of 419 implementations were not observed in play/summon events.
Ten external tooling/observation checks also pass, including own-hand weapon
buff visibility, hidden-hand isolation and current-cost consistency.

### Hero damage this turn

Players now retain a public hero-damage counter that resets for both sides at
every turn boundary. Endtime Survivor uses it rather than current missing Health.
Seven fixtures cover actual damage, Armor absorption, subsequent healing, zero
damage, opponent damage, reset and observation visibility. Healing performed by a
player still needs explicit source attribution; this counter does not stand in
for healing or hero-Health-change history. Hero immunity and replacement-specific
counter exceptions remain part of the broader audit.

### Healing source attribution

All explicit candidate healing calls now identify the player responsible for the
healing. Actual restored Health increments that player's public turn counter;
healing an enemy does not credit the enemy, and defensive Lifesteal credits the
defender. Six fixtures cover these distinctions, overhealing, no-op healing,
turn resets and observation visibility. The unmodified legacy engine remains
separate. Direct private `_heal` calls without a source do not infer ownership.
Healing conversion, amplification and hero maximum-Health changes remain wider
fidelity work; this counter records the existing healing operation's result.

### Priest of An'she

The pinned Core minion uses attributed healing history to conditionally buff
itself. Six fixtures cover absent healing, healing an enemy or minion, zero actual
restoration, receiving an opponent's healing and Silence removing the buff.
Other healing-related cards still require their own mechanics: permanent healing
bonuses, forced attacks/Colossal, or complete Discover/generated pools.

### Cleansing Cleric review: unresolved Lifesteal grouping

Cleansing Cleric remains unregistered. A reproducible synthetic probe at
`runs/semantic_probes/area_lifesteal.json` shows that two simultaneous one-damage
hits currently create two separate Lifesteal heals. A naive per-heal +2 modifier
would therefore restore six Health, whereas a combined-heal interpretation would
restore four. Existing additive-healing-free checks cannot distinguish those
semantics. Community discussion suggests grouped area Lifesteal, but this is not
yet verified for the pinned patch; do not treat that discussion as conformance
proof. Sequential damage and simultaneous area damage must be tested separately
before enabling permanent healing bonuses.

Research leads:
- https://hearthstone.wiki.gg/wiki/Cleansing_Cleric
- https://hearthstone.wiki.gg/wiki/Healing
- https://www.reddit.com/r/wildhearthstone/comments/1reuhq6/cleansing_cleric_spirit_lash/

Direct wiki page retrieval returned HTTP 403 during this review; search snippets
and community discussion did not settle the exact aggregation boundary.

### Minion-sourced effect Lifesteal

Minion damage effects now read Lifesteal from their source's current keywords,
including attack triggers and Deathrattles. Spell contexts retain their own
Lifesteal flag. Prevented damage no longer emits a zero-amount heal event. Five
fixtures cover granted Lifesteal, Deathrattle damage, Reborn losing the grant,
after-attack damage, Silence and Divine Shield prevention.

Reference inspected: https://raw.githubusercontent.com/jleclanche/fireplace/master/fireplace/actions.py
Its Damage action applies Lifesteal from the damage source for each hit. This
supports source-keyword propagation but is not pinned-patch proof of additive
healing behavior. No reference code was copied. Cleansing Cleric's aggregation
review remains open; the previously saved diagnostic is historical evidence.

### Minion-sourced effect Poisonous

Effect damage now reads Poisonous from its minion source alongside Lifesteal.
Eight fixtures verify high-Health destruction, Divine Shield, immunity, zero
damage, Silence, heroes, Lifesteal amount and unrelated spell isolation. The
previously inspected Fireplace Damage action also propagates Poisonous from its
source; this implementation uses the candidate's existing damage and death rules.
Complete Poisonous destruction timing among all nested triggers remains covered
by the broader unresolved scheduler audit, not claimed by these fixtures.

### Spiritspeaker and fixed summon choices

A fixed-summon choice now uses the resumable player-choice path, separate from
random generation and deck Discover. Spiritspeaker offers all three reviewed
Animal Companions. Six fixtures cover every option, suspended legal actions,
invalid-choice rollback, private option observation, Charge and direct summoning.
The fixed UI order is a deterministic engine convention. Full-board choice
presentation and all nested summon-trigger interactions remain fidelity audit
items; this does not certify every choice-generating card.

### Ancient Stegodon and self-effect choices

Self-effect choices retain their source entity identity and expose a readable
label for each option without exposing internal operation declarations. Ancient
Stegodon uses this to choose Taunt, Poisonous or +1/+1. Six fixtures cover the
three outcomes, distinguishable private labels, one-time mana payment, frame
completion and Silence. The labels are engine presentation, not newly invented
collectible card records. Complex source removal/control changes during nested
choices remain part of the broader choice-lifecycle audit.

### Agent of the Old Ones and hand transformation

A private hand choice retains selected entity identity; resolution replaces that
card at its existing position with a fresh Coin and no inherited buffs. Owner
observations expose hand-option UIDs so identical card names with different buffs
remain distinguishable. Six fixtures cover replacement, privacy, an empty hand,
Coin play, non-discard semantics and invalid-choice rollback. General hand
transform triggers, public animation information and every enchantment exception
remain separate fidelity review items.

Choice milestone validation at `f1988b10d663`: all 110 random games completed
with zero errors or action caps; 42 of 424 implementations were not observed.
All 13 external tooling tests pass, including the three new choice kinds through
PolicyEnvironment rather than only direct engine calls. This remains validation,
not training or full Standard conformance.

### Malevolent Mutant and hand copying

Shared card filters now support spell schools. Malevolent Mutant offers a private
choice among Fel spells remaining in hand and copies the chosen entity with its
modifications and a fresh identity. Six fixtures cover school filtering, preserved
cost adjustments, independent copies, empty choices, hand capacity and opponent
privacy. The full candidate suite passes 546 checks at `be16ab177ed1`.
Public generation animations and unusual enchantment-copy exceptions remain
fidelity audit items; these fixtures do not certify every copying card.

### Tricky Satyr and opponent-hand copying

Tricky Satyr compares current costs in the opponent's hand, chooses randomly
among tied cheapest entities, and uses the existing independent hand-card clone
operation. Six fixtures cover modified costs, preserved minion buffs, tied
entities, an empty opposing hand, capacity and private copied identity. This
implements the pinned catalog's Battlecry; exhaustive enchantment exceptions and
alternative resource costs remain part of the broader cost/copy fidelity audit.

### Backward zone transition correction

The shared shuffle-leftmost-hand operation now removes card enchantments when
moving the card back to the deck, while retaining entity/card identity. This
follows Blizzard's documented zone direction rule:
https://hearthstone.blizzard.com/en-us/news/21965466
Six regression fixtures distinguish this backward move from a forward draw,
cover redrawing the cleaned card, unaffected other hand cards and privacy.
This is a targeted correction, not a complete audit of all zone transitions.
Mimicry remains unimplemented pending verification of burned-draw copying and
its timing; community reports alone were not treated as conformance evidence.

### Sheltered Survivor and private shuffle choices

Sheltered Survivor suspends its Battlecry for a private hand-entity choice,
shuffles the selected card without its enchantments, then resumes the draw.
An empty hand skips only the choice: the draw still occurs and may cause fatigue.
Six fixtures cover that ordering, duplicate identities, cleanup of buffs,
privacy, invalid choices, and empty hand/deck behavior. Normal shuffle removes
enchantments; the existing Tradeable action remains a separate preserving path.
General shuffle-trigger quests and all enchantment exceptions are not yet
certified by this implementation.

### Policy choice ownership and integration validation

PolicyEnvironment now routes pending choices to their explicit owner instead of
always to the current-turn player. The acting policy receives that owner's
observation; after resolution, normal turn ownership resumes. External tooling
fixtures cover opponent-owned private choices as well as hand-copy and
hand-shuffle choices through revision-checked policy actions (16 tooling tests).

Before this interface-only correction, random validation at `003239beb639`
completed all 110 games across all classes with zero errors or caps; 29 of 427
implemented collectibles were unobserved. That receipt applies to its recorded
fingerprint, not the later interface edit. No training was run; random completion
does not establish Hearthstone conformance or policy quality.

### Paired evaluation reporting

`evaluate_pair` now includes results by starting player, individual seed-pair
scores, the number of complete pairs, and a standard error across those pairs.
The two games sharing a seed are treated as one sampling unit. A single complete
pair has no standard-error estimate. The original completed-game score remains
available for compatibility, with its truncation warning.

`action_cap_score_bounds` gives the lowest/highest overall score possible if
unfinished games scored 0/1. These are not confidence intervals. Incomplete pairs
are excluded from the paired estimate and can cause selection bias; no statistic
here establishes best-deck status, unseen-opponent strength or simulator fidelity.
Six analytic fixtures cover starting bias, pair-level variance, partial pairs,
draws, all-capped runs and invalid pair structure. No learning run was launched.

### Shadowcloaked Assailant and shared hand shuffling

Assailant chooses one random opposing hand entity whose card ID matches a card
still held by its controller. It moves only that entity, removes enchantments,
and does not draw or discard. Playing Assailant itself does not count as holding
it. The normal shuffle helper is now shared with Crystal Tusk and Sheltered
Survivor; Tradeable remains separate. Six new fixtures exercise matching,
duplicates, selection, empty hands and enchantment cleanup.

The one-card/random selection behavior is documented in the card's wiki notes:
https://hearthstone.wiki.gg/wiki/Shadowcloaked_Assailant
This is reference evidence rather than a captured official-client replay. Public
animation/reveal details and generalized shuffle-trigger interactions still need
fidelity review; the implementation is not a full conformance certification.

### Explicit deck-insertion history

Normal hand shuffles and trades now record public event metadata: turn, actor,
destination, card count and operation kind. Setup/mulligan shuffling is excluded.
Assailant attributes the action to its controller while recording the destination
as the opposing deck. Observations copy this metadata without card identities or
positions. A future batch insertion can represent multiple cards in one event.

This is an event ledger, not a certified quest/payoff counter. Knockback's wiki
notes distinguish shuffle instances from card counts:
https://hearthstone.wiki.gg/wiki/Knockback
Trade and opponent-caused payoff eligibility still require stronger rule evidence;
Knockback, Underbrush Tracker and the shuffle quest remain unregistered. Six
fixtures cover attribution, trades, setup exclusion, privacy, counts and invalid
records. Future insertion effects must explicitly record their event boundary.

### Run-specific notebook reports

The random validator writes each report to an exclusive UUID archive, returns
its path and run ID, and atomically updates the optional latest-report file.
Notebook 09 reads its subprocess's exact archive and verifies identity instead
of reading a potentially overwritten latest report. Two tooling fixtures verify
archive independence and unchanged caller input. An 11-game, one-action smoke
run verified the handoff; all games were intentionally capped, not completed.

### Mythical Runebear and current-Attack thresholds

Runebear uses a shared source-Attack threshold operation followed by the existing
self-copy operation. The Battlecry sees current Attack, including hand buffs and
active auras. Copying excludes the source's aura contribution before the copy's
own auras apply. Six fixtures cover the threshold, hand stats, auras disappearing,
board capacity, health-only buffs and summons without Battlecries. General
copying of every attached enchantment/deathrattle remains an unresolved engine
audit area; this addition does not certify that broader lifecycle.

### Copy lifetime correction

Self-copies now retain tracked temporary Attack expiration, Silence, and the
end-of-turn expiration flag. Previously an until-end-of-turn Attack bonus could
become permanent on a copy. Four regressions cover temporary versus permanent
buffs, silenced aura sources and expiring copies. This does not yet model every
possible enchantment or Frozen/copy timing interaction; the general copy audit
remains open. See Blizzard's zone-copy rule reference above for enchantment
retention and the wiki Copy/Faceless Manipulator notes for Silence inheritance.

Copy creation now installs the tracked copied state before board insertion and
its first aura refresh. This prevents a silenced health-aura source from briefly
buffing (and potentially healing) other minions while its copy is constructed.
Two additional fixtures cover the unwanted-healing case and copied damage under
an external health aura. Copied damage is restored after initial aura health is
applied, so a living source sustained by that aura does not produce a dead copy. Summon identity/exhaustion remain fresh; broader copy
state such as Frozen and unmodeled enchantments remains an open audit item.

### Endangered Dodo

Dodo checks its controller's current Health, ignoring Armor, then applies +5/+5
before copying itself when Health is at most 10. A full board still allows the
original buff but prevents the extra summon. Six fixtures cover the threshold,
Armor, opponent Health, hand buffs and capacity. This uses the shared copy state
implementation and retains its documented unresolved general-enchantment limits.

### Malignant Horror (Core)

The pinned Core version now uses the end-turn snapshot and corpse-funded
self-copy operation. Six fixtures cover a single activation per original source,
shared resources between sources, insufficient Corpses, Silence, opponent turns,
and copied damage/buffs/Reborn. The implementation requires board space before
spending; that full-board resource behavior remains a reference-verification
item, not a certified rule. No claim of complete card-interaction conformance is
made by registration. Reference identity: the Core card, not the Wild-only
original printing (https://hearthstone.wiki.gg/wiki/Malignant_Horror_(Core)).

### Specter Specialist

The keyword-or-copy operation grants Reborn when absent, otherwise summons a
copy with the tracked current minion state. Six fixtures cover both branches,
Reborn death resolution, an empty board, board capacity and the absence of a
second Battlecry. Copies currently use the position immediately right of the
target; exact client placement remains reference verification work, as do the
existing general-copy fidelity gaps. This uses the pinned CAP_804 record; it does
not independently establish live release or Standard eligibility.

### Omen of the End

Omen checks its controller's deck at Battlecry resolution and removes up to five
cards from the top of the opposing deck. This is neither draw nor minion death:
there is no fatigue for missing cards, no hand insertion, and no Corpse/death
history entry. Six fixtures cover top order, the condition, short/empty decks,
modified card entities and separation from death effects. Public destruction
animation/reveal details remain part of the observation fidelity audit; the
current event reports each removed card identity.

### Crumblecrusher and typed destruction

Crumblecrusher uses separate minion, location and weapon destruction operations.
Fixtures verify one enemy of each available type, independent empty-type handling,
friendly objects surviving, and minion Reborn. The current operation sequence
settles minion death before location and weapon destruction; exact cross-type
client death/trigger ordering remains a fidelity-verification item.

The existing top-deck removal effect also now logs a card ID for modified Card
entities, fixing non-JSON observation data after removal. A fixture exercises
that case through the actual card and serializes its observation.

### Bitter End

Bitter End snapshots the target and neighboring board slots, freezes minions in
that snapshot, then destroys those already damaged before death resolution.
Locations occupy a slot but are not frozen or destroyed. Six fixtures cover
healthy survivors, damaged Divine Shield targets, outer neighbors, locations,
friendly targets and newly Reborn minions excluded from the original snapshot.
This exercises existing positional and death-boundary rules, not every possible
freeze-trigger or immunity interaction.

### Disciple of Demise and resumable repetitions

A repeat-held-tribe declaration snapshots the held Dragon count and expands into
one base destruction plus that many repeated operations in the current play
frame. Each destruction receives its own death/trigger checkpoint and can pause
for choices. The played Disciple is no longer in hand and is excluded from
random targets. Seven fixtures cover counts, friendly targets, no other minions,
Reborn between repeats and a synthetic death-choice interruption. Whether exotic
hand changes during resolution alter the real client's repeat count remains an
independent-reference audit item; this implementation snapshots at expansion.

### Bounded trajectory recording for future learning

`expanded.trajectories.record_episode` streams a replay-only header, policy-visible
decisions and a final outcome. Callers must supply both policies, their identifiers,
a seed and an action limit, and explicitly consume the iterator. No parameters
are trained. The header includes both decks for replay and MUST NOT become model
input. Decision records contain only the actor's observation and legal actions.
Copies protect recorded inputs from policy mutation. Truncated outcomes have
`terminal_rewards=None`, not a false draw label. Policy RNG/checkpoint restoration
remains the caller's responsibility; policy names alone do not reproduce stochastic
policies. Five fixtures cover privacy, labels, mutation, deterministic replay and
completed episodes. A learned encoder/policy, optimizer, checkpoints and notebook
training controls are still required.

`save_episode(path, records)` consumes one trajectory into a temporary JSONL
file, validates sequential actions and its outcome, then atomically publishes a
new file without overwriting an existing one. It returns a SHA-256 receipt. A
missing outcome, iterator failure or invalid truncation label leaves no final
file. The destination directory must already exist. Publication uses a hard link
within the same directory/filesystem. Three fixtures cover round-trip content,
checksums, overwrite refusal, interrupted records and invalid draw labels.

### Trainable policy core (not yet connected to self-play)

`expanded.learning.SparsePolicy` scores a variable list of action-specific sparse
feature maps with a linear softmax policy. It supports seeded sampling and an
explicit REINFORCE gradient update with caller-supplied advantage and learning
rate. Stable softmax and finite-update checks protect numerical state. Six
synthetic numerical fixtures test gradient direction/magnitude, variable action
counts and reproducibility; no game-based training experiment was run.

This is a baseline component, not the old subset model and not a strong-player
claim. It still needs full observation/action features, on-policy return handling,
self-play opponents and notebook training controls.
Offline random-policy trajectories cannot simply be passed to this on-policy
update without accounting for their different behavior policy. The final learner
may require a richer model than this linear baseline.

### Visible features and policy snapshots

`expanded.features.encode_decision` provides versioned, action-conditioned sparse
features for visible cards, targets, positions and choices. Opponent hand contents,
replay headers and events are excluded; entity IDs resolve to visible attributes.
This baseline is lossy and does not yet represent game history or every rule
counter. The current policy is not a claim of optimal play.

`expanded.checkpoints.save_policy` atomically saves a new JSON snapshot containing
weights, sampling RNG state, completed episode count, engine fingerprint and
feature schema. `load_policy` restores exact sampling and rejects incompatible
code/schema, malformed state and optionally a mismatched SHA-256 receipt. Existing
files are never overwritten. These snapshots do not yet resume an in-flight game,
opponent schedule or training-loop state. No game-based training was launched.

### Bounded self-play update API

`expanded.training.train_episode` runs one explicitly action-budgeted match with
the shared sparse policy in both seats. Weights stay fixed until the terminal
result. It sums each player's own reward-weighted decision gradients at those
unchanged weights, then commits once. Action-capped games produce no training
label and no weight update. Exceptions restore policy weights and sampling RNG.
This is an experimental baseline: no opponent archive, variance-reduction
baseline, recurrent memory, deck search or strength certification yet. Long
training remains user-controlled; validation uses synthetic outcomes and a
two-action capped real-game fixture, not a training experiment.

Ocular Occultist (`CATA_490`) now uses a resumable chosen-hand discard. Shared
discard removal records public history and serves random and Kindred discards
as well. Six fixtures cover exact duplicate choice, empty hands, privacy,
rollback, public history and summon-versus-play. General on-discard triggers
and discard payoffs remain unimplemented and are not certified by this addition.

Duke of Below (`CATA_493`) uses a continuous +2/+2 contribution per owner discard,
including visible hand stats and owner-aware deck/hand stat filters. It is removed
by Silence and recomputed when copied. Seven fixtures cover growth, damage,
Silence, owner isolation, copying, filters and stat setting. Card text source:
https://hearthstone.blizzard.com/en-gb/cards/122713-duke-of-below/ . Complex
stat-swapping interactions are not independently certified by these fixtures.

Discard removal now emits an internal event with an independent snapshot of the
discarded card and existing listeners. Owner-specific discard/minion-discard
filters use the shared resumable event machinery. Synthetic fixtures validate
listener snapshots, ownership, Silence, type filters and choice continuation.
This infrastructure does not yet certify Maloriak or other on-discard cards:
ordering of repeated discards versus card-owned effects remains to be implemented.

Multiple-discard operations now select from the pre-trigger hand and remove the
whole batch before any event resolves. Listener snapshots exclude minions summoned
by earlier events in that batch. Fixtures cover trigger-drawn cards, later-created
listeners, invalid selections and a choice on each queued event. This follows the
Advanced rulebook's discard zone-transition description:
https://hearthstone.wiki.gg/wiki/Advanced_rulebook . Current-patch client trace
confirmation and discarded cards' own effect ordering remain outstanding.

Maloriak (`CATA_494`) now uses the friendly-minion-discard event to summon a
fresh copy, with normal board limits and no Battlecry. Seven fixtures cover
owner/type filters, Silence, multiple listeners, batch listener snapshots,
Duke's continuous bonus and stripping hand buffs. The last rule is inferred
from Blizzard's graveyard transition rules, not an independently verified
Maloriak client trace; it is recorded in `fidelity_gaps.json`.

Chronoclaws (`END_016`) discards one highest-current-cost hand card after its
controller's hero attacks, choosing randomly among ties. It uses the shared
discard path and last-charge weapon trigger behavior. Seven fixtures cover
damage/durability, discounts, ties, empty hands, minion attacks and Maloriak.
Cost-selection reference: https://hearthstone.wiki.gg/wiki/Discard-related .

Overheat (`FIR_906`) and Scorching Winds (`FIR_910`) use shared filtered-discard
and conditional continuation operations. Only matching spell schools qualify;
the played spell has already left hand. The discard checkpoint supports a
trigger choice before the bonus effect resumes. Nine fixtures cover failed
discards, empty boards, school selection, spell damage on both hits, removed
targets and choice continuation.

Gemstone Hoarder (`CATA_897`) remembers its selected discard on the board entity
and returns a fresh card with a one-mana discount on death. Memory is copied
independently and cleared by Silence; it is public only after the public discard.
Eight fixtures cover selection, enchantment reset, discount floor, empty/full
hands, copying, Silence and summon-without-Battlecry. This field is only for
publicly discarded card identities, not for privately drawn/observed cards.

### Deck search building blocks

`expanded.deck_search.single_card_neighbors` enumerates deterministic legal
one-card replacements, preserving class/runes and enforcing canonical copy
limits. `sample_neighbors` takes an explicitly sized seeded sample without
replacement. `rune_profiles` enumerates all ten Death Knight allocations. These
functions run no games and rank nothing; evaluation against independent opponent
policies and deck-search orchestration remain unfinished. Experimental mode
uses implemented 30-card decks, while full Standard search remains gated.

`expanded.deck_comparison.compare_decks` runs explicitly budgeted paired games
against an equally weighted, named opponent panel. Fresh frozen policies are
provided by a factory for each seed pair. All decks and the complete game budget
are checked before matches start. If any game caps, the whole ranking is withheld
and cap bounds remain available. Results are panel-specific estimates, not a
best-deck claim; search winners require new held-out seeds and opponents.

`expanded.frozen_policy.checkpoint_policy_factory` connects two saved policies
to deck comparisons. It verifies compatible checkpoints once, snapshots their
weights, and returns fresh read-only actors with deterministic independent seat
RNGs for each seed pair. The returned metadata identifies exact checkpoint hashes
and the sampling scheme. Training RNG states are not consumed, and files changed
after loading cannot alter the running comparison. No evaluation strength claim
follows from adapter/unit-test correctness.

Immune minions now reject enemy-selected attacks, spells, Hero Powers and
Battlecries. An Immune Taunt does not restrict attack targets; friendly targeting
remains allowed. Automatic/random effects still select normally: damage is
prevented, but destruction is not. Seven fixtures cover these boundaries.
Reference: https://hearthstone.wiki.gg/wiki/Immune . Hero Immunity and conditional
keyword-aura bookkeeping are separate unfinished systems.

Survivalist (`CATA_613`) and Scaled Lancer (`CATA_898`) use a shared effective-
keyword query. Their continuous Immunity/Taunt are derived from board state,
not stored as permanent enchantments. Targeting, damage prevention and public
observations use effective keywords; copying preserves only stored keywords.
Nine fixtures cover Silence, copy transitions, multiple sources, locations,
ownership and the Immune/Taunt interaction. This is not yet a generic engine for
all continuously granted or consumable keywords.

Air Support (`CATA_564`) grants Mega-Windfury plus a persistent no-hero-attack
restriction. Shared attack legality supports four total attacks (including attacks
already taken), without granting Rush or Charge. Silence removes both grants;
copies preserve them. Combat reads effective keywords for action limits,
summoning sickness, Poisonous and Lifesteal. Seven fixtures cover these cases.

Glowroot Lure (`EDR_477`), Prescient Slitherdrake (`END_033`) and Gladesong Siren
(`TLC_819`) now use current Hero Power-use history, other held Dragons, and
this-turn Holy/Shadow spell history respectively. Successful Hero Power uses
have an owner-specific public counter, including uses that restore no Health.
Ten fixtures cover actual-turn reset, conditions, cost modifiers, payment, rejected actions and
owner isolation.

Remnant of Rage (`END_004`), Devious Coyote (`TIME_047`) and Haywire Hornswog
(`END_030`) use shared per-player death, hero-damage-event and lifetime Overload
counters. Death and damage-event counters reset for both players every turn;
Overload persists. Positive damage absorbed by Armor is a damage event. Nine
fixtures cover ownership, reset, Counterspell, draw effects, and observations.

Blackpaw's Whip (`JAIL_503`) counts the explicit reviewed Coin identity family
and draws on weapon destruction. All 62 frozen cosmetic Coin records share the
same temporary-mana rule with `TOKEN_COIN`; these are tokens, not collectible
deck entries or claims that every cosmetic is obtainable on the target date.
No runtime name/text matching is used. Six fixtures cover every variant's
effect, deck exclusion, cost/payment, unrelated free spells and last-charge draw.
