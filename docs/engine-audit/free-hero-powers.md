# One-use Hero Power cost modifiers

Dreambound Disciple (EDR_847) maps its Battlecry and Deathrattle to the same `next_power_set_cost` operation. Both create a player effect that persists until the next Hero Power use. Repeated effects are consumed together, not queued as multiple free uses. Summoning bypasses the Battlecry; Silence prevents the Deathrattle but does not remove an already-created player effect. The usual once-per-turn restriction is unchanged.

Blowtorch Saboteur's existing additive effect now enters the same ordered list. Current experimental behavior applies modifiers in creation order. That precedence has not been confirmed against the pinned client: it is explicitly tracked as `hero_power_cost_order` in fidelity_gaps.json. Hero Power replacement and persistent cost auras remain outside this implementation.

The public observation includes a defensive copy of the modifier list and the calculated cost. Feature schema v4 encodes calculated Hero Power cost and the ordered public modifier sequence, retaining only the declared kind and amount fields. Seven fixtures cover consumption, Deathrattle renewal, Silence, summon-versus-play, repeated effects, provisional ordering/public-copy isolation, and Demon Hunter's base cost.

Text reference: https://hearthstone.wiki.gg/wiki/Dreambound_Disciple . The pinned local catalog is the implementation's card-data authority; this page does not constitute interaction conformance evidence.
