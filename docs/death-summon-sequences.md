# Deathrattle summon continuations

Both fixed-count death_summon and mixed death_summon_group operations now use the existing resumable operation scheduler. Remainders carry their original sequence offset, preserving the existing death-position-plus-offset placement policy. Child reactions and choices finish before the next entry; terminal games clear remaining work. The change applies to existing rules using these helpers and adds no collectible implementations (506/1185).

Seven new checks cover placement, mixed order, suspended choices, rollback/retry, lethal interruption, full boards and empty groups. The assistant only parsed source syntax; run notebook 13 locally. Previous user-reported baseline: 1158/1158 passed.

This preserves the candidate's placement policy; independent client evidence is still needed for positional behavior when reactions rearrange the board, simultaneous death waves and precise summon/death timing. Compound corpse payments, recruitment, copies and group enchantments retain their existing helpers.
