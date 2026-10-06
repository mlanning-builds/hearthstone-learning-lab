# Filtered highest/lowest-cost draws

Taelan Fordring (`CS3_024`) declares a highest-cost draw filtered to minions. The shared operation snapshots eligible deck entries and their deck-zone costs, chooses uniformly among physical entries tied at the extremum, then uses the existing indexed draw path. Cost/stat modifiers attached to a deck card survive the draw; hand-only discounts do not determine deck selection.

An empty eligible pool does nothing, including an empty deck (no fatigue for a failed targeted search). A full hand burns the selected card rather than selecting an alternative. Silence suppresses the deathrattle. Seven fixtures cover selection, ties, modified deck cards, full hands, Silence, empty pools and the generic lowest-cost branch.

Source: pinned metadata and [Blizzard's Taelan Fordring card](https://hearthstone.blizzard.com/en-us/cards/66856-taelan-fordring). General enchantment ordering and independent client conformance remain incomplete; this adds an explicit effect implementation, not full Standard certification.
