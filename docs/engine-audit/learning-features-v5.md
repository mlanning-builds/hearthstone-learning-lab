# Visible play-history features, v5

The learner now counts visible card IDs in each player's public play history. It also attaches the corresponding prior-play count to each own-hand entity when encoding an action's source. This action-level feature matters because state-only terms shared by every play candidate cancel in the linear policy's softmax comparison.

History records contribute only `card_id`. The redacted `SECRET` marker does not become a card identity/count feature; unknown nested fields are ignored. Opponent hands and private replay records remain excluded. Four new fixtures cover source conditioning, privacy, order-independent counts, player-seat relativity and invalid records.

These counts use visible card IDs, not a catalog lookup. Equivalent printing IDs are still separate features, even though the simulator's repeated-play rule uses canonical identity. The baseline remains lossy and does not encode complete chronological history or learn optimal play merely by receiving these inputs.

The feature schema is `visible-action-features-v5`; older schemas are rejected by checkpoint loading. No training is started by this change.
