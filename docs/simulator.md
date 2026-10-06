# Simulator scope and validation

Version: `dk-subset-0.1`. This is an experimental closed-pool implementation, not Blizzard's engine and not a full Standard simulator.

## What works

- Two Death Knights, 30-card decks, 30 starting health, three-rune allocations, and normal copy limits.
- Shuffled decks, 3/4-card openings, selectable mulligans, the second player's Coin, and the first turn's draw.
- One mana crystal per own turn up to ten; once-per-turn Ghoul Charge.
- Seven board slots, ten-card hands, burned draws, fatigue, armor, healing, and hero defeat.
- Target selection and minion positioning, combat with simultaneous damage, attack exhaustion, summoning sickness, Taunt, Charge, Rush, Divine Shield, Elusive, Poisonous, Lifesteal, and Reborn.
- A Corpse for each friendly minion death, including the hero-power Ghoul and reborn minions. Body Bagger creates one directly. Blood Tap, Grave Strength, and Marrow Manipulator spend Corpses.
- All effects of 33 explicitly selected collectible cards and four internal tokens. Run the coverage cell in notebook 02 for the exact list. The other 84 cards from notebook 01 are rejected before a game begins.
- The only weapon is Corrupted Ashbringer. Its frozen JSON record has `durability: 0` and `health: 2`; weapon construction uses the nonzero health value as durability. The regression test expects two attacks before it breaks.

## Boundaries

No Discover, unrestricted random card generation, Freeze, secrets, locations, other heroes, other classes, or unsupported card text. Decks from notebook 01 may contain unsupported cards; notebook 02 deliberately creates a new population from the playable subset. There are no silent vanilla-card substitutions.

The card pool is skewed toward simpler effects. Rune profiles therefore do not have equally rich choices (for example, no triple-Blood or triple-Frost payoff is implemented). Results cannot rank runes fairly, establish the best Standard deck, or stand in for live-client matches. Current Standard legality and temporary bans still need a separate audit.

Individual card fixtures check the implemented semantics against the frozen card descriptions and documented game mechanics. There is **no live-client differential validation yet**. Complex event-order interactions should be checked against recorded games before expanding the supported pool or trusting optimization conclusions.

## Experimental method

Players choose uniformly among complete legal actions, including end turn, targets, positions, and mulligan subsets. This is intentionally a weak baseline. It is not uniform over action categories or card identities: cards with more possible targets/positions have more action entries. No strategy heuristics, pretrained weights, or training updates are used.

Each sampled deck pairing plays twice with initiative reversed and the same environment seed. Environment randomness and player-choice randomness use separate streams. This balances starting position per pairing, but does not provide an exhaustive tournament or equal numbers of games per rune. The 89-turn cap produces a separately identified draw. A safety-limit breach or implementation exception is an error, never a win/loss observation.

The next learning experiment can consume `Game.observe(player)`, choose one of its `legal_actions`, then call `step`. Terminal rewards are +1/-1, or zero for a draw. Observations reveal public state and the viewer's hand and starting deck; they omit the opponent's cards/runes and both shuffled deck orders. The actual `Game` object contains hidden information and must not be passed to a policy.

## Validation

```sh
python3 -m unittest discover -s tests -v
```

Scenario tests cover every supported card's behavior, resource costs, target legality, hand/board limits, mulligans, deathrattles, fatigue, damage keywords, duplicate/rune rejection, observation privacy, deterministic replays, paired schedules, interrupted-run resumption, and errors excluded from results. Random-game tests exercise all ten rune profiles. Every action checks state invariants.

Hashes bind the implemented card records to their frozen definitions. If a record changes, the engine refuses to run until its implementation is reviewed. Runs also include a fingerprint of the engine and card data, preventing an old checkpoint from being resumed under different rules.

## Saved experiments

`runs/matches_<fingerprint>/checkpoint.json` records configuration, decks, match schedule, completed results, and status. It is atomically replaced after each completed game. An interrupted game is replayed from its seed; completed games are retained. `summary.json` holds aggregate results. `sample_match.json` contains the first match's starting decks, action sequence, and public event log for exact replay. This replay is an experiment artifact, not an agent observation.

Runs with identical settings resume automatically. Change the seed for a new experiment. A failure is shown immediately, with completed results preserved. The notebook does not catch an engine error and continue as if it were a normal match.

## Reference material

- [Blizzard: Death Knight Deep Dive](https://hearthstone.blizzard.com/en-us/news/23852696) — Ghoul Charge, Corpses, and rune allocations.
- [HearthstoneJSON card data](https://hearthstonejson.com/docs/cards.html) — data format; exact downloaded source and hashes are in `data/provenance.json`.
- [Blizzard: Corrupted Ashbringer](https://hearthstone.blizzard.com/en-us/cards/78357-corrupted-ashbringer) — card reference.

All game content belongs to Blizzard Entertainment. This is an unofficial fan experiment.
