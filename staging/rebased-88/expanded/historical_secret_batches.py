"""Physical historical Secret consumers and private transformations; unvalidated."""
from copy import deepcopy
from engine.game import Card
from .generation_cards import pool
from .selectors import has_class

OWN=pool(card_type='SPELL',mechanic='SECRET',classes='own')
ANY=pool(card_type='SPELL',mechanic='SECRET')
HUNTER=pool(card_type='SPELL',mechanic='SECRET',classes='HUNTER')
MAGE=pool(card_type='SPELL',mechanic='SECRET',classes='MAGE')
RULES={
 'AT_079':('none',[('historical_secret_deck','each',False)]),
 'WON_334':('none',[('historical_secret_deck','each',False)]),
 'BAR_430':('none',[('historical_secret_copy_enemy',)]),
 'DMF_079':('none',[('historical_secret_deck','one',True)]),
 'DMF_109':('none',[('historical_secret_sayge',)]),
 'DRG_252':('none',[]),'EX1_080':('none',[]),
 'EX1_274':('none',[]),'GVG_089':('none',[]),
 'FP1_004':('none',[]),
 'GIL_634':('none',[('historical_secret_deck','one',False)]),
 'GVG_074':('none',[('historical_secret_steal',)]),
 'ICC_204':('none',[]),'BT_188':('none',[]),
 'MIS_914':('none',[('historical_secret_recast',)]),
 'REV_826':('none',[('historical_secret_deck','combo',True)]),
 'TRL_530':('none',[('historical_secret_deck','conditional',True)]),
 'TOY_520':('none',[('historical_secret_temporary',ANY,2)]),
 'GIL_116':('none',[('historical_secret_discover',OWN,'place')]),
 'UNG_011':('none',[('historical_secret_discover',OWN,'cast')]),
 'ETC_028':('none',[('historical_secret_solo_discover',OWN)]),
 'YOP_016':('none',[('historical_secret_hand_cast',)]),
 'MAW_032':('none',[]),
 'REV_515':('none',[]),
 'REV_829':('none',[]),
 'BAR_879':('none',[('historical_secret_soldiers',)]),
}
DEATH_EFFECTS={'FP1_004':[('historical_secret_deck','one',False)],
 'GIL_634':[('historical_secret_deck','one',False)],
 'REV_829':[('historical_secret_store_soul',)]}
END_EFFECTS={'EX1_274':[('historical_secret_if_active','buff')],
 'GVG_089':[('historical_secret_if_active','heal')]}
TRIGGERS={
 'DRG_252':('hero_power_used',[('historical_secret_deck','one',True)]),
 'EX1_080':(('historical_event','any_secret_played'),[('buff_self',1,1)]),
 'ICC_204':(('historical_event','secret_played'),[('historical_secret_random',HUNTER,'place')]),
 'BT_188':(('historical_event','secret_played'),[('historical_secret_discover',ANY,'other_hand')]),
 'REV_515':(('historical_event','secret_revealed'),[('historical_secret_random',MAGE,'different_cast'),('buff_self',2,2)]),
}
TOKEN_RULES={'BAR_879t':('none',[])}
# Its Deathrattle is a physical, donor-bound restore operation, not a text lookup.
DEATH_EFFECTS['BAR_879t']=[('historical_secret_soldier_restore',)]
GENERATED_IDS=frozenset(RULES)
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)


def blocked(game):
 return any(m.card_id=='MAW_032' and not m.silenced and m.health>0 and not m.dormant for p in game.players for m in p.minions)


def sequence(game,operations,ctx):
 operations=tuple(operations)
 return game._split_fixed_summon(('replay_context',operations,dict(ctx)),ctx) if operations else (('batch30_noop',),())


def split(game,op,ctx):
 name=op[0];owner=ctx['owner'];p=game.players[owner]
 if name=='historical_secret_sayge':return game._split_fixed_summon(('draw',1+len(getattr(p,'historical_triggered_secrets',()))),ctx)
 if name=='historical_secret_deck':
  mode=op[1]
  if mode=='conditional' and not p.secrets:return ('batch30_noop',),()
  count=2 if mode=='combo' and ctx.get('combo') else 1
  if mode=='each':
   from .identities import canonical_identity
   groups={}
   for value in p.deck:
    if 'SECRET' in game._card_data(value).get('mechanics',()):groups.setdefault(canonical_identity(game._card_data(value),game.cards),[]).append(value)
   values=[game.rng.choice(group) for group in groups.values()];game.rng.shuffle(values)
   return sequence(game,(('historical_secret_take_deck',{'card':value,'cast':op[2]}) for value in values),ctx)
  return sequence(game,(('historical_secret_pick_deck',op[2]),)*count,ctx)
 if name=='historical_secret_pick_deck':
  values=[v for v in p.deck if 'SECRET' in game._card_data(v).get('mechanics',())]
  if not values:return ('batch30_noop',),()
  return split(game,('historical_secret_take_deck',{'card':game.rng.choice(values),'cast':op[1]}),ctx)
 if name=='historical_secret_take_deck':
  value=op[1]['card'];index=next((i for i,v in enumerate(p.deck) if v is value),None)
  if index is None:return ('batch30_noop',),()
  # Failed put-into-play admission keeps the physical card in the deck.
  cid=game._card_data(value)['id']
  if not op[1]['cast'] and not admissible(game,owner,cid):return ('batch30_noop',),()
  value=p.deck.pop(index);card=value if isinstance(value,Card) else Card(game._new_id(),value);game._refresh_auras()
  if op[1]['cast']:return game._cast_spell_split(('cast_physical_spell',card,'random'),ctx)
  return ('historical_secret_place',{'card':card}),()
 if name=='historical_secret_hand_cast':
  values=[c for c in p.hand if 'SECRET' in game._card_data(c).get('mechanics',())]
  if not values:return ('batch30_noop',),()
  card=game.rng.choice(values)
  first,tail=game._cast_spell_split(('cast_zone_spell','hand',card.uid,'random'),ctx)
  return first,tuple(tail)+(('draw',1),)
 if name=='historical_secret_random':
  values=list(game._generation_candidates(op[1],owner))
  if op[2]=='different_cast':
   from .identities import canonical_identity
   previous=ctx['event']['card_id'];identity=canonical_identity(game.cards[previous],game.cards)
   values=[cid for cid in values if canonical_identity(game.cards[cid],game.cards)!=identity]
  if not values:return ('batch30_noop',),()
  cid=game.rng.choice(values)
  if op[2]=='place':return ('historical_secret_place',{'card':Card(game._new_id(),cid)}),()
  return game._cast_spell_split(('cast_fixed_spell',cid,'random'),ctx)
 if name=='historical_secret_recast':
  values=list(getattr(p,'historical_triggered_secrets',()));game.rng.shuffle(values)
  return sequence(game,(('cast_physical_spell',game._copy_card(c,source_owner=owner),'random') for c in values),ctx)
 if name=='historical_secret_temporary':
  game._generation_candidates(op[1],owner);state={'uids':[]}
  operations=(('historical_secret_temporary_cast',op[1],state),)*op[2]+(('historical_secret_schedule_destroy',state),)
  return sequence(game,operations,ctx)
 if name=='historical_secret_temporary_cast':
  values=game._generation_candidates(op[1],owner)
  if not values:return ('batch30_noop',),()
  state=op[2];card=Card(game._new_id(),game.rng.choice(values));state['uids'].append(card.uid)
  return game._cast_spell_split(('cast_physical_spell',card,'random'),ctx)
 if name=='historical_secret_soldiers':
  values=list(p.secrets);p.secrets.clear();operations=[]
  for card in values:
   key=game._new_id();ledger=getattr(game,'_historical_secret_forms',{});ledger[key]=deepcopy(card);game._historical_secret_forms=ledger
   operations.append(('historical_secret_soldier',key))
  return sequence(game,operations,ctx)
 return None


def admissible(game,owner,cid):
 from .identities import canonical_identity
 p=game.players[owner];identity=canonical_identity(game.cards[cid],game.cards)
 return len(p.secrets)+game._quest_slots(owner)<5 and all(canonical_identity(game._card_data(c),game.cards)!=identity for c in p.secrets)


def execute(game,op,ctx):
 name=op[0]
 if not name.startswith('historical_secret_'):return False
 owner=ctx['owner'];p=game.players[owner];source=ctx.get('source')
 if name=='historical_secret_place':
  card=op[1]['card'];game._place_secret(owner,card.card_id,physical=card)
 elif name=='historical_secret_copy_enemy':
  for secret in tuple(game.players[1-owner].secrets):
   card=game._copy_card(secret,source_owner=1-owner);game._place_secret(owner,card.card_id,physical=card)
 elif name=='historical_secret_steal':
  values=list(game.players[1-owner].secrets)
  if values:
   card=game.rng.choice(values)
   if admissible(game,owner,card.card_id):game.players[1-owner].secrets.remove(card);game._place_secret(owner,card.card_id,physical=card)
 elif name=='historical_secret_if_active':
  if p.secrets:game._effect(('buff_self',2,2) if op[1]=='buff' else ('heal_own_hero',4),ctx)
 elif name in ('historical_secret_discover','historical_secret_solo_discover'):
  if name=='historical_secret_solo_discover' and any(m is not source for m in p.minions):return True
  values=list(game._generation_discover_candidates(op[1],ctx));mode=op[2] if len(op)>2 else 'cast'
  if mode=='other_hand':
   previous=game.cards[ctx['event']['card_id']];classes=set(previous.get('classes',()))|{previous.get('cardClass')}
   values=[cid for cid in values if not any(has_class(game.cards[cid],c) for c in classes if c)]
  if values:
   game.pending_choice=dict(owner=owner,kind='historical_secret_discover',mode=mode,options=[dict(card_id=cid) for cid in game.rng.sample(values,min(3,len(values)))])
   game.phase='choice'
 elif name=='historical_secret_schedule_destroy':game._schedule_turn_effect(owner,'start',1,1,(('historical_secret_destroy_instances',tuple(op[1]['uids'])),),source_card_id='TOY_520')
 elif name=='historical_secret_destroy_instances':
  # Track instances, even if control changed; replacement Secrets are untouched.
  for player in game.players:player.secrets[:]=[c for c in player.secrets if c.uid not in op[1]]
 elif name=='historical_secret_store_soul':
  if p.secrets:
   state=game._b60_state(game.rng.choice(p.secrets));state['historical_halkias_souls']=state.get('historical_halkias_souls',0)+1
 elif name=='historical_secret_soldier':
  m=game._summon(owner,'BAR_879t',entry_origin='transform',entry_site='cannonmaster_smythe')
  if m is not None:m.rule_state['historical_secret_form_key']=op[1]
 elif name=='historical_secret_soldier_restore':
  key=getattr(source,'rule_state',{}).get('historical_secret_form_key');card=getattr(game,'_historical_secret_forms',{}).get(key)
  if card is not None:
   card=game._copy_card(card,source_owner=owner);game._place_secret(owner,card.card_id,physical=card)
 else:return False
 return True


def resolve_choice(game,choice,selected):
 if choice['kind']!='historical_secret_discover':return False
 owner=choice['owner'];cid=selected['card_id']
 if choice['mode']=='other_hand':game._add(owner,cid)
 elif choice['mode']=='place':game._place_secret(owner,cid)
 else:game._rule_events.append(('captured_effects',dict(operations=(('cast_fixed_spell',cid,'random'),),context=dict(owner=owner,source=None,target=0,bonus=0,lifesteal=False)),[]))
 return True
