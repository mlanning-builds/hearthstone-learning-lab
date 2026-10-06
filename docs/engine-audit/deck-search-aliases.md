# Deck-search copy identities

Single-card replacement search groups both removals and additions by the same copy-limit identity used by deck validation (`countAsCopyOfDbfId`, falling back to `dbfId`). When a parent contains two alternate IDs for one card, removing either must not generate two candidate decks with the same canonical composition. Otherwise reservoir sampling would give those compositions extra probability.

The iterator removes one deterministic representative per identity, preserves the other cards and their IDs, and still validates every result. It does not rewrite the parent deck. A constructed legal 30-card fixture with mixed aliases proves exactly 15 distinct canonical replacements in its limited pool, validates every result, and verifies sampling the entire neighborhood returns those 15 once each. The current candidate metadata has no implemented alias pairs; this fixture exercises a required case before such aliases enter coverage.

This change does not implement deck-size exceptions, certify full Standard legality or establish deck strength. Experimental subset search remains explicitly gated from full Standard search.
