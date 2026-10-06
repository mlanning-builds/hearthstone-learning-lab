# Oasis Ally

The candidate implements the Core Secret `CORE_BAR_812`. On the opponent's turn, an attack against a friendly minion summons a Water Elemental before combat if board space exists, without redirecting the attack. Attacks against the hero and spell damage do not trigger it. A full board keeps the Secret untriggered, even if combat subsequently frees a slot.

`SECRET_SUMMONS` declares the `CS2_033` dependency explicitly for the dependency audit. The generated minion uses the existing damage-freeze implementation. Secret identities remain private until revealed. Existing Secret play-order processing handles an earlier Freezing Trap canceling the attack.

Seven fixtures cover minion/hero attackers, precombat placement, no redirection, board capacity, own-turn/spell exclusion, identity privacy and cancellation. General proposed-attack ordering and redirection remain in the combat conformance backlog; passing these fixtures is not independent client validation.

Sources: frozen Core card metadata and [Blizzard's Oasis Ally card](https://hearthstone.blizzard.com/en-gb/cards/120392/). The spell and generated minion belong to regular Constructed gameplay.
