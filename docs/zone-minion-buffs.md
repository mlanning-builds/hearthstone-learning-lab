# Hand and deck minion buffs

The shared zone_minion_buff operation selects explicit hand/deck zones, filters minions, and optionally filters rarity. Seismopod uses both zones for +3/+3; Release the Beasts uses hand-only +1/+1 and an additional +2/+1 for Legendary minions. Definitions come from the pinned DINO_421 and JAIL_387 card records.

Deck strings become physical Card objects only when affected, preserving position and existing objects/enchantments. Drawing and playing preserve bonuses; Silence removes them on the board. Regression checks cover rarity, zone/owner exclusion, repeated buffs, spell exclusion, draw/play transitions, Silence, Counterspell and empty zones.

Generic reactions to gaining stats in hand/deck are not yet implemented; cards depending on those reactions remain unsupported. No new claim of complete enchantment or client conformance is made.
