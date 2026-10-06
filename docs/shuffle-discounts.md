# Shuffle counts and Underbrush Tracker

Underbrush Tracker counts own shuffle operations into its owner's deck, not the number of inserted cards. Trading, opponent insertions and shuffling into an opponent's deck do not discount it. Costs floor at zero and the played minion retains Rush.

The shared hand-to-deck shuffle now randomizes the entire destination deck after adding the clean card. Trading retains its separate random-insertion behavior and preserves enchantments. References: https://hearthstone.wiki.gg/wiki/Tradeable and https://hearthstone.wiki.gg/wiki/Lie_in_Wait . Applying the same instance-count semantics to Tracker follows its pinned text; independent Tracker/client conformance remains outstanding.

Tests cover whole-deck randomization, batch counts, actor/destination, real trading, payment and Rush. Bone Flurry remains unsupported pending investigation of its ImmuneToSpellpower metadata and patch-specific behavior; it was not approximated in this block.
