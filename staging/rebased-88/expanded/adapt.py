"""Explicit regular-game Adapt effects, separate from Bonus Effects.

This defines application only. Choice eligibility, repeated selections and
Ashalon's persistent play timing require family-level review before admission.
"""
from engine.cards import UnsupportedCard
ADAPTATIONS={
 'UNG_999t2':('spores',),
 'UNG_999t3':('stats',3,0),
 'UNG_999t4':('stats',0,3),
 'UNG_999t5':('keyword','ELUSIVE'),
 'UNG_999t6':('keyword','TAUNT'),
 'UNG_999t7':('keyword','WINDFURY'),
 'UNG_999t8':('keyword','DIVINE_SHIELD'),
 'UNG_999t10':('stealth',),
 'UNG_999t13':('keyword','POISONOUS'),
 'UNG_999t14':('stats',1,1),
}
PLANT='UNG_999t2t1'
def apply_adaptation(game,minion,choice):
 if choice not in ADAPTATIONS:raise UnsupportedCard('Unknown Constructed Adaptation: '+str(choice))
 if minion is None or minion.health<=0 or minion.dormant:return False
 op=ADAPTATIONS[choice]
 if op[0]=='spores':
  if game.cards.get(PLANT,{}).get('type')!='MINION':raise UnsupportedCard('Missing Adapt Plant dependency')
  minion.attached_death_effects.append(('death_summon',PLANT,2))
 elif op[0]=='stats':game._buff(minion,op[1],op[2])
 elif op[0]=='keyword':minion.keywords.add(op[1])
 else:
  minion.temporary_keywords.append(dict(keyword='STEALTH',phase='start',turn=game.turn+(2 if minion.owner==game.current else 1)))
 return True
