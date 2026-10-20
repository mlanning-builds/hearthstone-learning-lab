# Battle at the End Time: ordinary registry admission

`END_017` and generated reward `END_017t` are pinned to their exact frozen records. The collectible Quest is provisionally playable in legal Hunter and Warlock starting decks; its reward remains generated-only.

The Quest observes the owner's physical hand in order: ten cards, then zero. Emptying the last card is captured before that card's effects refill the hand. A single reward is delivered after completion. The reward's paid Battlecry draws until ten using the existing bounded draw operation; its unsilenced Deathrattle discards the opposing hand through the shared discard transition. This does not require a generated outcome pool.

Production-path checks cover starting-hand Quest placement, both class deck validators, paid costs, ordered progress, transient empty/refill, overdraw, physical shuffle identity, one reward, physical draw order, ten fatigue draws on an empty deck, opposing-only discard, Silence, private hand state and clone independence. Existing staged tests remain interaction fixtures, not independent certification.

Independent pinned-client traces are still needed for transient hand states, simultaneous discard trigger ordering and interrupted draw effects. The frozen printed effect is the implementation source; provisional admission does not certify all client interactions.

Primary references: the [official reward card](https://hearthstone.blizzard.com/en-gb/cards/121160/) confirms draw-to-full and opposing-hand removal. Blizzard's [34.4.1 hotfix](https://us.forums.blizzard.com/en/hearthstone/t/3441-hotfix-patch/156351) connects empty/refill from Plot Twist; the later [34.4.3 correction](https://us.forums.blizzard.com/en/hearthstone/t/3443-hotfix-patch/156699) fixes Gatekeeper and Finley. These establish that a settled nonempty hand does not erase a real emptying transition. They do not establish that every internal list replacement counts as emptying; atomic swaps, Tradeable and effect-specific boundaries still require review. Historical Gatekeeper, Finley and Plot Twist remain unsupported outcomes rather than silently approximated generated cards.
