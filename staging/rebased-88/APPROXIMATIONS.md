# Approximate special-card mode

The owner-authorized default profile is `special-approximations-v1`. It provides executable approximations for the remaining special cards. It is not a claim of Blizzard fidelity or validated training readiness.

Existing `Game(...)` callers receive the profile automatically. Pass `special_approximations=False` to disable the new defaults and require explicitly supplied contracts. Zephrys/Wish retain their previously authorized approximate policy.

Every observation includes `approximation_profile`, with policy descriptions and `validated: false`. Recorded games also include an `approximation_profile` event. Keep this profile and the source fingerprint with datasets and saved models.

**Wonderful Whizbang uses 22 synthetic legal Standard proxy recipes, not Blizzard's actual recipes.** This is the largest recipe-content approximation. Zayle uses all five documented 2020 lists; experimental Whizbang uses all eleven documented candidate recipes and the full Rogue treasure pool. Harth preserves all thirteen ordered hands and actual original-edition Demon Hunter tokens, with approximate class weights and other printing choices.

Uluu samples complete eligible branch pairs with documented exclusions and targeting restrictions. Holmes uses actual answer-zone cards and two distinct current-format class/neutral distractors. Khadgar uses public-state usefulness thresholds, uniform useful-spell selection and legal enemy targets. Reno uses seven bullets with no consecutive repeat.

Elise and Avatar use explicit boosted rarity weights C29/R28/E24/L19 for four independent slots, followed by E24/L19 for a guaranteed Epic-or-better slot. Identity selection is uniform within rarity. These weights, independence, final-slot guarantee and Avatar/Elise equivalence are approximations, not official probabilities. No retail pity timer or collection duplicate protection is assumed. All declared eligible identities remain included.

The initial implementation pass used static checks only. The October 16 regression repair subsequently passed 5,416 non-training simulator checks and 75 supporting checks. The simulator receipt confirms unchanged source with fingerprint `e8c3c34ba1c7037580126fc904075f50795b70456253199239d4d851a1ba41c1`. No training, learning, deck search or notebook training cells ran. These are internal regression results; independent client-fidelity certification remains outstanding.

Known historical generation gaps remain for Whack-A-Gnoll, Tear Reality, Convoke the Spirits, Alternate Reality and Alter Time. Missing retired spell or weapon outcomes still cause explicit rejection before sampling; no pool is narrowed to implemented outcomes. These known gaps and the special-card approximations mean this is not a claim of complete simulator fidelity. See `../../docs/engine-audit/regression-repair-current.json` for evidence.
