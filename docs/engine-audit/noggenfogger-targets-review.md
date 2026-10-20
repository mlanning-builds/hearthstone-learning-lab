# Staged Noggenfogger target restrictions

The previous staged code rerouted attacks across both players and reduced printed
card restrictions to a broad character/minion distinction. It could select
friendly attack defenders or send an enemy-only effect to a friendly minion.

The [official printed card](https://hearthstone.blizzard.com/en-us/cards/40955)
does not enumerate all targeting exceptions. Player reports describe enemy-only
attack defenders in [2024](https://us.forums.blizzard.com/en/hearthstone/t/what-the-hell-is-going-on-mayor-noggenfogger/132885)
and [2026](https://us.forums.blizzard.com/en/hearthstone/t/mayor-noggenfogger-not-randomizing-targets-for-opponent/161675).
These reports support reviewing friendly rerouting as a defect; they are not a
developer conformance ruling.

The applied repair restricts attack candidates to the opposing controller and
uses the existing printed target helper for targeted cards. Replacement Hero
Powers use their own target helper, preserving friendly Shaman targeting. Twelve
isolated checks pass for both attacker controllers, hero attacks, enemy/friendly
spells and Battlecries, large/damaged restrictions, Shaman power targeting,
Elusive, Silence, and targetless actions.

The old staged fixture that expected friendly-hero attacks now checks opposing
attack defenders. The twelve focused checks and 91 existing final-path checks
pass. The changed candidate requires a fresh full regression receipt.
Stealth/Immune attack eligibility, Taunt bypass, repeated target selection,
Choose Both, source entry timing, secret ordering, forced attacks, and location
activation remain separate admission gates. No ordinary-registry admission is
implied by these twelve internal checks.
