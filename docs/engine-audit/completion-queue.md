# All-card completion queue

890 live collectibles; 295 pending. No card-count batch limit.

Generated output: run `tools/build_completion_queue.py --engine-root staging/rebased-88` from the project root. JSON contains every card, selector, explicit token and unresolved dependency.

**Planning candidates, not approved pools.** A missing edge does not prove no dependency; unresolved selectors and named tokens remain blockers. Runtime declaration presence is not completed behavior. Explicit mapped dependencies resolve identity only; behavior, timing, complete pools and live admission remain separate gates.

56 cards have unresolved selector/dependency mappings. 2 candidate cyclic groups require coordinated review and admission; the largest has 202 cards.

The priority score is (family size + distinct external generators affected) / relative effort. Effort is an explicit engineering estimate, not a delivery estimate. Break ties and dependency cycles using reviewed mechanics; do not enable incomplete pools.

| Priority | Family | Pending | Runtime declarations present | External generators affected | Relative effort | Score |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 1 | generation | 101 | 101 | 105 | 4 | 51.5 |
| 2 | discover | 34 | 34 | 128 | 4 | 40.5 |
| 3 | dark_gift | 12 | 12 | 104 | 3 | 38.67 |
| 4 | rewind | 12 | 12 | 131 | 5 | 28.6 |
| 5 | transformation | 14 | 14 | 128 | 5 | 28.4 |
| 6 | imbue | 19 | 19 | 137 | 6 | 26.0 |
| 7 | void_soul | 4 | 4 | 73 | 3 | 25.67 |
| 8 | secret | 1 | 1 | 44 | 2 | 22.5 |
| 9 | control | 1 | 1 | 39 | 2 | 20.0 |
| 10 | infinity | 3 | 3 | 56 | 3 | 19.67 |
| 11 | animal_companion | 3 | 3 | 75 | 4 | 19.5 |
| 12 | herald | 15 | 15 | 117 | 7 | 18.86 |
| 13 | hidden_state | 1 | 1 | 54 | 3 | 18.33 |
| 14 | leyline | 3 | 3 | 70 | 4 | 18.25 |
| 15 | hidden_choice | 2 | 2 | 70 | 4 | 18.0 |
| 16 | persistent | 2 | 2 | 66 | 4 | 17.0 |
| 17 | colossal | 11 | 11 | 90 | 7 | 14.43 |
| 18 | automatic_casting | 7 | 7 | 79 | 6 | 14.33 |
| 19 | map | 6 | 6 | 46 | 4 | 13.0 |
| 20 | replacement_effect | 5 | 5 | 54 | 5 | 11.8 |
| 21 | automatic_play | 3 | 3 | 79 | 7 | 11.71 |
| 22 | deathrattle | 1 | 1 | 31 | 3 | 10.67 |
| 23 | setup | 5 | 5 | 63 | 7 | 9.71 |
| 24 | stored_cards | 1 | 1 | 37 | 4 | 9.5 |
| 25 | deck_construction | 1 | 1 | 45 | 5 | 9.2 |
| 26 | quest | 8 | 8 | 44 | 6 | 8.67 |
| 27 | custom_creation | 3 | 3 | 63 | 8 | 8.25 |
| 28 | stored_spells | 3 | 3 | 42 | 7 | 6.43 |
| 29 | location | 3 | 3 | 8 | 4 | 2.75 |
| 30 | custom_choice | 1 | 1 | 7 | 4 | 2.0 |
| 31 | fabled | 8 | 8 | 0 | 7 | 1.14 |
| 32 | timeline | 1 | 1 | 4 | 6 | 0.83 |
| 33 | conditional_aura | 1 | 1 | 0 | 2 | 0.5 |

## Completion gates

1. Review each printed effect and resolve named tokens, dynamic selectors and historical pools.
2. Implement shared behavior and all family bindings; test interactions with controlled complete fixture pools.
3. Review actual production membership. Complete all behavior in a cyclic group before admitting it together.
4. Run consolidated regression and random legal-game checks against an unchanged source fingerprint.
5. Resolve independent fidelity gaps; then proceed to learning and deck optimization.

The former fixed 60-card ledger is historical evidence only. It is not the work queue or a completion constraint.
