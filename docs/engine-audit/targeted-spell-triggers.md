# Spells cast on minions

Fragment of Nothing (END_026) uses an owner-specific spell-cast listener. The play pipeline captures whether the selected target is a minion before resolving spell effects, and carries that Boolean through the existing pending-play continuation. Thus a target dying to the spell does not erase its original type. Countered spells do not emit the event. The listener must still be present and unsilenced after resolution.

Seven fixtures cover killed enemy targets, self-targeted healing, hero/untargeted spells, Counterspell, a silenced/dead listener, opposing casts and multiple listeners. The full suite also exercises existing suspended play continuations after the pending-play tuple change. The pinned local card record supplies the rule text.

This metadata describes directly selected targets in the implemented play path. General target redirection, nested automatically cast spells and expanded multi-target cast rules still require their own verified boundaries before claiming complete trigger coverage.
