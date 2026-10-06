# Hero Divine Shield

Shared hero state now supports a single non-stacking shield. Positive damage consumes it before armor; zero damage does not. Prevented damage yields no damage event or Lifesteal. Immunity is checked first. Hardlight Protector heals then grants the shield; Curious Cumulus grants it at its controller end turn unless silenced. Both players can observe it, and sparse features include hero/target shield state (schema v9).

Six focused checks passed. Written coverage: 516/1185, 669 remaining. Combination ordering with weapon damage replacement remains an explicit unverified assumption. No training ran.
