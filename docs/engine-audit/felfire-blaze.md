# Felfire Blaze

The frozen Standard catalog's FIR_904 uses the shared owner-specific Fel spell trigger, followed by self-destruction and two damage to every enemy character. The self-destruction operation marks the source for normal death resolution; it is not damage and bypasses Divine Shield and Immune. The existing event frame retains the remaining explosion operation. Trigger damage uses the minion context, not the triggering spell's Spell Damage bonus.

The card text is corroborated by https://hearthstone.wiki.gg/wiki/Felfire_Blaze . This is text-level evidence, not an independent target-patch event trace.

Seven fixtures cover friendly Fel casting, other schools/owners, Silence, Counterspell, two sources, source protection versus enemy Divine Shield, and a Fel spell that kills the source before its after-cast event. Exact ordering with arbitrary attached Deathrattles and more complex simultaneous-death interactions still needs independent reference validation; passing these fixtures does not certify those interactions.
