# Historical fixed transformations

The applied bindings are Polymorph, Polymorph: Boar, Polymorph: Jellyfish, and Luna's Pocket Galaxy. They use explicit existing transformation and deck-cost-setting primitives. Boar and Jellyfish are literal generated records; Sheep is already registered. These identities are not approval of any historical generation pool.

The frozen Jellyfish record (TID_708t, DBF 75557) has printed Spell Damage +2 and a numeric `spellDamage` field of 1. Its parent TID_708 also explicitly promises +2. The applied explicit SPELL_DAMAGE_VALUES override uses the printed +2 while preserving the original record and its metadata hash. [Official parent card](https://hearthstone.blizzard.com/en-us/cards/75556-polymorph-jellyfish). The official library page resolves but did not expose its rendered card text to the retrieval tool; the frozen parent and child printed texts are the directly inspected evidence. This is not an independent client trace.

Six registry-backed fixtures pass for both controllers, board position, fresh transformed entity identities, removal of prior damage/buffs/Deathrattles, Charge, Spell Damage and Silence, and deck-only cost setting. Bindings are applied; a full unchanged-source regression is still required for the changed candidate.
