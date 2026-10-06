# Four Colossal body implementations

Scope: frozen regular Standard patch 36.6.0.251952. No live admission: 877 live collectibles and 308 staged recipes remain. Staged runtime declarations increase from 222 to 226; 82 staged collectibles still lack declarations.

The new `expanded/colossal_bodies.py` composes existing entry, army, generation, combat legality and effect replay systems:

- **Ragnaros, the Great Fire:** end-of-turn replay of friendly minion Deathrattles. Captures the initial entity list, checks later sources are still alive and friendly, and uses each minion's own effect context. Choices resume the remaining sequence without replaying completed effects. Newly summoned minions are not appended to the captured group.
- **Azshara, Ocean Lord:** an active, unsilenced body grants its owner's hero two attacks. Multiple bodies do not stack; death or Silence removes the extra allowance without resetting attacks already spent. This implements this aura, not every possible hero Windfury source.
- **Al'Akir, Lord of Storms:** Battlecry snapshots current Attack after the candidate appendage/aura entry sequence, then generates two exact-Cost minions with a cost modifier making each cost one. Full exact-Cost membership is required; empty reviewed pools do not fall back to another Cost. Summoning the body without playing it does not run the Battlecry.
- **Vulcanos:** end-of-turn damage to all other minions. Both Plume identities share the existing damage listener and generate a Fire spell discounted by three. Their triggers cover both surviving and lethal damage; Divine Shield prevention and Silence suppress rewards as appropriate in the candidate event model.

Twenty-eight focused checks cover these compositions, including source identity, upgrades, Silence, full rollback when a generation contract is missing, interrupted choices, health/death triggers and copied/shared entry interactions already exercised by preceding suites. The completion queue now counts these four runtime declarations and retains a body pool/order review gate. Their appendages and the existing Herald gates remain prerequisites.

Printed behavior comes from the frozen `data/standard/all_cards.json.gz` records. These fixtures verify the implementation, not independent client conformance. Admission still needs reviewed Colossal placement/notification order; Ragnaros source capture and effect ordering; Al'Akir aura/Battlecry ordering; complete exact-Cost and Fire pools; Plume lethal-damage ordering; and relevant shared Herald gates.

Remaining Colossal body families: Wickerfang, Sinestra, Arisen Onyxia, The Black Blood, Chromatus, Magmaw and Cho'gall. Ultraxion and Deathwing also remain in the connected Herald block.

Full regression and smoke results are recorded in STATUS.md once complete. No training or deck search ran.

## Final validation

**3,467/3,467 full-suite checks passed**, zero failures/errors/skips; unchanged source. Receipt: `staging/rebased-88/runs/expanded_validation/validation-4bf916660f02407daa00ac77dc85171b.json`. Fingerprint: `536c3e2879daf2cbdce9c754c445a8dfd085f5248184592a2a93c54983116429`.

**22/22 smoke games terminal**, zero errors/caps, using v44 and the same fingerprint. Receipt: `staging/rebased-88/runs/random_validation/summary-536c3e2879da-b4e15a9bf57e4782b2bca314b1733c2c.json`. Smoke games cover the enabled pool; the 28 focused tests exercise staged bodies. Twenty-two completion-queue checks pass. Counts: 877 live / 308 staged / 226 staged runtime declarations / 82 missing declarations / 81 unresolved mappings or exceptional rules.
