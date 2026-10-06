# Negative Attack and Twisted Treant

Twisted Treant (EDR_495) uses a shared random-hand-minion modifier. Each player's eligible physical cards are sampled independently; spells are excluded, and an empty eligible hand is a no-op. The chosen card retains its signed Attack bonus. No opponent hand identity or target is added to public events.

Minions now retain `attack_deficit` when their signed Attack is below zero. Displayed/combat `attack` stays nonnegative. Additive buffs, aura changes and temporary-buff expiration use the signed total; setting Attack replaces it. Silence removes the deficit. Copying preserves the signed total after removing the source's aura contribution, then applies the destination's auras. This avoids both negative combat damage and incorrectly gaining Attack after a small buff to an already-negative minion.

Nine fixtures cover both hands/privacy, empty/Silenced cases, duplicate physical cards, play plus later buffs, aura removal, copies, combat, temporary buffs, and stat setting. Existing general copy/enchantment and death-order limitations remain; these fixtures are not full conformance certification. The baseline learner encodes the public deficit through board and action-target data; a regression fixture verifies that equally displayed zero-Attack states remain distinguishable.

References: pinned local EDR_495 data; https://hearthstone.wiki.gg/wiki/Twisted_Treant ; https://hearthstone.wiki.gg/wiki/Attack-related (negative Attack is displayed/used as zero while subsequent buffs retain the underlying reduction).
