# Version 0.8 card batch

30 additional collectible cards bring the frozen-catalog implementation count to 287 of 1,185 (898 missing). Nine generated-card dependencies are included. These are written implementations, pending the user's notebook execution; they are not full-game certification.

26 new scenario checks bring the prepared total to 163. They exercise hand limits, generated spells, shared battlefield capacity, end effects, spell damage, death chains, Reborn, targeted Beast buffs, discounts, hero-power refresh, and weapon destruction. The existing copy effect now excludes continuous aura bonuses from copied base stats so the copy receives only the aura at its own position.

The user's saved v0.7 receipt reports 137 checks passed. That receipt does not validate v0.8. No simulator imports, tests, matches, training or notebook cells were executed by the assistant.

## Cards added

| Card | ID | Frozen rules text |
| --- | --- | --- |
| Earthen Drake | `CATA_999` | At the end of your turn, deal 4 damage to the enemy hero. |
| Bronze Keeper | `CATA_476` | [x]At the end of your turn, summon a 6/6 Elemental Dragon with <b>Divine Shield</b>. |
| Priestess of Fury | `CORE_BT_493` | At the end of your turn, deal 6 damage randomly split among all enemies. |
| Violet Spellwing | `CORE_DRG_107` | <b>Deathrattle:</b> Add an 'Arcane Missiles' spell to your hand. |
| Moonwell | `EDR_476` | Deal $4 damage to all enemy characters. Restore #4 Health to all friendly characters. |
| Mother Duck | `EDR_492` | <b>Battlecry:</b> Summon three 1/1 Ducklings with <b>Rush</b>. |
| Monstrous Mosquito | `EDR_816` | At the end of your turn, give your other minions +1 Attack. |
| Critter Caretaker | `EDR_971` | At the end of your turn, restore #3 Health to both heroes. |
| Avatar of Destruction | `FIR_778` | [x]<b>Taunt</b> <b>Deathrattle:</b> Deal 9 damage to all enemy minions. |
| Living Flame | `FIR_929` | <b>Deathrattle:</b> Draw a Fire spell. |
| Sewer Imp | `JAIL_007` | [x]<b>Taunt</b> <b>Deathrattle:</b> Deal 2  damage to all enemies. |
| Contraband Wands | `JAIL_312` | Get 3 Arcane Missiles. |
| Caged Cranium | `JAIL_513` | [x]<b>Taunt</b> <b>Battlecry:</b> Gain +1 Health   for each card in your hand.  |
| Lotus Bookie | `JAIL_720` | <b>Deathrattle:</b> Get a Coin. |
| Epoch Stalker | `TIME_605` | <b>Rush</b>, <b>Elusive</b> <b>Battlecry:</b> Summon a copy of this. |
| Troubled Double | `TIME_710` | <b>Stealth</b> <b>Combo:</b> Summon a copy of this. |
| Hourglass Attendant | `TIME_100` | [x]<b>Divine Shield</b> At the end of your turn, give all minions in your hand +1/+1. |
| Yesterloc | `TIME_428` | At the end of your turn, give your other minions +1 Health. |
| Cinderfin | `TLC_225` | <b>Deathrattle:</b> Summon a 2/1 Sizzling Cinder. |
| Skyscreamer Eggs | `TLC_237` | <b>Deathrattle:</b> Summon four 2/1 Hatchlings. |
| Reluctant Wrangler | `TLC_443` | [x]<b>Reborn</b> <b>Deathrattle:</b> Summon a 2/2 Undead Beast with <b>Taunt</b>. |
| Blob of Tar | `TLC_468` | [x]<b>Poisonous</b>, <b>Taunt</b> <b>Deathrattle:</b> Summon a 2/2 Blob with <b>Poisonous</b> and a 2/2 Blob with <b>Taunt</b>. |
| Rockskipper | `TLC_427` | <b>Battlecry:</b> Get a 1-Cost Rock that deals $3 damage. |
| Cower in Fear | `TLC_823` | Deal $3 damage to a minion. The next Beast you play this turn costs (2) less. |
| Staff of the Endbringer | `TLC_EVENT_402` | <b>Deathrattle:</b> Destroy all minions. |
| Living Paradox | `TIME_059` | <b>Elusive</b> <b>Battlecry:</b> Summon two 2/1 Living Paradoxes with <b>Elusive</b>. |
| Longneck Egg | `DINO_130` | <b>Deathrattle:</b> Summon a 3/3 Beast. Give your minions +1/+1. |
| Herbivore Assistant | `DINO_419` | <b>Battlecry:</b> Give a friendly Beast +2/+2 and <b>Rush</b>. |
| Drink Blood | `JAIL_441` | <b>Lifesteal</b> Deal $3 damage to a minion. Refresh your Hero Power. |
| Sizzling Cinder | `TLC_249` | <b>Deathrattle:</b> Deal 2 damage randomly split among all enemies. |

## Scope and follow-up

The implementation uses the pinned project archive, not a fresh claim of live Standard legality. TIME_856 (Algeth'ar Instructor) was excluded because its archived Spell Damage field disagrees with its rules text. Full random generation, general nested timing and remaining card mechanics are still unfinished. Copy enchantment handling beyond the supported stat/keyword representation still needs further work.

Generated Arcane Missiles and Rock are playable when created, but are excluded from Standard deck construction. Fixed generated minions are included explicitly; none are replaced by an approximate token or restricted random pool.

Open notebook 08. If Jupyter offers a file-conflict choice, choose **Revert**, then restart the kernel and run all cells. Confirm the header says `all-class-experimental-0.8` and the final validation reports 163 checks with zero failures/errors. Do not interpret the old receipt or the initial pre-run status as a result for this version.
