# Validation status — October 23, 2026

The active simulator is `staging/rebased-88`. Registered card counts describe implementation inventory, not independent client fidelity. Known gaps and approximations remain tracked in that candidate.

## Latest repair

A departed-target destroy operation caused the owner-started notebook 22 comparison to stop after 136 completed MLP games. Destroy now safely completes when the locked minion has left the battlefield. Live-target behavior is preserved.

**93 targeted non-training checks passed:** effect executor 4, effect replay 16, choice continuation 5, entity effects 46, targeted spell triggers 7, and research contracts 15. Resume preflight passed. The full resume payload was preserved, including eight pending completed-game trajectories, Adam and random states. Original 19,931-game Transformer weights remain unchanged. No training was launched during the repair.

This is not a full-suite pass. The October 22 full suite checked 5,697 cases and found two failures; both then passed among 103 affected rechecks. A fresh complete regression on the latest repaired source remains pending. CI is configured to run the non-training suite on publication; its result must be checked separately.

## Research scope

The small-Transformer lineage has reached 19,931 completed games. The equal-game architecture study is in progress; no winner or expert-level strength is established. Its existing-model reference has a different training history from the fresh alternatives. One seed and the current fixed-opponent panel limit generalization claims.

Checkpoint files, private diagnostic receipts and live notebook outputs are local artifacts and are not distributed. Public resume configurations document local experiments; they require the corresponding artifacts. Use notebook 15 for a fresh training setup.

## Publication checks

The cleaned publication snapshot passed staged lint, strict facade typing, Python syntax, 75 supporting-tool checks, 58 tool checks, a bounded non-learning smoke check, 15 equal-game research contracts and nine earlier research contracts. Published notebooks contain no outputs or execution counts, and a staged artifact scan found no credentials or personal machine paths. The local full-suite attempt was stopped to avoid competing with an owner-started training run; it produced no pass receipt. The GitHub rules job remains responsible for a fresh full-suite result on this publication.
