# Distinct high-cost resurrection

Merithra (EDR_238) uses resurrect_distinct_min_cost with threshold eight. The operation filters the owner's death history by printed cost, collapses copy aliases, randomizes eligible distinct identities, and summons fresh minions until the board fills. Death history is not consumed and Battlecries are not replayed.

Five regression scenarios cover duplicate deaths, threshold/owner, a real enchanted death followed by fresh resurrection, board capacity, empty/direct-summon behavior and copy aliases. Source: pinned EDR_238 card metadata. Random summon order, alias edge cases and general summon-trigger timing remain subject to independent client verification.
