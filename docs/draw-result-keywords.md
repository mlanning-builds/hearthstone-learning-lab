# Draw-result keyword conditions

Getaway Hogdriver (JAIL_462) uses a shared draw_type_keyword operation: draw the requested count, stop on terminal fatigue, require a card for every draw, check every type and grant the source keyword. Summoning bypasses the Battlecry; Silence removes granted Charge. Source: pinned JAIL_462 record.

Six regression scenarios cover two minions, mixed orders, one/zero available cards, lethal fatigue, direct summoning and Silence. Burned-card qualification is explicitly an unverified assumption (hogdriver_burned_draws), and general draw replacement remains incomplete. The implementation uses the existing draw-identity path rather than treating fatigue as a card.
