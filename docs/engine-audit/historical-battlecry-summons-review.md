# Fixed historical Battlecry summons

Twelve historical minion bodies now use literal fixed child recipes: Hog Rancher,
Alleycat, Big-Time Racketeer, Dragonling Mechanic, Grim Necromancer, Pantry
Spider, Arcanosmith, Sewer Crawler, Bilefin Tidehunter, Crud Caretaker, City
Architect and Former Champ. Twelve exact child identities carry their unchanged
frozen stats, tribes and keywords; they are generated tokens rather than
historical collectible pool members or Standard deck entries.

The pre-admission draft passed 36 isolated placement/capacity cases. The applied
ordinary-registry group and shared summon/resolution group pass 41 checks.
Checks cover paid consumption, placement to the source's right, exact child
stats, parent versus child capacity, parent buffs, recruiting without Battlecry,
child replay, Rush/Taunt, individual reaction checkpoints, and paid-play rollback
when a source disappears before its next child summon.

The shared right-side summon helper previously batched multiple children before
settling reactions. It now yields between children and carries a sibling offset.
Source disappearance now raises an explicit UnsupportedCard rather than an
incidental list lookup failure. Client placement after source death, control
change or intervening board movement remains unresolved; the repair does not
invent a fallback position. Historical random pool membership remains separate.

The historical inventory is 322 collectible bodies. Full-suite verification of
this changed source is required; this count is not client certification.
