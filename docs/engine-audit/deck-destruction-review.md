# Explicit deck destruction callback repair

Three explicit destruction paths previously removed cards without notifying the
shared off-board Deathrattle callback: Willful Watcher's top-three destruction,
Warmaster Blackhorn's both-deck cheap-card destruction, and Commander Geddon's
unchosen offer destruction. They now dispatch `deck/destroy` with each original
deck owner and physical card. No off-board minion death or corpse is invented.

Nine new focused cases cover the paid Watcher Deathrattle, two physical copies,
Geddon's selected versus destroyed cards, original owner attribution, the
existing printed-cost threshold, ordinary removal, Void storage and empty decks.
Gnomeferatu's printed removal is deliberately not reclassified as destruction.

IMPFERNAL remains staged. This patch connects missing destruction notifications;
it does not settle off-board multiplier rules, interleaving during mass
replacement, hand damage/destruction, or generated overflow behavior. The frozen
card text is the rule source for the three explicit destroy recipes. Primary
player discussion of overdraw is conflicting and is not treated as a developer
ruling: https://us.forums.blizzard.com/en/hearthstone/t/impfernal-augur-and-duke/163553.
