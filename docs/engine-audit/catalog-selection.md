# Frozen catalog selection audit

Run `.venv/bin/python tools/audit_catalog_selection.py` from the project root.
It verifies existing file hashes, reconstructs the declared selection from the
full frozen card records, compares complete records and IDs, and writes
`catalog-selection.json`. It does not update the snapshot or claim live legality.
The September 18, 2026 snapshot reconstructs exactly 1,185 records with no missing,
extra, changed or duplicate entries and no expired exclusion dates.

Independent announcement review: Blizzard's 36.6 notes announce M.O.T.H.E.R. as
a login card, the Black Empire release on October 20, and three early event
cards starting October 6. These support the corresponding recorded release
exceptions. They do not establish all Standard bans or deck-building rules.
https://hearthstone.blizzard.com/en-us/news/24294373

The 36.4.2 announcement separately labels Arena generation changes; those are
not evidence for Standard generation restrictions. Battlegrounds changes in
36.6 likewise do not define regular Constructed mechanics.
https://hearthstone.blizzard.com/en-us/news/24296231

Still required: independently establish every included set/Core/Event eligibility,
patch-specific bans, exceptional construction and complete generation rules.
