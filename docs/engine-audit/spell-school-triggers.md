# School-filtered spell triggers

Veteran Warmedic (`CORE_BAR_878`) uses a `spell_school_cast` listener parameterized by Holy. It consumes the existing after-spell event and requires the caster to own the listener. A qualifying spell summons `BAR_878t`, a pinned 2/2 Battlefield Medic with Lifesteal. The dependency is explicit and generated-only, with support for being returned to hand and replayed.

Deathchiller (`CORE_RLK_083`) uses the existing owner spell-cast listener and distinct random enemy damage operation. It deals one damage to each of up to two different enemy characters; an otherwise empty enemy board means one hit to the hero, not two. Neither trigger fires for an opponent's spell or after the listener is silenced. Countered spells do not reach the after-spell event.

The seven new fixtures verify school/owner filtering, countering, Silence, board capacity, Medic Lifesteal, distinct targets and a single available target. The full rule suite also covers generated minion replay. Definitions come from the hash-pinned regular Constructed metadata; tests verify internal behavior, not complete independent client conformance.
