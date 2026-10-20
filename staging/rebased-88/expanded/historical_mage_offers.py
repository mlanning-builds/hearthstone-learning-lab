"""Historical Mage offers and held Scroll transformations; unvalidated rules."""
from engine.game import Card
from engine.cards import UnsupportedCard
from .generation_cards import pool
from .identities import canonical_identity
from .pools import require_fixed_cards
from .discover_offer import DiscoverOffer

MAGE_MINIONS=pool(card_type='MINION',classes='MAGE')
OWN_SPELLS=pool(card_type='SPELL',classes='own_or_neutral')
MAGE_SPELLS=pool(card_type='SPELL',classes='MAGE')
GIFT=('CS2_024','CS2_023','CS2_029')
def op(name,*args):return ('historical_utility_mage_offer_'+name,)+args
TOKEN_RULES={
 'BT_021':('none',[op('font')]),
 'GDB_133':('none',[op('pocket')]),
 'GIFT_02':('none',[op('gift')]),
 # Random casting the untransformed Scroll explicitly has no effect.
 # Its nontrivial held behavior is implemented in turn_entries/scroll_tick.
 'LOOT_104':('none',[('batch30_noop',)]),
}
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

def open_offer(game,ctx,mode,ids,**state):
 if game.pending_choice is not None:raise UnsupportedCard('Cannot overwrite Mage Discover choice')
 if not ids:return
 game.pending_choice=dict(owner=ctx['owner'],kind='historical_mage_offer',mode=mode,context=dict(ctx),options=[dict(card_id=cid) for cid in ids],**state)
 game.phase='choice'

def split(game,operation,ctx):
 if operation[0]==op('pocket')[0]:return op('pocket_open',dict(seen=set())),()
 return None

def execute(game,operation,ctx):
 prefix='historical_utility_mage_offer_'
 if not operation[0].startswith(prefix):return False
 mode=operation[0][len(prefix):];owner=ctx['owner'];p=game.players[owner]
 if mode=='font':
  values=game._generation_discover_candidates(MAGE_MINIONS,ctx)
  ids=game.rng.sample(list(values),min(3,len(values)))
  if not ids:return True
  if any(game._card_data(c)['type']=='MINION' for c in p.deck):open_offer(game,ctx,'font',ids)
  else:
   results=[game._enter_hand(owner,Card(game._new_id(),cid)) for cid in ids]
   offer=DiscoverOffer(owner,'historical_mage_font_all',0,tuple(dict(card_id=cid) for cid in ids),getattr(p.equipped_card,'uid',None),tuple(range(len(ids))))
   game._record_discover(owner,offer)
   for result in results:game._defer_discover_followups(owner,result)
 elif mode=='gift':
  require_fixed_cards(GIFT,game.cards);open_offer(game,ctx,'gift',GIFT)
 elif mode=='pocket_open':
  state=operation[1];values=game._generation_discover_candidates(OWN_SPELLS,ctx)
  ids=game.rng.sample(list(values),min(3,len(values)))
  identities={canonical_identity(game.cards[cid],game.cards) for cid in ids}
  stop=bool(identities & state['seen']);state['seen'].update(identities)
  open_offer(game,ctx,'pocket',ids,state=state,stop=stop)
 elif mode=='scroll_tick':
  card=next((c for c in p.hand if c.uid==operation[1]),None)
  if card is None:return True
  state=game._b60_state(card)
  if state.get('historical_scroll_tick')==game.turn:return True
  values=game._generation_created_candidates(MAGE_SPELLS,dict(ctx,card_id='LOOT_104',generation_creator_id='LOOT_104'))
  if values:
   state['historical_shifting_scroll']=True;state['historical_scroll_tick']=game.turn
   game._b60_transform_card(card,game.rng.choice(values))
   game._log('hand_transformed',player=owner,entity=card.uid)
 else:return False
 return True

def resolve_choice(game,choice,selected):
 if choice['kind']!='historical_mage_offer':return False
 owner=choice['owner'];card=Card(game._new_id(),selected['card_id'])
 if choice['mode']=='gift':game._make_temporary(card)
 game._discovery_result=game._enter_hand(owner,card)
 if choice['mode']=='pocket' and not choice['stop']:
  game._rule_events.append(('captured_effects',dict(operations=(op('pocket_open',choice['state']),),context=dict(choice['context'])),[]))
 return True

def turn_entries(game,phase):
 if phase!='end':return []
 owner=game.current
 return [dict(source=None,order=c.uid,card_id='LOOT_104',operations=(op('scroll_tick',c.uid),)) for c in game.players[owner].hand if c.card_id=='LOOT_104' or getattr(c,'rule_state',{}).get('historical_shifting_scroll')]
