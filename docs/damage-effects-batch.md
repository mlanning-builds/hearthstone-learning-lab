# Shared damage effects: three additional cards

Pinned catalog declarations now connect Asphyxiodon (DINO_132) to end-turn random enemy-minion damage, Sporegnasher (EDR_110) to the same damage operation as a Deathrattle, and Crowd Control (JAIL_307) to two distinct area-damage operations. Crowd Control checks the current deck size for its discount.

Sporegnasher damage uses the dead source's Poisonous keyword; damage prevention stops Poisonous. Reference: https://hearthstone.wiki.gg/wiki/Sporegnasher . Tests cover enemy-only targeting, Silence, empty board, shield/immunity, both boards, Reborn between pulses, Counterspell and the 24/25-card threshold. These tests exercise shared engine behavior; independent client conformance remains incomplete.

This brings the old +200 implementation milestone to 491 written collectible implementations (291 preserved originals plus 200 candidate additions). It does not complete the 1185-card Standard pool or certify those implementations.
