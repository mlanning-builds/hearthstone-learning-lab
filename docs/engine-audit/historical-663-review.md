# Historical dependency and remaining Standard review

This integration adds 175 explicitly written historical collectible bodies, moving the separate inventory from 488 to 663. It adds nine exact fixed tokens. Standard bindings remain 1,182 / 1,185; the three source cards remain unbound. Counts are written implementations, not independent game-client certification.

## Implemented effects

- 25 Spell Damage or attack-restriction bodies, including Azure Drake draw and Squallhunter Overload. Printed +2/+5 amounts override raw Boolean SPELLPOWER metadata rather than mutating the frozen archive. Damaged Spellzerker is conditional; Silence removes the intrinsic contribution or attack restriction.
- 32 physical hand buffs, self-injury and effects on both heroes, including owner start/end listeners and Deathrattles. Tribe selectors include ALL and preserve random empty-set behavior.
- 31 spell, attack and damage trigger roots, plus five literal child tokens. Missing TRIGGER_VISUAL does not suppress an explicitly declared listener.
- 36 Deathrattle roots, plus four exact tokens, including filtered physical draws, armor/healing, board damage and fixed summons.
- 26 weapon, friendly tribe, keyword and temporary self-attack Battlecries, retaining no-target body plays and intrinsic Overload.
- 16 self-scaling Battlecries evaluate current physical hand, board, damage and death counters at resolution.
- Nine further healing/draw/armor Battlecries include their additional damage and Overload clauses.

The per-turn spell-cast counter includes successful paid and automatic casts, excludes Counterspell, resets each turn, and appears at the public observation boundary. Feature schema v59 includes this counter; old model artifacts are preserved and are not represented as compatible with the changed source/schema. No learning or training cells were executed.

## Remaining Standard mechanics

Avatar pack cards now execute as five detached physical entities, preserving full-hand behavior without hand-entry/burn/payment events. This follows Blizzard's [31.2 change](https://hearthstone.blizzard.com/en-us/news/24163459/31-2-patch-notes), which removed the hand-space requirement. The exact joint pack distribution remains unavailable; synthetic fixture weights are not installed as production probabilities.

Victor Nefarius and Storm the Gates validate explicit component identities, payload shapes and legal second-stage completion before sampling. Empty completion, stale selection, overwritten choice and unbound composite tokens reject. A read-only audit of the complete frozen XML also found no component-list/script/pool definitions or qualifying membership tags; the 3,200 referenced tags only expose metadata and identity links. Avatar raw tags likewise encode no probability law. No curated component list was guessed: [Victor's official record](https://hearthstone.blizzard.com/en-us/cards/122778) and [the 35.0.2 hotfix](https://us.forums.blizzard.com/en/hearthstone/t/3502-hotfix-patch/158856) do not publish the full lists or inherited composition semantics.

## Completion limits

The exact pinned TIME_052 historical-minion pool still has 3,226 identities and **2,718 unwritten bodies**. See [the complete remaining membership inventory](historical-minion-remaining-663.json). Some added bodies are alternate archived identities outside that canonical pool; subtracting 175 from the previous missing count would overstate closure. This inventory is not the full recursive dependency closure of all historical effects.

The three unbound Standard sources, guarded probability laws, inherited construction effects and other known interaction gaps remain. Passing fixtures include correct explicit rejection cases. Full Standard readiness remains false. No generated pools were narrowed to implemented outcomes. GitHub remains paused.

## Validation

Focused family checks pass. The first consolidated run executed 5,150 cases with unchanged source: 5,149 passed and one old review-inventory assertion failed. Its immutable run is `9b6996d7a9c74537a734603bc77ee6d1`. The original 40-card source-equivalence review is preserved; the test now also accounts explicitly for nine new healing identities with separate production behavior checks. Both the six-case original/simple suite and five-case healing suite pass. Final consolidated validation passes all **5,150 non-training cases**, with unchanged source and zero failures, errors, skips or unexpected successes. Its fingerprint is `342d8b6250bc41b3a168418782a5149bb4abe435514d9f12c5ab2ee77f8550ed`, immutable run ID `1def9aa446ea4bbf81dd9a7ca9b261d7`, and UTC completion `2026-10-08T01:31:58.398326+00:00`. Supporting tooling passes 69 cases. Full Standard readiness remains false; fixture success includes explicit rejection scenarios and is not complete simulator certification.

Correction: the historical 2,718 remainder used a broader request than Amber Warden actually executes. See [the corrected request audit and subsequent batch](historical-862-review.md).
