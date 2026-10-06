# Before-combat hand buffs

Overlord Runthak (`CS3_025`) uses a `before_minion_attack` event with an `attacking_self` listener. It grants the existing +1/+1 hand-minion buff before combat damage. The separate `minion_attack` event remains the after-damage boundary for supported "After this attacks" effects.

The event is dispatched after the current attack-canceling Secret processing. It captures its listeners at that boundary and disallows suspended choices. Runthak's effect itself requires neither a choice nor a new combat target. Seven fixtures verify before-damage timing, minion-only buffs, lethal retaliation, Silence, another minion attacking, Rush face restrictions, repeated attacks and cancellation (some scenarios share a fixture).

References: [Runthak](https://hearthstone.wiki.gg/wiki/Overlord_Runthak) and the [advanced combat rulebook](https://hearthstone.wiki.gg/wiki/Advanced_rulebook), plus the pinned metadata. The machine-readable fidelity-gap list explicitly retains the unfinished general combat-phase work: arbitrary redirection, precombat death processing and resumable choices. This implementation does not certify that broader timing model.
