# Third 30-card batch: persistent bonuses and multi-step choices

Candidate coverage: **576 → 606 / 1,185 written collectible implementations**; **579 remain**. Scope is the pinned regular Standard snapshot, 36.6.0.251952, not live legality or Mercenaries/Battlegrounds. Generated tokens do not count toward the 30.

## Validation

- **1346 full-suite checks passed**, zero failures or errors.
- **46 new batch scenarios**, covering each new collectible and interactions including Silence, copying, private choices, rollback, turn expiry, full boards, no qualifying choices, and complete fixed-token chains.
- The older Morbid Swarm scenario now checks that insufficient-Corpse options are absent from legal actions.
- Source fingerprint: `078f4c4565d8ca4c94cbca8916e90760dcc1daf5ca7384c8e487fb7b875238ed`.
- Receipt: `/Users/matthewlanning/Desktop/HearthStone AI /death-knight-lab/staging/rebased-88/runs/expanded_validation/validation-95a4ac46aa2142dca8f64aecc4bb8f46.json`.
- Log: `staging/rebased-88/runs/expanded_validation/batch30-606.log`.
- Explicit literal dependency report: no missing IDs. This is not a complete dynamic-pool audit.
- No training or deck search was launched.

## Reusable additions

Silver Hand Recruit bonuses are stored per player, affect existing recruits, and apply to later recruits generated, played or summoned. Hand/deck stat views include the bonuses. Copies do not accidentally apply them twice; Silence removes the summoned minion's acquired stats.

Individual spells can carry damage bonuses through hand/deck movements; these modify the selected spell rather than global Spell Damage. Public observations show these modifiers only to the hand owner. Recurring discounts and temporary play locks use physical-card state and turn counters.

The existing continuation frames handle repeated keyword choices, Choose Thrice, repeated enemy selections, and multiple summons. The Egg of Khelos and Eternal Bloodpetal include their entire fixed generated chains. Delayed Phoenix returns work on either player's turn. Resistance Aura uses the existing timed cost system.

Feature schema is now **v12**. Older policy checkpoints remain incompatible.

## Added cards

| ID | Card |
| --- | --- |
| `MEND_800` | Brash Battlemaster |
| `MEND_801` | Resilient Savior |
| `MEND_802` | Convalescence |
| `MEND_803` | Emboldening Blade |
| `MEND_804` | Arator the Redeemer |
| `MEND_900` | Teamwork |
| `CATA_209` | Battlefield Blaster |
| `CATA_458` | Archmage Kalec |
| `EDR_874` | Stellar Balance |
| `TLC_223` | Volcanic Thrasher |
| `BE_036` | M.O.T.H.E.R. |
| `TIME_036` | Royal Informant |
| `FIR_951` | Volcoross |
| `CORE_ULD_178` | Siamat |
| `EDR_491` | Archdruid of Thorns |
| `DINO_410` | The Egg of Khelos |
| `TLC_234` | Eternal Bloodpetal |
| `EDR_209` | Forest Lord Cenarius |
| `CATA_566` | Tol'vir Carver |
| `END_032` | Winged Aberration |
| `FIR_919` | Everburning Phoenix |
| `END_025` | Eternal Firebolt |
| `TTN_851` | Resistance Aura |
| `EDR_234` | Emerald Bounty |
| `CATA_215` | Daze |
| `EDR_527` | Ashamane |
| `JAIL_379` | Spire Security |
| `JAIL_510` | Annihilation |
| `TIME_042` | King Maluk |
| `CATA_699` | Dread Leviathan |

## Evidence and limits

The local pinned `data/standard/all_cards.json.gz` supplies printed rules, enchantment descriptions, token IDs and stats; `expanded/reviewed_cards.json` pins their hashes. The [Corpse rules](https://hearthstone.wiki.gg/wiki/Corpse) explicitly describe hiding unaffordable options for Morbid Swarm and Volcoross. [Convalescence](https://hearthstone.wiki.gg/wiki/Convalescence) identifies its generated Recruits and Divine Shields; [Infinite Banana](https://hearthstone.wiki.gg/wiki/Infinite_Banana) describes its retained-hand behavior.

Internal tests are not independent client conformance. General modifier ordering, complete random-generation pools, all event-timing exceptions, and full-game interaction verification remain open. Deathrattle inheritance currently uses recorded death-time operations, including granted operations. That contract and cross-zone modifier/control interactions still require pinned-client traces before a fidelity claim. Full Standard readiness remains false.

## Jupyter

Use `notebooks/13_shared_rules_checks.ipynb`; restart the kernel and Run All to reproduce checks locally. Reusable code is in `staging/rebased-88/expanded`. Notebook 08 still uses the older engine. Validation does not start training.
