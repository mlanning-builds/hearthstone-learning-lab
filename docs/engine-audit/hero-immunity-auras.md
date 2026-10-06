# Hero immunity auras and next-card cost setting

Tichondrius (`CORE_CATA_001`) is registered from the frozen regular Constructed Core record. A shared hero-immunity query combines timed player effects with active, unsilenced aura providers. Damage prevention, legal targets and public observation all use the same query. Removing one of several providers leaves protection; removing the last ends the aura unless a timed immunity effect remains.

Its Battlecry creates a turn-limited, one-use Demon cost-setting effect. It is consumed by the next matching played card, not by non-Demons or summons, and survives removing or silencing the Battlecry source. The shared cost evaluator distinguishes setting a cost from subtracting a discount.

Seven fixtures verify ownership, summon-only aura behavior, source removal, overlapping immunity, free Demon payment, consumption, expiration, existing card modifiers and source-independent Battlecry effects. The full generic ordering of timestamped cost enchantments and continuous taxes is **not** implemented; this limitation is explicitly tracked in `fidelity_gaps.json`. Passing fixtures do not certify those unresolved interactions or full Standard fidelity.
