# All 519 remaining collectible cards

See [classification method and summary](README.md). Each ID appears exactly once below. Secondary tags are review prompts and are not additional card counts.

## Mostly existing mechanics — 12 cards (A)

Existing draw, summon, choice, history, payload and trigger helpers cover the main behavior; add bounded glue and fixed dependencies, then validate.

| ID | Card | Printed rule | Additional note / review tags |
| --- | --- | --- | --- |
| `CAP_102` | Land Ho! | Draw 2 cards. Summon two 1/1 Cannoneers. | Requires CAP_107t Cannoneer, including its end-turn shot; token does not count as another collectible. |
| `CAP_107` | Cannonmaster | Battlecry: Get a 1/1 Cannoneer that deals 1 damage to a random enemy at end of turn. | Pinned CAP_107t is a 1/1 with an end-turn random-enemy shot; existing summon/end-turn primitives cover it. |
| `CAP_403` | Frame Job | Destroy two random enemy minions. Discover a minion in the enemy deck to put on top. | Selection is from the actual enemy deck, not a global generated pool; implement private options and deck reorder. |
| `CATA_586` | Destructive Blaze | After this survives damage, summon a Destructive Blaze. Deathrattle: Deal 2 damage to a random enemy. | Self-summoning dependency forms a cycle, not an unknown random pool; verify trigger/death ordering. |
| `CATA_EVENT_001` | Destructive Phoenix | Battlecry: Choose a card in your hand to set on fire. In 3 turns, discard it and summon a copy of this. | Reuse held-card timers/private selection; distinguish discard from destruction and preserve the correct summoned-copy payload. |
| `EDR_271` | Grove Shaper | After you cast a Nature spell, summon a 2/2 Treant with "Deathrattle: Get a copy of that spell." | Capture the cast Nature spell identity in the generated Treant deathrattle; no random global card pool. |
| `EDR_455` | Succumb to Madness | Discover a friendly Dragon that died this game. Resummon it. | Discover from recorded friendly Dragon deaths; check duplicates and fresh resurrection semantics. |
| `EDR_494` | Hungering Ancient | At the end of your turn, eat a minion in your deck and gain its stats. Deathrattle: Add them to your hand. | Choose from the actual deck, retain consumed identities and add them on death; no global pool. |
| `JAIL_734` | Hellraiser | Taunt Battlecry: Discover a card in your deck. If it's empty, gain +4/+4 instead. | Existing deck-choice and self-buff helpers cover the two branches; verify what counts as an empty deck. |
| `JAIL_851` | Inspector Murloc Holmes | Battlecry: Investigate a card in the enemy hand. If they play a card with that name next turn, get 3 Coins. | Reuse private enemy-hand choice; add the named-card next-turn watch and fixed Coin reward. |
| `TIME_713` | Time Adm'ral Hooktail | Battlecry: Summon a 0/8 Chest for your opponent. It's FULL of Coins! | Pinned TIME_713t is a 0/8 Chest whose deathrattle fills its opponent’s hand with Coins; owner semantics matter. |
| `TIME_870` | Gladiatorial Combat | Summon a random minion from your deck. Summon a 5/5 Tiger with Stealth for your opponent. | Recruit from the actual deck and create a fixed enemy Stealth Tiger; include the exact token. |

## Animal Companion replacement and count — 4 cards (B)

Centralize Companion generation and persistent substitutions/counts; replacement Beast pools must also be complete.

| ID | Card | Printed rule | Additional note / review tags |
| --- | --- | --- | --- |
| `MEND_300` | Tame Pet | Replace your future Animal Companions with random Beasts that cost (1) more. Draw a card. | global_pool_review |
| `MEND_303` | Migrating Elekk | Taunt. Battlecry: Replace your future Animal Companions with random Beasts that cost (1) more. | global_pool_review |
| `MEND_304` | Talya Earthstrider | Battlecry: Your cards that summon Animal Companions summon 1 more this game. | Review timing, generated dependencies and interactions. |
| `MEND_307` | Roam Free | Replace your future Animal Companions with random Beasts that cost (2) more. Choose one to summon. | global_pool_review |

## Bounded state/choice extensions — 22 cards (B)

A local feature extension is needed beyond composing current opcodes; inspect the card-specific explanation and generated dependencies.

| ID | Card | Printed rule | Additional note / review tags |
| --- | --- | --- | --- |
| `CATA_213` | Vyranoth | Battlecry: If the total Cost of your starting minions was 100, split 100 stats among minions in your deck. | Review timing, generated dependencies and interactions. |
| `CATA_472` | Inspiring Maul | Deathrattle: Trigger a random friendly minion's end of turn effect. | global_pool_review |
| `CATA_591` | Commander Geddon | Battlecry: Instead of drawing each turn, Discover a card from your deck. It costs (3) less. Destroy the others. | global_pool_review, draw_resolution |
| `CORE_EDR_003` | Falric | You gain twice as many Corpses as normal. Battlecry: Draw a card that spends Corpses. | Review timing, generated dependencies and interactions. |
| `CORE_LOOT_101` | Explosive Runes | Secret: After your opponent plays a minion, deal $6 damage to it and any excess to their hero. | Existing Secret event plus excess damage are close, but ordering needs a dedicated integration check. |
| `DINO_136` | Horn of Feasting | Summon three 2/1 Raptors with Rush. Outcast: Give them Immune while attacking this turn. | Review timing, generated dependencies and interactions. |
| `DINO_414` | Tribute Dance | Choose a minion. Choose a different minion to transform it into. | Review timing, generated dependencies and interactions. |
| `EDR_001` | Hopeful Dryad | Battlecry: Get a random Dream card. | global_pool_review |
| `EDR_454` | Clutch of Corruption | Choose a friendly Dragon. Summon a 0/2 Egg that hatches into a copy of it. | This is a LOCATION, not a spell; the generated Egg must retain the chosen Dragon copy payload. |
| `EDR_526` | Renferal, the Malignant | Battlecry: Trap 1 random card in your opponent's hand for a turn. (Improved for each time you've played this.) | global_pool_review |
| `EDR_780` | Bloodthistle Illusionist | Battlecry: Summon a copy of this. One secretly dies when it takes damage. | Review timing, generated dependencies and interactions. |
| `EDR_781` | Harbinger of the Blighted | Whenever this enters your hand from the battlefield, summon two random 2-Cost minions. | global_pool_review |
| `EDR_846` | Shaladrassil | Get all 5 Dream cards. If you've played a higher Cost card while holding this, corrupt them! | Review timing, generated dependencies and interactions. |
| `JAIL_421` | Warptooth | Charge. If four friendly characters take damage on one of your turns, summon this from hand or deck. | Review timing, generated dependencies and interactions. |
| `JAIL_852` | Togwaggle, Smuggler King | Battlecry: Shuffle both players' hands together. | Review timing, generated dependencies and interactions. |
| `JAIL_987` | Low Security Wing | Get a random Shaman minion. It's locked in your hand until you play another card. | global_pool_review |
| `TIME_030` | Divergence | Split a random minion in your hand into two halves. | global_pool_review |
| `TIME_620` | Untimely Death | Secret: When a friendly minion dies the turn after being played, resummon it. | Review timing, generated dependencies and interactions. |
| `TLC_241` | Ido of the Threshfleet | While this is alive, you get a 2-Cost Holy spell that gives a minion +2/+2 and Divine Shield. | Review timing, generated dependencies and interactions. |
| `TLC_251` | Primalfin Challenger | Battlecry: Your next Kindred triggers twice. | Review timing, generated dependencies and interactions. |
| `TLC_515` | Cultist Map | Discover a card from your deck. If you play it this turn, also pick one of the others. | global_pool_review |
| `TLC_987` | Questing Assistant | Battlecry: If you played a Quest this game, deal 3 damage to an enemy minion. | Damage and play-history lookup are simple, but normal activation depends on supported Quest cards. |

## Cannoneer shared firing rules — 2 cards (B)

Add a shared firing operation and permanent extra-shot modifier; include fixed Cannoneer token behavior.

| ID | Card | Printed rule | Additional note / review tags |
| --- | --- | --- | --- |
| `CAP_103` | Hand Cannon | After your hero attacks, your Cannoneers FIRE! | Review timing, generated dependencies and interactions. |
| `CAP_106` | Captain Crowley | Your Cannoneers fire an additional shot. Battlecry: Summon two 1/1 Cannoneers. | Review timing, generated dependencies and interactions. |

## Card origin and hand-entry tracking — 10 cards (B)

Track physical starting-deck origin, copied-from-opponent identity and hand-entry time through every draw, copy, shuffle and control transition.

| ID | Card | Printed rule | Additional note / review tags |
| --- | --- | --- | --- |
| `CORE_REV_946` | Steamcleaner | Battlecry: Destroy ALL cards in both players' decks that didn't start there. | Review timing, generated dependencies and interactions. |
| `DINO_409` | Techysaurus | Taunt. Costs (1) less for each card you played this game that didn't start in your deck. | Review timing, generated dependencies and interactions. |
| `EDR_251` | Dragonscale Armaments | Draw a spell that started in your deck and one that didn't. | Review timing, generated dependencies and interactions. |
| `EDR_256` | Dreamwarden | Taunt. Battlecry: If there is a card in your deck that didn't start there, draw it and gain +2/+2. | Review timing, generated dependencies and interactions. |
| `JAIL_205` | Rat Burglar | At the end of your turn, steal all cards that entered your opponent's hand during your turn. | Review timing, generated dependencies and interactions. |
| `JAIL_380` | Smuggled Shovel | Deathrattle: Draw a spell that didn't start in your deck. | Review timing, generated dependencies and interactions. |
| `JAIL_432` | Mind Sweeper | Battlecry: If you played a copy of an opponent's card while holding this, deal 2 damage to all enemy minions. | Review timing, generated dependencies and interactions. |
| `JAIL_433` | Unshackle Soul | Destroy a minion. If you played a copy of an opponent's card while holding this, this costs (1). | Review timing, generated dependencies and interactions. |
| `JAIL_434` | Enthralled Shade | Deathrattle: Reduce the Cost of cards in your hand that were copied from your opponent by (1). | Review timing, generated dependencies and interactions. |
| `TLC_364` | Story of the Waygate | Reduce the Cost of cards in your hand that didn't start in your deck by (1). | Review timing, generated dependencies and interactions. |

## Damage, healing, costs and temporary control — 14 cards (B)

Extend source-aware damage/healing replacement or ordered modifiers; existing flat buffs alone do not cover the rule.

| ID | Card | Printed rule | Additional note / review tags |
| --- | --- | --- | --- |
| `CAP_104` | Blastpowder Engineer | On your turn, friendly Pirates deal 1 more damage. | Review timing, generated dependencies and interactions. |
| `CATA_186` | Stickybomb Saboteur | Battlecry: Give your opponent a 2-Cost Sabotage. Cards next to it cost (1) more. | Review timing, generated dependencies and interactions. |
| `CATA_301` | Ruby Sanctum | Your next Healing effect this turn deals damage instead. | Review timing, generated dependencies and interactions. |
| `CATA_307` | Alexstrasza, Guardian of Life | Battlecry: Set your remaining Health to 15. When you reach full Health, deal 15 damage to your opponent. | Review timing, generated dependencies and interactions. |
| `CATA_480` | Sandfury Aura | Your minions' end of turn effects trigger twice. Lasts 3 turns. | Review timing, generated dependencies and interactions. |
| `CATA_496` | Cursed Chains | Take control of an enemy minion until the end of their turn. It can't attack this turn. | Review timing, generated dependencies and interactions. |
| `CATA_621` | Gelbin's Triumph | Get a random Paladin Aura. It lasts an additional turn. | Review timing, generated dependencies and interactions. |
| `EDR_258` | Toreth the Unbreaking | Divine Shield, Taunt Your Divine Shields take three hits to break. | Review timing, generated dependencies and interactions. |
| `EDR_480` | Goldrinn | Rush Friendly Beasts deal double damage. | Review timing, generated dependencies and interactions. |
| `EDR_525` | Barbed Thorn | Choose One - Gain Poisonous this turn; or Gain "Deathrattle: Deal 2 damage to all enemies." | Review timing, generated dependencies and interactions. |
| `JAIL_330` | Dalaran Champion | Divine Shield, Taunt After this gains stats, gain an extra +1/+1 (wherever this is). | Review timing, generated dependencies and interactions. |
| `TIME_214` | Flux Revenant | Taunt Whenever you would damage this with a Nature spell, it gains +2/+1 instead. | Review timing, generated dependencies and interactions. |
| `TIME_217` | Stormrook | Whenever you would damage this with a Nature spell, summon a random 5-Cost minion instead. | global_pool_review |
| `TLC_228` | Bralma Searstone | Your Elementals deal 1 extra damage. | Review timing, generated dependencies and interactions. |

## Dark Gifts — 19 cards (B)

Implement the complete Dark Gift effect pool and attached-state behavior; Discover variants also depend on generated-card pools.

| ID | Card | Printed rule | Additional note / review tags |
| --- | --- | --- | --- |
| `EDR_102` | Treacherous Tormentor | Battlecry: Discover a Legendary minion with a Dark Gift. | global_pool_review, dark_gift |
| `EDR_105` | Creature of Madness | Battlecry: Discover a 3-Cost minion with a Dark Gift. | global_pool_review, dark_gift |
| `EDR_456` | Darkrider | Battlecry: If you're holding a Dragon, Discover a Dragon with a Dark Gift. | global_pool_review, dark_gift |
| `EDR_487` | Wallow, the Wretched | While this is in your hand or deck, it gains a copy of every Dark Gift given to your minions. | dark_gift |
| `EDR_488` | Avant-Gardening | Discover a Deathrattle minion with a Dark Gift. | global_pool_review, dark_gift |
| `EDR_528` | Nightmare Fuel | Discover a copy of a minion in your opponent's deck. Combo: With a Dark Gift. | global_pool_review, dark_gift |
| `EDR_654` | Overgrown Horror | Taunt Battlecry: Reduce the Cost of minions in your hand with Dark Gifts by (2). | dark_gift |
| `EDR_811` | Rite of Atrocity | Discover an Undead. Spend 2 Corpses to give it a Dark Gift. | global_pool_review, dark_gift |
| `EDR_856` | Nightmare Lord Xavius | Battlecry: Discover a minion from your deck. Give it a Dark Gift. | global_pool_review, dark_gift |
| `EDR_882` | Jumpscare! | Discover a Demon that costs (5) or more with a Dark Gift. Shuffle the other two into your deck. | global_pool_review, dark_gift |
| `END_013` | Brutish Endmaw | Battlecry: Discover a 1-Cost minion with a Dark Gift. | global_pool_review, dark_gift |
| `END_027` | Wings of Eternity | Discover a Dragon from the past with a Dark Gift. | global_pool_review, dark_gift |
| `FIR_900` | Cremate | Discover a minion with a Dark Gift. It costs (2) less. | global_pool_review, dark_gift |
| `FIR_901` | Frostburn Matriarch | Battlecry: If you're holding a minion with a Dark Gift, summon two 4/4 Dragons with Taunt. | dark_gift |
| `FIR_920` | Smoke Bomb | Discover a Combo, Battlecry, or Stealth minion with a Dark Gift. | global_pool_review, dark_gift |
| `FIR_922` | Cindersword | Battlecry: If you're holding a minion with a Dark Gift, gain +3 Attack. | dark_gift |
| `FIR_924` | Shadowflame Stalker | Battlecry: Discover a Demon with a Dark Gift. Get a copy of it. | global_pool_review, dark_gift |
| `FIR_939` | Shadowflame Suffusion | Deal $2 damage. Discover a Warrior minion with a Dark Gift. | global_pool_review, dark_gift |
| `FIR_956` | Dragon Turtle | Battlecry: If you're holding a minion with a Dark Gift, give your hero +3 Attack this turn and 6 Armor. | dark_gift |

## Discover history and delayed rewards — 7 cards (B)

Add Discover-specific events/counters and follow-up choice ownership; ordinary choices must not count as Discover.

| ID | Card | Printed rule | Additional note / review tags |
| --- | --- | --- | --- |
| `TLC_365` | Storage Scuffle | Deal $3 damage to a minion. Costs (0) if you've Discovered this turn. | global_pool_review |
| `TLC_435` | Crypt Map | Discover a Frost Rune card. If you play it this turn, also pick one of the others. | global_pool_review |
| `TLC_442` | Submerged Map | Discover a Murloc. If you play it this turn, also pick one of the others. | global_pool_review |
| `TLC_464` | Mountain Map | Discover a minion with a type you haven't played. If you play it this turn, also pick one of the others. | global_pool_review |
| `TLC_483` | Vault Breaker | After you Discover a card, reduce its Cost by (1). | global_pool_review |
| `TLC_824` | Odd Map | Discover an odd-Attack Beast. If you play it this turn, also pick one of the others. | global_pool_review |
| `TLC_900` | Hive Map | Discover a Fel spell. If you play it this turn, also pick one of the others. | global_pool_review |

## Dormant and awakening — 18 cards (B)

Add inactive board entities, targeting/trigger suppression, wake timing and conditional awakening.

| ID | Card | Printed rule | Additional note / review tags |
| --- | --- | --- | --- |
| `CATA_481` | Iso'rath | Battlecry: Devour 2 random cards from the opponent's hand, then go Dormant for 2 turns. Deathrattle: Return them. | global_pool_review, dormant |
| `CORE_BT_156` | Imprisoned Vilefiend | Dormant for 2 turns. Rush | dormant |
| `EDR_416` | Shepherd's Crook | After your hero attacks, summon a 3/3 Sheep that's Dormant for 2 turns. | dormant |
| `EDR_469` | Slumbering Sprite | Starts Dormant. After you use your Hero Power, this awakens. | dormant |
| `EDR_820` | Wyvern's Slumber | Choose One - Summon two Dormant Dreadseeds; or Deal $2 damage to all minions. | dormant |
| `EDR_840` | Grim Harvest | Draw a card. Summon a random Dormant Dreadseed. | dormant |
| `EDR_841` | Dreadsoul Corrupter | Battlecry and Deathrattle: Summon a random Dormant Dreadseed. | dormant |
| `EDR_979` | Ancient of Yore | Dormant for 2 turns. While Dormant, gain 3 Armor and draw a card at the end of your turn. | dormant |
| `JAIL_850` | Warden Maiev | After you play a minion, give it +3/+3 and make it go Dormant for 1 turn. | dormant |
| `JAIL_997` | Demonic Confinement | Make a minion go Dormant for 2 turns. If it’s a friendly Demon, give it +3/+3 instead. | dormant |
| `MEND_040` | Ash Worm | Starts Dormant. When your board is full, awaken. | dormant |
| `MEND_044` | Tranquil Clearing | Give a minion +2 Health and Taunt. It falls asleep until the end of your next turn. | dormant |
| `TIME_022` | Perennial Serpent | Rush Costs (4) less if a minion is Dormant. | dormant |
| `TIME_046` | Cyborg Patriarch | Dormant for 3 turns. Taunt | dormant |
| `TIME_058` | Paltry Flutterwing | Deathrattle: Summon a random 2-Cost minion that is Dormant for 2 turns. | global_pool_review, dormant |
| `TIME_063` | Timelord Nozdormu | Dormant for 5 turns. Rush. After you play a card from the newest expansion, awaken 1 turn sooner. | dormant |
| `TIME_442` | Timeway Warden | Battlecry: Imprison an enemy minion. It goes Dormant for 10,000 turns. Deathrattle: Awaken it. | dormant |
| `TLC_253` | Petrified Ogre | Starts Dormant. While Dormant, gain +2/+2 at the start of your turn. (50% chance to awaken instead.) | dormant |

## Draw listeners — 2 cards (B)

Add draw-event publication with burn, fatigue, copy and continuation semantics.

| ID | Card | Printed rule | Additional note / review tags |
| --- | --- | --- | --- |
| `CORE_SCH_717` | Keymaster Alabaster | Whenever your opponent draws a card, add a copy to your hand that costs (1). | draw_resolution |
| `CORE_TTN_843` | Eredar Deceptor | Whenever you draw a card, summon a 1/1 Demon with Rush. | draw_resolution |

## Health/Corpse payment — 7 cards (B)

Add alternate payment to legal actions and resolution, including prevention, lethal payment and modifier interactions.

| ID | Card | Printed rule | Additional note / review tags |
| --- | --- | --- | --- |
| `CATA_180` | War'loc | Battlecry: Your next Murloc that costs (3) or less costs Health instead of Mana. | alternate_payment |
| `CORE_ETC_523` | Death Metal Knight | Taunt Costs Health instead of Mana if your hero was healed this turn. | alternate_payment |
| `EDR_489` | Agamaggan | Battlecry: The next card you play costs your OPPONENT'S Health instead of Mana (up to 10). | alternate_payment |
| `TIME_612` | Blood Draw | Discover a spell. This costs Health instead of Mana. | global_pool_review, alternate_payment |
| `TIME_615` | Forgotten Millennium | Fill your hand with random Undead. They cost Health instead of Mana this turn. | global_pool_review, alternate_payment |
| `TLC_436` | Reanimated Pterrordax | Rush, Lifesteal Costs Corpses instead of Mana. | alternate_payment |
| `TLC_467` | Whispering Stone | Taunt Deathrattle: Get 2 random Fel spells. They cost Health instead of Mana. | global_pool_review, alternate_payment |

## Held upgrades and turn counters — 7 cards (B)

Extend physical-card progress and expiry hooks; verify threshold and turn-boundary semantics before reuse.

| ID | Card | Printed rule | Additional note / review tags |
| --- | --- | --- | --- |
| `CATA_131` | Felwood Treant | Battlecry: Gain a temporary Mana Crystal. If you spent 4 Mana while holding this, it's permanent. ({0} left!)@Battlecry: Gain a temporary Mana Crystal. If you spent 4 Mana while holding this, it's permanent. (Ready!)@Battlecry: Gain a temporary Mana Crystal. If you spent 4 Mana while holding this, it's permanent. | Previous batch deliberately deferred whether its own payment contributes to the held-mana threshold. |
| `CATA_132` | Broodwatcher | Battlecry: Get two 3/3 Whelps with Taunt. If you spent 8 Mana while holding this, summon them. ({0} left!)@Battlecry: Get two 3/3 Whelps with Taunt. If you spent 8 Mana while holding this, summon them. (Ready!)@Battlecry: Get two 3/3 Whelps with Taunt. If you spent 8 Mana while holding this, summon them. | Same unresolved held-mana timing as Felwood Treant; simple-looking text does not make it ready. |
| `CATA_498` | Rafaams' Last Stand | Deal $2 damage to two random enemy minions. (Upgrades each turn!) | global_pool_review |
| `FIR_911` | Smoldering Grove | Draw {0} card. (Upgrades each turn, but discards after {1}!)1Draw {0} cards. (Discards this turn!) | Review timing, generated dependencies and interactions. |
| `FIR_914` | Smoldering Strength | Give a friendly minion +{0}/+{0}. (Upgrades each turn, but discards after {1}!)1Give a friendly minion +{0}/+{0}. (Discards this turn!) | Review timing, generated dependencies and interactions. |
| `FIR_916` | Smoldering Ascent | Deal ${0} damage to all enemy minions. (Upgrades each turn, but discards after {1}!)1Deal ${0} damage to all enemy minions. (Discards this turn!) | Review timing, generated dependencies and interactions. |
| `JAIL_501` | Picklock | All numbers on this card equal your remaining Mana. Battlecry: Deal 1 damage to an enemy minion. | Review timing, generated dependencies and interactions. |

## Herald and Deathwing upgrades — 15 cards (B)

Implement Herald progress, Soldier generation and Deathwing upgrade dependencies together.

| ID | Card | Printed rule | Additional note / review tags |
| --- | --- | --- | --- |
| `CATA_156` | Experimental Animation | Herald {0}. Deal $4 damage to all enemy minions. | herald |
| `CATA_158` | Maniacal Follower | Stealth Deathrattle: Herald {0}. | herald |
| `CATA_160` | Scorching Ravager | Battlecry: Herald {0}. Give the Soldier Rush. | herald |
| `CATA_190h` | Deathwing, Worldbreaker | Battlecry: Choose {0} Cataclysm to unleash! Herald twice to upgrade.@Battlecry: Choose {0} \|4(Cataclysm,Cataclysms) to unleash! Herald once to upgrade.@Battlecry: Choose {0} \|4(Cataclysm,Cataclysms) to unleash! | herald |
| `CATA_492` | Shrine of Twilight | Herald {0}. Draw a card. | herald |
| `CATA_497` | Ultraxion | Battlecry: Herald {0}. Reduce Deathwing's Cost by ({1}). (Herald to improve!) | herald |
| `CATA_525` | Armored Bloodletter | Rush Battlecry: Herald {0}. | herald |
| `CATA_530` | Fel Infusion | Herald {0}. Your hero has Lifesteal this turn. | herald |
| `CATA_561` | Ritual of Power | Herald {0}. Get two 1/1 Elementals with Rush. | herald |
| `CATA_565` | Skywall Sentinel | Taunt Battlecry: Herald {0}. | herald |
| `CATA_580` | Cataclysmic War Axe | Battlecry: Herald {0}. | herald |
| `CATA_722` | Envoy of the End | Taunt Battlecry: Herald {0}. | herald |
| `CATA_725` | Shadowsworn Disciple | Battlecry: Herald {0}. Deathrattle: Restore #3 Health to your hero. | herald |
| `CATA_780` | Obsessive Technician | Lifesteal Battlecry: Herald {0}. | herald |
| `CATA_785` | Rite of Twilight | Herald {0}. Combo: Deal $3 damage. | herald |

## Imbue and upgraded hero powers — 19 cards (B)

Implement all affected hero-power upgrades and Imbue progress plus generated dependencies.

| ID | Card | Printed rule | Additional note / review tags |
| --- | --- | --- | --- |
| `EDR_226` | Exotic Houndmaster | Battlecry: Draw a Beast. Imbue your Hero Power. | imbue |
| `EDR_227` | Umbraclaw | Rush Deathrattle: Imbue your Hero Power. | imbue |
| `EDR_231` | Aspect's Embrace | Restore #4 Health. Draw a card. Imbue your Hero Power. | imbue |
| `EDR_264` | Aegis of Light | Summon a random 2-Cost minion and give it Taunt. Imbue your Hero Power. | global_pool_review, imbue |
| `EDR_449` | Lunarwing Messenger | Lifesteal Battlecry: Imbue your Hero Power. | imbue |
| `EDR_451` | Goldpetal Drake | Battlecry and Deathrattle: Imbue your Hero Power. | imbue |
| `EDR_518` | Living Garden | Battlecry: Imbue your Hero Power. Reduce the Cost of a minion in your hand by (1). | imbue |
| `EDR_519` | Wisprider | Battlecry: Imbue your Hero Power, then trigger it. | imbue |
| `EDR_800` | Flutterwing Guardian | Taunt, Divine Shield Battlecry: Imbue your Hero Power. | imbue |
| `EDR_845` | Hamuul Runetotem | Start of Game: If each spell in your deck is Nature, Imbue your Hero Power. Repeat this every 3 spells you cast. | imbue, deck_or_setup |
| `EDR_852` | Bitterbloom Knight | Battlecry: Imbue your Hero Power. | imbue |
| `EDR_860` | Resplendent Dreamweaver | Lifesteal Battlecry: If you've Imbued your Hero Power twice, deal 4 damage to a minion. | imbue |
| `EDR_871` | Spirit Gatherer | Battlecry: Get a Wisp. Imbue your Hero Power. | imbue |
| `EDR_888` | Malorne the Waywatcher | Battlecry: Discover a Legendary Wild God. If you've Imbued your Hero Power 4 times, set its Cost to (1). | global_pool_review, imbue |
| `EDR_970` | Kaldorei Priestess | Battlecry: Give all enemy minions -2 Attack until your next turn. Imbue your Hero Power. | imbue |
| `END_000` | Eventuality | Deal $2 damage. Imbue your Hero Power. | imbue |
| `END_001` | Jagged Edge of Time | Battlecry: Imbue your Hero Power. | imbue |
| `END_003` | Finality | Draw an Undead. Imbue your Hero Power twice. | imbue |
| `FIR_921` | Petal Picker | Battlecry: If you've Imbued your Hero Power twice, draw 2 cards. | imbue |

## Leech health stealing — 3 cards (B)

Implement the fixed Leech token and player-level steal amount; include lowest-health ties and hero/minion health semantics.

| ID | Card | Printed rule | Additional note / review tags |
| --- | --- | --- | --- |
| `EDR_810` | Hideous Husk | Your Leeches steal 1 more Health from their victims. Battlecry: Summon two 0/2 Leeches. | Pinned EDR_810t steals health from the lowest-health enemy for the hero; not an ordinary damage/heal pair. |
| `EDR_814` | Infested Breath | Deal $2 damage. Summon a 0/2 Leech. | Simple parent spell depends on the complete Leech token behavior. |
| `EDR_817` | Sanguine Infestation | Draw 2 cards. Summon two 0/2 Leeches. | Simple draw spell depends on the complete Leech token behavior. |

## Leyline scaling and persistent upgrades — 7 cards (B)

Implement the three related Leylines and shared upgrade/cost/repetition state; random-minion Leyline also needs pool closure.

| ID | Card | Printed rule | Additional note / review tags |
| --- | --- | --- | --- |
| `MEND_500` | Bursting Leyline | Deal ${0} damage to a random enemy minion. Excess damage hits the enemy hero. | global_pool_review |
| `MEND_501` | Ley Walker | Battlecry: Your Leylines cost (1) less this game. Deathrattle: Get a random Leyline. | Review timing, generated dependencies and interactions. |
| `MEND_502` | Crystallized Leyline | Summon a random {0}-Cost minion. | global_pool_review |
| `MEND_503` | Surge Needle | Battlecry: Your Leylines trigger an additional time this game. | Review timing, generated dependencies and interactions. |
| `MEND_504` | Leyline Nexus | Draw a card. It costs ({0}) less. | Review timing, generated dependencies and interactions. |
| `MEND_505` | The Arcanomicon | Get all 3 Leylines. Choose an upgrade for your Leylines. | Review timing, generated dependencies and interactions. |
| `MEND_506` | Mystic Runesaber | Elusive Battlecry: Increase the effects of your Leylines by 1 this game. | Review timing, generated dependencies and interactions. |

## Play onto either board — 5 cards (B)

Extend action encoding, board-space legality and controller-dependent Battlecries/deathrattles.

| ID | Card | Printed rule | Additional note / review tags |
| --- | --- | --- | --- |
| `CAP_004` | Disguised Operator | Can be played on either side. Rush. Deathrattle: Your opponent draws 2 cards. | Review timing, generated dependencies and interactions. |
| `JAIL_442` | Disguised Doctor | Can be played on either side. Deathrattle: Shuffle 4 Blights into your deck that deal 2 damage when drawn. | Also depends on Blight draw-autocasting; playing on either side alone does not complete it. |
| `JAIL_452` | Disguised Detective | Can be played on either side. Overload that player for (2). | Review timing, generated dependencies and interactions. |
| `JAIL_455` | Disguised Watchman | Can be played on either side. Battlecry: Deal 1 damage to all other friendly minions, twice. | Review timing, generated dependencies and interactions. |
| `JAIL_461` | Disguised Executioner | Can be played on either side. Battlecry: Destroy a random adjacent minion. | global_pool_review |

## Prepare — 19 cards (B)

Implement shared Prepare action, discount/progress state and associated triggers; complex reward effects remain separate dependencies.

| ID | Card | Printed rule | Additional note / review tags |
| --- | --- | --- | --- |
| `CAP_407` | Wanted Poster | Discover a minion that costs (5) or more. Give it Prepare. | global_pool_review, prepare |
| `CATA_EVENT_400` | Commissary Crook | Prepare Battlecry: Spend all your Mana. Summon a random minion of that Cost. | global_pool_review, prepare |
| `CATA_EVENT_401` | Tunneling Geomancer | Prepare Spell Damage +1 | prepare |
| `JAIL_321` | Tricksy Improviser | Prepare Battlecry: If you've cast a spell this turn, cast two random Mage Secrets. | prepare, nested_casting |
| `JAIL_326` | Judgment | Prepare Choose a friendly minion. Set all minions' stats equal to that minion's. | prepare |
| `JAIL_395` | Sewer Swimmer | Prepare Battlecry: Trigger a friendly minion's Deathrattle. | prepare |
| `JAIL_407` | Vanessa the Ringleader | Prepare After you play a card, get a random Battlecry minion. It costs (2) less. | global_pool_review, prepare |
| `JAIL_444` | Sawbones | Prepare. Battlecry: Destroy all your other minions. Draw a card and refresh a Mana for each one destroyed. | prepare |
| `JAIL_453` | Jailbird | Taunt. When you Prepare while holding this, reduce this card's Cost by the same amount. | prepare |
| `JAIL_457` | Hijacked Securitybot | Prepare Battlecry: Give your other minions +1/+1. | prepare |
| `JAIL_718` | Black Market Auctioneer | Prepare Whenever you cast a spell, draw a card. | prepare, nested_casting, draw_resolution |
| `JAIL_721` | Tras'tath, Soul Parasite | Prepare, Rush After you summon a Demon, gain its stats. | prepare |
| `JAIL_735` | Code Violet | Prepare. Summon an 8-Cost minion. If you've cast 3 other spells this turn, do it again.@ ({0} left!) @ (Ready!) | prepare |
| `JAIL_890` | Captive Nathrezim | Prepare, Taunt ALL minions cost (2) more. | prepare |
| `JAIL_906` | Moragg | Prepare. Deathrattle: Summon a random Demon from your deck. Give it "Deathrattle: Summon Moragg." | global_pool_review, prepare |
| `JAIL_909` | Defias Wannabe | Prepare Combo: Gain +1/+1 for each other card played this turn.@ (@) | prepare |
| `JAIL_912` | Soothsayer | Prepare, Taunt Deathrattle: Restore #6 Health to your hero. Summon a random 6-Cost minion. | global_pool_review, prepare |
| `JAIL_913` | Hold Them Off! | Prepare Give a minion +5/+5 and Lifesteal. | prepare |
| `JAIL_998` | Defias Smuggler | Prepare. Battlecry: Give a friendly minion +2 Attack and Rush. | prepare |

## Random Bonus Effects — 6 cards (B)

Define the exact keyword pool, exclusions, stacking and steal/transfer rules; shared by multiple cards.

| ID | Card | Printed rule | Additional note / review tags |
| --- | --- | --- | --- |
| `CATA_206` | Twisted Monstrosity | {0}, {1} Each turn this is in your hand, swap between two random Bonus Effects. | Review timing, generated dependencies and interactions. |
| `EDR_849` | Dreambound Raptor | After you play a minion, give it a random Bonus Effect. | Review timing, generated dependencies and interactions. |
| `JAIL_101` | Violet Punisher | Battlecry: Choose an enemy minion. Steal its Bonus Effects and gain +1/+1 for each stolen. | Review timing, generated dependencies and interactions. |
| `TLC_240` | Tyrannogill | Rush Deathrattle: Summon three 2/1 Murlocs. Give them each a random Bonus Effect. | Review timing, generated dependencies and interactions. |
| `TLC_444` | Story of Galvadon | Give a minion three random Bonus Effects. | Review timing, generated dependencies and interactions. |
| `TLC_465` | Stranglevine | Deathrattle: Give a random friendly minion a random Bonus Effect and this Deathrattle. | global_pool_review |

## Recorded deathrattle replay — 3 cards (B)

Reuse captured death records but add nested resumable effect replay and listener/death ordering.

| ID | Card | Printed rule | Additional note / review tags |
| --- | --- | --- | --- |
| `DINO_415` | Story of Umbra | Discover a Deathrattle minion that costs (5) or more. Summon it and trigger its Deathrattle. | global_pool_review |
| `JAIL_940` | Undeath Sentence | Trigger the Deathrattle of a random friendly minion that died this game. | global_pool_review |
| `TLC_106` | Endbringer Umbra | Battlecry: Trigger the Deathrattles of 5 friendly minions that died this game. | Review timing, generated dependencies and interactions. |

## Temporary cards and attached hand effects — 10 cards (B)

Add temporary generated-card expiry and playable-hand-card grant semantics; generated pools remain separate dependencies.

| ID | Card | Printed rule | Additional note / review tags |
| --- | --- | --- | --- |
| `CAP_002` | Follow the Footsteps | Discover a Stealth minion. Give it this effect for a turn. | global_pool_review |
| `CAP_101` | Follow the Fuse | Deal $2 damage to a random enemy. Give a playable Pirate in your hand this effect for a turn. | global_pool_review |
| `CAP_402` | Follow the Evidence | Put a 3/3 Imp-formant into the enemy deck. Give a playable card in your hand this effect for a turn. | Also needs enemy-deck Imp-formant auto-summoning; temporary hand grants are not its only dependency. |
| `CAP_802` | Follow the Ghosts | Summon a 2/1 Ghost with Reborn. Give a playable card in your hand this effect for a turn. | Review timing, generated dependencies and interactions. |
| `JAIL_986` | Frantic Forger | Battlecry: Get a random playable spell. It is Temporary. | global_pool_review |
| `TLC_446` | Escape the Underfel | Quest: Play 6 Temporary cards. Reward: Underfel Rift. | Also needs Quest tracking and its complete reward, not only Temporary cards. |
| `TLC_449` | Bloodpetal Biome | Discover a Temporary 1-Cost minion. | global_pool_review |
| `TLC_450` | Spelunker | Battlecry: Your next Temporary card costs (2) less. | Review timing, generated dependencies and interactions. |
| `TLC_451` | Cursed Catacombs | Discover another card from your deck. Make it Temporary. | global_pool_review |
| `TLC_469` | Tunnel Terror | Deathrattle: Get two random Temporary 2-Cost minions. | global_pool_review |

## Type matching and Kindred selectors — 5 cards (B)

Extend multi-type matching, distinct selection and Kindred partner eligibility; verify ALL-type and overlapping-type cases.

| ID | Card | Printed rule | Additional note / review tags |
| --- | --- | --- | --- |
| `CORE_WON_141` | Menagerie Mug | Battlecry: Give 3 random friendly minions of different minion types +1/+1. | global_pool_review |
| `TLC_102` | Torga | Battlecry: Draw a Kindred card and another card that activates it. | Review timing, generated dependencies and interactions. |
| `TLC_110` | City Chief Esho | Battlecry: If every minion in your deck shares a minion type, give your other minions +2/+2 (wherever they are). | Review timing, generated dependencies and interactions. |
| `TLC_222` | Flight of the Firehawk | Draw two minions of different minion types. Give them +1/+1. | Review timing, generated dependencies and interactions. |
| `TLC_254` | Tortollan Storyteller | At the end of your turn, give +1/+1 to each friendly minion of a different type. | Review timing, generated dependencies and interactions. |

## Void Soul generation and upgrades — 4 cards (B)

Review and implement the fixed Void Soul dependency plus persistent upgrade state; a random-generator member also needs its full pool.

| ID | Card | Printed rule | Additional note / review tags |
| --- | --- | --- | --- |
| `JAIL_730` | Stardust Scythe | After your hero attacks, get a Void Soul. | Review timing, generated dependencies and interactions. |
| `JAIL_732` | Void Soul | Summon a random 1-Cost Demon. Improve your future Void Souls. | global_pool_review |
| `JAIL_733` | Vicious Voidscale | Taunt Deathrattle: Get a Void Soul. | Review timing, generated dependencies and interactions. |
| `JAIL_891` | Void Blast | Deal $3 damage to a minion. If it dies, get a Void Soul. | Review timing, generated dependencies and interactions. |

## Global generation/Discover pool dependencies — 127 cards (C)

Main effect often uses familiar operations, but exact pool eligibility and every possible generated card must work. No supported-only pool substitution. Additional card-specific conditions may still need local glue.

| ID | Card | Printed rule | Additional note / review tags |
| --- | --- | --- | --- |
| `CAP_105` | Hook n' Heave | Discover a Pirate. Summon two 1/1 Cannoneers. | global_pool_review |
| `CATA_136` | Azshara's Triumph | Shuffle 5 random minions into your deck that cost (8) or more. Double their stats. | global_pool_review |
| `CATA_140` | Merithra of the Dream | Battlecry: Fill your hand with random Dragons. If you spent 25 Mana while holding this, they cost (1). ({0} left!)@Battlecry: Fill your hand with random Dragons. If you spent 25 Mana while holding this, they cost (1). (Ready!)@Battlecry: Fill your hand with random Dragons. If you spent 25 Mana while holding this, they cost (1). | global_pool_review |
| `CATA_471` | Talanji's Last Stand | Give your minions "Deathrattle: Summon a random 4-Cost minion." | global_pool_review |
| `CATA_474` | Spearheart Sentry | At the end of your turn, get a random Holy spell. Reduce its Cost by (3). | global_pool_review |
| `CATA_484` | Winterspring Whelp | Battlecry: Discover a 1-Cost spell from any class. | global_pool_review |
| `CATA_499` | Disposable Acolytes | When you play or discard this, summon two random 1-Cost minions. | global_pool_review |
| `CATA_556` | Carrier Whelp | Battlecry: Get a random Dragon that costs (3) or less. | global_pool_review |
| `CATA_569` | Ceremonial Clash | Summon a random 3, 2, and 1-Cost minion. Overload: (1) | global_pool_review |
| `CATA_614` | Shadowed Informant | Battlecry: Discover a spell from your class. (Swaps class each turn!) | global_pool_review |
| `CATA_723` | Drakeadon Mongrel | Deathrattle: Summon two random 4-Cost minions. | global_pool_review |
| `CATA_979` | Conjuration Specialist | Battlecry: Choose a spell in your hand. Split it into two random spells of the same Cost. | global_pool_review |
| `CORE_AT_062` | Ball of Spiders | Summon three 1/1 Webspinners with "Deathrattle: Get a random Beast." | global_pool_review |
| `CORE_AV_107` | Glaciate | Discover an 8-Cost minion. Summon and Freeze it. | global_pool_review |
| `CORE_BAR_541` | Runed Orb | Deal $2 damage. Discover a spell. | global_pool_review |
| `CORE_BOT_256` | Astromancer | Battlecry: Summon a random minion with Cost equal to your hand size. | global_pool_review |
| `CORE_BT_321` | Netherwalker | Battlecry: Discover a Demon. | global_pool_review |
| `CORE_CATA_006` | Ulfar | Battlecry: Give your other minions "Deathrattle: Summon a minion with this minion's Cost." | Review timing, generated dependencies and interactions. |
| `CORE_CATA_009` | Death's Advance | Freeze a character. Discover a spell. | global_pool_review |
| `CORE_CFM_781` | Shaku, the Collector | Stealth Whenever this attacks, add a card from another class to your hand. | Review timing, generated dependencies and interactions. |
| `CORE_DRG_024` | Sky Raider | Battlecry: Add a random Pirate to your hand. | global_pool_review |
| `CORE_EDR_001` | Babbling Bookcase | Battlecry: Add 2 random Mage spells to your hand. | global_pool_review |
| `CORE_ETC_111` | Merch Seller | At the end of your turn, put a random spell on the top of your opponent's deck. | global_pool_review |
| `CORE_EX1_189` | Brightwing | Battlecry: Add a random Legendary minion to your hand. | global_pool_review |
| `CORE_GIL_531` | Witch's Apprentice | Taunt Battlecry: Add a random Shaman spell to your hand. | global_pool_review |
| `CORE_GIL_836` | Blazing Invocation | Discover a Battlecry minion. It costs (1) less. | global_pool_review |
| `CORE_GVG_114` | Sneed's Old Shredder | Deathrattle: Summon a random Legendary minion. | global_pool_review |
| `CORE_KAR_057` | Ivory Knight | Battlecry: Discover a spell. Restore Health to your hero equal to its Cost. | global_pool_review |
| `CORE_KAR_062` | Netherspite Historian | Battlecry: If you're holding a Dragon, Discover a Dragon. | global_pool_review |
| `CORE_KAR_069` | Swashburglar | Battlecry: Add a random card from another class to your hand. | global_pool_review |
| `CORE_KAR_077` | Silvermoon Portal | Give a minion +2/+2. Summon a random 2-Cost minion. | global_pool_review |
| `CORE_LOE_039` | Gorillabot A-3 | Battlecry: If you control another Mech, Discover a Mech. | global_pool_review |
| `CORE_ONY_022` | Battle Vicar | Battlecry: Discover a Holy spell. | global_pool_review |
| `CORE_REV_308` | Maze Guide | Battlecry: Summon a random 2-Cost minion. | global_pool_review |
| `CORE_RLK_066` | Hematurge | Battlecry: Spend a Corpse to Discover a Blood Rune card. | global_pool_review |
| `CORE_RLK_116` | Necrotic Mortician | Battlecry: If a friendly Undead died after your last turn, Discover an Unholy Rune card. | global_pool_review |
| `CORE_TID_931` | Jackpot! | Add two random spells from other classes that cost (5) or more to your hand. | global_pool_review |
| `CORE_UNG_912` | Jeweled Macaw | Battlecry: Add a random Beast to your hand. | global_pool_review |
| `CORE_WON_096` | Dark Peddler | Battlecry: Discover a 1-Cost card. | global_pool_review |
| `CORE_WON_337` | Ironforge Portal | Gain 4 Armor. Summon a random 4-Cost minion. | global_pool_review |
| `CORE_WON_350` | I Know a Guy | Discover a Taunt minion. Give it +1/+2. | global_pool_review |
| `CORE_WW_374` | Corpse Farm | Spend up to 8 Corpses to summon a random minion of that Cost. | global_pool_review |
| `CORE_YOP_001` | Illidari Studies | Discover an Outcast card. Your next one costs (1) less. | global_pool_review |
| `Core_LOE_115` | Raven Idol | Choose One - Discover a minion; or Discover a spell. | global_pool_review |
| `Core_UNG_072` | Stonehill Defender | Taunt Battlecry: Discover a Taunt minion. | global_pool_review |
| `DINO_412` | Tortotem | At the end of your turn, get a random minion with multiple minion types. | global_pool_review |
| `DINO_424` | Hero's Welcome | Discover a Legendary minion to summon. Set its stats to 10/10. | global_pool_review |
| `DINO_426` | Ritual of Life | Discover a 3-Cost minion. Summon a 2/3 copy of it. | global_pool_review |
| `DINO_427` | Costume Merchant | Battlecry: Get a random Mask from another class. Combo: It costs (2) less. | Review timing, generated dependencies and interactions. |
| `DINO_430` | Beast Speaker Taka | Battlecry: Discover a Legendary Beast from any class to gain its stats. Deathrattle: Summon it. | global_pool_review |
| `DINO_431` | Atlasaurus | Taunt. Deathrattle: Summon a random Taunt minion that costs (5) or more. | global_pool_review |
| `DINO_433` | Guard Duty | Summon a random 6, 4, and 2-Cost Taunt minion. | global_pool_review |
| `DINO_434` | Raptor-Nest Nurse | Battlecry: Get a random 1-Cost minion. Deathrattle: Get a random 1-Cost spell. | global_pool_review |
| `EDR_060` | Ward of Earth | Gain 5 Armor. Summon a random 5-Cost minion and give it Taunt. | global_pool_review |
| `EDR_270` | Horn of Plenty | Discover a Nature spell. It costs (2) less. | global_pool_review |
| `EDR_273` | Symbiosis | Discover a Choose One card from another class. | global_pool_review |
| `EDR_461` | Ritual of the New Moon | Summon two random 3-Cost minions. (Cast 3 spells to summon 6-Cost minions instead.) | global_pool_review |
| `EDR_462` | Selenic Drake | Elusive At the end of your turn, get a random Dragon. | global_pool_review |
| `EDR_463` | Twilight Influence | Choose One - Destroy a minion with 3 or less Attack; or Summon a random 2-Cost minion. | global_pool_review |
| `EDR_465` | Ysondre | Taunt. Deathrattle: Summon a random Dragon for each time Ysondre has died this game. | global_pool_review |
| `EDR_493` | Alara'shi | Battlecry: Transform minions in your hand into random Demons. (They keep their original stats and Cost.) | global_pool_review |
| `EDR_517` | Q'onzu | Battlecry: Discover a spell. Choose to keep it or put it on top of your opponent's deck. | global_pool_review |
| `EDR_530` | Daydreaming Pixie | At the end of your turn, get a random Nature spell. | global_pool_review |
| `EDR_848` | Photosynthesis | Restore #6 Health. Get 3 random Druid spells. | global_pool_review |
| `EDR_872` | Spark of Life | Choose One - Discover a Mage spell; or Discover a Druid spell. | global_pool_review |
| `EDR_873` | Envoy of the Glade | Battlecry: Transform all Neutral cards in your deck into random Druid ones. | Review timing, generated dependencies and interactions. |
| `EDR_999` | Gnawing Greenfin | Battlecry: Get a random Murloc. | global_pool_review |
| `END_005` | Bygone Echoes | Summon a random 4-Cost minion. Spend 4 Corpses to summon another. Outcast: And another. | global_pool_review |
| `END_015` | Triennium Rex | Kindred and Deathrattle: Get a random Deathrattle minion. It costs (2) less. | global_pool_review |
| `END_020` | Eternal Toil | Deal $1 damage to a minion. If it survives, draw a card. If it dies, summon a random 1-Cost minion. | global_pool_review |
| `END_029` | Voodoo Totem | At the end of your turn, get a random Shadow spell. | global_pool_review |
| `FIR_907` | Amirdrassil | Summon a 1-Cost minion. Gain 1 Armor. Draw 1 card. Refresh 1 Mana \|4(Crystal, Crystals). (Improves each use!) | Review timing, generated dependencies and interactions. |
| `FIR_913` | Inferno Herald | After you cast a Fire spell, get a random Elemental and reduce its Cost by (3). | global_pool_review, nested_casting |
| `FIR_927` | Emberscarred Whelp | Battlecry: Discover a 5-Cost card. Gain 1 Mana Crystal next turn only. | global_pool_review |
| `FIR_952` | Scorchreaver | Battlecry: Discover a Fel spell. Reduce the Cost of Fel spells in your hand by (1). | global_pool_review |
| `JAIL_122` | Jailhouse Manastorm | Battlecry: After you cast a spell this game, summon a random minion of the same Cost. | global_pool_review, nested_casting |
| `JAIL_125` | Cold Snap | Freeze an enemy. Get a random Frost spell. | global_pool_review |
| `JAIL_200` | Infest the Scullery | Summon two random 3-Cost minions. (Improved by your hero attacks this game.) | global_pool_review |
| `JAIL_201` | Secret Ingredient | Choose One - Give your hero +2 Attack this turn; or get a random Druid card. | global_pool_review |
| `JAIL_313` | Bootleg Alchemist | Battlecry: Choose a card in your hand. Transform it into a spell that costs (5) more (keeps its original Cost). | Review timing, generated dependencies and interactions. |
| `JAIL_328` | Scarlet Bruiser | Deathrattle: If your deck has no Neutral cards, get a random Paladin card. It costs (2) less. | global_pool_review |
| `JAIL_448` | Karov the Broken | Taunt Deathrattle: Get three 1/1 copies of random Legendary minions. They cost (1). | global_pool_review |
| `JAIL_451` | Blood Clone | Discover a 5-Cost minion. Spend 5 Corpses to summon a copy of it. | global_pool_review |
| `JAIL_460` | Concealing Confection | Deathrattle: Get a random weapon. | global_pool_review |
| `JAIL_474` | Jade Guardians | Get two random 8-Cost minions. They cost (1) less for each card you played for 2 Mana this game.@ (@) | global_pool_review |
| `JAIL_507` | Spiteful Chef | Battlecry: Summon a 2-Cost Taunt minion. If you have 10 or more Mana, summon a 6-Cost instead. | Review timing, generated dependencies and interactions. |
| `JAIL_706` | Thief's Tools | Get two random 4-Cost spells. Reduce their Costs by (2). | global_pool_review |
| `JAIL_806` | Hexmarshal | Battlecry: Get a random spell that costs (5) or more. If your deck started with no spells, it costs (5) less. | global_pool_review |
| `JAIL_875` | Staff of Trickery | After your hero attacks, Discover a Druid card. Reduce its Cost by your hero's Attack. | global_pool_review |
| `JAIL_876` | Dig for Freedom | Give a friendly minion "Deathrattle: Summon two random 4-Cost minions." | global_pool_review |
| `JAIL_878` | Guard Dog | Deathrattle: Summon a random 1-Cost Deathrattle minion. | global_pool_review |
| `JAIL_892` | Cosmic Manifestations | Deal $2 damage. Shuffle a random Demon Hunter spell into your deck. Outcast: Do it again. | global_pool_review |
| `JAIL_EVENT_102` | Desperate Bribe | Summon two 2-Cost minions for each player. Transform your minions into ones that cost (1) more. | Review timing, generated dependencies and interactions. |
| `MEND_042` | Lifebloom | Restore #8 Health to all friendly characters. Summon two random 8-Cost minions. | global_pool_review |
| `MEND_045` | Seeding Dragon | Taunt Deathrattle: Get a random Dragon. It costs (2) less. | global_pool_review |
| `RLK_025` | Frost Strike | Deal $3 damage to a minion. If it dies, Discover a Frost Rune card. | global_pool_review |
| `TIME_013` | Farseer Wo | Elusive After you cast a spell, Discover a Nature spell from the past. | global_pool_review, nested_casting |
| `TIME_016` | Neon Innovation | Discover a Paladin Mech from the past. Give it +5/+5. | global_pool_review |
| `TIME_040` | Fading Memory | Deathrattle: Get a random 5-Cost minion from the past. | global_pool_review |
| `TIME_049` | Dangerous Variant | At the start of your turn, transform into a random 5-Cost minion. | global_pool_review |
| `TIME_052` | Amber Warden | Taunt Deathrattle: Summon a random minion from the past. | global_pool_review |
| `TIME_055` | Unknown Voyager | After this survives damage, transform into a random 7-Cost minion. | global_pool_review |
| `TIME_102` | Circadiamancer | Battlecry: Add a random 8-Cost minion to your hand. At the start of your turns, reduce its Cost by (1). | global_pool_review |
| `TIME_444` | Time-Lost Glaive | Deathrattle: Get a random Demon from the past. | global_pool_review |
| `TIME_446` | The Eternal Hold | Discover any Demon that costs (5) or more. If your deck has no minions, your next one costs (1). | global_pool_review |
| `TIME_448` | Solitude | Discover 2 minions. If your deck has no minions, reduce the Cost of any in your hand by (2). | global_pool_review |
| `TIME_613` | Cryofrozen Champion | Deathrattle: Get a random Legendary minion. Reduce its Cost by (1). | global_pool_review |
| `TIME_707` | Alternate Reality | Replace your hand and deck with random Choose One cards from the past. They cost (1) less. | global_pool_review |
| `TIME_711` | Flashback | Summon two random 1-Cost minions from the past. Combo: With +1 Attack. | global_pool_review |
| `TIME_712` | Dethrone | Destroy a minion. Combo: Summon a random 8-Cost minion. | global_pool_review |
| `TIME_730` | Kaldorei Cultivator | Battlecry: Discover 2 Beasts. Put them on the bottom of your deck with +5/+5. | global_pool_review |
| `TIME_857` | Alter Time | Discover two Arcane spells from the past. They cost (2) less. | global_pool_review |
| `TIME_859` | Anomalize | Summon a random 10 and 1-Cost minion. Scramble their stats. | global_pool_review |
| `TIME_872` | Undefeated Champion | Rush. Battlecry: Fill your opponent's board with random 1-Cost minions. | global_pool_review |
| `TIME_EVENT_997` | Welcome Home! | Reopen a location. Give it "Deathrattle: Summon a random 3-Cost minion." | global_pool_review |
| `TLC_109` | Relic Miner | Battlecry: Destroy the top card of your deck. Discover a card of the same Rarity. | global_pool_review |
| `TLC_235` | Life Cycle | Destroy a minion. Summon a random minion of the same Cost to replace it. | global_pool_review |
| `TLC_334` | Relic of Kings | Discover a spell from any class that costs (8) or more. It costs (1). | global_pool_review |
| `TLC_434` | Paleomancy | Discover an Undead. Spend 5 Corpses to keep all 3 instead. | global_pool_review |
| `TLC_461` | Scrappy Scavenger | Battlecry: Discover a card with Cost equal to your remaining Mana Crystals. | global_pool_review |
| `TLC_462` | Unearthed Artifacts | Summon a random 2-Cost minion. If you've Discovered this turn, summon a random 4-Cost minion instead. | global_pool_review |
| `TLC_477` | Threshrider's Blessing | Give a friendly minion +4/+4 and "Deathrattle: Summon a random 4-Cost minion." | global_pool_review |
| `TLC_479` | Deathrot Maw | Taunt Deathrattle: Summon a random Fel Beast. | global_pool_review |
| `TLC_514` | Merchant of Legend | Battlecry: Discover a Legendary minion. Shuffle the other two into your deck. | global_pool_review |
| `TLC_516` | Neferset Weaponsmith | Battlecry: Get a random weapon from another class. Combo: Give it +2 Attack. | global_pool_review |
| `TLC_814` | Twilight Mender | Deathrattle: Get a random Holy and Shadow spell. | global_pool_review |
| `TLC_815` | Gravedawn Voidbulb | Summon a random 4-Cost minion and give it Taunt. Kindred: Do it again. | global_pool_review |

## Casting/replaying cards inside effects — 21 cards (D)

Need nested play frames, legal/random targets, counter/trigger timing and resumable repeated effects; damage-only substitutions are insufficient.

| ID | Card | Printed rule | Additional note / review tags |
| --- | --- | --- | --- |
| `CATA_154` | Sinestra | Colossal +2 Your spells from other classes cast twice. | colossal, nested_casting |
| `CATA_563` | Crackling Cloudstrider | Battlecry: Choose a spell in your hand that costs (4) or less to absorb. Deathrattle: Cast it. | Review timing, generated dependencies and interactions. |
| `CATA_786` | Chaos Supplicant | After you cast a spell, cast a random spell of the same Cost from another class. | global_pool_review, nested_casting |
| `CORE_WON_145` | Avatar of Hearthstone | Battlecry: Open a Standard Pack. Play all cards from it. | Review timing, generated dependencies and interactions. |
| `EDR_031` | Ohn'ahra | At the end of your turn, play the top 3 cards from your deck. | Review timing, generated dependencies and interactions. |
| `EDR_259` | Ursol | Battlecry: Cast the highest Cost spell from your hand as an Aura that lasts 3 turns. | Review timing, generated dependencies and interactions. |
| `EDR_464` | Tyrande | Battlecry: The next 3 spells you play cast twice. | nested_casting |
| `EDR_520` | Forbidden Shrine | Spend all your Mana. Cast a random spell that costs that much. | global_pool_review, nested_casting |
| `FIR_959` | Fyrakk the Blazing | Immune to Fire spells. Battlecry: Cast 15 Mana worth of Fire spells at random enemies. | Review timing, generated dependencies and interactions. |
| `JAIL_123` | Breakout Architect | Battlecry: Discover a spell that costs (5) or more. It casts twice when played. | global_pool_review |
| `JAIL_500` | Slice and Dice | Replay all other cards played this turn (targeting enemies if possible). End your turn. | nested_casting |
| `JAIL_515` | Shadow Rounds | Deal $2 damage to an enemy minion. If it dies, cast this on another random enemy minion. | global_pool_review |
| `JAIL_974` | Captured Archmage | Deathrattle: If you had 4 other Captured Archmages die this game, cast 'Fireball' at a random enemy.@ (@/4) | Review timing, generated dependencies and interactions. |
| `MEND_046` | Bashana Runetotem | Battlecry: Get three 2/2 Treants. Carve 12 Mana worth of Nature spells into them. | Review timing, generated dependencies and interactions. |
| `MEND_100` | Cultivating Sprite | Battlecry: Get a 3-Cost Bulb that casts three random 1-Cost spells. It upgrades each turn. | global_pool_review |
| `TIME_033` | Druid of Regrowth | Rewind Battlecry: Cast 2 random Nature spells. | Also has Rewind and exact Nature-spell eligibility; nested casting is the primary blocker. |
| `TIME_860` | Faceless Enigma | Battlecry: Look at 2 random Secrets. Pick one to cast for yourself. The other casts for your opponent. | Review timing, generated dependencies and interactions. |
| `TLC_430` | Creature of the Sacred Cave | At the end of your turn, recast a random Holy spell you cast this turn (targets this if possible). | global_pool_review, nested_casting |
| `TLC_438` | Violet Treasuregill | Battlecry: Cast a random spell from your deck that costs (2) or less (targets this if possible). | global_pool_review, nested_casting |
| `TLC_522` | Opu the Unseen | Stealth. Battlecry, Combo, and Deathrattle: Cast 'Fan of Knives'. | Review timing, generated dependencies and interactions. |
| `TLC_836` | Niri of the Crater | Whenever you play a 1-Cost minion, double its stats. Whenever you cast a 1-Cost spell, cast it twice. | nested_casting |

## Casts/Summons When Drawn — 16 cards (D)

Need a resumable draw pipeline, automatic effect resolution/replacement draw, burned-card rules and correct summon controller.

| ID | Card | Printed rule | Additional note / review tags |
| --- | --- | --- | --- |
| `CAP_400` | Kabal Conspirator | Deathrattle: Put two 3/3 Imp-formants into the enemy deck. They summon for YOU when drawn. | draw_resolution |
| `CAP_401` | Corrupt Constable | Battlecry: If the enemy deck has any Imp-formants, move one to the top and give it +2/+2. | Review timing, generated dependencies and interactions. |
| `CAP_404` | Harsh Sentence | Enemy minions cost (2) more next turn. Put two 3/3 Imp-formants into the enemy deck. | Review timing, generated dependencies and interactions. |
| `CAP_406` | Kabal Mastermind | Taunt. Battlecry: Whenever you summon an Imp-formant this game, give it +2/+2. | Review timing, generated dependencies and interactions. |
| `CORE_SW_439` | Vibrant Squirrel | Deathrattle: Shuffle 4 Acorns into your deck. When drawn, summon a 2/1 Squirrel. | draw_resolution |
| `EDR_260` | Illusory Greenwing | Taunt. Deathrattle: Shuffle two 4/5 Dragons with Taunt into your deck. They're Summoned When Drawn. | draw_resolution |
| `JAIL_386` | Scramble for Gear | Gain 2 Armor. Shuffle five Gear spells into your deck that give 2 Armor when drawn. | draw_resolution |
| `JAIL_443` | The Living Plague | Charge. Instead of damaging heroes, this shuffles that many Blights into their deck that deal 2 damage when drawn. | draw_resolution |
| `JAIL_879` | Beast Tripwire | Summon a random 5-Cost Beast. Shuffle 2 spells into your deck that do it again when drawn. | global_pool_review, draw_resolution |
| `JAIL_881` | Arcane Tripwire | Deal $4 damage split among all enemies. Shuffle 2 spells into your deck that do it again when drawn. | draw_resolution |
| `TIME_025` | Twilight Timehopper | Battlecry: Shuffle 2 Shreds of Time into your deck. When drawn, deal 3 damage to your hero. | draw_resolution |
| `TIME_026` | Entropic Continuity | Give your minions +1/+1. Shuffle 2 Shreds of Time into your deck. | Review timing, generated dependencies and interactions. |
| `TIME_027` | Tachyon Barrage | Deal $6 damage split among all enemies. Shuffle 2 Shreds of Time into your deck. | Review timing, generated dependencies and interactions. |
| `TIME_028` | Fatebreaker | Lifesteal Battlecry: Cast a Shred of Time from your deck to gain +3/+3. | nested_casting |
| `TIME_029` | Ruinous Velocidrake | Rush Battlecry: Cast a Shred of Time from your deck to summon a copy of this. | nested_casting |
| `TLC_518` | Interrogation | Shuffle three 3/3 Ninjas with Stealth into your deck that are Summoned When Drawn. | draw_resolution |

## Colossal and appendages — 12 cards (D)

Implement appendage placement, lifecycle and component-specific effects; some also require forced attacks or spell repetition.

| ID | Card | Printed rule | Additional note / review tags |
| --- | --- | --- | --- |
| `CATA_139` | Wickerfang | Colossal +4 After one of Wickerfang's Legs gains stats, this gains them too. | colossal |
| `CATA_150` | Ragnaros, the Great Fire | Colossal +2 At the end of your turn, trigger your minions' Deathrattles. | colossal |
| `CATA_151` | Azshara, Ocean Lord | Colossal +2 Your hero has Windfury. | colossal |
| `CATA_153` | Al'Akir, Lord of Storms | Colossal +2, Rush, Windfury Battlecry: Get 2 minions with Cost equal to this minion's Attack. They cost (1). | colossal |
| `CATA_155` | Arisen Onyxia | Colossal +2. When your hero would lose Health on your turn, gain that much max Health instead. | colossal |
| `CATA_300` | The Black Blood | Colossal +3. After you restore Health to a character, attack a random enemy minion. | global_pool_review, colossal, forced_combat |
| `CATA_432` | Chromatus | Colossal +4 Taunt, Lifesteal, Elusive, Divine Shield | colossal |
| `CATA_488` | Vulcanos | Colossal +2 At the end of your turn, deal 3 damage to all other minions. | colossal |
| `CATA_527` | Nespirah, Enthralled | Deal 1 damage. After you cast a Fel spell, reopen. Deathrattle: Summon Nespirah, Unshackled. | Generated Nespirah adds an appendage lifecycle dependency despite no Colossal keyword in the parent text. |
| `CATA_550` | Magmaw | Colossal +99 Summon any leftover appendages when there is room. | colossal |
| `CATA_726` | Cho'gall, Mastermind | Colossal +2 Your Arms and Soldiers destroy minions in the enemy's deck instead. | colossal |
| `CATA_EVENT_000` | Primordial Lord | Battlecry: Get a random Colossal minion from the past. | global_pool_review, colossal |

## Custom or unusual persistent systems — 36 cards (D)

Needs a dedicated state/action contract and generated effects; research/implementation effort is not established by a short card description.

| ID | Card | Printed rule | Additional note / review tags |
| --- | --- | --- | --- |
| `CAP_405` | Godfather Kazakus | Battlecry: Plot a custom sham trial! Then choose the trial's length. | Review timing, generated dependencies and interactions. |
| `CAP_805` | Slime 'em! | Destroy all minions. Each player gets a 3-Cost spell that resummons theirs. | Review timing, generated dependencies and interactions. |
| `CATA_470` | Victor Nefarius | Battlecry: Craft a custom Undead Dragon. If you're holding a Dragon, reduce the Creation's Cost by (3). | Review timing, generated dependencies and interactions. |
| `CATA_567` | Ascendance | Transform all friendly minions into ones that cost (1) more. They summon the originals when they die. | Review timing, generated dependencies and interactions. |
| `CATA_EVENT_110` | Dragon Soul, Shattered | Start of Game: Break into 6 Essences. Adjoining Essences are cast together. | deck_or_setup |
| `CORE_CFM_670` | Mayor Noggenfogger | All targets are chosen randomly. | Review timing, generated dependencies and interactions. |
| `CORE_DAL_575` | Khadgar | Your cards that summon minions summon twice as many. | Review timing, generated dependencies and interactions. |
| `EDR_529` | Plucky Podling | If this would transform into a minion, it transforms into one that costs (2) more. | Review timing, generated dependencies and interactions. |
| `EDR_818` | Nythendra | Taunt. Deathrattle: Split into 1/1 Beetles. At the start of your turn, reform with any remaining. | Review timing, generated dependencies and interactions. |
| `EDR_895` | Aviana, Elune's Chosen | Battlecry: Start a three turn lunar cycle. When the Full Moon rises, your cards cost (1) this game. | Review timing, generated dependencies and interactions. |
| `END_012` | Hand of Infinity | Can't attack heroes. Battlecry: Set this weapon's Attack to INFINITY this turn! | Review timing, generated dependencies and interactions. |
| `END_018` | Acolyte of Infinity | Battlecry: Set the Cost of a random card in your hand to INFINITY! Deathrattle: Change it back. | global_pool_review |
| `END_024` | Flames of Infinity | Secret: When your enemy's turn ends, deal INFINITE damage to their highest Health minion. | Review timing, generated dependencies and interactions. |
| `END_037` | Endtime Murozond | Battlecry: Fill your board with random Dragons. Fully heal your hero. Skip your next turn. | global_pool_review |
| `JAIL_319` | The Skeleton Key | Discover a spell, or refresh your options (20% chance to take 5 damage each refresh!) | global_pool_review |
| `JAIL_398` | IMPFERNAL! | Deathrattle: Deal 3 damage to all other characters. (Also triggers in hand or deck.) | Review timing, generated dependencies and interactions. |
| `JAIL_458` | Tiny Pal | Battlecry: Choose your elemental ammunition! (After your hero attacks, choose another). | Review timing, generated dependencies and interactions. |
| `JAIL_502` | Alarm-o-Matic | At the start of your turn, swap this minion with a random one in your opponent's hand. | Review timing, generated dependencies and interactions. |
| `JAIL_509` | Godfrey the Betrayer | Start of Game: Overdrawn cards return to your hand when you have space. They cost (1) less. | deck_or_setup |
| `JAIL_719` | Irida Sinseeker | Lifesteal. Battlecry: Send your deck to the Void, except 1 card. At the start of your turns, get two cards from the Void. | Review timing, generated dependencies and interactions. |
| `JAIL_861` | Noxious Bribe | Discover a Choose One card. It has both effects combined. Give your opponent a plain copy. | global_pool_review |
| `JAIL_887` | Zuramat's Prison | Choose a card to discard to summon a 5/5 Taunt. Deathrattle: Free Zuramat who plays one each turn! | Review timing, generated dependencies and interactions. |
| `JAIL_EVENT_100` | Watfin | Battlecry: Discover a minion. Pick the suspicious one to gain +1/+1. | global_pool_review |
| `JAIL_EVENT_101` | Soul Immolation | Your Hero Power becomes 'Collapsing Star'. If it already is, increase its damage by 1. | Review timing, generated dependencies and interactions. |
| `TIME_024` | Murozond, Unbounded | Battlecry: At the start of your next turn, set this minion's Attack to INFINITY! | Review timing, generated dependencies and interactions. |
| `TIME_041` | Futuristic Forefather | Taunt. Battlecry: Look at 3 cards. Guess which one is in your opponent's hand to gain +4 Health. | Review timing, generated dependencies and interactions. |
| `TIME_064` | Chrono-Lord Deios | Your Battlecries, Deathrattles, Hero Power, and end of turn effects trigger twice. | Review timing, generated dependencies and interactions. |
| `TIME_618` | Husk, Eternal Reaper | Battlecry: Give your hero "Deathrattle: Spend up to 20 Corpses to resurrect with that much Health." | Review timing, generated dependencies and interactions. |
| `TIME_704` | Highborne Mentor | Battlecry: Get a 2/2 Pupil. Discover a spell that costs (7) or more from the past to teach it. | global_pool_review |
| `TIME_706` | The Fins Beyond Time | Battlecry: Replace your hand with your starting hand. Swap back at the end of your turn. | deck_or_setup |
| `TIME_861` | Timelooper Toki | Battlecry: Get 3 random spells from the past. When you play ALL 3, get another Timelooper Toki. | global_pool_review |
| `TIME_EVENT_998` | Runi, Temporal Guardian | Battlecry: Send all minions in your hand 2 turns into the future. They return with +5/+5. | Review timing, generated dependencies and interactions. |
| `TLC_100` | Elise the Navigator | Battlecry: If your deck started with 10 cards of different Costs, craft a custom location. | Review timing, generated dependencies and interactions. |
| `TLC_452` | Titanographer Osk | Gains a random Titan ability in your hand that changes each turn. | Review timing, generated dependencies and interactions. |
| `TLC_632` | Story of Sulfuras | Swap your Hero Power to "Deal 8 damage to a random enemy." After 2 uses, swap back. | Review timing, generated dependencies and interactions. |
| `TLC_841` | Entomologist Toru | Battlecry: Put each minion in your hand into 0/1 Jars that cost (1). Break them to release the minions! | Review timing, generated dependencies and interactions. |

## Forced attacks and combat interruption — 24 cards (D)

Need an owner-correct resumable combat API, precombat interruption, retaliation, kill attribution and death/choice checkpoints.

| ID | Card | Printed rule | Additional note / review tags |
| --- | --- | --- | --- |
| `CAP_806` | Raith Van Geist | Battlecry: Resurrect your minions that were Reborn this game. They attack random enemy minions. | global_pool_review, forced_combat |
| `CATA_185` | Faceless Replicator | Elusive Deathrattle: Transform the minion that killed this into a Faceless Replicator. | Review timing, generated dependencies and interactions. |
| `CORE_BT_120` | Warmaul Challenger | Battlecry: Choose an enemy minion. Battle it to the death! | forced_combat |
| `CORE_RLK_086` | Frostmourne | Deathrattle: Summon every minion killed by this weapon. | Review timing, generated dependencies and interactions. |
| `CORE_TTN_866` | Mythical Terror | Lifesteal At the end of your turn, force all enemy minions to attack this. | forced_combat |
| `CS3_020` | Illidari Inquisitor | Rush. After your hero attacks an enemy, this attacks it too. | forced_combat |
| `DINO_400` | Barricade Basher | Whenever you gain Armor, gain +2/+2 and attack a random enemy minion. | global_pool_review, forced_combat |
| `DINO_422` | Ankylodon | Taunt. Deathrattle: Summon two random 3-Cost Beasts. They attack random enemies. | global_pool_review, forced_combat |
| `DINO_428` | Behemoth Mask | Set a minion's stats to 8/10 and give it Lifesteal. Force a random enemy minion to attack it. | global_pool_review, forced_combat |
| `EDR_014` | Verdant Dreamsaber | Battlecry: If this costs (3) or less, attack two random enemy minions. | global_pool_review, forced_combat |
| `EDR_453` | Briarspawn Drake | At the end of your turn, attack a random enemy minion (excess damage hits the enemy hero). | global_pool_review, forced_combat |
| `EDR_819` | Ursoc | Battlecry: Attack ALL other minions. Deathrattle: Resurrect any this killed. | Review timing, generated dependencies and interactions. |
| `JAIL_315` | Mystic Misdirection | Secret: When an enemy minion attacks, transform it into a 1/1 Sheep. | Review timing, generated dependencies and interactions. |
| `JAIL_435` | Rampaging Hound | Prepare Battlecry: Force all enemy minions to attack this. | Also has Prepare; the forced-attack engine is the larger blocker. |
| `JAIL_454` | Emergency Surgery | Choose an enemy minion. Summon four 3/1 Undead with Lifesteal that attack it. | Review timing, generated dependencies and interactions. |
| `JAIL_511` | Spire of Solitude | Summon a Demon with stats equal to your hand size. It attacks a random enemy minion. | global_pool_review, forced_combat |
| `RLK_720` | Gnome Muncher | Taunt, Lifesteal At the end of your turn, attack the lowest Health enemy. | Review timing, generated dependencies and interactions. |
| `TIME_434` | Temporal Traveler | Deathrattle: Summon a 4/1 Shadow that attacks a random enemy minion. | global_pool_review, forced_combat |
| `TIME_443` | Hounds of Fury | Summon two 3/2 Demons. If your deck has no minions, they attack the lowest Health enemy. | forced_combat |
| `TIME_602` | Wormhole | Rewind Summon a random 3-Cost Beast. It attacks a random enemy. | Also has Rewind and a random Beast pool; forced attacks alone do not complete it. |
| `TLC_107` | Stormbrewer | Whenever this attacks, deal 3 damage to the target first. Kindred: Gain Rush. | Stormbrewer was intentionally excluded from the previous release pending proper precombat interruption. |
| `TLC_230` | TREEEES!!! | Choose a minion. Summon four 2/2 Treants that attack it. | Review timing, generated dependencies and interactions. |
| `TLC_810` | High Cultist Herenn | Battlecry: Summon two Deathrattle minions from your deck. They fight! | forced_combat |
| `TLC_821` | Wilted Shadow | Lifesteal Whenever you heal an enemy, this attacks it. | forced_combat |

## Noncombat simulation scope decisions — 2 cards (D)

Decide explicitly whether emote/timer behavior is modeled or intentionally omitted in this ML simulator; do not silently count it as implemented.

| ID | Card | Printed rule | Additional note / review tags |
| --- | --- | --- | --- |
| `CS3_035` | Nozdormu the Eternal | Start of Game: If this is in BOTH players' decks, turns are only 15 seconds long. | Rope/real-time turn limits require an explicit ML-simulator scope decision; not automatically a no-op. |
| `JAIL_703` | Gullible Guard | Deathrattle: You can say Sorry this game. | Emote unlocking is outside combat but still needs an explicit scope decision; not silently marked supported. |

## Quests and rewards — 12 cards (D)

Add quest slots/progress, event conditions and complete reward effects; each reward needs separate review.

| ID | Card | Printed rule | Additional note / review tags |
| --- | --- | --- | --- |
| `END_017` | Battle at the End Time | Quest: Fill your hand, then empty it. Reward: Tick and Tock. | quest |
| `TLC_229` | Spirit of the Mountain | Quest: Play 6 minions of unique types. Reward: Ashalon. | quest |
| `TLC_239` | Restore the Wild | Quest: Fill your board on 3 of your turns. Reward: The Everbloom. | quest |
| `TLC_426` | Dive the Golakka Depths | Repeatable Quest: Summon 6 Murlocs. Reward: Murlocs you summon gain +1/+1. | quest |
| `TLC_433` | Reanimate the Terror | Quest: Spend 15 Corpses. Reward: Tyrax, Bone Terror. | quest |
| `TLC_460` | The Forbidden Sequence | Quest: Discover 8 cards. Reward: The Origin Stone. | global_pool_review, quest |
| `TLC_513` | Lie in Wait | Quest: Shuffle cards into your deck, 5 times. Reward: Master Dusk. | quest |
| `TLC_602` | Enter the Lost City | Quest: Survive 10 turns. Reward: Latorvius, Gaze of the City. | quest |
| `TLC_631` | Unleash the Colossus | Quest: Deal exactly 2 damage to an enemy on your turn, 12 times. Reward: Gorishi Colossus. | quest |
| `TLC_817` | Reach Equilibrium | Quest: Cast 4 Holy spells Reward: Life's Breath. Quest: Cast 4 Shadow spells. Reward: Death's Touch. | quest |
| `TLC_830` | The Food Chain | Quest: Play a 1, 3, 5, and 7-Attack Beast. Reward: Shokk. | quest |
| `TLC_EVENT_400` | Storm the Gates | Sidequest: Play 3 Beasts or Undead. Reward: Craft a custom Zombeast. It costs (3) less. | quest |

## Rewind and alternate outcomes — 17 cards (D)

Rollback/counterfactual outcomes, RNG and hidden-information handling need a shared contract.

| ID | Card | Printed rule | Additional note / review tags |
| --- | --- | --- | --- |
| `CORE_EDR_004_2026` | Raptor Herald | Rewind Battlecry: Discover a Beast with a Dark Gift. Kindred: It costs (1) less. | Also needs Dark Gifts, complete Beast Discover eligibility and Kindred; Rewind is primary. |
| `END_036` | Morchie | Your Rewinds keep BOTH potential outcomes. Battlecry: Discover a Rewind card from any class. | global_pool_review, rewind |
| `TIME_000` | Semi-Stable Portal | Rewind Add a random minion to your hand. It costs (3) less. | global_pool_review, rewind |
| `TIME_001` | Chrono Daggers | Rewind Throw 3 knives at random enemies that deal $2 damage each. | rewind |
| `TIME_002` | Aeon Wizard | Rewind Battlecry: Get 2 random spells from your class. | global_pool_review, rewind |
| `TIME_003` | Portal Vanguard | Rewind Battlecry: Draw a random minion. Give it +2/+2. | global_pool_review, rewind |
| `TIME_004` | Conflux Crasher | Rewind Battlecry: Deal 7 damage to a random enemy. | rewind |
| `TIME_008` | Bygone Doomspeaker | Rewind Battlecry: Both players discard a random card. | global_pool_review, rewind |
| `TIME_014` | Instant Multiverse | Rewind Summon 12 Mana worth of random minions. Overload: (3) | global_pool_review, rewind |
| `TIME_018` | Mend the Timeline | Rewind Get 2 random Holy spells. Restore Health to your hero equal to their Costs. | global_pool_review, rewind |
| `TIME_034` | Stadium Announcer | Rewind Battlecry: Both players equip a random weapon. Give yours +1/+1. | global_pool_review, rewind |
| `TIME_035` | Time Machine | Taunt Deathrattle: Get a random Rewind card. | global_pool_review, rewind |
| `TIME_038` | Mister Clocksworth | Rewind, Rewind, Rewind Battlecry: Summon 2 random Legendary minions. | global_pool_review, rewind |
| `TIME_433` | Cease to Exist | Rewind Silence and destroy a random enemy minion. | global_pool_review, rewind |
| `TIME_441` | Aeon Rend | Rewind Deal $4 damage to two random enemies. | rewind |
| `TIME_610` | Shadows of Yesterday | Rewind Summon four 3/2 Shades. They each gain two random Bonus Effects. | rewind |
| `TIME_EVENT_999` | Sands of Time | Rewind Discover a spell from ANY class. (Or just your class after you Rewind!) | global_pool_review, rewind |

## Setup, deckbuilding and hero replacement — 22 cards (D)

Touches deck legality, initial state, starting hands/hero powers or attached special cards; cannot be implemented as a normal Battlecry.

| ID | Card | Printed rule | Additional note / review tags |
| --- | --- | --- | --- |
| `CATA_615` | Genn, Cursed King | While holding this, if the rest of your hand is all even or all odd, transform into the 6/5 Worgen King. | Generated CATA_615t upgrades the starting Hero Power and makes it cost 1: not just a hand parity transform. |
| `CORE_EX1_323` | Lord Jaraxxus | Battlecry: Equip a 3/8 Blood Fury. | Hero replacement and resulting Hero Power matter in addition to the printed weapon Battlecry. |
| `EDR_000` | Ysera, Emerald Aspect | Start of Game: Increase both players'maximum Mana by 5. Battlecry: Gain 3 Mana Crystals. | deck_or_setup |
| `JAIL_384` | Chainbreaker Hogger | Taunt Start of Game: Duplicate all other Legendary cards in your deck. | deck_or_setup |
| `JAIL_397` | Commander Beatrix | Taunt While building your deck, pick a 2-Cost minion. Ten copies join your deck! | deck_or_setup |
| `JAIL_430` | Azalina Soulsever | Your starting Health is 40. Your deck is 20 cards, plus 20 copied from your enemy. Battlecry: Draw until your hand is full. | Review timing, generated dependencies and interactions. |
| `JAIL_446` | Blood Doctor Thal'ena | Battlecry: Get a second Hero Power that costs Corpses. | alternate_payment |
| `JAIL_504` | Aya, Lotus Kingpin | You always go second. Battlecry: Pick an upgraded counterfeit to replace your Coins this game. Get 3. | deck_or_setup |
| `JAIL_800` | Mug'Zee | Start of Game: If your deck has no other minions, get Mug's Hero Power. If it has no spells, get Zee's! | deck_or_setup |
| `JAIL_831` | King of the Underbelly | While building your deck, pick 3 contraband Beasts. Battlecry: Discover one. It costs (3) less. | global_pool_review, deck_or_setup |
| `JAIL_860` | Chef Neth'rek | Start of Game: If your deck only has cards that cost (3) or less, set your Mana to 10 after five turns! | deck_or_setup |
| `TIME_005` | Timethief Rafaam | Fabled+. Your deck size is 40, but has 10 Rafaams! Battlecry: If you played the rest, destroy the enemy hero.@ ({0} left!)@ (Ready!) | deck_or_setup |
| `TIME_009` | Gelbin of Tomorrow | Fabled Battlecry: Put one of each Aura from your deck into the battlefield. | deck_or_setup |
| `TIME_020` | Broxigar | Fabled, Charge Start of Game: Disappear. Kill all 4 Demons from Argus to reappear in hand. | deck_or_setup |
| `TIME_209` | Muradin, High King | Fabled, Rush. Battlecry: Bring the High King's Hammer to ME! Deathrattle: Add it to your hand. | deck_or_setup |
| `TIME_211` | Lady Azshara | Fabled. Choose One - Empower Zin-Azshari; or The Well of Eternity. (The other gets destroyed!) | deck_or_setup |
| `TIME_609` | Ranger General Sylvanas | Fabled. Battlecry: Deal 2 damage to all enemies. If you've played Alleria or Vereesa, repeat for each. | deck_or_setup |
| `TIME_619` | Talanji of the Graves | Fabled. Battlecry: Draw Bwonsamdi (or resurrect him if he has died). Choose a Boon to give him. | deck_or_setup |
| `TIME_850` | Lo'Gosh, Blood Fighter | Fabled, Rush. Deathrattle: Summon a Blood Fighter from your hand. It gains +5/+5 and attacks a random enemy. | deck_or_setup, forced_combat |
| `TIME_852` | Azure Queen Sindragosa | Fabled If you control another Dragon, your Arcane spells cost (2) less. | deck_or_setup |
| `TIME_875` | Garona Halforcen | Fabled. Battlecry: If your opponent is holding King Llane, destroy him and cut their Health in half. | deck_or_setup |
| `TIME_890` | Medivh the Hallowed | Fabled. Costs (0) if you control Karazhan. Battlecry: Silence and destroy all other minions. | deck_or_setup |

## Shatter and Advance — 10 cards (D)

Split/recombined card identity and Advance transformations need new hand/deck/action semantics.

| ID | Card | Printed rule | Additional note / review tags |
| --- | --- | --- | --- |
| `CATA_134` | Wildwood Circle | Shatter. Summon two 2/2 Treants. Give your minions "Deathrattle: Summon a 2/2 Treant." | shatter_or_advance |
| `CATA_202` | Stolen Power | Get a random Shatter card from another class. (It's already combined). | global_pool_review, shatter_or_advance |
| `CATA_306` | Schism | Shatter Give a friendly minion +2/+3 and Elusive. Summon a copy of it. | shatter_or_advance |
| `CATA_479` | Flight Maneuvers | Shatter. Summon two 4/2 Drakes. Give your minions +1 Attack and Divine Shield. | shatter_or_advance |
| `CATA_489` | Arcane Flow | Shatter Deal $4 damage. Deal $2 damage to all enemies. | shatter_or_advance |
| `CATA_820` | Supply Run | Shatter Draw 3 minions. Give minions in your hand +2/+2. | shatter_or_advance |
| `TIME_044` | Past Gnomeregan | Give a minion +2/+1. Advance to the present! | shatter_or_advance |
| `TIME_101` | Misplaced Pyromancer | Whenever you Shatter a card, deal 2 damage to all enemy minions. | shatter_or_advance |
| `TIME_436` | Past Conflux | Summon a random Dragon that costs (5) or more. Advance to the present! | global_pool_review, shatter_or_advance |
| `TIME_810` | Past Silvermoon | Deal 5 damage to a random enemy minion. Advance to the present! | global_pool_review, shatter_or_advance |
