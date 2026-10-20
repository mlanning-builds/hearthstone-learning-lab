"""Complete literal companion, Vortex, Bandit and Val'kyr generation families."""
from .pools import require_fixed_cards
COMPANIONS=('DEEP_002t','DEEP_002t2','DEEP_002t3')
VORTEXES=('TTN_480t',)+tuple('TTN_480t'+str(i) for i in range(1,8))
BANDITS=tuple('WW_345t'+str(i) for i in range(1,9))
TOKEN_RULES={
 'DEEP_002':('none',[('historical_bonus_companion',)]),
 'TTN_719':('none',[('historical_copy_literal_family','sparkbot','hand') for _ in range(3)]),
 'TTN_480':('none',[('historical_bonus_inspiration',)]),
 'WW_345':('none',[('historical_bonus_bandits',)]),
 'TTN_470':('none',[('summon','TTN_470t',5)]),
}
for cid in COMPANIONS+VORTEXES+BANDITS+('TTN_470t',):TOKEN_RULES[cid]=('none',[])
DEATH_EFFECTS={'TTN_470t':[('historical_bonus_valkyr',)]}
SPELL_DAMAGE_VALUES={'DEEP_002t2':2}
COST_AURAS={'DEEP_002t':('SPELL','own',-1,0)}
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)


def split(game,op,ctx):
 name=op[0];owner=ctx['owner']
 if name=='historical_bonus_inspiration':
  require_fixed_cards(VORTEXES,game.cards)
  count=len(getattr(game.players[owner],'historical_spell_schools',()))
  operations=tuple(('historical_bonus_vortex',) for _ in range(count))
  return (operations[0],operations[1:]) if operations else (('batch30_noop',),())
 if name=='historical_bonus_bandits':
  require_fixed_cards(BANDITS,game.cards);ids=list(BANDITS);game.rng.shuffle(ids)
  operations=tuple(('historical_bonus_deliver_bandit',cid) for cid in ids)
  return operations[0],operations[1:]
 return None


def execute(game,op,ctx):
 name=op[0];owner=ctx['owner'];p=game.players[owner]
 if name=='historical_bonus_companion':
  require_fixed_cards(COMPANIONS,game.cards)
  game._summon(owner,game.rng.choice(COMPANIONS),entry_origin='effect',entry_site='elemental_companion')
 elif name=='historical_bonus_vortex':
  require_fixed_cards(VORTEXES,game.cards)
  game._summon(owner,game.rng.choice(VORTEXES),entry_origin='effect',entry_site='elemental_inspiration')
 elif name=='historical_bonus_deliver_bandit':
  if len(p.hand)<getattr(p,'hand_capacity',10):game._add(owner,op[1])
  else:game._summon(owner,op[1],entry_origin='effect',entry_site='badlands_bandits_overflow')
 elif name=='historical_bonus_valkyr':
  for minion in p.minions:
   if minion.card_id=='TTN_470t' and minion.health>0:game._buff(minion,1,1)
 else:return False
 return True
