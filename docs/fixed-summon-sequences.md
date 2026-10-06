# Fixed summon continuations

Fixed `summon` and active `combo_summon` operations now keep their remaining count in the owning play, event, death, or turn frame. Each individual summon uses that frame's existing reaction checkpoint. Choices suspend the remainder; terminal games discard it. No new collectible implementations are claimed.

This is an experimental checkpoint policy, not independently verified client timing. Play and turn frames use their existing full settlement boundary; event frames drain child events; death frames retain their existing death-wave ordering. These boundaries are not interchangeable. Compound corpse payments, group buffs, copying, recruitment, retain their existing boundaries. Positional Deathrattle continuations were subsequently added; see death-summon-sequences.md.

Eleven new checks cover play-frame interleaving, repeated choices, lethal interruption, board capacity, Combo, zero count and compound exclusion, and trigger/death/turn continuations. The 18 fixed/Deathrattle summon checks and full 1174-check candidate suite have now passed. Independent timing evidence remains required before claiming complete summon fidelity.
