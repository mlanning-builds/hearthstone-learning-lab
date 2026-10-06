# Policy observation contract review

The candidate exposes its current actor's `Game.observe` result through the policy interface. Complete hidden-information fidelity is not yet certified.

## Verified cases

The tool-level suite now has eight passing checks, including three new observation checks:

- Replacing the opponent's hidden hand identities and enchantments leaves the observer's entire view unchanged.
- Reversing either player's remaining deck leaves both observations unchanged.
- Repeated observation calls do not consume RNG state or mutate event/action histories.

Run from the project root:

```sh
.venv/bin/python -m unittest discover -s tests/tools
```

These checks supplement the candidate's Secret-history and pending-choice tests. They do not add playable cards or establish visibility correctness for every event. No engine source changed in this review, so the previous full engine-suite receipt remains applicable.

## Open generated-card visibility question

`_add` and `_clone_hand_card` record `burn_generated` with a card identity when the hand is full. The event currently crosses the observation boundary. Do not assume that drawn overburn visibility establishes generated-card visibility.

The [Generate reference](https://hearthstone.wiki.gg/wiki/Generate) states that generation cannot create a card in a full hand; [Gameplay](https://hearthstone.wiki.gg/wiki/Gameplay) describes publicly revealed overdraw for drawn cards. Neither retrieved passage establishes exactly which failed-generation outcomes the client reveals. This requires card-specific replay or independent implementation evidence before changing the event contract. Also review generated choices, return-to-hand identities and secret-derived public counters as part of the complete visibility audit.

The policy interface is experimental and must not be described as independently certified for fair full-Standard learning until this audit is complete.

## Pending choice ownership

Candidate raw observations now use the pending choice's owner for legal-action
visibility, matching PolicyEnvironment. The turn owner receives no choice actions
when the opponent owns the choice. Hidden option count changes must leave the
waiting player's complete observation unchanged. Two metamorphic fixtures cover
this case; this closes one action-list leak without certifying all hidden-state
paths or the full observation schema for learning.

## Complete-game observation checks

The random validator now checks both player views after every action for JSON
serialization, opponent private-zone fields, and legal-action ownership. At game
end it also serializes full event histories. Replay applies the same contracts.
These checks detect structural leaks, not every semantic inference leak.

Validation at engine `420b314b3922`: 11 games (one seed per class, 500-action cap)
all completed, with zero errors or caps, in 7.178 seconds. All 23 tooling tests
passed, including deliberately broken observations for each new contract. This
was validation, not policy training or proof of full Standard correctness.
