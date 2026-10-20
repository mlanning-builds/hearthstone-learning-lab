# Chrono-Lord Deios interaction review

TIME_064 remains staged. Its printed multiplier must cover friendly Battlecries,
Deathrattles, activated Hero Powers, and end-of-turn effects. Written mechanics
and focused checks are not independent client certification.

## Evidence

- [Official card](https://hearthstone.blizzard.com/en-us/cards/120985/).
- [Blizzard ruling on passive Hero Powers](https://us.forums.blizzard.com/en/hearthstone/t/death-knite-imbue-issues/156215): passive powers are unaffected. The existing Death Knight Imbue hook therefore applies its buff once per eligible play.
- [Player report of nested weapon and minion triggers](https://us.forums.blizzard.com/en/hearthstone/t/chrono-lord-deios-triggers-deathrattle-4-times/154076): a doubled weapon Deathrattle can produce minions whose own Deathrattles are doubled. This is corroborating player evidence, not a developer ruling.
- [Player report with simultaneous-death replays](https://us.forums.blizzard.com/en/hearthstone/t/deios-doubling-deathrattles-from-the-aoe-that-also-kills-him/154606): ordinary simultaneous removal reportedly stops doubling, while a Rune of the Archmage sequence reportedly retained it. This conflicting event context does not establish a universal death-wave rule; review the actual replay boundaries before changing aura lifetime.

## Applied repair

The weapon break path previously omitted the shared trigger multiplier. The repaired path snapshots the printed and attached weapon Deathrattle operations and
repeats them using the same owner-specific multiplier as minion Deathrattles.
The weapon is detached once. Sixteen focused checks pass, covering ownership,
Silence, Dormant sources, multiple sources, captured Frostmourne identities,
printed summons, attached effects, nested end-turn effects, and passive powers.
The repair is now applied to the candidate. Deios remains staged while the admission gates below remain open.

## Remaining admission gates

- Free activation through Wisprider now explicitly rejects an active Deios multiplier, rather than silently dropping its second activation. Passive powers remain a no-op. Reviewed continuation semantics are still required before admitting this interaction.
- Repeating a targeted transformation needs explicit continuation semantics: transformation creates a new board entity, so blindly repeating the original target UID loses the second effect.
- Weapon effects that suspend for choices need reviewed continuation and equipment replacement ordering.
- A simultaneous death wave containing Deios needs independent evidence for when the aura ceases to apply.

Do not admit this card by hiding these interactions or by reducing eligible pools.
