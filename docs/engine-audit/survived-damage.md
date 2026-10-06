# Survived-damage triggers

Rioter (JAIL_029) maps to an owner-specific friendly-minion damage listener and a shared event-target buff. The target and listener must remain on the board with positive Health at trigger evaluation. The effect can buff Rioter itself and can operate on either player's turn. The listener snapshot excludes minions summoned after the damage event.

Eight fixtures cover friendly/self targets, enemy/hero exclusion, lethal damage, Divine Shield/Immune/zero damage, Silence and late listeners, multiple listeners, Poisonous, and a mortally wounded listener in a damage batch. Each surviving target receives +1 Attack per eligible Rioter. The pinned local card record supplies the text.

These fixtures do not independently establish target-patch timing for every combination of damage-trigger healing, removal, and death replacement. The shared event engine still requires broader client conformance work.
