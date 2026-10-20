# Remaining eight approximation policy

Authorized by the owner on October 19, 2026. Policy: `remaining-eight-v1`.
These are runnable simulator rules, not claims about Blizzard's exact algorithms.
They supplement the existing Zephrys/Wish and special-card approximations.
Observations expose `additional_approximations`; executions emit
`approximation_used` events with the policy and rule name.

| Case | Implemented approximation | Possible training difference |
| --- | --- | --- |
| Copied Muradin return | Capture held Hammer templates at inheritance. Each trigger creates fresh physical copies for the current bearer controller. The original donor's cards are never moved or duplicated by UID. | Repeated triggers and attachment inheritance may differ from the client. |
| Inherited Hammer shuffle | Generate a fresh High King's Hammer using the new bearer's Attack plus two, and shuffle it into its controller's deck. | This unusual inherited relationship and its actual reachability are not client-certified. |
| Bashana | Uniformly sample ordered spell-identity tuples with the maximum reachable total cost at or below twelve, using exactly the surviving Treant count. Integer dynamic-programming weights preserve the complete pool without enumerating or truncating tuples. Explicit supplied distributions override the default. | Spell-cost combinations and correlations can differ materially from Blizzard's selection algorithm. |
| Watfin | Uniform applicable mutation type: cost -1, attack +1, health +1, added tribe, or changed name. Tribe and name choices are uniform from eligible alternatives. The selected physical card retains the overlay through ordinary copying and zone moves. | Mutation weights and hidden identity/token behavior differ or are unverified. Renaming retains the original card's executable body and ID; identity-sensitive interactions are approximated. |
| Vyranoth | Allocate +50 Attack and +50 Health evenly. Each remainder is independently assigned to a uniformly sampled subset without replacement. | Attack/Health remainder correlation and recipient weighting may differ. |
| Garona | Uniformly select one held King Llane, destroy that physical card, and halve current enemy health once per Battlecry. | Selection among distinct modified copies may differ. |
| Free Rogue Imbue | Run the generation body and ordinary trigger repetitions without Rewind, payment, or paid-use consumption. | Real free-trigger Rewind availability/timing may differ. |
| Exhausted Camouflage Mount | If no new keyword is eligible, uniformly pick any of the eight Chameleon variants and attach its summon Deathrattle. | Client fallback token selection may differ. |

All normal non-exhausted, non-overlapping rules retain their existing paths.
No eligible generation pool is reduced to implemented coverage. Missing real
metadata/dependencies and malformed explicit contracts still fail explicitly.
The owner runs training in Jupyter. No training or GitHub actions are part of
this implementation or its regression checks.

A passing internal regression suite establishes consistency with fixtures;
it does not establish independent game-client fidelity or policy sufficiency.
