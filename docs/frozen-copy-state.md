# Frozen state in board copies

Previously the shared board-copy path silently discarded Frozen. It now carries the source frozen_until value, preserving attack blocking and visible state. Silence on one entity does not affect the other. Five checks cover direct copies, Nablya's subsequent Rush grant, independent Silence, unfrozen originals and both observations.

Historical reference discussions confirm Frozen copying but disagree on precise thaw timing: https://us.forums.blizzard.com/en/hearthstone/t/mechanism-for-copy-summoning-a-frozen-minion-does-not-work-properly/8416 and https://www.reddit.com/r/hearthstone/comments/clkgp2/ . Neither is pinned-client proof. Preserving the expiry is an explicit candidate assumption, not a certified rule. Gap copied_freeze_expiry requires direct traces for summoning sickness, exhausted originals, Rush grants and cross-owner copies.
