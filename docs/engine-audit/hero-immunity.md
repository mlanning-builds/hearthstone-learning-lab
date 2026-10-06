# Timed hero immunity

Doomsday Prepper (`TIME_021`) grants the owner hero Immune through Outcast until that owner's next turn starts. The player effect survives Silence or death of the minion and expires before start-of-turn effects. It prevents damage before Armor, damage counters and Bulwark's replacement. Fatigue counts still advance. It does not prevent healing or Armor gain.

Enemy selected spell/ability targets and attacks exclude an immune hero; friendly targeting remains possible. Automatically selected/random effects may still attempt damage, which the shared damage entry point prevents. An immune hero can attack while ignoring retaliation damage. Eight fixtures cover Outcast, prevention, targeting, expiration, source removal, healing, combat and public/model state.

The public `immune` flag is encoded in player state and hero action references. This changes the feature schema to `visible-action-features-v3`; older checkpoints remain preserved and incompatible without explicit migration. This remains a lossy baseline, not an optimal-play model.

Sources: the hash-pinned Doomsday Prepper record and the [regular Hearthstone Immune rule](https://hearthstone.wiki.gg/wiki/Immune). Aura-based hero immunity and broader effect precedence still need implementation and independent conformance; this entry covers timed player immunity.
