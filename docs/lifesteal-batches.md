# Lifesteal healing batches

Effect damage now accumulates Lifesteal inside each explicit simultaneous damage batch, then heals once per owner after all hits. Separate hits outside such batches still heal separately. Combat keeps its explicit attacker/defender heals. Failed batches discard pending healing; action rollback remains responsible for undoing damage. Nested batches retain distinct scopes. No new cards are registered.

Five focused checks passed for aggregation, separate hits, damage prevention, failure cleanup and nested scopes. Full regression validation is pending. No training ran.

Evidence limitation: the existing healing_aggregation gap identified this prerequisite. Community rule notes distinguish a single area-effect Lifesteal heal from separate missile heals: https://hearthstone.wiki.gg/wiki/Cleansing_Cleric . This is not an independent patch-matched client trace. Blizzard's 35.4 notes confirm a Healing Rain/Cleansing Cleric interaction fix but do not specify general aggregation: https://hearthstone.blizzard.com/en-gb/news/24266874 . Permanent bonuses, conversion to damage and modifier ordering remain incomplete; Cleansing Cleric remains unsupported.

## Persistent bonuses

Cleansing Cleric now adds a persistent +2 healing modifier to its controller. Repeated Battlecries stack; source removal or Silence does not remove the player modifier. Positive heals use the healing source owner, cap to missing health and record actual restored health. Six focused integration checks passed. Coverage is 507/1185. This supersedes the earlier unsupported-card note. Healing-to-damage conversion and multiplier interactions remain open; this is experimental support, not independent client certification.

## Learning boundary

The permanent healing bonus is now included in sparse policy features, with feature schema v7. Existing checkpoint schema validation rejects older feature versions rather than silently changing their inputs. The existing parameterized public-counter test covers the new feature. Full candidate engine checks passed at 1185 before this feature correction; focused feature/checkpoint checks are required for this change.
