# Mimicry

EDR_522 uses `opponent_draw_copy`: draw twice for the opponent, then copy the resulting cards to the caster's hand with distinct entity IDs. The shared draw helper has an opt-in `include_burned` result for this effect; ordinary callers still receive no card when a full hand burns a draw. Fatigue produces no card, and lethal fatigue stops the sequence. Both hands retain their normal ten-card cap.

Burned draws still produce copies, consistent with the documented 32.0 fix: https://hearthstone.wiki.gg/wiki/Patch_32.0.0.217964 . Card text: https://hearthstone.wiki.gg/wiki/Mimicry . The frozen EDR_522 record remains authoritative for this project patch.

Eight fixtures cover ordinary draws, opponent/caster hand limits, empty and one-card decks, lethal fatigue, supported stat/cost modifiers with independent copies, and Counterspell. Copies currently retain supported modifiers through the shared deep-copy helper. General cast-when-drawn cards, draw replacement/trigger timing and burned-card enchantment semantics still require reference-client validation; these tests do not certify those cases.
