# Per-player turns taken

Each player starts with zero turns taken. Entering that player's turn increments their counter before start-of-turn effects. Clockwork Rager (TIME_048) uses the shared `buff_self_turns_taken` Battlecry operation to gain one Health per owner turn, including the current turn. The counter is public in both observations. Summoning does not invoke the Battlecry; Silence removes its stat bonus.

Six fixtures cover the first turn, independent alternating counts, reversed first player, summon versus play, Silence, public observation and illegal-action rollback. The pinned TIME_048 record supplies the text. Extra-turn effects are not yet implemented; any future extra turn must enter through the shared turn boundary to update the counter.

The baseline learner still uses its existing turn features and does not separately encode this new public counter. No training is launched by this implementation.
