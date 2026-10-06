# Summon from deck, then grant a keyword

Possessed Animancer (DINO_131) and Scarlet Recruiter (JAIL_516) extend summon_from_zone with an optional keyword. Existing minion/type filters select physical cards, remove them from the source zone only when board space exists, preserve stat bonuses, and do not run Battlecries. Deathrattle summons use the dead minion's position.

The six tests cover Lifesteal healing, immediate Rush restrictions, death position, distinct physical duplicates, cost-set cards, stat preservation, full-board limits, missing candidates and Silence. Sources: pinned DINO_131 and JAIL_516 records. General summon-trigger ordering and post-summon keyword-grant timing still need independent reference validation.
