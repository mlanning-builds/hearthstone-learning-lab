# Staged Living Plague capacity repair

The existing staged replacement limits inserted Blights to the engine's current
99-card deck capacity. When no slot remains, it nevertheless calls the shared
shuffle recorder with a zero count. That recorder rejects nonpositive insertion
counts, causing a runtime error.

The repaired path now skips deck mutation, RNG, and insertion bookkeeping when the bounded
count is zero. Four isolated checks pass for a full deck, one available slot,
Silence, and minion targets. No damage replacement ordering rule or random
distribution is changed. The repair is now applied to the candidate; the card remains staged.

The Living Plague remains staged. Its [official card identity](https://hearthstone.blizzard.com/en-us/cards/126259/)
is distinct from Blight, whose frozen body is already registered. The exact cap,
Infinity arithmetic, Immune/prevention ordering, and Lifesteal/source behavior
still require review before admission.
