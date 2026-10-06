# Conditional kill buffs

Synchronized Spark (END_014) uses the pinned Hunter/Paladin card record and enemy-character targeting. The shared `damage_buff_if_dead` operation deals spell-scaled damage, records whether the victim has lethal Health, resolves the existing settlement boundary, and gives one random surviving friendly minion the specified stats if the game continues. With no friendly minion, the follow-up is a no-op. Spell Damage affects damage only, not the +3/+3 buff.

Seven fixtures cover one random buff, surviving targets, Divine Shield, an empty friendly board, Spell Damage, face damage/lethal termination, legal target restrictions, and Counterspell. General post-damage/death-trigger timing remains subject to the engine's documented conformance gaps; this checks the implemented cases, not arbitrary replacement interactions.

Spirit Bond was also inspected but not registered: the local snapshot did not expose an unambiguous matching Wolf token from a direct ID/name lookup. A visually similar token must not be substituted without dependency evidence.
