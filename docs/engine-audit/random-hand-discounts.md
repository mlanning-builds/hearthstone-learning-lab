# Filtered random hand discounts

The candidate registers Dinositter (`TLC_822`) and Curious Explorer (`TLC_244`) against the frozen Standard metadata. Both use `discount_random_hand(side, filters, amount)` rather than separate cost implementations. Selection is over eligible physical hand cards; identical copies remain separate outcomes. Empty pools do nothing. The existing cost evaluator floors payable cost at zero while retaining the full discount modifier.

Dinositter uses the owner's end-of-turn trigger and selects a Beast minion in that player's hand. Curious Explorer's deathrattle selects a minion in the opposing player's hand. Silence suppresses both triggers through the existing lifecycle rules. The effect does not reveal the selected card to the opponent.

References: [Blizzard's Dinositter card](https://hearthstone.blizzard.com/en-us/cards/117574-dinositter/) and [Curious Explorer rules reference](https://hearthstone.wiki.gg/wiki/Curious_Explorer), plus the project's pinned card records. Fixtures cover owner/zone/type selection, duplicate physical cards, silence, empty pools, stacked discounts and the zero-cost floor. These fixtures do not constitute full client conformance or cover every future cost-setting interaction.
