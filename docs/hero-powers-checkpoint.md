# Shared replacement and secondary Hero Powers

Internal progress toward the **785 → 845** delivery, not a completed batch. **791 / 1185** collectible implementations are connected; **394 remain overall**. The current batch is **6 / 60** connected, leaving 54 additions.

## Four connected cards

| Card | ID | Shared behavior |
| --- | --- | --- |
| Lord Jaraxxus | CORE_EX1_323 | Modern Hero card, Armor, Warlock identity, Blood Fury, and INFERNO! |
| Soul Immolation | JAIL_EVENT_101 | Replace/upgrade Collapsing Star and refresh its captured instance on Demon summons |
| Story of Sulfuras | TLC_632 | Temporary two-use replacement and restoration of saved power state |
| Blood Doctor Thal’ena | JAIL_446 | Independent second Hero Power with Corpse payment and minion targeting |

## Implementation

Primary powers have explicit identity and state. Base powers remain class-based when no override exists. Power costs pass through the existing next-use and board-aura modifiers. Replacement powers use the same use counters and after-use triggers as base powers; their damage does not gain Spell Damage.

Sulfuras saves the previous primary power, including its damage upgrades or remaining uses. Nested swaps restore that saved state. A replacement readies the new power instance. Collapsing Star upgrades its existing instance without refreshing it; Demon summon notifications capture the instance identity so an old summon cannot refresh a subsequently installed power.

The secondary slot is separately usable once per turn, targets visible eligible minions, and pays Corpses instead of Mana. It consumes shared next-Hero-Power cost modifiers and participates in after-use events. Generic refresh readies both slots; Collapsing Star's “refresh this” affects only its captured primary instance. Regranting the second power replaces/readies that slot rather than creating a third.

New Hero Power, Infernal and Blood Fury records are pinned in the hash-reviewed token manifest. Generated tokens are not counted as collectible additions. Hero cards participate in ordinary card history and after-card handling, not spell-cast events.

Power identity, saved swap state, secondary use state and costs are visible to the policy. Feature schema is now **v20**; earlier policy schemas are incompatible. No training was run.

## Evidence and remaining fidelity gaps

The [official Hero card introduction](https://hearthstone.blizzard.com/en-us/news/20888401/join-the-knights-of-the-frozen-throne-07-07-2017) establishes Hero replacement, Armor, Battlecry and new Hero Power behavior. [The official Story of Sulfuras entry](https://hearthstone.blizzard.com/en-us/cards/117874-story-of-sulfuras) specifies the temporary two-use swap. Exact card values and token identities come from the checked-in Standard snapshot.

Independent target-patch traces are still required for nested swap/reset timing, repeated secondary grants, secondary retention across Hero replacement, generic refresh scope, Dormant Demon publication, and broader Hero enchantment preservation. These are recorded in `expanded/fidelity_gaps.json`; local fixtures do not constitute full client certification.

## Validation

**2,012 / 2,012 checks pass**, zero failures/errors/skips, including 50 new Hero Power checks. Final source stayed unchanged throughout validation: `bf10a12e30fc3571a77e2185a2f7cf41a09abb337565f7d138bab7c4eb33fa1c`.

Full receipt: `/Users/matthewlanning/Desktop/HearthStone AI /death-knight-lab/staging/rebased-88/runs/expanded_validation/validation-b84d8790a0944a3bad81554add0a3cdd.json`.

**22 random games completed**, zero errors/caps; **2,309 feature decisions checked**. Random receipt: `/Users/matthewlanning/Desktop/HearthStone AI /death-knight-lab/staging/rebased-88/runs/random_validation/summary-df9cf2013e63-281fb097ae75422c98a7e13b78811aa3.json`. The random run used `df9cf2013e6361646c1ae16662df75a38d9907735cbf8ec69fb0006c7f867e97`; only an outdated statement in the fidelity-gap documentation was corrected afterward. Runtime source is unchanged from that passing game run.

The [current generation dependency inventory](engine-audit/generation-current.json) reflects 791 registered cards. All 60 staged generator declarations remain excluded from collectible coverage while their pool contracts and outcome closure remain incomplete.

No Jupyter action required for this internal checkpoint. No long training or deck search was launched. The full objective and the 60-card delivery remain unfinished.
