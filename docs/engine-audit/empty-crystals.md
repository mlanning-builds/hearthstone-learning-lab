# Empty Mana Crystals

Tranquil Treant (EDR_861) is registered from the frozen Standard catalog. Its Deathrattle invokes the shared `empty_crystals` operation for both players. The operation increases capacity without adding spendable mana or modifying locked mana or pending Overload. Each player independently caps at the engine's ordinary ten-crystal limit. No replacement card is drawn at that limit.

Six fixtures cover both recipients, opponent ownership, independent caps, Silence, multiple simultaneous deaths with Overload, and refill at the next turn. The existing death pipeline handles removal and repeated triggers; this implementation does not certify arbitrary death-order interactions.

The engine still uses a fixed ten-crystal cap. Cards that alter the maximum mana limit require a separate persistent-cap model before they can be implemented faithfully. The operation's friendly/enemy recipient variants are available for future mappings; this card and its fixtures exercise the both-player variant.
