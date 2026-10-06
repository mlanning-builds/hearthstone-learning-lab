# Shared summon listeners — experimental implementation

Three cards now use the same declarative event selector: Murloc Tidecaller (`CORE_EX1_509`, friendly Murloc → +1 Attack); Windswept Pageturner (`TLC_220`, friendly Elemental → 3 random enemy damage); Corpse Flower (`EDR_815`, enemy minion → spend 2 Corpses to deal 3 damage to it). The earlier conversational name “Sizzling Cinder” was incorrect; the pinned card is Windswept Pageturner.

The reusable selector is `('summon', relation, tribe)`, where relation is friendly/enemy/either and tribe is an identity tribe or null. It uses the existing Constructed tribe matcher, including ALL, rather than interpreting rules text. Trigger operations reuse shared buff and damage handling. A generic resource-checked event-target damage operation supplies Corpse Flower.

Successful `_summon` calls capture eligible existing listeners and exclude the subject itself. Failed board entry and `_create_minion` replacements do not emit summons. Effect summons enqueue at existing operation/event checkpoints. Played-minion notifications are retained privately until their effects/choices finish. Reborn notifications release after its health and keyword initialization. Removed/Silenced/dead listeners are skipped; a removed or dead Corpse Flower target does not consume resources. These are candidate behaviors with explicit unresolved timing assumptions.

This implementation deliberately does not drain arbitrary triggers inside `_summon`: callers may still be applying keywords, copy adjustments or Reborn state. That also means this is **not a complete individual-summon phase scheduler**. In particular, notifications from multiple summons in one effect may wait until its operation checkpoint. General nested/recursive summon reactions, choice-producing listeners, Battlecry self-transformation, Secret ordering, control changes and competition between multiple resource-spending listeners need independent validation. See `summon_listener_phase_order` in the candidate fidelity-gap register. Do not treat the three written declarations as externally certified cards or full Standard support.

Khadgar requires summon multiplication/copy semantics; Kabal Mastermind requires persistent player-owned listeners; Tras'tath also requires Prepare and stat transfer. They are not silently treated as covered by this event selector.

## Validation

The previous local receipt passed 1,114 checks at fingerprint `b2a524cf9154f5720730a9ae775a307ad6219e9a85636d89a7a99760e670143f`. It predates this change. Twenty-two additional checks are prepared; none were run by the assistant. Run notebook 13 locally to obtain the new result. No training is started.

Fixtures cover self exclusion, friendly/enemy/tribe filtering, normal play plus Battlecry tokens, full boards, transformation, Silence/removal, listener snapshots, non-spell damage, Corpses, Shield, dead targets, Reborn initialization, Battlecry-before-notification, copying, recruiting, rollback, suspended choices and ALL tribes. They test the declared candidate behavior and do not replace independent client traces. Several isolate rules with synthetic setups; those are not claims of legal constructed deck combinations.

Written inventory: 506 collectibles; 679 still missing. Generated dependencies and broader interaction checks remain unfinished. Counts in older audit checkpoints retain their historical scope.

## Evidence

Card text and identity: frozen build-251952 catalog and reviewed hashes. Public Blizzard press kits list the Windswept Pageturner (`TLC_220`, 117531) and Corpse Flower (`EDR_815`, 114306) assets:
- https://blizzard.westus-v2.propressroom.com/zh-TW/Hearthstone-The-Lost-City-of-UnGoro---Press-Kit
- https://blizzard.gamespress.com/th/Kit/Details/Hearthstone-Into-The-Emerald-Dream---Press-Kit

Historical Fireplace has summon listeners, but its old Tidecaller declaration reacts to both players, unlike the pinned current text. It was not copied as a current-rule oracle. The local source audit and phase contract explain the known timing gaps. Exact target-build interaction evidence remains outstanding.

Follow-up: [resumable post-play stages](postplay-stages.md) prevent later Secret checks from overtaking queued minion reactions. Eleven new checks await local execution. Multi-summon loop timing remains unfinished.
