# Persistent effects and defensive replacements

Frozen regular Standard patch 36.6.0.251952; no Mercenaries, Battlegrounds, training, or deck search.

Seven additional collectibles are registered, bringing the candidate to 862 live definitions and 323 staged recipes. These are dependencies outside the fixed 60-card batch; that batch remains 2/60 complete.

| ID | Card | Implemented behavior |
| --- | --- | --- |
| CATA_307 | Alexstrasza, Guardian of Life | Set current Health, then a player-bound, one-shot full-health reward. Repeated Battlecries install separate rewards. |
| CATA_591 | Commander Geddon | Replace ordinary turn draw with private Discover from the actual deck; discount the selected physical card and remove the offered alternatives. Empty deck still fatigues. |
| CORE_EDR_003 | Falric | Shared corpse-gain multiplier and an explicit corpse-spender draw selector. Dead, dormant, silenced and opposing copies do not supply the aura. |
| EDR_258 | Toreth the Unbreaking | Friendly minion and hero shields absorb three positive damage hits; partial shield progress is visible state. |
| EDR_525 | Barbed Thorn | Choose One attaches turn-limited Poisonous or weapon Deathrattle damage; weapon replacement uses the same break path. |
| JAIL_703 | Gullible Guard | Deathrattle enables the player's Sorry emote flag. There is no gameplay effect or emote UI in this simulator. |
| MEND_044 | Tranquil Clearing | A two-charge location, not the spell described by the old staged recipe. Buff and Taunt, then wake at the end of the activating player's next turn, even for an enemy target. |

`expanded/lasting_rules.py` owns these shared hooks. `tests/test_expanded_lasting_rules.py` has 48 focused checks covering normal play, silence/death, physical identities, private choices, fatigue/burn, aura eligibility, poison expiry and the activation player's clock. Full-suite and random-game receipts are recorded in the candidate STATUS.md when complete.

Feature schema `visible-action-features-v32` adds pending life rewards, the turn-draw replacement, hero shield progress and the cosmetic emote flag. Minion shield progress is in existing public rule_state; attached weapon effects are in the existing weapon view. Existing schema compatibility gates reject older policy artifacts.

## Rule evidence and remaining conformance work

Printed text and card types come from hashed pinned catalog records, not the symbolic pending recipes. Corpse-spender membership is explicit; a mention of Corpses is insufficient (Falric, the quest, and the hero-power provider are excluded).

The developer reply in the [Commander Geddon reveal discussion](https://www.reddit.com/r/hearthstone/comments/1rjysmp/new_warrior_legendary_commander_geddon/) confirms that the empty-deck replacement still causes fatigue. The [Toreth shield report and replay correction](https://us.forums.blizzard.com/en/hearthstone/t/toreth-the-unbreaking-divine-shield-bug/158549) supports fresh shields taking three hits again.

Independent client traces remain needed for partial shields crossing aura ownership changes, multiple Toreths, corpse multipliers during simultaneous death waves, reduced maximum-health boundaries and competing turn-draw replacements. Focused fixtures validate the stated engine contracts; they do not independently certify all client interactions or best play.
