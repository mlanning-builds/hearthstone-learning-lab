# Owner-turn hero damage triggers

Emberroot Destroyer (FIR_955) uses the existing damage-event snapshots. Its matcher requires damage to its owner's hero while that owner is the current player. The triggered operation chooses an enemy minion and deals three damage using minion-source attribution. Empty enemy boards do not redirect the effect to the enemy hero.

Armor absorption counts as damage; zero damage, Immune and Bulwark's damage replacement produce no damage event. Silence disables the listener. A listener summoned after an event was queued cannot observe that earlier event. Each damage instance and each eligible listener resolves separately.

Eight fixtures cover Life Tap, Armor, turn/target scope, prevention, Silence and snapshot timing, empty boards, repeated damage, fatigue and multiple listeners. Exact lethal-hero/queued-trigger and complex simultaneous-death ordering still needs independent target-patch validation; this does not certify the general event engine.

The pinned FIR_955 catalog record is the card-text authority. Merry Moonkin remains unregistered pending review of the exact Wisp identity family; name-based inclusion of all similarly named records would also include unrelated modes.
