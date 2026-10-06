# Random hand copies across alternative filters

Cloud Serpent (`TLC_888`) uses `copy_random_hand_any` with Elemental and Dragon alternatives. Each alternative is a conjunction of typed filters; alternatives form a union over physical cards, so a dual-type card has one selection entry. The played card has already left hand before its battlecry resolves. Another copy of Cloud Serpent still in hand remains eligible.

The existing hand-copy helper deep-copies the selected card and assigns a new entity ID. Supported hand buffs and cost modifiers survive; later changes to the copy do not mutate the original. Full hands use the existing generated-card burn path. A summon alone does not execute the battlecry.

Printed effect: [Blizzard card library](https://hearthstone.blizzard.com/en-us/cards/122318/). The frozen local metadata determines stats for this patch. Same-zone copy behavior follows [Blizzard's zone and copy rules](https://hearthstone.blizzard.com/en-us/news/21965466). Six fixtures cover both tribes, duplicate-type membership, played-card exclusion, independent modifiers, summon timing and capacity. Exotic enchantments such as Dark Gifts remain outside current supported behavior and require separate conformance work; adding this card does not certify arbitrary enchantment copying or full Standard readiness.
