# End repetition, damage replacement and live hand costs

Internal progress in the unfinished 785 → 845 batch: **806/1185**, **379 remaining**, **21/60** additions. No Jupyter or training run is requested.

## Connected cards

- CATA_480 Sandfury Aura: double minion end-of-turn sequences for three owner ends. Separate repetitions revalidate their source and preserve choice continuations; expiration, player effects and scheduled spell effects are not doubled. Explicit replay through Inspiring Maul also uses the multiplier. Multiple copies extend independent durations without multiplying the multiplier. Public durations use feature schema v27.
- TIME_214 Flux Revenant: replace positive friendly Nature-spell damage with +2/+1. Shared spell damage dispatch preserves other targets, later effects, spell attribution, and zero actual-damage/Lifesteal credit. Opponent spells, combat and silenced sources use ordinary damage.
- CATA_186 Stickybomb Saboteur and CATA_186t Sabotage: live hand-adjacency surcharges update when cards move or leave. The playable token costs two before modifiers and has no cast effect. Full-hand generation burns normally. The token is a dependency, not a collectible addition.

Time Skipper explicitly rewards the player whose turn ends; the repeat multiplier belongs to the minion controller. An initial incorrect recipient change was caught by the full suite and reverted. Explicit replay also respects the current-turn recipient.

46 focused checks pass (18 repetition, 16 replacement, 12 adjacency), plus 17 existing scheduled-effect and 17 replay checks. After correcting the three initial regression failures, **2284 checks passed**, with zero failures/errors/skips. Repeated random validation completed **22 games**, zero errors/caps. Both runs use fingerprint `4883fa903c60e457e695380e64a93714af71e1008baee727d8bad4cda6aebdf3`.

Receipts under `staging/rebased-88`:
- `runs/expanded_validation/validation-52b36fee202746ed821f23d8d3a7fbeb.json`
- `runs/random_validation/summary-4883fa903c60-77fbd8981cdd463d8f641c56f25e6af2.json`

## Evidence and limits

[Blizzard Sandfury text](https://hearthstone.blizzard.com/en-us/cards/123691-sandfury-aura?set=cataclysm) and [Flux Revenant text](https://hearthstone.blizzard.com/en-us/cards/120175-flux-revenant/) establish printed effects. A [July 2026 firsthand Sabotage report](https://us.forums.blizzard.com/en/hearthstone/t/sabotage-does-not-increase-card-cost-past-10/163424) establishes an observed ten-cost cap rather than an unlimited generic tax.

Exact repeating-aura stacking/expiration ordering, Divine Shield/Immune replacement priority, and cost-setting/discount ordering remain explicit reference gaps in `expanded/fidelity_gaps.json`. These implementations and fixtures do not certify full Standard fidelity. Stormrook is still blocked by its full random 5-Cost minion pool; it is not counted.

## Next family: nested spell resolution

There are 21 unimplemented primary cards in the nested cast/replay family. Not all become ready with one dispatcher: random spell pools, Colossal, Rewind, spell-carving and pack contents retain separate dependencies.

Prioritize the bounded consumers (Opu the Unseen, Captured Archmage, Shadow Rounds), then physical hand/deck casts (Crackling Cloudstrider, Violet Treasuregill), then stored/repeated spells. Extend the existing `replay_context` continuation mechanism where possible rather than treating internal casts as ordinary paid hand plays.

Required distinctions before counting a consumer: controller and actual caster attribution; target eligibility and preferred targets; mana/Overload; Spell Damage and Lifesteal; Choose One and Discover; physical removal versus copied spell; played versus cast counters/triggers; Secrets; terminal/choice interruptions and rollback. Old Yogg rule descriptions alone do not establish current pinned semantics for every caster. Do not publish ordinary `spell_played` or `spell_cast` events by assumption.
