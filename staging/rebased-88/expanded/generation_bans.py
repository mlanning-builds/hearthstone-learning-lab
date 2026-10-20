"""Explicit Constructed generation bans missing from the reduced JSON export.

These exclusions describe client eligibility, never executable coverage. They
apply to random generation and Discover; literal copies, steals, resurrection
and configured deck cards retain their normal physical definitions.

Frozen identities: TOY_330/dbfId 102983, JAIL_831/dbfId 125998.
Sources checked October 19, 2026:
https://hearthstone.wiki.gg/wiki/Zilliax_Deluxe_3000
https://hearthstone.wiki.gg/wiki/King_of_the_Underbelly
Zilliax's full client tags include DONT_PICK_FROM_SUBSETS=1, omitted by the
frozen reduced card JSON. Both pages explicitly document generation bans.
"""
CONSTRUCTED_GENERATION_BANS=frozenset(('TOY_330','JAIL_831'))
