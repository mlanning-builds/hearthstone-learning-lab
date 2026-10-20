"""Explicit historical Forge identities and a non-play two-mana hand action.

No text-to-rule inference or automatic admission of other Forge cards.
"""
from .historical_saidan import add as _saidan_add
from engine.cards import UnsupportedCard
from copy import deepcopy
from . import historical_upgrade_batches as recipes
FORGE_FORMS={'YOG_525':'YOG_525t'}
CORRUPT_FORMS={'DMF_064':('DMF_064t',3,3),'YOP_003':('YOP_003t',0,0)}
FORGE_FORMS.update(recipes.FORGE_FORMS)
CORRUPT_FORMS.update(recipes.CORRUPT_FORMS)
class HistoricalUpgrades:
 def _can_forge(self,card,owner):
  if card.card_id not in FORGE_FORMS or self.players[owner].mana<2:return False
  lock=getattr(card,'play_lock',None);state=getattr(card,'rule_state',{})
  if lock and lock['owner']==owner and lock.get('not_before',-1)<=self.players[owner].turns_taken<lock['until']:return False
  played_lock=state.get('locked_until_play')
  return not (played_lock and played_lock['owner']==owner and len(self.players[owner].played_history)<played_lock['count'])
 def _forge_card(self,uid):
  owner=self.current;p=self.players[owner]
  card=next((c for c in p.hand if c.uid==uid),None)
  if card is None or not self._can_forge(card,owner):raise ValueError('Illegal Forge action')
  following=FORGE_FORMS[card.card_id]
  if following not in self.cards:raise UnsupportedCard('Missing exact Forged card identity: '+following)
  original=card.card_id
  before=tuple(self._card_stat(card,key,owner) for key in ('attack','health'))
  p.mana-=2;card.card_id=following
  gain=(3,2) if original=='TTN_042' else (0,0)
  after=tuple(self._card_stat(card,key,owner) for key in ('attack','health'))
  _saidan_add(card,'attack_bonus',gain[0]+before[0]-after[0]);_saidan_add(card,'health_bonus',gain[1]+before[1]-after[1])
  if original in ('TTN_724','TTN_724t'):
   if hasattr(card,'set_cost'):card.set_cost-=2
   elif original=='TTN_724t':card.cost_delta-=2
  p.historical_forges=getattr(p,'historical_forges',0)+1
  self._b60_spend_mana(owner,2)
  # The public animation exposes mana spent, not the private hand identity.
  self._log('forge',player=owner,spent=2)
  self._queue_event('historical_forged',owner=owner,card=deepcopy(card))

 def _corrupt_held(self,owner,paid_cost):
  for card in self.players[owner].hand:
   following=CORRUPT_FORMS.get(card.card_id)
   if following is None or paid_cost<=self._cost(card,owner):continue
   identity,attack,health=following
   if identity not in self.cards:raise UnsupportedCard('Missing exact Corrupted identity: '+identity)
   from .base_stats import base_stats
   before=tuple(self._card_stat(card,key,owner) for key in ('attack','health'))
   if card.card_id=='DMF_124t' and identity=='DMF_124t':
    state=self._b60_state(card);state['historical_corrupt_growth']=state.get('historical_corrupt_growth',0)+1
   card.card_id=identity
   after=tuple(self._card_stat(card,key,owner) for key in ('attack','health'))
   _saidan_add(card,'attack_bonus',attack+before[0]-after[0])
   _saidan_add(card,'health_bonus',health+before[1]-after[1])
   self._log('corrupt',player=owner)
 def _after_play(self,context):
  # Shared completed-play boundary: effect casts, Forge and Trade never enter it.
  if not self.terminal:
   self._corrupt_held(context[1],context[3])
   from .historical_condition_batches import record_held_play
   record_held_play(self,context[1],context[3])
   miniatures=recipes.MINI_FORMS.get(context[0],())
   if miniatures:
    from .pools import require_fixed_cards
    require_fixed_cards(miniatures,self.cards)
    for cid in miniatures:self._add(context[1],cid)
  from .historical_stormwind_questline_finish import finish as finish_stormwind
  finish_stormwind(self,clear_paid=True)
  return super()._after_play(context)
