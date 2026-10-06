# Rogue Quest and resumable Hero Powers

Internal progress toward **785 → 845**: **798/1185** collectible implementations, **387 remaining**, **13/60** batch additions. The batch remains unfinished; no notebook run is requested at this boundary.

## Implementation

Hero Power resolution now retains an explicit private continuation across choices. Ordered effects finish before the after-use event is published. That event and the use counter are emitted once, even if listeners open further choices. Existing candidate lethal-check deferral spans the suspended sequence. Whole-action rollback and copied games preserve the continuation. Eight new synthetic sequencing fixtures cover payment, two choices, after-use choices, lethal timing, invalid selections, rollback, copied games and privacy.

Lie in Wait reserves an opening Quest slot, counts five own-deck shuffle events, and awards Master Dusk. A batch of several cards counts once; trading, previous shuffles, enemy destinations and opponent-caused insertions do not count. Full hands burn the reward through the existing hand boundary.

Master Dusk uses the pinned three-mana/eight-armor record, preserves current Health, replaces the primary power with Way of the Shell, summons two Stealth Ninjas, and enables a player-bound return effect. The one-mana power performs two filtered physical draws in sequence. A drawn Ninja's summon and replacement draw resolve before selecting the second filtered card. Missing matches do not produce fatigue, while replacement ordinary draws retain normal draw behavior.

Ninja returns are captured only on actual friendly Ninja deaths. They create clean cards, retain Summoned When Drawn, survive Silence and Hero replacement, and are not attached or replayable Deathrattles. Existing friendly Ninjas also use the player effect. The candidate represents that effect as a boolean, so replaying the Hero does not stack it. The visible effect is included in **feature schema v24**; previous policy schemas are incompatible.

Twenty-four integration fixtures cover Quest accounting, reward burn, Hero replacement, full boards, draw filtering/choices/burn/on-draw chains, silence, prior Ninjas, enemy ownership, simultaneous deaths, actual-death versus Deathrattle replay, and observations. These are implementation checks, not proof of independent client conformance.

## Evidence and unresolved details

Pinned local card records provide the Quest, Hero, power, Ninja and player-enchantment identities. Blizzard's [33.0.3 notes](https://hearthstone.blizzard.com/en-us/news/24224212/33-0-3-patch-notes) confirm Master Dusk's three mana and eight armor. An [August 2025 player bug report](https://us.forums.blizzard.com/en/hearthstone/t/master-dusk-not-giving-presummoned-ninjas-the-deathrattle/150608) says previously summoned Ninjas did not gain the effect. That is conflicting historical evidence, not confirmation for this pinned patch.

The candidate follows the printed player-bound behavior. Independent traces remain required for previously summoned Ninjas, control changes, repeat-Hero stacking, death during the reward's summons, simultaneous death-listener ordering, and filtered-draw/after-power lethal timing. These are explicitly retained in `expanded/fidelity_gaps.json`. No training was run.

Full validation: **2145/2145 passed**, zero failures/errors/skips, receipt `validation-067e1a444bac4a31adcaf03ebaf85138.json`. Random validation: **22 terminal games**, zero errors/caps, receipt `summary-abb0966f4fed-b5cebb11ec6848448e0c3d770954e7ce.json`. Both use fingerprint `abb0966f4fedaa00f4a42d5b931c618bca2815f043afb7bc47cc57b8cf6eca2d`.

## Next Quest dependency inspected

Dive the Golakka Depths has direct developer evidence in the [reveal discussion](https://www.reddit.com/r/hearthstone/comments/1lckfdz/new_paladin_repeatable_quest_dive_the_golakka/): ClayByte confirms automatic replay without further mana, retaining the occupied Quest slot; immediate completion between summons; only subsequent Murlocs receive the newly increased bonus; later summons in the same group advance the next cycle. This avoids inferring a delayed batch reset. Use the pinned six-summon requirement, not older five-summon text. Implement summon-time buffs separately from an aura, and verify played/summoned/copied/Reborn entries and the sixth-versus-seventh summon boundary. This Quest is not yet registered or counted.
