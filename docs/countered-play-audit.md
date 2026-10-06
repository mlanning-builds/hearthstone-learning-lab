# Countered play accounting audit

The candidate does not count a countered spell in completed-play history, cards_played (used for Combo), school history, or Overload. It does remove the card, pay mana, consume matching cost modifiers and run pre-spell listeners. This is an inventory of current behavior, not a certification.

References inspected: https://hearthstone.wiki.gg/wiki/Counterspell , https://hearthstone.wiki.gg/wiki/Counter , and https://hearthstone.wiki.gg/wiki/Advanced_rulebook?section=66 . Counterspell notes distinguish playing an Overload card from actually gaining Overload; the historical advanced rulebook distinguishes pre-text and after-text listeners. General Counter descriptions are not sufficiently specific to establish every history counter for the pinned build.

Do not move all counters ahead of the counter check merely because the user physically played a card. Obtain independent client traces for Combo, school histories, repeated-card histories, and cost modifier consumption, recording build, setup, exact actions and resulting state. No counter-accounting semantics were changed in this audit. See machine-readable gap countered_play_accounting.
