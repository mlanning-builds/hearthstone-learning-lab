# Latest bounded integration validation

Run: 89d175243d0442d590d01a62122b84c5

Candidate fingerprint: `ff42673adc830dad07036c7486628a0519751b322f69135a63be3a1d91a435f1`. A separate fingerprint read after completion matched the starting fingerprint. No source edits were made during execution.

- 33 games across all 11 classes, three seeds per class, at most 500 actions per game.
- 33 terminal games, 0 errors, 0 action cutoffs.
- 3817 decisions encoded using `visible-action-features-v6`; no policy training or deck ranking.
- Both observations checked at each step for serialization, private-zone fields and decision ownership.
- 304 of 501 implemented collectibles played or summoned; 197 unseen.

An observed card does not prove its effects or interactions were exercised correctly. These decks sample only the implemented pool. Full Standard coverage, complete generated dependencies and independent client conformance remain unfinished.

Immutable report: `/Users/matthewlanning/Desktop/HearthStone AI /death-knight-lab/staging/rebased-88/runs/random_validation/summary-ff42673adc83-89d175243d0442d590d01a62122b84c5.json`.
