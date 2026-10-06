# Filtered summons from hand and deck

`CORE_SCH_181` (the regular Constructed Core version of Archwitch Willow) declares two `summon_from_zone` operations, for hand and deck, filtered to Demons. The reusable operation only selects minions, removes the selected physical entry, and transfers supported Attack/Health modifiers into the summon. It performs no draw and no Battlecry. It does nothing for an empty eligible pool or full board; cards remain in the source zone if no space exists.

Six fixtures cover both zones, non-Demons, a missing source, modified card objects in deck, Battlecry suppression, full-board behavior and the current hand-first policy with one available slot. That last policy is an implementation assumption, not independent fidelity evidence, and appears in `expanded/fidelity_gaps.json`. General enchantment transfer and precise inter-summon event timing remain incomplete.

Sources: pinned metadata and [Archwitch Willow (Core)](https://hearthstone.wiki.gg/wiki/Archwitch_Willow_%28Core%29). Neither the Wild-only historical entry nor the Duels hero is the registered collectible. Full Standard completion is still gated.
