"""One pending combined Choose One effect and Plague Lord choices."""
from engine.cards import UnsupportedCard
ROOT_RULES={'TTN_503':('none',[('historical_eonar_prepare',)])}
TOKEN_RULES={
 'ICC_832':('none',[]),
 'ICC_832a':('none',[('summon','ICC_832t4',2)]),
 'ICC_832b':('none',[('summon','ICC_832t3',2)]),
 'ICC_832pa':('none',[('armor',3)]),
 'ICC_832pb':('none',[('hero_attack',3)]),
 'ICC_832t3':('none',[]),'ICC_832t4':('none',[]),
}
CHOICES={'ICC_832':[('Scarab Plague','none',[('summon','ICC_832t4',2)]),('Spider Plague','none',[('summon','ICC_832t3',2)])]}
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)|{'ICC_832p'}

def combined(game,owner,card=None):
 return bool(getattr(game.players[owner],'historical_eonar_pending',False) or game._active('CORE_OG_044',owner) or game._active('OG_044',owner) or getattr(card,'rule_state',{}).get('choose_both'))

def consume(game,owner):
 game.players[owner].historical_eonar_pending=False

def start_power(game,owner):
 if combined(game,owner):
  consume(game,owner);game._start_power_effects(owner,(('hero_attack',3),('armor',3)))
 else:
  if game.pending_choice is not None:raise UnsupportedCard('Cannot overwrite Plague Lord choice')
  game.pending_choice=dict(owner=owner,kind='historical_eonar_power',options=[dict(card_id='ICC_832pb'),dict(card_id='ICC_832pa')]);game.phase='choice'

def resolve_choice(game,choice,selected):
 if choice['kind']!='historical_eonar_power':return False
 owner=choice['owner'];operations=TOKEN_RULES[selected['card_id']][1]
 game._start_power_effects(owner,operations)
 return True
