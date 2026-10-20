# Additional historical primitive bodies

The following 23 generated-only identities were reviewed against the frozen source metadata. Every declaration is literal and uses the existing paid-play lifecycle; runtime support does not parse card text or substitute another identity. Production admission and regression receipts are recorded separately. No historical generation pool is approved by this list.

Old Core reprints and Fire Plume Phoenix remain excluded from this batch. The historical identity guard accepts every listed record as outside the frozen Standard identities. Future pool membership must still exclude duplicate canonical identities.

| ID | Name | Frozen printed effect |
| --- | --- | --- |
| AT_001 | Flame Lance | Deal $25 damage to a minion. |
| BAR_745 | Hecklefang Hyena | <b>Battlecry:</b> Deal 3 damage to your hero. |
| BT_235 | Chaos Nova | Deal $4 damage to all minions. |
| CFM_021 | Freezing Potion | <b>Freeze</b> an enemy. |
| CFM_065 | Volcanic Potion | Deal $2 damage to all minions. |
| CS2_025 | Arcane Explosion | Deal $1 damage to all enemy minions. |
| CS2_057 | Shadow Bolt | Deal $4 damage to a minion. |
| CS2_117 | Earthen Ring Farseer | <b>Battlecry:</b> Restore #3 Health. |
| DRG_226 | Amber Watcher | <b>Battlecry:</b> Restore #8 Health. |
| EX1_019 | Shattered Sun Cleric | <b>Battlecry:</b> Give a friendly minion +1/+1. |
| EX1_195 | Kul Tiran Chaplain | <b>Battlecry:</b> Give a friendly minion +2 Health. |
| EX1_313 | Pit Lord | <b>Battlecry:</b> Deal 5 damage to your hero. |
| ICC_058 | Brrrloc | <b>Battlecry:</b> <b>Freeze</b> an enemy. |
| ICC_094 | Fallen Sun Cleric | <b>Battlecry:</b> Give a friendly minion +1/+1. |
| ICC_802 | Spirit Lash | <b>Lifesteal</b> Deal $1 damage to all minions. |
| LOOT_291 | Shroom Brewer | <b>Battlecry:</b> Restore #4 Health. |
| OG_083 | Twilight Flamecaller | <b>Battlecry:</b> Deal 1 damage to all enemy minions. |
| SCH_535 | Tidal Wave | <b>Lifesteal</b> Deal $3 damage to all minions. |
| TRL_526 | Dragonmaw Scorcher | <b>Battlecry:</b> Deal 1 damage to all other minions. |
| TRL_546 | Ornery Tortoise | <b>Battlecry:</b> Deal 5 damage to your hero. |
| ULD_714 | Penance | <b>Lifesteal</b> Deal $3 damage to a minion. |
| UNG_817 | Tidal Surge | <b>Lifesteal</b> Deal $5 damage to a minion. |
| WON_341 | Flame Lance | Deal $25 damage to a minion. |

Flame Lance deals 25 damage in this frozen dataset. Its older balance history is not used to override the pinned record. Lifesteal and spell schools come from the individual metadata records; spell damage applies to spell effects, while battlecries keep their printed amount.

The fixtures check full paid play for every listed identity and grouped numerical behavior for hero damage, healing, minion buffs, Freeze, spell damage, area Lifesteal, targeted Lifesteal, the large Flame Lance target, and Dragonmaw Scorcher excluding its own newly played body.

## Further keyword and zone primitives

Twenty-one additional exact frozen bodies are now generated-only: `AT_074`, `BAR_534`, `BT_257`, `BT_512`, `CFM_094`, `CFM_305`, `CFM_614`, `CS2_039`, `CS2_075`, `CS2_087`, `CS2_089`, `CS2_105`, `DRG_206`, `DS1_233`, `EX1_184`, `EX1_192`, `ICC_056`, `TRL_243`, `ULD_143`, `ULD_265` and `WORK_005`.

They use literal existing operations for targeted stat/keyword grants, board and hand buffs, temporary hero Attack, own-hero healing, enemy-hero damage and simultaneous character damage. Sharp Shipment adds two Attack and two Durability to the same equipped physical weapon; the shared weapon operation now accepts an optional Durability amount. Tests check actual paid paths and keyword lifecycle behavior, including Windfury attacks, Reborn, shield consumption and Silence.

The historical primitive module now contains 63 bodies. The overall historical inventory contains 289 bodies. These counts do not approve any historical generation membership. Legacy Deadly Poison was deliberately excluded from this batch: its Standard Core counterpart must not become an eligible past outcome merely because the original belongs to a retired set.
