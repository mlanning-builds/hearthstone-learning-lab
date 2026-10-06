# Core block 0.13 — user-run validation release

This release combines shared Constructed selectors and resumable death/turn sequences. It is not the completion of the entire roadmap.

## Included

- Dual/ALL tribe, class and spell-school selectors used by active effects.
- Saved death-wave and Reborn positions across decisions.
- Saved start/end-turn state across decisions, with deferred draw/cleanup.
- Nested death choices inside turn/card sequences.
- Copyable private continuation state, rollback and terminal cleanup.
- 28 additional prepared scenarios; 231 total methods.

## Run once locally

In notebook 08: File → Reload Notebook from Disk, then Kernel → Restart Kernel and Run All Cells. Confirm version 0.13. This notebook runs rules checks and saves reports; it does not train. Send the final summary and any failure tracebacks. The assistant has not executed the checks.

The prior 203-check receipt remains historical and must not be applied to this source version. Full Standard readiness remains false regardless of this suite's outcome.

## Still unfinished

Ordered modifier/enchantment semantics, self-trigger compensation, detailed phase exceptions, complete generation/deck legality rules, hero-card systems, remaining card definitions and independent client validation. The staged 88-card overlay needs rebasing and is not installed.
