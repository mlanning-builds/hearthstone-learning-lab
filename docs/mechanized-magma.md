# Mechanized Magma

TLC_224 uses a shared pre-spell school matcher and extends the existing paid-spell-cost buff operation to support both Attack and Health multipliers. Existing Attack-only consumers retain their behavior. The pinned catalog defines the Fire condition and dual Elemental/Mech type.

Tests cover before-damage Health gain, discounted and zero cost, wrong school/owner, Silence, multiple sources and Counterspell. Counterspell follows the candidate pre-spell phase, documented in pre-spell-triggers.md; independent pinned-client timing conformance is still outstanding. No general summon trigger was added by this change.
