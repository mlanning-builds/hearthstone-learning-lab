# Damage-based freezing and Deep Freeze

The Core Deep Freeze spell (`CORE_BT_072`) explicitly freezes an enemy character and summons two `CS2_033` Water Elementals. The generated dependency is pinned and reviewed from the full metadata archive, but is not added to the Standard deck-building pool. It can be played if returned to hand.

The shared damage-freeze hook runs for the attacking minion, retaliating minion, and attributed effect damage. It requires positive damage and an unsilenced registered freezing source. Divine Shield and Immune prevent damage and therefore prevent this freeze. Armor absorption still counts as damage to a hero. A mortally wounded defender can freeze through simultaneous retaliation. Existing Freeze duration rules determine thawing.

Eight new fixtures cover the spell and token dependency, armor, retaliation, Silence, prevention, attributed damage and a full board. The full suite also checks returned generated minions. General combat ordering remains subject to the already documented combat-phase fidelity gaps.

References: [Deep Freeze (Core)](https://hearthstone.wiki.gg/wiki/Deep_Freeze_%28Core%29), [Water Elemental](https://hearthstone.wiki.gg/wiki/Water_Elemental), and the frozen metadata. The dependency uses database ID 395, matching the spell's related-card metadata; importing this token does not make its Wild collectible version legal in Standard decks.
