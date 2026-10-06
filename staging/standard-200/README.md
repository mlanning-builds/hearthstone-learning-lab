# 200-card milestone — incomplete staging checkpoint

Requested target: 200 additional collectible card implementations beyond the active 291-card engine.

**88 additional effects are staged; 112 remain. This is not a completed 200-card release.** The staged overlay contains 379 collectible definitions and 266 prepared scenario checks (87 new). No simulator imports, games, checks, notebook cells or training were executed by the assistant. None of the new effects are marked validated.

## How these files are organized

`expanded/` contains replacement engine files plus the new `batch_effects.py` module. `tests/` contains two new prepared scenario suites. Other engine files are inherited from the active project. `progress.json` pins the active baseline fingerprint and lists the 88 staged IDs. The existing notebook and active engine have not been replaced with this incomplete milestone.

Do not copy this overlay into the active engine or run it as though the 200-card milestone were finished. Continue development from this checkpoint; preserve the baseline before integrating the eventual full release. Once the remaining cards and review are complete, prepare one combined notebook run for the user.

## Shared systems added

- Instance-aware filtered draws, bottom-deck draws, distinct-cost draws, and hand/deck stat modifications.
- Explicit location targeting and battlefield destruction; generated dependencies use exact archive IDs.
- Kindred tracking based on minion types/spell schools played on the previous own turn, including cost changes and effect conditions.
- Successful card-play history, friendly deaths, previous-turn spells, paid card cost, spell-damage and attack counters.
- Resurrection from recorded friendly deaths and persistent end-of-turn hero damage.

Kindred reference: [Blizzard expansion rules](https://hearthstone.blizzard.com/en-gb/expansions-adventures/the-lost-city-of-ungoro). Card-specific effects and tokens use the project's frozen archive, not a fresh assertion of live Standard legality.

## Review still required

Passing static checks establishes syntax, ID/hash consistency, and written opcode coverage only. It does not establish game behavior. All newly written scenario expectations need user execution and any failures must be resolved. General nested trigger/death ordering, ordered enchantment semantics, replacement hero powers and unrestricted generated-card pools remain broader engine limitations. The 200-card goal is not full Standard completion.

Special cases to confirm during continued rule review include left/right-most targeting when only one minion exists, death-count effects with nested reactions, and the meaning of historical card costs after discounts. Do not silently approximate unresolved interactions or certify these cards from declaration count alone.

## Staged card inventory

| ID | Card | Frozen rules text |
| --- | --- | --- |
| `CATA_473` | Nozdormu, Bronze Aspect | [x]At the end of your turn, give your minions <b>Divine Shield</b>. Any that already had one   gain +3/+3 instead. |
| `CATA_478` | Bronze Redeemer | At the end of your turn, summon a Dragon with stats equal to this minion's. |
| `CATA_483` | Unstable Spellcaster | [x]<b>Spell Damage +1</b> <b>Battlecry:</b> If you dealt damage with a spell this turn,  summon a copy of this. |
| `CATA_526` | Broxigar's Last Stand | [x]Deal $1 damage to all minions. Draw a card for each that died. |
| `CATA_529` | Ravenous Felfisher | [x]Costs (1) less for each Fel spell you've cast this game. |
| `CATA_557` | Sylvanas's Triumph | [x]Deal $3 damage. If you've played another copy of this,  hit all enemies instead. |
| `CATA_560` | Confront the Tol'vir | Summon each 1-Cost minion you've played this game. |
| `CATA_568` | Muradin's Last Stand | Draw 2 cards. Costs (1) less for each time a friendly character attacked this game. |
| `CATA_616` | Gronn Giant | [x]This minion's Cost is reduced by the Cost of the last card you played. |
| `CATA_EVENT_002` | Baleful Blazer | <b>Battlecry:</b> If you've played a Fire spell this turn, destroy a minion. |
| `CATA_EVENT_402` | Deadly Bribe | [x]Destroy a minion and give your opponent a Coin. <b>Combo:</b> You get one too. |
| `CORE_CATA_002` | Calia Menethil | <b>Battlecry:</b> Resurrect your highest-Cost minion that died this game. |
| `CORE_EX1_312` | Twisting Nether | Destroy all minions and locations. |
| `CORE_NEW1_031` | Animal Companion | Summon a random Beast Companion. |
| `CORE_REV_023` | Demolition Renovator | <b>Tradeable</b> <b>Battlecry:</b> Destroy  an enemy location. |
| `CORE_RLK_706` | Alexandros Mograine | <b>Battlecry:</b> For the rest of the game, deal 3 damage to your opponent at the end of your turns. |
| `CORE_TRL_345` | Krag'wa, the Frog | <b>Battlecry:</b> Return all spells you played last turn to your hand. |
| `DINO_138` | Diabolus Rex | <b>Kindred:</b> Deal 6 damage to your opponent's left and right-most minions. |
| `DINO_404` | Firegill | <b>Kindred:</b> Give your other minions <b>Rush</b>. |
| `DINO_406` | Fire Breath | Deal $4 damage. Give your Elementals +1/+1. |
| `DINO_408` | Crystal Tusk | [x]<b>Battlecry:</b> Shuffle the left- most card in your hand into your deck. <b>Deathrattle:</b> Draw 2 cards. |
| `DINO_411` | Holy Eggbearer | <b>Battlecry:</b> Draw a 0-Attack minion. |
| `DINO_413` | Chillspine Stegodon | [x]<b>Battlecry:</b> Deal 2 damage to two random enemy minions.  <b>Kindred:</b> And <b>Freeze</b> them. |
| `EDR_230` | Beanstalk Brute | <b>Battlecry:</b> Give +4/+4 to the top 3 minions in your deck. |
| `EDR_430` | Aessina | [x]<b>Battlecry:</b> If 20 friendly minions have died this game, deal 20 damage split among all enemies.@ <i>({0} left!)</i>@ <i>(Ready!)</i> |
| `EDR_459` | Afflicted Devastator | [x]<b>Battlecry:</b> Deal 3 damage to all other friendly minions. <b>Deathrattle:</b> Deal 3 damage to all enemy minions. |
| `EDR_468` | Eggbasher | <b>Battlecry:</b> Deal 1 damage to a minion and give it +4 Attack. |
| `EDR_485` | Rotheart Dryad | <b>Deathrattle:</b> Draw a minion that costs (7) or more. |
| `EDR_571` | Fae Trickster | <b>Deathrattle:</b> Draw a spell that costs (5) or more. |
| `EDR_572` | Tormented Dreadwing | <b>Deathrattle:</b> Draw 2 Dragons. Reduce their Costs by (1). |
| `EDR_891` | Ravenous Felhunter | <b>Deathrattle:</b> Resurrect a friendly <b>Deathrattle</b> minion that costs (4) or less. Summon a copy of it. |
| `EDR_892` | Ferocious Felbat | [x]<b>Deathrattle:</b> Resurrect a different friendly <b>Deathrattle</b> minion that costs (5) or more. Summon a copy of it. |
| `END_002` | Wicked Blightspawn | [x]<b>Reborn</b>. <b>Deathrattle:</b> Equip a 1/2 Dagger. If you already have a weapon equipped, give it +2 Attack instead. |
| `FIR_909` | Bursting Shot | Deal $2 damage to three random enemies. |
| `FIR_954` | Conflagrate | Deal $5 damage to a minion. Its owner draws a card. |
| `FIR_960` | Tending Dragonkin | <b>Battlecry:</b> Copy the lowest Cost Beast in your hand. |
| `FIR_961` | Ashleaf Pixie | <b>Battlecry:</b> If you're holding a spell that costs (5) or more, gain <b>Divine Shield</b> and <b>Lifesteal</b>. |
| `JAIL_118` | V'ama, Looming Death | <b>Battlecry:</b> Destroy all non-Paladin minions. |
| `JAIL_204` | Solitary Prisoner | Costs (2) if there are no minions on the battlefield. |
| `JAIL_311` | Scrappy Defender | [x]<b>Taunt</b> Has +5 Attack if your deck has 25 or more cards. |
| `JAIL_376` | Ball and Chain | <b>Deathrattle:</b> Give your damaged minions +1/+2. |
| `JAIL_377` | Holy Bola! | Draw a card. If it costs (2) or less, draw another. |
| `JAIL_450` | Corpse Cannon | After your hero attacks, summon a 1/1 Frail Ghoul. |
| `JAIL_456` | P1CK-P0K3T | <b>Battlecry:</b> If your deck has 25 or more cards, draw a card. |
| `JAIL_514` | The Unseen Atlas | Draw 3 cards. Costs (1) less for each card in your hand. |
| `JAIL_866` | Lethal Recipe | [x]Draw 2 minions. If you have 10 or more Mana, give them +3/+3. |
| `JAIL_941` | Holy Embrace | Restore #4 Health.  Get a 'Dark Embrace'  that deals 4 damage. |
| `JAIL_942` | Specter of Despair | <b>Taunt</b>  Can't attack. |
| `TIME_023` | Contingency | Draw the bottom two cards from your deck. |
| `TIME_031` | RAFAAM LADDER!! | Draw 3 cards of different Costs. |
| `TIME_062` | Chronicle Keeper | <b>Battlecry:</b> If you're holding a Dragon, gain <b>Taunt</b> and <b>Divine Shield</b>. |
| `TIME_427` | Cleansing Lightspawn | [x]<b>Lifesteal</b> <b>Battlecry:</b> Deal damage to an enemy minion equal    to this minion's Health. |
| `TIME_431` | Amber Priestess | [x]<b>Taunt</b> <b>Battlecry:</b> Restore Health to a character equal to this minion's Health. |
| `TIME_611` | Timestop | Deal $3 damage. <b>Freeze</b> two random enemy minions. |
| `TIME_616` | Memoriam Manifest | Summon the highest Cost friendly Undead that died this game. |
| `TIME_617` | Chronochiller | You no longer draw a card at the start of your turn. |
| `TIME_715` | For Glory! | Draw 2 cards. Costs (1) less for each minion your opponent controls. |
| `TIME_855` | Arcane Barrage | Deal $3 damage to an enemy and $2 damage to two other random ones. |
| `TIME_858` | Temporal Construct | [x]<b>Battlecry:</b> Deal 5 damage to an enemy minion. Draw cards equal to the excess damage. |
| `TIME_871` | Heir of Hereafter | [x]<b>Taunt</b> <b>Battlecry:</b> Gain +2/+2 for each damaged minion. |
| `TIME_873` | Unleash the Crocolisks | Gain 10 Armor. Summon two 2/3 Beasts for your opponent. |
| `TLC_221` | Sizzling Swarm | Deal $3 damage. Summon that many 2/1 Sizzling Cinders. |
| `TLC_226` | Conjured Bookkeeper | <b>Deathrattle:</b> Draw a spell. <b>Kindred:</b> Summon a copy of this. |
| `TLC_231` | Story of Barnabus | Draw a minion. If it has 5 or more Attack, give it +5 Health and gain 5 Armor. |
| `TLC_233` | Hatchery Helper | [x]<b>Battlecry:</b> Give your other minions with 2 or less Attack +1/+1 and <b>Taunt</b>. |
| `TLC_236` | Hybridization | Draw a 1, 2, 3, and 4-Cost minion. <b>Kindred:</b> They cost (1) less. |
| `TLC_366` | Pterrorwing Ravager | <b>Rush</b> <b>Kindred:</b> Costs (2) less. |
| `TLC_401` | Bonechill Stegodon | <b>Deathrattle:</b> Deal 6 damage to three random enemies. |
| `TLC_429` | Steamfin Thief | <b>Kindred:</b> Summon two 1/1 Murlocs with <b>Rush</b>. |
| `TLC_432` | Dread Raptor | <b>Battlecry:</b> Draw a <b>Deathrattle</b> minion that costs (3) or less. <b>Kindred:</b> It costs (0). |
| `TLC_440` | Cryosleep | Deal $4 damage and draw a card. <b>Kindred: </b>Draw another. |
| `TLC_447` | Caustic Fumes | Destroy an enemy minion. <b>Kindred:</b> Deal $2 damage to all minions. |
| `TLC_454` | Scalehide Kodo | [x]<b>Battlecry:</b> Destroy the lowest Attack enemy minion. <b>Kindred:</b> The highest Attack instead. |
| `TLC_463` | Razidir | [x]<b>Battlecry:</b> Discard a random card from your hand. <b>Kindred:</b> Your opponent's hand instead. |
| `TLC_482` | Slagclaw | [x]<b>Battlecry:</b> Summon two 2/1 Sizzling Cinders. <b>Kindred:</b> Trigger your Sizzling Cinders' <b>Deathrattles.</b> |
| `TLC_519` | Ambush Predators | Summon a 1/1 Spitter with <b>Stealth</b> and <b>Poisonous</b>. <b>Kindred:</b> Do it again. |
| `TLC_600` | Windpeak Wyrm | [x]<b>Battlecry:</b> Deal 5 damage and gain 5 Armor. <b>Kindred:</b> Costs (3) less. |
| `TLC_623` | Stonecarver | At the end of your turn, give another friendly damaged minion +2/+2. |
| `TLC_630` | Gorishi Wasp | <b>Rush</b>. Whenever this takes damage, get a 1-Cost Gorishi Stinger. |
| `TLC_816` | Gravedawn Sunbloom | Draw 2 cards. <b>Kindred:</b> This costs (2) less. |
| `TLC_818` | Resuscitate | Resurrect a 1, 2, and 3-Cost minion. Give them <b>Reborn</b>. |
| `TLC_825` | Ravasaur Matriarch | [x]<b>Kindred:</b> Deal damage to an enemy minion equal to this minion's Attack. |
| `TLC_828` | Supreme Dinomancy | Give +2/+2 to all Beasts in your hand, deck, and battlefield. |
| `TLC_829` | Ravenous Devilsaur | [x]<b>Battlecry:</b> Destroy a minion. <b>Kindred:</b> Gain its stats. |
| `TLC_833` | Insect Claw | After your hero attacks, summon a 2/1 Grub with <b>Rush</b>. |
| `TLC_901` | Fumigate | Deal $3 damage to a minion and all others of the same minion type. |
| `TLC_902` | Infestation | [x]Get two 1-Cost Gorishi Stingers. Each one deals $2 damage and summons a 2/1 Grub with <b>Rush</b>. |
| `TLC_903` | Silithid Queen | <b>Rush</b> <b>Kindred</b>: Give your hero +5 Attack this turn. |
