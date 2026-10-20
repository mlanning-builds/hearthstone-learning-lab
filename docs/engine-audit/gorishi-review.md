# Gorishi admission review

Unleash the Colossus (`TLC_631`) and Gorishi Colossus (`TLC_631t`) remain staged.
Their finite printed dependency is available in the archive, but shared damage
semantics must cover more than board and hero hits.

[Patch 33.0.3](https://hearthstone.blizzard.com/en-gb/news/24224212/3303-patch-notes)
changed the Quest requirement from fifteen exact-two events to twelve.
[Patch 33.2](https://news.blizzard.com/en-gb/article/24223019/33-2-patch-notes)
explicitly changed the reward to function on the opponent's turn as well. The
staged implementation follows those values and separates own-turn Quest progress
from both-turn reward triggers. Twelve existing fixtures cover its current model.

[Firsthand Kurtrus testing](https://us.forums.blizzard.com/en/hearthstone/t/gunslinger-kurtrus-gorishi-colossus-bug/148841)
reports Quest progress from damage to enemy hand minions, with disagreement and
bugs around the reward's additional hand damage. This is limited player evidence;
it does not establish the exact current pinned behavior of every off-board path.

The current damage primitive addresses heroes and board minions. Adding hand
damage needs reviewed treatment of current versus maximum card Health, physical
card identity, destruction from hand, special effects that trigger from anywhere,
and repeated-shot/reward order. Do not silently narrow the printed enemy domain
or turn missing off-board behavior into a successful no-op. Stacked rewards,
recursion guards, overkill, damage replacement, and Lifesteal remain separate
interaction review items in `expanded/fidelity_gaps.json`.
