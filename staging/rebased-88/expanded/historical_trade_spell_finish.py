"""Physical Tradeable upgrades and Doggie Biscuit's post-trade target choice."""
from .historical_resurrection_batches import resurrect

def op(name,*args):return ('historical_utility_trade_finish_'+name,)+args
TOKEN_RULES={
 'DED_009':('minion',[('buff',2,3)]),
 'DED_504':('none',[op('shipment')]),
 'DED_512':('none',[op('amulet')]),
 'CORE_GIL_191t':('none',[]),
}
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

def progress(game,card):
 if card.card_id in ('DED_504','DED_512'):
  state=game._b60_state(card);state['historical_trade_upgrades']=min(6,state.get('historical_trade_upgrades',0)+1)

def after_trade(game,owner,card):
 if card.card_id=='DED_009':
  game._rule_events.append(('captured_effects',dict(operations=(op('biscuit'),),context=dict(owner=owner,source=None,target=0,bonus=0,spell=False,card_id=card.card_id)),[]))

def split(game,operation,ctx):
 if operation[0] not in (op('shipment')[0],op('amulet')[0]):return None
 card=ctx.get('physical_card');trades=game._b60_state(card).get('historical_trade_upgrades',0) if card is not None else 0
 effect=('summon','CORE_GIL_191t',min(7,2+2*trades)) if operation[0]==op('shipment')[0] else resurrect('deathrattle',min(7,1+trades))
 return game._split_fixed_summon(effect,ctx)

def execute(game,operation,ctx):
 if operation[0]!=op('biscuit')[0]:return False
 options=[dict(card_id=m.card_id,target_uid=m.uid) for m in game.players[ctx['owner']].minions if m.health>0 and not m.dormant]
 if options:
  game.pending_choice=dict(owner=ctx['owner'],kind='historical_trade_biscuit',options=options);game.phase='choice'
 return True

def resolve_choice(game,choice,selected):
 if choice.get('kind')!='historical_trade_biscuit':return False
 target=game._force_live(selected['target_uid'])
 if target is not None and target.owner==choice['owner']:target.keywords.add('RUSH')
 return True
