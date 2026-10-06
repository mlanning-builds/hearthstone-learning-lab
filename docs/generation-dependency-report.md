# Recursive literal generation dependencies

Readiness now includes generated_dependency_report: missing generated IDs and a shortest declaration path from each implemented collectible root. The report follows nested declarations, generated-card declarations, mixed summon groups, and cycles without importing card text as rules. This makes missing fixed dependencies actionable alongside collectible counts.

Coverage is intentionally explicit: summon, combo_summon, death_summon, raise_corpses, tomb_guardians, add, equip, death_summon_group, and choose_fixed_summon. The report is not closure certification: computed IDs, dynamic pools, legacy/helper-only behavior and unreviewed operation schemas remain outside it. Metadata presence is not proof of executable fidelity. Complete_dependency_coverage stays false even when no missing IDs are found.

Nine focused dependency checks passed after correcting trigger-selector extraction. The current scan covers 506 collectible roots and 61 literal dependency edges, with no missing registered records in that limited scope. This does not prove generated behavior or complete pools.

The full candidate suite passed: 1174 tests in 58.981 seconds, zero failures/errors. Log: staging/rebased-88/runs/expanded_validation/goal-validation-1174.log. This direct unittest run does not replace the notebook fingerprint receipt; readiness correctly continues to distinguish that receipt from this run. No training was launched. Card coverage remains 506/1185.
