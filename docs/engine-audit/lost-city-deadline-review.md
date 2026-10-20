# Lost City deadline review

The current staged Quest advances at its owner's end of turn. This is an
explicit timing assumption, not evidence that Latorvius enters the hand at the
right client boundary. The finite reward recipe is now closed, but the Quest
root remains staged pending the deadline review and shared reward interactions.

A firsthand [August 2025 report](https://us.forums.blizzard.com/en/hearthstone/t/enter-the-lost-city-quest/150973)
places completion at the start of the tenth turn. A separate firsthand
[June 2026 account](https://www.reddit.com/r/hearthstone/comments/1twk4jy/opponent_got_his_quest_reward_when_his_hand_was/)
describes filling the opponent's hand before turn eleven. Both support holding
a completed reward until hand space exists. Neither supplies a complete event
trace for the exact counter transition, late Quest plays, stolen Quests or extra
turns. Their turn counts should not be silently reconciled into an invented rule.

The older isolated deadline tests assert current candidate behavior. They do
not independently establish client timing. Before root admission, verify
counter changes on the paid Quest turn, owner's end, opponent's end and owner's
start, then test lethal start/end effects, turn skips and consecutive extra turns.
