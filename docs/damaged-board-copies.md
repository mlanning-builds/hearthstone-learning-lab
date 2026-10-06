# Damaged-board copies

Nablya, the Watcher (TLC_624) uses copy_damaged_board. It selects living damaged originals once so newly created copies cannot recursively copy themselves. The existing summon-copy path preserves stat bonuses and damage, resets entity identity and attack usage, and skips Battlecries; Rush is granted to the copy.

Five regression scenarios cover selection, independent state, Battlecry exclusion, Rush attack restrictions and board capacity. The card remains written/unverified: board order, aura layering, Frozen and complete enchantment copying need independent client traces (nablya_copy_order and copy_state_completeness). Source is the pinned TLC_624 record.
