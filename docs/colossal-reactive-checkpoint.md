# Colossal healing and spell repetition

Scope: regular Standard, frozen patch 36.6.0.251952. This extends the Colossal body checkpoint with Sinestra and The Black Blood. Six of eleven Colossal bodies now have runtime declarations. No card admission: 877 live / 308 staged. Staged runtime declarations: 228; missing declarations: 80.

## Implemented

Sinestra uses the existing resumable spell-effect repetition path for paid hand spells and internally cast spells from another class. Own-class spells, neutral spells and multiclass spells including the owner's class are excluded. Payment and hand-play history are recorded once. Silence or removal disables the aura. Multiple Sinestras or a Sinestra combined with another repetition provider raise an unsupported-rule error and public actions roll back; stacking is not silently capped or multiplied.

The Black Blood captures each credited, positive healing event and queues a forced attack against a random enemy minion for each living unsilenced friendly Black Blood. Healing any character qualifies; overhealing, prevented healing and events attributed to another player do not. Unknown healing attribution does not invent an owner. The callback checks that the source is still alive, friendly and unsilenced before attacking, and consumes no ordinary attack allowance. Attacks can occur on either player's turn.

All three Black Blood appendage identities restore three Health to a random damaged friendly character at end of turn. Each effect chooses from the current damaged characters, so later appendages stop when no one remains damaged. Healing and forced combat use the existing event frames and death checkpoints.

## Evidence and gates

Printed effects are from the frozen `data/standard/all_cards.json.gz` records. Fifty focused Colossal body checks now pass (22 new), covering both new bodies, shared entry, generation, interruptions and earlier bodies. They test implementation behavior, not an independent client oracle.

Sinestra still needs independent cast/trigger notification, target retention, Overload, repetition stacking and entry timing review, plus complete other-class generation pools. The Black Blood still needs independent healing-attribution, simultaneous-heal, delayed-source eligibility and forced-attack ordering traces. Existing Colossal/Herald entry and pool gates remain. No staged card was enabled and no training ran.

The five remaining Colossal bodies are Wickerfang, Arisen Onyxia, Chromatus, Magmaw and Cho'gall. Ultraxion and Deathwing remain in the connected Herald block.

Full regression and smoke receipts are recorded in STATUS.md when complete.

## Final validation

**3,489/3,489 checks passed**, zero failures/errors/skips, source unchanged. Receipt: `staging/rebased-88/runs/expanded_validation/validation-b6066a5d4a9c4d2298c9bbb74b888ca2.json`. Fingerprint: `4b01597f22465416cc939c0204981c2ed8e18f79aa32d990643955286add7e5e`.

**22/22 smoke games terminal**, zero errors/caps; v44 and the same source fingerprint. Receipt: `staging/rebased-88/runs/random_validation/summary-4b01597f2246-5d0583d849bc4f9f8d7b06d6be1b6a6e.json`. Staged body coverage comes from the 50 focused tests, not enabled-pool smoke games. Twenty-three queue checks pass. Counts: 877 live / 308 staged / 228 staged runtime declarations / 80 without declarations / 81 unresolved mappings or exceptional behavior.
