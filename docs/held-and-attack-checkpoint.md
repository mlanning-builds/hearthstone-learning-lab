# Held keywords and conditional attack immunity

Internal progress in the unfinished 785 → 845 delivery: **802/1185**, 383 remaining, **17/60** additions. This checkpoint is superseded by the subsequent armor-trigger work.

Twisted Monstrosity (CATA_206) starts with Elusive/Taunt. Its owner-end held reroll selects a different unordered pair from the eight Bonus Effects, allowing one keyword to repeat. Physical copies and recruitment preserve the pair; mechanic filters read it. Owner observations expose the pair without exposing opponent hands. Feature schema is now v26.

Horn of Feasting (DINO_136) and its Raptor token use conditional attack windows. Outcast grants the successfully summoned Raptors immunity during their attacks for the current turn. Windows cover Secrets, pre-attack triggers and retaliation; cancellation, forced-attack choices, nested attacks, copies, Silence and expiry have regression coverage.

Validation: 2220 checks, zero failures/errors/skips; 22 completed random games, zero errors/caps. Fingerprint `709d44adcf77fc179d80ac44dc42d5e79075ac12d96cd94fd4ab0de42c4d0912`.

Receipts under `staging/rebased-88`:
- `runs/expanded_validation/validation-2c8aed1b85ee4d32831e0ba1ce49be3d.json`
- `runs/random_validation/summary-709d44adcf77-a1d6bd26b2d34a319e1cef49dc6b7a34.json`

Developer evidence for Monstrosity defaults and pair exclusion: [ClayByte reveal discussion](https://www.reddit.com/r/hearthstone/comments/1ra3iu7/reddit_exclusive_card_reveals_part_2_7_more/). Exact weighting, opponent-turn timing, copy semantics and combat phase interactions retain explicit reference gaps in `expanded/fidelity_gaps.json`. Passing fixtures do not certify client fidelity. No training.
