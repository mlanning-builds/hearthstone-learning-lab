# Divine Shield loss

Highlord Fordragon (CORE_SW_047) uses a shared shield-loss event emitted when damage removes a minion's Divine Shield. The event records the recipient owner and snapshots current listeners. Fordragon may observe its own shield loss or another friendly minion's loss on either turn, then uses the shared random-hand-minion +5/+5 operation. Its source must be alive and unsilenced at evaluation.

Eight fixtures cover self/friendly/enemy recipients, turn scope, zero damage, Immune, Silence, repeated shields, multiple Fordragons, empty/spell-only hands, selection of physical duplicate cards and carrying the buff into play. The pinned card record supplies the text.

Only shield loss through the implemented damage path is wired here. Future explicit shield-transfer or shield-removal effects must use the same event boundary with their verified rules. General simultaneous-damage/death ordering and such additional removal mechanisms are not certified by these tests.
