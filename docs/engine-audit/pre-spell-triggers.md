# Pre-spell triggers

Lorewalker Cho (CORE_EX1_100) and Archmage Antonidas (CORE_EX1_559) now use `spell_played`, emitted after mana payment/card removal but before the existing spell-counter check and spell effects. The existing `spell_cast` event remains the after-resolution boundary for explicitly after-cast listeners. Cho copies into the player opposite the caster, independent of Cho's controller. Adding a copy is not another cast.

Seven new fixtures cover a spell killing Cho, Counterspell with both listeners, opposing casts, Silence, hand capacity, multiple Chos, Coins and Secret copying. Existing resolution fixtures now expect Antonidas's reward before suspended choices and retain that reward if a later spell operation ends the game.

References: https://hearthstone.wiki.gg/wiki/Advanced_rulebook?section=66 ; https://hearthstone.wiki.gg/wiki/Template:Divine_Favor_notes ; https://hearthstone.wiki.gg/wiki/Lorewalker_Cho . These describe pre-effect spell triggers and Counterspell's distinction from after-cast triggers. They are reference-rule evidence, not fresh target-patch client traces.

The new boundary currently supports non-choice listeners. Joint arbitrary Secret/listener order, target redirection, spell-enchantment transfer, and public provenance of copied Secrets remain incomplete and are tracked in `pre_spell_phase_generalization`. Cho currently copies the registered base spell record. This change does not certify a complete casting-phase model.
