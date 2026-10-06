# Fill-board target copies

Bat Mask (DINO_402) reuses set_target_stats followed by fill_board_target_copies. It requires a friendly target, sets its stats, and fills available slots with distinct copy entities. A full board still allows the stat-setting part. Copies skip Battlecries and use the same shared copy-state path as other effects.

Six regression cases cover full/empty board boundaries, targeting, independent entities, Frozen, Silence, keyword retention and Counterspell. Source: pinned DINO_402 record. Existing gaps in aura/stat layering, copied Frozen expiry, complete enchantments and summon-trigger order remain; this addition does not certify those shared rules.
