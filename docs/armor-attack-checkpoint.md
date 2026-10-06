# Armor gain and forced-attack continuation

Internal progress: **803/1185** collectible implementations, **382 remaining**, **18/60** toward 845. This is not a completed delivery.

Added Barricade Basher (DINO_400). Armor gains from candidate spells, basic/replacement Hero Powers, Hero cards, Secrets, Deathrattles and compound effects now use one owner-specific event publisher. A positive gain buffs Basher once, then chooses a current enemy minion for a forced attack. No enemies means no attack, not a hero fallback. Normal attack charges are preserved.

The event scheduler permits the specifically supported Basher and EDR_471 damage/armor chains to recur through explicit frames. General unsupported trigger recursion still raises rather than silently truncating. The focused fixtures include a natural two-sided recurring armor/attack chain.

18 focused checks passed. Full suite: **2238 passed**, zero failures/errors/skips. Random validation: **22 terminal games**, zero errors/caps. Both source fingerprints: `4861d24f7a77a52cef29fedfd7e4434e0e87a275007d34a6c75cf77ff7c4beb0`.

Receipts under `staging/rebased-88`:
- `runs/expanded_validation/validation-a851ab3e3fbe415fa34cc7f4b67d0c2b.json`
- `runs/random_validation/summary-4861d24f7a77-fb58ab4266db4bac9a35e5012242bbf8.json`

No training.

Printed effect source: [Blizzard card library](https://hearthstone.blizzard.com/en-us/cards/118403-barricade-basher/). Detailed phase ordering remains an independent reference gap, including armor gained from Ice Barrier and Hero replacement. Passing local tests do not certify client fidelity.

Next shared candidates inspected: end-of-turn trigger repetition (Sandfury Aura), including explicitly replayed effects such as Inspiring Maul. Existing turn frames and replay_context provide resumable operations, but repetitions must revalidate source survival/Silence, avoid doubling expiry and scheduled non-minion effects, preserve all three owner-turn windows, and expose active duration publicly. Do not merely duplicate the entire turn-entry list. No Sandfury implementation is counted here.

Warmaul Challenger needs confirmation of repeated-attack orientation/limit. Wilted Shadow needs a pre-healing continuation with the heal amount captured before combat; an after-heal event is incorrect. Neither is counted.
