# Public learning features, version 2

`visible-action-features-v2` extends the sparse baseline inputs with public turn/game counters: cards played, Fire spell played, hero power uses, next power increase, Fel spells cast, friendly attacks, last paid cost, spell damage, hero damage amounts/events, minion deaths, lifetime Overload, healing done and permanent end damage. Public discard/death/shuffle history lengths are included; their contents are not encoded in this change.

Healing prevention appears both in player state and in hero action-target features. Expiry players are converted into self/opponent-relative flags rather than numerical seat IDs. Repeated identical prevention effects have the same effective feature state.

New nested counters use an explicit allowlist. Unknown counter payloads, opponent hands, replay-only information and events remain excluded. Existing entity-ID invariance and privacy tests continue to apply. The schema version changes checkpoint compatibility: version-1 checkpoints require an explicit future migration and are not silently accepted. No existing checkpoint is rewritten.

This remains a deliberately lossy linear baseline. It does not encode complete histories, arbitrary temporal reasoning, all enchantments or rich state/action interactions. These improvements make existing public rules visible to training; they do not demonstrate stronger play without a separately budgeted experiment.
