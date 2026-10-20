"""Explicit generated Discover spells with resumable private paired state."""
from engine.game import Card
from engine.cards import UnsupportedCard
from .generation_cards import pool,discover,random_cards
from .selectors import SCHOOLS
from .identities import canonical_identity
SPELL=pool(card_type='SPELL',classes='own_or_neutral')
CHEAP=pool(card_type='SPELL',maximum=3,classes='own_or_neutral')
SECRETS=pool(card_type='SPELL',mechanic='SECRET',classes='own_or_neutral')
SCROLL=tuple(pool(card_type='SPELL',school=school,classes='own_or_neutral') for school in ('FIRE','FROST','NATURE'))
def offer(mode,*requests):return ('historical_offer_open',mode,tuple(requests),{},'')
TOKEN_RULES={
 'DEEP_001':('none',[('historical_offer_pair','stats',pool(card_type='MINION',tribe='BEAST',classes='own_or_neutral'),pool(card_type='MINION',tribe='UNDEAD',classes='own_or_neutral'))]),
 'RLK_546':('none',[('historical_offer_pair','cost',CHEAP,CHEAP)]),
 'TOY_514':('none',[offer('copies',pool(card_type='SPELL',classes='other'))]),
 'WW_404':('none',[offer('naga',pool(card_type='MINION',tribe='NAGA',classes='own_or_neutral'))]),
 'YOG_511':('none',[offer('weapon',pool(card_type='WEAPON',classes='own_or_neutral'))]),
 'YOG_507':('none',[offer('void',SPELL)]),
 'TTN_302':('none',[offer('cast',SECRETS)]),
 'TTN_302t':('none',[offer('cast',SECRETS),offer('cast',SECRETS)]),
 'TTN_477':('character',[('damage',3),random_cards(pool(card_type='SPELL'))]),
 'TTN_477t1':('character',[('damage',3),('damage',3),random_cards(pool(card_type='SPELL'),2)]),
 'TSC_772':('none',[offer('ordinary',*SCROLL),('insert_fixed','TSC_772t',1,'bottom')]),
 'TSC_772t':('none',[random_cards(pool(card_type='SPELL',school=school,classes='own')) for school in ('FIRE','FROST','NATURE')]),
 'TTN_476':('none',[offer('new_school',pool(card_type='SPELL'))]),
 'ETC_206':('none',[discover(SPELL,cost_delta=-1),('historical_play_finale',(('historical_offer_return',),))]),
 'ETC_532':('none',[('historical_offer_rewind',)]),
}
TOKEN_RULES.update({
 'TTN_845':('none',[offer('adornment',CHEAP)]),
 'TOY_822':('friendly_minion',[offer('stitching',pool(card_type='SPELL',maximum=4,classes='own_or_neutral'))]),
})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)
FORMS={'TTN_302':'TTN_302t','TTN_477':'TTN_477t1'}


def split(game,op,ctx):
 if op[0]=='historical_offer_pair':
  state={}
  return ('historical_offer_open','pair',(op[2],),state,'first'),(('historical_offer_open','pair',(op[3],),state,'second'),('historical_offer_swap',op[1],state))
 return None


def open_choice(game,ctx,mode,values,state,key):
 if game.pending_choice is not None:raise UnsupportedCard('Cannot overwrite Discover choice')
 if not values:return
 options=[dict(card_id=cid) for cid in game.rng.sample(list(values),min(3,len(values)))]
 game.pending_choice=dict(owner=ctx['owner'],kind='historical_generated_spell',mode=mode,context=dict(ctx),options=options,state=state,key=key)
 game.phase='choice'


def execute(game,op,ctx):
 owner=ctx['owner'];p=game.players[owner];name=op[0]
 if name=='historical_offer_open':
  mode,requests,state,key=op[1:]
  values=tuple(sorted({cid for request in requests for cid in game._generation_discover_candidates(request,ctx)}))
  if mode=='new_school':values=tuple(cid for cid in values if game.cards[cid].get('spellSchool') in SCHOOLS-set(getattr(p,'historical_spell_schools',())))
  if mode in ('cast','void','adornment','stitching'):
   missing=[cid for cid in values if not game._supports_internal_spell(cid,owner)]
   if missing:raise UnsupportedCard('Discover-and-cast pool lacks internal spell support: '+', '.join(missing))
  open_choice(game,ctx,mode,values,state,key)
 elif name=='historical_offer_swap':
  first=op[2].get('first');second=op[2].get('second')
  if first is not None and second is not None:
   if op[1]=='cost':
    a=game._card_stat(first,'cost',owner);b=game._card_stat(second,'cost',owner)
    first.set_cost=b;first.cost_delta=0;second.set_cost=a;second.cost_delta=0
   elif op[1]=='gain_stats':
    from .historical_saidan import add
    a=(game._card_stat(first,'attack',owner),game._card_stat(first,'health',owner));b=(game._card_stat(second,'attack',owner),game._card_stat(second,'health',owner))
    add(first,'attack_bonus',b[0]);add(first,'health_bonus',b[1]);add(second,'attack_bonus',a[0]);add(second,'health_bonus',a[1])
   else:
    a=(game._card_stat(first,'attack',owner),game._card_stat(first,'health',owner));b=(game._card_stat(second,'attack',owner),game._card_stat(second,'health',owner))
    game._mutation_set_stats(first,owner,*b);game._mutation_set_stats(second,owner,*a)
 elif name=='historical_offer_return':
  original=ctx.get('physical_card');card=Card(game._new_id(),'ETC_206')
  if original is not None:game._carry_origin(original,card)
  game._schedule_turn_effect(owner,'end',0,1,(('historical_offer_return_hand',card),),source_card_id='ETC_206')
 elif name=='historical_offer_return_hand':game._enter_hand(owner,op[1])
 elif name=='historical_offer_rewind':
  creator=canonical_identity(game.cards['ETC_532'],game.cards)
  ids={record['card'].card_id for record in getattr(p,'_historical_cast_records',()) if canonical_identity(game._card_data(record['card']),game.cards)!=creator}
  open_choice(game,ctx,'ordinary',tuple(sorted(ids)),{},'')
 else:return False
 return True


def resolve_choice(game,choice,selected):
 if choice['kind']!='historical_generated_spell':return False
 owner=choice['owner'];p=game.players[owner];ctx=choice['context'];mode=choice['mode'];cid=selected['card_id']
 if mode=='mage_summon_twice':
  game._rule_events.append(('captured_effects',dict(operations=(('summon',cid,1),('summon',cid,1)),context=dict(ctx)),[]))
  return True
 if mode=='adornment':
  cards=[Card(game._new_id(),cid) for _ in range(2)]
  for card in cards:game._b60_state(card)['historical_cast_when_drawn']=True
  p.deck.extend(cards);game.rng.shuffle(p.deck);game._record_deck_insertion(owner,owner,2,'shuffle',cards=tuple(cards));game._refresh_auras()
  return True
 if mode=='stitching':
  target=next((m for m in p.minions if m.uid==ctx.get('target') and m.health>0),None)
  if target is not None:
   target.attached_death_effects.append(('cast_fixed_spell',cid,'random'));target.keywords.add('DEATHRATTLE')
  return True
 if mode=='cast':
  game._rule_events.append(('captured_effects',dict(operations=(('cast_fixed_spell',cid,'random'),),context=dict(ctx)),[]))
  return True
 card=Card(game._new_id(),cid)
 if mode=='pair':choice['state'][choice['key']]=card
 elif mode=='naga' and getattr(ctx.get('physical_card'),'rule_state',{}).get('historical_cost_naga_played'):card.cost_delta=getattr(card,'cost_delta',0)-(1)
 elif mode=='weapon' and p.corpses>=3:
  game._spend_corpses(owner,3);card.attack_bonus+=1;card.health_bonus+=1
 copy=game._copy_card(card,source_owner=owner) if mode=='void' else None
 cast_copy=mode=='void' and game._cost(card,owner)<=p.mana
 game._discovery_result=game._enter_hand(owner,card)
 if mode=='copies':game._enter_hand(owner,Card(game._new_id(),cid))
 if cast_copy:game._rule_events.append(('captured_effects',dict(operations=(('cast_physical_spell',copy,'enemies'),),context=dict(ctx)),[]))
 return True
