# Pinned Standard generation membership

The candidate now derives ordinary Standard generation membership from all 1,185 records in the frozen patch 36.6.0.251952 catalog. The loader checks the snapshot hash, unique identities and manifest count; immutable metadata can be shared safely across game copies. The executable registry never determines membership.

Generation excludes Fabled roots, Legendary Quests, triple-Rune cards and each request's explicit exclusions. Random board creation also excludes Colossals; generation into hand and literal summons of chosen cards remain separate. Side Quests and selection of physical cards already in a deck do not inherit the Legendary Quest exclusion. Past-era and exceptional named families require separate membership contracts.

Every eligible outcome must have executable card data before a pool can be sampled. An unwritten outcome rejects the complete request before random selection. This supplies membership without declaring unfinished card effects complete or reducing pools to supported outcomes.

Sources: [Standard format introduction](https://news.blizzard.com/en-us/article/19995505/a-new-way-to-play), [Quest generation exclusions](https://hearthstone.blizzard.com/en-gb/blog/23190444/draconic-details-getting-to-know-galakrond), [triple-Rune generation exclusion](https://hearthstone.blizzard.com/en-gb/news/23935323), and [35.6 correction to Hero's Welcome summoning Colossals](https://hearthstone.blizzard.com/en-us/news/24276665/35-6-patch-notes). These sources establish individual eligibility rules; the simulator's general board-generation exclusion is their documented implementation interpretation.

Focused validation: six frozen-catalog integrity and coverage tests plus 159 generation, historical-boundary, payment and Imbue tests passed on October 7, 2026. A consolidated regression is required before updating the passing source receipt. This is rule-fixture validation, not independent client certification.
