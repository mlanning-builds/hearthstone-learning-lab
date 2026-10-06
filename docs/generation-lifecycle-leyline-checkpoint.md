# Generation lifecycle and Leyline checkpoint

Frozen regular Standard scope: build 251952. Mercenaries and Battlegrounds are excluded.

Deathrot Maw is now live, using the same three implemented Fel Beast tokens as Underfel Rift. Its pinned metadata hash and implementation index are updated; the obsolete recipe is removed. Focused tests cover every outcome, Silence and a full board freeing the dying minion’s slot.

The final five previously missing generation/Discover bodies are staged: Vanessa the Ringleader (including Prepare and after-card-play generation), Beast Tripwire (including its explicit JAIL_879t cast-when-drawn token), Welcome Home! (location reopening and attached Deathrattles), Endtime Murozond (board fill, full healing and skipped turns) and The Skeleton Key (repeatable choices and fixed refresh self-damage). Complete pools remain required. No subset pool is substituted. Twenty-seven focused tests passed.

All seven Leyline cards now have runtime bodies with shared persistent cost, effect and repetition upgrades. Starting values 4/6/1 are read for review from the frozen card_tags.json and explicitly encoded in leylines.py. Crystallized Leyline’s value 6 differs from the earlier May 19 official patch announcement (5); the frozen snapshot is retained, and later-patch provenance remains a review item. Twenty focused tests passed, including scaling, selection, repeated resolution, excess damage prevention, missing pools and cloning. Source context: https://hearthstone.blizzard.com/en-gb/news/24276662/35-4-2-patch-notes .

Coverage after the subsequent opening-deck block is 875 live registrations and 310 staged recipes. All 135 remaining generation/Discover cards have runtime declarations. Four Leylines are live (Bursting Leyline, Surge Needle, Leyline Nexus and Mystic Runesaber); three remain staged. All six Maps also have staged runtime bodies, with 17 focused checks for retained original options, physical deck identity, expiry and privacy. These are implementation milestones, not a full Standard fidelity claim. The completion queue retains explicit dependency and conformance gates.

Feature schema v40 introduced skip-turn and Leyline upgrade state and reflects location attachment/refresh-choice behavior. No training or deck search ran. Subsequent schemas add mana capacity (v41) and persistent Manastorm state (v42). Consolidated receipts are recorded in candidate STATUS.md.

Ysera raises both players' mana capacity from the original submitted deck; Hogger creates new physical copies of the other original Legendary minions before opening hands. Opening-hand cards are included when checking deck-size conservation. Thirteen focused tests cover both-player stacking, provenance, generated Ysera, ramp/temporary mana and the capacity bound. Temporary mana followed by filled-crystal ramp can no longer exceed that bound.
