# Weapon-based hero damage replacement

Bulwark of Azzinoth (`CORE_BT_781`) declares a replacement that spends one weapon Durability instead of applying a positive damage instance to its owner's hero. The shared damage entry point handles attacks, effects, self-damage and fatigue. Armor and Health remain unchanged, damage counters do not increase, and zero damage is returned to Lifesteal and freeze-on-damage callers. Zero proposed damage does not spend a charge.

Its printed Durability is loaded from the frozen `health: 4` field, consistent with the existing weapon loader. A hero attack separately spends normal attack Durability, so retaliation plus attacking can consume two charges. The final charge still prevents its damage instance. The current engine removes depleted weapons through its existing break-weapon path; more complex replacement ordering and weapon-death phase timing still need broad conformance work.

Eight fixtures cover armor/counters, repeated hits, fatigue progression, attack Durability, last-charge retaliation, other targets, Lifesteal/freezing and self-damage/replacement. Sources: pinned Core metadata, [Core Bulwark](https://hearthstone.wiki.gg/wiki/Bulwark_of_Azzinoth_%28Core%29), and [Blizzard's card text](https://hearthstone.blizzard.com/en-gb/cards/57721-bulwark-of-azzinoth/). Full Standard fidelity remains unproven.
