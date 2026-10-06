# Hand-position and distinct-cost discounts

Nightmare Dragonkin (`EDR_890`) discounts the current rightmost card in its owner's hand by two when its deathrattle resolves. Empty hands do nothing; Silence suppresses the deathrattle. Hand position is resolved at effect time rather than remembered at summon time.

Zaqali Flamemancer (`FIR_940`) checks the effective costs of cards remaining in hand after it is played. If all costs differ, it discounts the entire remaining hand by two. The check takes one cost snapshot before mutation, includes all card types, and uses the shared cost evaluator (including modifiers and the zero floor). Identical card IDs can qualify if their effective costs differ.

Both operations reuse the same additive discount helper as filtered random hand discounts. Eight fixtures cover ordering, Silence, empty hands, accumulation, cost floors, modified-cost equality, played-card exclusion and summon-only behavior. Arbitrary future cost-setting enchantment order and battlecry replay mechanisms remain separate conformance work.

References: frozen local metadata, [Nightmare Dragonkin](https://hearthstone.wiki.gg/wiki/Nightmare_Dragonkin), and [Blizzard's Zaqali Flamemancer page](https://hearthstone.blizzard.com/en-us/cards/115654-zaqali-flamemancer?set=into-the-emerald-dream). This is regular Constructed behavior, not Battlegrounds or Mercenaries.
