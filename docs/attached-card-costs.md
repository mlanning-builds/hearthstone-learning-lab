# Attached card cost setting and Krona

TIME_705 (Krona, Keeper of Eons) sets the bottom five cards' costs to one. Deck index zero is the bottom; normal draws pop the top. Short decks affect every remaining card. Physical card identities and stat enchantments survive conversion and drawing. Summoning Krona does not run its Battlecry.

Shared _set_card_cost stores a set value and clears prior additive card-local changes; later discounts still apply. The existing Kindred free-draw operation uses the same setter. Deck cost filters, hand legality, payment and own-hand observations now read this value. Hidden decks and opponent hands remain private.

Source is pinned cards.json TIME_705, build 251952. The ordering relative to dynamic self-discounts and player-wide auras remains unverified and is tracked as attached_set_cost_order. Seven regression scenarios test basic boundaries and transitions; they do not certify all enchantment layering.
