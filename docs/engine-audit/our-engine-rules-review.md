# Keep our engine: rules architecture review

> Current work sequence: [engine decision and bounded completion plan](recovery-plan-2026-09-23.md). Card expansion is on hold pending the shared-system coverage specification.

2026-09-22. This decision supersedes the earlier recommendation to migrate to Fireplace. Source review only; no simulator imports, tests, notebook execution, games or training. Fireplace is a design reference, not an authoritative oracle for current Hearthstone rules.

## Decision

Keep `expanded` as the active engine. Its existing Jupyter interface, Death Knight resources, class-aware deck construction and current card work are valuable. Fireplace offers useful resolution infrastructure, but this review does not establish that replacing our engine would cost less than improving it. The 253 locally written effects and 174 historical Fireplace candidates are not comparable measures of correctness.

Do not claim full Standard support. Continue rejecting unsupported cards. Keep the original `engine`, saved models and earlier notebooks intact.

## What is already worth keeping

| Area | Our source evidence | Assessment |
| --- | --- | --- |
| Deck restrictions | `expanded/decks.py`: `validate`, `eligible` | Checks class, rune allocation, canonical copy limits and explicitly supported 30-card decks. This is already tailored to our experiment. |
| Safe action boundary | `expanded/game.py`: `step` | Validates action membership, snapshots the state including RNG, and restores it on failure. Useful while developing new effects. Deep-copy cost is a future measurement question, not a reason to remove it now. |
| Hidden information | `expanded/game.py`: `observe`; `engine/game.py`: `observe` | Opponent hands/deck order are omitted, secrets are redacted, pending-choice options are owner-only. Retain and expand observation checks. This source review is not proof that every event is safe. |
| Determinism | `expanded/game.py`: constructor; inherited state | Uses an instance-local seeded RNG. Preserve this for replay and comparisons. |
| Explicit effects | `expanded/cards.py`; `expanded/game.py`: `_effect` | Unknown opcodes/generated cards raise errors instead of guessing from card text. |
| Event listener snapshots | `expanded/systems.py`: `_queue_event` | Captures listeners when an event is queued. This is already more deliberate than rescanning all current minions later. |
| Existing systems | `expanded/systems.py`, `expanded/secrets.py` | Has working code paths for auras, silence, transformations, choices, secrets and modifiers. Their presence is not equivalent to comprehensive conformance. |

## Specific changes worth borrowing

### 1. Explicit action boundaries and death-resolution scheduling — first priority

Our `_settle` drains events, refreshes auras, removes dead minions, resolves deathrattles, then handles Reborn. It can also be called from an effect inside `_drain_events`. The `_draining_events` flag stops nested event draining, but it does not stop nested `_settle` calls from processing deaths. The resulting ordering depends on which helper happens to call `_settle`.

Fireplace's `game.py` has `action_start`, `action_end`, an action stack, and `process_deaths`. This makes its intended resolution boundaries explicit. Its exact old timing rules should not be copied blindly.

**Our implementation target:** introduce explicit action frames with documented checkpoints for attacks, area damage, individual missiles, triggers and death processing. A reentrant settle request should be scheduled according to that contract rather than relying on scattered helper calls. Do not simply defer all deaths until the entire card finishes; sequential effects can require intermediate death processing.

**User-run acceptance cases:** simultaneous combat deaths; area damage with a damage listener dying in the same batch; sequential missiles killing a Deathrattle minion between shots; aura-source death changing surviving stats; deathrattle summons plus Reborn on a nearly full board; lethal damage and healing within the same resolution sequence. Expected outcomes must be pinned to current rules evidence, not merely to whichever engine passes.

### 2. Resumable choices — confirmed architectural limitation

`_play` currently loops through every operation even when an operation sets `pending_choice`. It saves only a final `_after_play` context in `pending_play`. `_resolve_choice` resolves the selection and invokes that final callback. There is no saved remaining-effect sequence.

This is sufficient for the currently narrow deck-choice implementation, but a future card with “choose, then perform another effect based on that choice” cannot safely use this mechanism unchanged. This is a concrete limitation, not a claim that current Tracking is broken.

Fireplace's choice actions and callbacks in `actions.py` demonstrate an explicit continuation mechanism.

**Our implementation target:** save remaining operations and their context in a suspended action frame. Resolve the choice, resume exactly once, then publish after-play events. Handle empty choices, a full hand and terminal states deliberately.

**User-run acceptance cases:** effect before a choice; effect after a choice; a second choice following the first; no eligible options; selected card burned in a full hand; opponent observation never reveals choice options.

### 3. One card-play lifecycle — maintainability risk, not a demonstrated current Counterspell bug

`expanded/game.py::_play` delegates older cards to `LegacyGame._play`, while newer cards use the expanded path. Costs, logging and effect resolution therefore have two implementations; hooks must be kept aligned manually. However, current legacy spells are explicitly overridden in `expanded/cards.py`, so the branch difference alone is not evidence that today's spells evade Counterspell.

Fireplace routes play through a common `Play` action, with cost payment, pre-effect events, effect execution and after-play handling.

**Our implementation target:** one shared lifecycle for payment, card movement, counters, effects, choice continuation and post-play events. Retain legacy card-specific effects behind that lifecycle while preserving the original engine module for old saved experiments.

**User-run acceptance cases:** normal and discounted costs; countered spell consumes the card/cost but performs no effect; countered spell does not produce an after-cast reward; card-count triggers still use the agreed rules; invalid action leaves state and RNG unchanged.

### 4. Explicit modifier records — needed before complex enchantments

Our code stores aggregate attack/health changes, `cost_delta`, aura totals and temporary attack, then changes those values directly in silence, transform, swap-stat and buff handlers. That is manageable for a restricted pool, but it cannot generally represent the source, application order, expiration and removal rules for interacting modifiers.

Fireplace has separate buff/enchantment actions and entities. Reuse the idea of tracked modifier records, not unreviewed upstream code.

**Our implementation target:** retain base stats and ordered modifier records with source, duration and removal semantics. Centralize recalculation. Define what survives return-to-hand, trading, transformation and silence separately.

**User-run acceptance cases:** buff plus damage plus silence; aura removal from a damaged minion; stat-setting combined with an aura; temporary buff expiry after transformation; traded enchanted card redrawn. Document expected values rather than only asserting generic invariants.

### 5. Coverage means dependency-complete and checked

Our allowlist is safer for this experiment than Fireplace's missing-script fallback to an empty behavior class. Keep it. Extend the support inventory so each card records required systems, generated tokens/choices, written effects and validation status separately. A loaded metadata record or a written opcode is not permission to include a card in a full-Standard training run.

**Acceptance gate:** deck construction and generated-card paths reject missing dependencies with a useful explanation. The notebook reports imported / written / dependency-complete / checked counts separately. Existing unrun checks remain pending rather than being marked passed.

## Implementation order

1. Add action frames and focused resolution fixtures; user runs them in Jupyter.
2. Use those frames for suspended choices and the common play lifecycle.
3. Add modifier records before cards needing complex enchantment interactions.
4. Expand mechanics and card coverage under the stronger support manifest.
5. Resume training only against a clearly identified validated rules subset; full-Standard claims require the full requested coverage gate.

This review does not add playable cards or change engine behavior. It resolves the foundation decision and identifies concrete engineering work. Runtime correctness and performance remain unmeasured.

## Pinned reference source

Fireplace revision `47a2572a000db66645bb74a425a090d51f1004fa`:

- [Action boundaries, event processing and deaths](https://github.com/jleclanche/fireplace/blob/47a2572a000db66645bb74a425a090d51f1004fa/fireplace/game.py)
- [Play lifecycle, buffs and choices](https://github.com/jleclanche/fireplace/blob/47a2572a000db66645bb74a425a090d51f1004fa/fireplace/actions.py)
- [Missing-script fallback](https://github.com/jleclanche/fireplace/blob/47a2572a000db66645bb74a425a090d51f1004fa/fireplace/cards/__init__.py)

No upstream implementation was copied into the project.
