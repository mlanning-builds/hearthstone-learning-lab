# Timed hero healing prevention

Crater Gator (`TLC_250`) attaches a healing prohibition to the enemy player until the battlecry owner's next turn begins. This is a player effect, not an aura from the minion: Silence, death and removal of the source do not clear it. Duplicate applications are retained and expire at the matching player's next turn start, before start-of-turn effects.

All existing hero restoration paths use `_heal`, including Priest's base power and Lifesteal. A blocked restoration returns zero and does not increase healing-done counters; the original power cost and Lifesteal damage still occur. Minion healing and the other hero's healing remain possible. Armor gain and direct Health-setting effects are not healing. The expiry owners are public in observations, with independent state in copied games.

References: [Blizzard card library](https://hearthstone.blizzard.com/en-gb/cards/118247/) and [Crater Gator rules reference](https://hearthstone.wiki.gg/wiki/Crater_Gator), checked against the frozen catalog text. Eight fixtures cover target scope, Silence/death persistence, power payment, turn-start expiry, Lifesteal, duplicate effects, public/copied state and summon-without-battlecry behavior. Extra-turn and arbitrary enchantment interactions still require broader conformance work; these fixtures do not certify the full Standard engine.
