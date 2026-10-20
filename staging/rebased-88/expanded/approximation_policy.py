"""Owner-authorized approximations. These are not Blizzard fidelity claims."""
POLICY_VERSION='remaining-eight-v1'
RULES={
 'muradin_return':'Copied Deathrattle snapshots held Hammers; each trigger creates fresh physical copies for the bearer controller.',
 'hammer_shuffle':'Inherited shuffle creates a fresh High King Hammer with the bearer attack plus two; no original weapon is moved.',
 'bashana':'Uniform ordered spell-identity tuples at the greatest reachable total cost at or below twelve.',
 'watfin':'Uniform among applicable cost -1, attack +1, health +1, added tribe, renamed card; tribe/name choices uniform.',
 'vyranoth':'Split fifty attack and fifty health evenly; allocate each remainder independently without replacement.',
 'garona':'Destroy one uniformly chosen held King Llane and halve current health once per Battlecry.',
 'rogue_free_imbue':'Free trigger generates the discounted minion without a Rewind offer or consuming a paid power use.',
 'camouflage':'When all eight effects are present, choose uniformly from all eight Chameleon variants.'}
def mark(game,rule):
    game._log('approximation_used',policy=POLICY_VERSION,rule=rule)
