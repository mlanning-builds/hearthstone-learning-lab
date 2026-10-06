# Shared Colossal entry checkpoint

Scope: frozen regular Standard patch 36.6.0.251952. This is entry infrastructure, not completed card support. Live counts remain 877 collectibles and 308 staged recipes; none of the 26 Herald/Colossal collectibles is admitted by this change.

## Implemented

`expanded/colossals.py` defines ten explicit body-to-appendage layouts from the existing pinned source inventory. Summons, copied summons and board transformations use one entry path. Dependencies are checked before board mutation, even when the board is full. Failed parent summons produce no appendages. The board limit truncates ordinary appendage entry. Copies receive fresh appendages and parent links rather than duplicating prior limb buffs or identifiers. Transformations create appendages without publishing a summon notification for the transformed parent.

The entry path captures appendage notifications before the parent's notification. Left/right layout and notification timing are candidate behavior and still require independent client evidence. The completion queue lists these explicit token dependencies and a specific entry-only blocker; it does not count layouts as complete runtime card declarations.

Twenty-one focused checks cover the ten layouts, existing neighbors, board capacity, owner separation, dependencies, copy links, transformations and blocked cases. The fixtures intentionally install token records without claiming their card-specific abilities are implemented.

## Explicitly unfinished

- Herald soldier selection, upgrade values/timing, generation restrictions and Deathwing choices.
- Each Colossal's body ability and each appendage's ability.
- Specialized entity replacement paths, including `entity_tribute` (which directly creates a copied replacement), must route through reviewed Colossal entry before admission. The shared summon and ordinary transform paths are covered; this is not a claim that every replacement path is connected.
- Magmaw's 99 appendages and replenishment lifecycle. It raises an unsupported-rule error rather than substituting six tokens.
- Dormant entries and silenced copies. These fail closed pending reviewed semantics.
- Independent ordering evidence, including listener-triggered deaths and choices during the complete entry sequence. The current entry helper captures events without resolving arbitrary effects inside it.

The next work is the shared Herald upgrade model and the six army ability families, then remaining non-Herald Colossal abilities and Magmaw. Passing infrastructure fixtures does not authorize enabling these cards or training on them.

## Evidence

The [pinned inventory](engine-audit/herald-colossal-source-inventory.json) preserves card identities and numeric left-limb metadata from hash-verified XML. The [official Cataclysm announcement](https://hearthstone.blizzard.com/en-us/news/24245219) establishes the broad Colossal/Herald relationship, but does not settle precise event ordering. Explicit layout association and runtime ordering remain candidate interpretations until independently checked.

## Validation receipt

Full suite: 3,395/3,395 passed, zero failures/errors/skips, source unchanged. Receipt: `staging/rebased-88/runs/expanded_validation/validation-e379b840ec4849d9998b4ac6199999d6.json`. Twenty-two smoke games completed with zero errors/caps and 2,463 feature decisions checked. Both runs use source fingerprint `2bd86cd20bf96fbb907f1bdfcd77c52494a0544a43b8ea6a81f312ccf5966735`. Completion queue: 21 checks passed; 877 live / 308 staged / 79 unresolved mappings or reviews.

## Subsequent work

The [Herald armies checkpoint](herald-armies-checkpoint.md) connects the specialized `entity_tribute` replacement path and adds the six Soldier/appendage ability families. The unfinished list above records the state at this earlier entry checkpoint; independent review and all collectible admission gates remain.
