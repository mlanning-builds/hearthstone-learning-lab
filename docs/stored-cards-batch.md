# Stored-card integration batch

Scope: frozen regular Standard patch 36.6.0.251952. No training ran.

11 collectibles are connected to the live engine, with 47 focused behavioral checks. The family now has two staged members: Irida Sinseeker and Timelooper Toki. This batch also connects Raith Van Geist through recorded Reborn events.

- `CAP_805`: Slime 'em! (SPELL).
- `CAP_806`: Raith Van Geist (MINION).
- `CATA_481`: Iso'rath (MINION).
- `CATA_EVENT_001`: Destructive Phoenix (MINION).
- `CORE_RLK_086`: Frostmourne (WEAPON).
- `EDR_454`: Clutch of Corruption (LOCATION).
- `EDR_818`: Nythendra (MINION).
- `JAIL_852`: Togwaggle, Smuggler King (MINION).
- `TIME_706`: The Fins Beyond Time (MINION).
- `TIME_EVENT_998`: Runi, Temporal Guardian (MINION).
- `TLC_841`: Entomologist Toru (MINION).

## Shared implementation

`expanded/stored_cards.py` owns bound copies, physical set-aside hands, delayed return/discard payloads and resurrection histories. Raw payload objects are kept out of public operation arguments and serialized observations. Owner-only views expose remembered hands; played eggs/jars expose their bound minion's identity and stats. Card choices remain private.

Clutch of Corruption uses the location activation/cooldown pipeline. Frostmourne records its final killing blow before its Deathrattle. Nythendra uses attack for its beetle count and combines surviving beetle stats. Reborn history records successful rebirths, not merely printed keywords. Hand mixing preserves physical enchantments and both hand sizes.

Feature schema is now `visible-action-features-v31`, adding Reborn history, starting-hand memory and set-aside hand information. Older policy artifacts must pass the existing schema compatibility check; passing fixtures is not evidence of optimal play or complete Standard fidelity.

## Evidence and limits

Pinned collectible and generated metadata are hashed in `expanded/reviewed_cards.json`. Runtime fixtures are in `tests/test_expanded_stored_cards.py`. Full-suite and smoke receipts are linked in the candidate `STATUS.md` once completed.

Rule references consulted:

- https://hearthstone.wiki.gg/wiki/Nythendra
- https://hearthstone.wiki.gg/wiki/Nythendric_Beetle
- https://hearthstone.wiki.gg/wiki/Togwaggle%2C_Smuggler_King
- https://hearthstone.wiki.gg/wiki/Destructive_Phoenix
- https://us.forums.blizzard.com/en/hearthstone/t/maloriak-the-meme-powerhouse/160304
- https://hearthstone.wiki.gg/wiki/Runi%2C_Temporal_Guardian
- https://hearthstone.wiki.gg/wiki/Entomologist_Toru

Independent client traces are still needed for arbitrary enchantment retention across storage, combined aura/reformation interactions, nested hand-swap ordering, and replacement/trigger edge cases. Engine fixtures validate the implemented contracts, not full client conformance.
