# Generated dependency audit

The candidate is `staging/rebased-88`; the generated report gives its current collectible-root count. Run from the project root:

```sh
.venv/bin/python tools/build_dependencies.py --engine-root staging/rebased-88
```

This validates the frozen registry and inventories explicit card references from literal declarations across the expanded and legacy engines, including nested choices and triggers. The report is `staging/rebased-88/runs/dependency_audit/references.json`. Source hashes and engine fingerprint bind results to inspected code. It runs no games or training.

Initial result: 67 declared reference edges, no missing registered references reachable from collectible roots. This does **not** certify generated-card closure: card comparisons can appear as references, metadata presence does not establish effect fidelity, computed IDs are not extracted, and dynamic pools need reviewed membership. Unassigned source references retain file/line locations for manual mapping; these include registry declarations and comparisons as well as generated entities.

Next: map the remaining hard-coded generation branches to their source cards, encode reviewed dynamic pools, and verify generated entities' behavior and interaction scenarios. All 1,185 catalog cards remain in scope; this audit does not shrink that requirement to the current candidate.

The schema-2 reference report tags remaining literal occurrences by syntax:
identity inventory, declaration key, identity comparison, local metadata or
unresolved expression. This separates review work without deleting references
or treating syntax classifications as proof of generated-card closure. Counts
remain occurrence counts, not counts of distinct missing cards.

Tomb Guardians (`CORE_RLK_118`) and the `JAIL_450` Frail Ghoul trigger now declare their generated token IDs as operation arguments. Their engine handlers consume those arguments, so the audit can follow both edges without guessing from branches. This is a dependency visibility change, not new card coverage or closure certification.
