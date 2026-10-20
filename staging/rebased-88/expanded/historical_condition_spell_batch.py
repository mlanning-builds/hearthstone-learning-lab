"""Historical conditional summons, physical copies and Librams; unvalidated."""
from engine.game import Card
from .generation_cards import pool,random_cards
from .historical_draw_batches import draw
from .historical_saidan import add
from .historical_starships import building
from .selectors import has_tribe

def op(name,*args):return ('historical_utility_condition_batch_'+name,)+args
MINION=(('type','eq','MINION'),)
TOKEN_RULES={
 'CS3_002':('friendly_minion',[op('ritual')]),'CS3_002t':('none',[]),
 'GDB_113':('none',[op('breach')]),'GDB_113t':('none',[]),
 'GDB_124':('none',[op('omen')]),'GDB_124t2':('none',[]),
 'GDB_137':('none',[op('clarity')]),
 'GDB_138':('minion',[('buff',3,3),op('divinity')]),
 'GDB_139':('none',[op('faith')]),'GDB_139t':('none',[]),
 'SCH_357':('none',[('summon','SCH_357t',3)]),'SCH_357t':('none',[]),
 'SCH_533':('none',[op('commence')]),
 'SCH_617':('minion',[('buff',1,1),('summon','SCH_617t',1),('add','SCH_617t',1)]),'SCH_617t':('none',[]),
 'SCH_702':('none',[op('felosophy')]),
 'SC_404':('none',[('summon','SC_403t',2),('historical_utility_repeat_batch_launch_discount',)]),
 'SW_034':('none',[random_cards(pool(card_type='MINION',minimum=5,maximum=5),4,destination='board',stats=(2,2))]),
 'SW_085':('none',[op('fiend')]),'SW_085t':('none',[]),
 'SW_095':('none',[draw((('mechanic','eq','OVERLOAD'),))]),
 'SW_321':('character',[('damage',3),op('aimed')]),
 'VAC_558':('none',[('summon','VAC_558t',3)]),'VAC_558t':('none',[]),
 'VAC_925':('none',[('schedule_turn_effect','start',1,1,(('summon','VAC_926t',2),))]),
 'VAC_949':('none',[op('heights')]),
 'YOP_005':('none',[('summon','YOP_005t',1),op('barricade')]),'YOP_005t':('none',[]),
 'ULD_324':('minion',[('destroy',),('insert_fixed','ULD_324t',3,'shuffle')]),'ULD_324t':('none',[]),
 'SCH_302':('minion',[('keyword','DIVINE_SHIELD'),op('luminance')]),
}
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

def zero_cost(game,ctx):
 if 'internal_cast_depth' not in ctx and 'paid_cost' in ctx:return ctx['paid_cost']==0
 card=ctx.get('physical_card')
 return card is not None and game._cost(card,ctx['owner'])==0

def sequence(game,ctx,operations):
 operations=tuple(operations)
 if not operations:return ('batch30_noop',),()
 first,tail=game._split_fixed_summon(operations[0],ctx)
 return first,tuple(tail)+operations[1:]

def split(game,operation,ctx):
 prefix='historical_utility_condition_batch_'
 if not operation[0].startswith(prefix):return None
 name=operation[0][len(prefix):];owner=ctx['owner'];p=game.players[owner]
 if name=='ritual':return ('destroy',),(('summon','CS3_002t',1),) if len(p.all_minions)>=5 else ()
 if name=='breach':return sequence(game,ctx,(('summon','GDB_113t',1),op('hero_health',5),op('breach_repeat')))
 if name=='breach_repeat':
  if p.corpses<5:return ('batch30_noop',),()
  game._spend_corpses(owner,5);return sequence(game,ctx,(('summon','GDB_113t',1),op('hero_health',5)))
 if name=='omen':
  summon=('summon','GDB_124t2',2)
  return game._split_fixed_summon(summon,ctx) if building(game,owner) is not None else (('schedule_turn_effect','start',2,1,(summon,)),())
 if name=='clarity':
  operation=draw(MINION,'buff',(2,1)) if zero_cost(game,ctx) else draw(MINION)
  return sequence(game,ctx,(operation,operation))
 if name=='faith':
  state=dict(rush=zero_cost(game,ctx));return op('faith_one',state),(op('faith_one',state),op('faith_one',state))
 if name=='commence':
  state={};return ('historical_copy_recruit_one','deck',MINION,'TAUNT',state),(op('shield_recruit',state),)
 if name=='barricade':return game._split_fixed_summon(('summon','YOP_005t',1),ctx) if len(p.all_minions)==1 else (('batch30_noop',),())
 return None

def event(game,kind,data):
 if kind!='minion_died':return
 for card in game.players[data['owner']].hand:
  if card.card_id=='SCH_357':
   state=game._b60_state(card);state['historical_fel_guardian_deaths']=state.get('historical_fel_guardian_deaths',0)+1

def execute(game,operation,ctx):
 prefix='historical_utility_condition_batch_'
 if not operation[0].startswith(prefix):return False
 name=operation[0][len(prefix):];owner=ctx['owner'];p=game.players[owner]
 if name=='hero_health':
  p.max_health+=operation[1];p.health+=operation[1];p.hero_health_changed_turn=True
  game._queue_event('historical_hero_health_gained',owner=owner,amount=operation[1])
 elif name=='divinity':
  if zero_cost(game,ctx):
   card=ctx.get('physical_card') or Card(game._new_id(),'GDB_138')
   game._schedule_turn_effect(owner,'end',0,1,(op('return',card),),source_card_id='GDB_138')
 elif name=='return':game._enter_hand(owner,operation[1])
 elif name=='faith_one':game._summon(owner,'GDB_139t',entry_keywords=('RUSH',) if operation[1]['rush'] else (),entry_origin='effect',entry_site='libram_of_faith')
 elif name=='shield_recruit':
  m=game._force_live(operation[1].get('uid'))
  if m is not None:m.keywords.add('DIVINE_SHIELD')
 elif name=='felosophy':
  values=[c for c in p.hand if game._card_data(c)['type']=='MINION' and has_tribe(game._card_data(c),'DEMON')]
  if values:
   lowest=min(game._cost(c,owner) for c in values);original=game.rng.choice([c for c in values if game._cost(c,owner)==lowest]);copy=game._copy_card(original,source_owner=owner)
   if ctx.get('outcast'):
    add(original,'attack_bonus',1);add(original,'health_bonus',1);add(copy,'attack_bonus',1);add(copy,'health_bonus',1)
   game._enter_hand(owner,copy)
 elif name=='fiend':
  size=len(p.hand);data=game.cards['SW_085t'];game._summon(owner,'SW_085t',attack_bonus=size-data.get('attack',0),health_bonus=size-data.get('health',0),entry_origin='effect',entry_site='dark_alley_pact')
 elif name=='aimed':
  # Aimed Shot lasts until the next Hero Power, rather than expiring this turn.
  p.historical_aimed_shot_bonus=getattr(p,'historical_aimed_shot_bonus',0)+2
 elif name=='heights':p.mana_capacity+=3;p.max_mana=min(p.mana_capacity,p.max_mana+1)
 elif name=='luminance':
  target=game._force_live(ctx.get('target'))
  if target is not None:game._summon(owner,target.card_id,copy_from=target,entry_stats=(1,1),entry_origin='copy',entry_site='gift_of_luminance')
 else:return False
 return True
