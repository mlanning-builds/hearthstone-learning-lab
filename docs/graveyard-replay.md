# Graveyard replay prerequisite

The prior history stores only card IDs. Death processing now additionally records controller, death position, turn, a detached minion snapshot, and the operations captured for that death. Existing resurrection continues to use the unchanged ID history. Internal snapshots are not added to policy observations.

Five focused checks passed for independent snapshots, Silence, recorded operations, Reborn separation and observation boundaries. This is storage groundwork, not implemented graveyard replay: no new collectible support is claimed. Undeath Sentence and Endbringer Umbra still need explicit eligibility, repeated-death selection, printed-versus-attached effect semantics, and resumable execution with independent source contexts. Stored death-time operations must not automatically be treated as the correct replay operations.

## Printed effects versus death-time effects

Blizzard 32.4.2 explicitly fixed Umbra replaying granted Deathrattles: https://hearthstone.blizzard.com/en-us/news/24205944 . The engine now exposes a separate printed-rule lookup; death records preserve both printed_operations and operations actually captured at death. Silence can therefore suppress an actual death trigger without erasing the base rule definition. This does not establish whether any particular replay selects silenced deaths; eligibility remains a separate unresolved rule. No replay card has been enabled from this distinction alone.
