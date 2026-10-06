# Learning feature schema v4

The encoder includes the ordered, public next-Hero-Power cost modifiers, selecting only each modifier's `kind` and `amount`. Invalid kinds, negative values, noninteger amounts and malformed entries are rejected. Unknown fields inside modifier records are ignored. Current Hero Power cost remains available separately.

Board data already included the public signed-Attack deficit introduced with Twisted Treant. New regression tests verify that equal displayed Attack with different deficits gives different state and action-target features without depending on entity IDs. Modifier-order tests also verify player-seat relativity and that extra nested information is not consumed.

The schema is now `visible-action-features-v4`. Existing checkpoint loaders reject different feature schemas and engine fingerprints, so v3 checkpoints are not silently reused. This is an expanded sparse baseline representation, not proof of optimal play or complete observability of every implemented interaction. No training is launched by this change.
