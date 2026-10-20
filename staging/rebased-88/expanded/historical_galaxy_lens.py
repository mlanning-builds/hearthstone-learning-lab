"""Nobundo's physical Location Spellburst and stored spell replay."""
from copy import deepcopy
from engine.cards import UnsupportedCard
LENS='GDB_136t'
ROOT_RULES={'GDB_447':('none',[])}
DEATH_EFFECTS={'GDB_447':[('historical_lens_open',)]}
# The Location's action is bound through TIME_LOCATION_EFFECTS.
TOKEN_RULES={LENS:('none',[])}

def snapshot(game,card,owner):
 card._historical_lens_candidates=tuple(location.uid for location in game.players[owner].locations if location.card_id==LENS and not location.rule_state.get('historical_lens_used'))

def capture(game,data):
 owner=data['owner'];card=data.get('physical_card')
 candidates=getattr(card,'_historical_lens_candidates',())
 locations=[location for location in game.players[owner].locations if location.uid in candidates and location.card_id==LENS and not location.rule_state.get('historical_lens_used')]
 if not locations:return
 # A missing executable spell is explicit, never replaced by an easier spell.
 game._learned_mode(card.card_id,owner)
 for location in locations:
  location._historical_lens_spell=deepcopy(card)
  location.rule_state['historical_lens_used']=True
  location.rule_state['historical_lens_spell_id']=card.card_id
  game._log('lens_absorb',player=owner,entity=location.uid,card=card.card_id)

def targets(game,location):
 card=getattr(location,'_historical_lens_spell',None)
 if card is None:return []
 mode=game._learned_mode(card.card_id,location.owner)
 return game._targets_for(card.card_id,location.owner,mode)

def split(game,op,ctx):
 if op[0]!='historical_lens_cast':return None
 location=ctx.get('source');card=getattr(location,'_historical_lens_spell',None)
 if card is None:raise UnsupportedCard('Galaxy Lens activation requires its absorbed physical spell')
 physical=game._copy_card(card,source_owner=ctx['owner'])
 return game._cast_spell_split(('cast_physical_spell',physical,'selected'),ctx)

def execute(game,op,ctx):
 if op[0]!='historical_lens_open':return False
 game._place_location(ctx['owner'],LENS,ctx.get('death_position',-1))
 return True
