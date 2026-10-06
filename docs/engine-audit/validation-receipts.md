# Candidate validation receipts

The candidate fixture runner captures its source fingerprint before discovery and again after the suite finishes. A passing suite only produces `success: true` when those fingerprints match. `fixture_success` records the test outcome separately; `source_unchanged` records the comparison. The primary fingerprint identifies the starting source, never newly edited code at the end of a run.

Each invocation retains an exclusive, uniquely named `validation-<run_id>.json` archive. The `validation.json` convenience pointer is replaced atomically through a per-run temporary file, so overlapping writers do not share a temporary filename. Readiness still compares the receipt fingerprint with current source.

This is an integrity guard, not an isolated checkout or filesystem lock: edits that are reverted between snapshots are not detectable. Run validation without editing the candidate, and use an isolated immutable checkout for release certification. Passing targeted fixtures does not certify complete Standard rules or card interactions.

Regression checks cover source drift during a passing suite, failure preservation, independent repeated archives, and latest-receipt replacement. These checks use synthetic runner results; the actual engine suite is also run separately.
