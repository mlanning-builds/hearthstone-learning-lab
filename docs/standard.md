# Standard expansion status

The requested full Standard simulator is **not complete**. Notebook 05 supplies a dated all-class card catalog and an honest implementation audit. No game or training run was executed while preparing this milestone. Static file/schema checks were used; the notebook itself is unexecuted.

## Snapshot

As of September 18, 2026, build 251952 (36.6.0.251952): 1,185 collectible catalog records. Source data is pinned to https://api.hearthstonejson.com/v1/251952/enUS/cards.json. SHA-256 hashes, retrieval date, source references, and per-file hashes are in `data/standard/manifest.json`.

Filter: collectible records in CORE, EMERALD_DREAM, THE_LOST_CITY, TIME_TRAVEL, CATACLYSM, ESCAPEFROM_VIOLET_HOLD, EVENT; include BE_036 (M.O.T.H.E.R.) individually. Exclude BE_EVENT_100, BE_EVENT_101, BE_EVENT_102 until their October 6 release. Other BE cards currently in source are unreleased until October 20. The published expansion listing contains upcoming expansions and must not be copied blindly as an active deck pool.

Core-hidden/trial duplicate records, Wild, cosmetics and other game modes are outside this filtered catalog. Collectible HERO cards are retained. Multi-class records can lack `cardClass`; the `classes` array is authoritative for those records. All original fields are retained, including runes and copy-equivalence metadata. `card_tags.json` supplements public JSON with scalar client tags from HearthSim/hsdata CardDefs build 251952, including deck-size modifications. These tags are metadata, not implementations.

The complete source archive (36,022 records, including noncollectible references) is compressed in `all_cards.json.gz`. **It is not a legal deck or Discover pool.** Generation eligibility depends on the effect and format and still needs implementation. Eleven base heroes and their linked hero powers are in `classes.json`; only the existing DK subset has class gameplay logic.

Live bans and all exceptional deck-construction rules are not independently certified. The catalog is a reviewed set/date snapshot, not a claim of authenticated live-server legality for every possible deck. Sources reviewed include Blizzard's rotation page and patch notes 35.0, 36.4.2 and 36.6. The empty ban list means no Standard ban was identified in the reviewed announcements, not proof that none can exist.

## Engine gap

Existing `engine/`, `learner/`, and `data/core_pool.json` are preserved so saved models and replay fingerprints remain usable. No broadening of their allowlist has occurred. Notebook 05 reads the old allowlist as syntax and compares frozen data; it never instantiates Game. It writes one coverage report only when the user runs it.

The existing linear policy encodes fixed card IDs and DK-specific observations. It is not an all-class model. Full Standard needs effect implementations, timing/trigger infrastructure, class powers, choice flows, construction rules, generated pools, replay fixtures and a redesigned agent interface. Unsupported effects must fail explicitly; importing text or extracting keywords cannot substitute for these rules.

External simulators reviewed did not document complete current-Standard support: Fireplace's README targets patch 17.6; SabberStone's documented coverage is July 2019; RosettaStone's card coverage table does not include modern Standard. None was installed or represented as a ready full-Standard backend.

## User workflow

Open `05_standard_card_book.ipynb`, then Run → Run All Cells. This loads, displays, and audits data; it does not train. Search by class, name, or rules text in its settings. The coverage report is saved under `runs/standard_catalog_2026-09-18/coverage.json`. No additional packages or API credentials are required. The full simulator remains a separate unfinished implementation task.
