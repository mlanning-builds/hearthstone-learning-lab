# Scheduled turn effects

A shared player-owned schedule now supports start/end phases, owner-turn delays and finite repeats. Due effects transfer into the existing resumable turn frame before dispatch, so a choice cannot repeat the trigger. Failed summons still consume an occurrence. Future effects expose phase, relative delay, remaining occurrences and declared operations to observations and sparse features (schema v8). Internal ordering IDs are omitted from observations.

Connected cards: CATA_528 Sigil of the Seas; DINO_405 Hatching Ceremony; TIME_700 Chronological Aura. Explicit generated tokens are pinned and hash-reviewed. Written collectible coverage: 510/1185; 675 remaining. Five focused checks passed.

Turn timing follows the pinned card text. Ordering uses creation IDs for scheduled effects and minions; independent client verification of mixed delayed-effect/minion interactions remains open. This is not a complete system for all auras, delayed card enchantments, turn skipping or duration modifiers. Existing permanent end-damage entries retain their previous after-minion position.

## Additional recurring effects

Acceleration Aura and Reinforcement Aura now use the same finite schedule. Checks cover three start-turn Mana grants, expiration, recruitment without Battlecry, and preserving deck contents when no board space exists. The generated Naga Monstrosity and Chronological Drake are registered as playable tokens for bounce/copy-to-hand paths. Nine scheduler checks passed. Written coverage: 512/1185; 673 remaining.

## Board filling

Story of Lakkari now schedules discard followed by a shared fill_board_summon operation. It snapshots available slots after the discard operation checkpoint and uses resumable fixed summons. Empty hands do not prevent summoning; full boards do not prevent discarding. Fifteen scheduler checks passed. Generated Nether Imp is pinned and playable after return to hand. Official token association: https://hearthstone.blizzard.com/en-us/cards/118243-story-of-lakkari/ . Reaction-driven changes to board capacity still need independent verification (fill_board_reaction_capacity). Coverage: 513/1185; 672 remain.

## Consolidated validation

Ravenous Flock now uses the scheduler and existing pinned Skyscreamer Hatchling token. Full candidate suite: 1202 checks passed in 61.555 seconds, zero failures/errors. Log: staging/rebased-88/runs/expanded_validation/goal-scheduler-1202.log. Literal dependency report: 514 roots, 65 edges, no missing registered IDs in the covered operations. This does not certify dynamic pools or client timing. Written coverage: 514/1185; 671 remain. No training ran.
