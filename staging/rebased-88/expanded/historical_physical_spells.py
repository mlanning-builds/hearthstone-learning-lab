"""Physical-zone spell choices and captured draw/history offers; unvalidated."""
from copy import deepcopy
from engine.game import Card
from engine.cards import UnsupportedCard
from .pools import deck_choice_options
from .selectors import has_tribe,has_class
from .identities import canonical_identity
TOKEN_RULES={
 'ETC_074':('none',[('historical_physical_mixtape',)]),
 'ETC_205':('none',[('historical_physical_draw_three',True)]),
 'REV_253':('none',[('historical_physical_offer','enemy_hand'),('historical_physical_offer','enemy_deck')]),
 'REV_507':('none',[('hero_attack',3),('historical_physical_offer','dispose')]),
 'REV_948':('none',[('historical_physical_offer','bell')]),
 'RLK_533':('none',[('historical_physical_draw_three',False)]),
 'WW_092':('none',[('historical_physical_offer','fracking')]),
 'NX2_015':('none',[('historical_physical_offer','companions')]),
 'REV_311':('none',[]),
 'REV_311t':('none',[('historical_physical_offer','bud_spell')]),
 'REV_311t2':('none',[('historical_physical_offer','bud_minion')]),
 'MAW_002':('none',[('historical_physical_offer','corpses')]),
}
CHOICES={'REV_311':[
 ('Awaken the Ancient','none',[('historical_physical_offer','bud_minion')]),
 ('Empower the Spell','none',[('historical_physical_offer','bud_spell')]),
]}
TOKEN_RULES['MIS_102']=('none',[('historical_physical_return_policy',)])
TOKEN_RULES.update({'TOY_879':('none',[('historical_physical_repackage',)]),'TOY_879t':('none',[('historical_physical_box',)])})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)


def split(game,op,ctx):
 owner=ctx['owner'];p=game.players[owner];name=op[0]
 if name=='historical_physical_box':
  card=ctx.get('physical_card')
  if card is None or not hasattr(card,'_historical_resealed_cards'):raise UnsupportedCard('Repackaged Box requires captured physical contents')
  operations=tuple(('historical_physical_box_add',game._fresh_replay_card(c)) for c in card._historical_resealed_cards)
  return (operations[0],operations[1:]) if operations else (('batch30_noop',),())
 if name=='historical_physical_policy_trigger':
  card=op[1];data=game._card_data(card)
  context=dict(ctx,card_id=card.card_id,physical_card=card,death_position=len(p.board),target=0,spell=False,bonus=0,lifesteal=False)
  if data['type']=='MINION':
   from .historical_devout import base_source
   source,definition=base_source(game,owner,card);context.update(source=source,physical_card=definition)
   operations=game._death_operations(source)
  elif data['type']=='WEAPON':
   weapon=dict(card_id=card.card_id,attack=game._card_stat(card,'attack',owner),durability=game._card_stat(card,'health',owner))
   context.update(source=None,broken_weapon=weapon,broken_weapon_card=card)
   operations=game._printed_death_operations(card.card_id)
  else:raise UnsupportedCard('Return Policy selected unsupported Deathrattle card type: '+data['type'])
  if not operations:return ('batch30_noop',),()
  return game._split_fixed_summon(('replay_context',tuple(operations),context),ctx)
 if name=='historical_physical_draw_three':
  states=tuple({} for _ in range(3));filters=(('type','eq','SPELL'),) if op[1] else None
  operations=tuple(('historical_draw_capture',filters,'random',state) for state in states)+(('historical_physical_draw_offer',op[1],states),)
  return operations[0],operations[1:]
 if name=='historical_physical_bell_draw':
  operations=tuple(('historical_physical_draw_uid',card.uid) for card in p.deck if canonical_identity(game._card_data(card),game.cards)==op[1])
  return (operations[0],operations[1:]) if operations else (('batch30_noop',),())
 if name=='historical_physical_companion_copy':
  minion=op[1].get('minion')
  return (('historical_physical_copy_summon',minion),()) if minion is not None and op[1].get('double') else (('batch30_noop',),())
 return None


def offer(game,ctx,mode,cards,*,zone=None,recipient=None,discovering=True,all_options=False):
 if game.pending_choice is not None:raise UnsupportedCard('Cannot overwrite physical spell choice')
 if all_options:options=[dict(card_id=game._card_data(card)['id'],index=i) for i,card in enumerate(cards)]
 else:options=deck_choice_options(cards,game.cards,3,game.rng)
 for option in options:
  card=cards[option['index']];option.update(uid=card.uid,snapshot=deepcopy(card))
 if options:
  game.pending_choice=dict(owner=ctx['owner'],kind='historical_physical_spell',mode=mode,context=dict(ctx),options=options,zone=zone,recipient=ctx['owner'] if recipient is None else recipient,discovering=discovering)
  game.phase='choice'


def execute(game,op,ctx):
 owner=ctx['owner'];p=game.players[owner];name=op[0]
 if name=='historical_physical_repackage':
  box=Card(game._new_id(),'TOY_879t');captured=[m for player in game.players for m in tuple(player.all_minions)]
  box._historical_resealed_cards=tuple(game._fresh_replay_card(m) for m in captured)
  for minion in captured:
   game.players[minion.owner].board.remove(minion);game._log('remove_minion',player=minion.owner,entity=minion.uid,card=minion.card_id)
  game._refresh_auras();recipient=1-owner;game.players[recipient].deck.append(box);game.rng.shuffle(game.players[recipient].deck)
  game._record_deck_insertion(recipient,owner,1,'shuffle',cards=(box,))
 elif name=='historical_physical_box_add':game._enter_hand(owner,op[1])
 elif name=='historical_physical_return_policy':
  cards=[record.card for record in tuple(p.replay_history) if 'DEATHRATTLE' in game._card_mechanics(record.card)]
  offer(game,ctx,'return_policy',cards)
 elif name=='historical_physical_mixtape':
  ids=sorted({r['card_id'] for r in getattr(game.players[1-owner],'_historical_paid_card_records',())})
  offer(game,ctx,'copy',[Card(game._new_id(),cid) for cid in ids],recipient=1-owner)
 elif name=='historical_physical_draw_offer':
  volume=op[1]
  if volume and not ctx.get('finale'):return True
  cards=[state['card'] for state in op[2] if state.get('card') is not None]
  if not volume:cards=[card for card in cards if any(card is held for held in p.hand)]
  offer(game,ctx,'copy' if volume else 'discard',cards,zone=None if volume else 'hand',discovering=volume,all_options=not volume)
 elif name=='historical_physical_offer':
  mode=op[1];recipient=1-owner if mode in ('enemy_hand','enemy_deck') else owner;player=game.players[recipient]
  if mode=='corpses':
   offer(game,ctx,mode,[record['entity'] for record in player.death_records]);return True
  zone='hand' if mode in ('enemy_hand','dispose') else 'deck';cards=list(getattr(player,zone))
  if mode=='bell':cards=[card for card in cards if not has_class(game._card_data(card),'NEUTRAL')]
  elif mode=='companions':cards=[card for card in cards if game._card_data(card)['type']=='MINION' and has_tribe(game._card_data(card),'BEAST')]
  elif mode.startswith('bud_'):cards=[card for card in cards if game._card_data(card)['type']==('SPELL' if mode=='bud_spell' else 'MINION')]
  elif mode=='fracking':cards=cards[:3]
  elif mode=='dispose':cards=game.rng.sample(cards,min(3,len(cards)))
  if mode=='bud_spell':
   missing=[card.card_id for card in cards if not game._supports_internal_spell(card.card_id,owner)]
   if missing:raise UnsupportedCard('Nightshade Bud deck has unsupported internal spells: '+', '.join(missing))
  offer(game,ctx,mode,cards,zone=zone,recipient=recipient,discovering=mode not in ('dispose','fracking'),all_options=mode in ('dispose','fracking'))
 elif name=='historical_physical_draw_uid':
  index=next((i for i,card in enumerate(p.deck) if card.uid==op[1]),None)
  if index is not None:game._take_deck_draw(owner,index,include_burned=True)
 elif name=='historical_physical_destroy_uid':
  card=next((card for card in p.deck if card.uid==op[1]),None)
  if card is not None:p.deck.remove(card);game._zone_card_removed(owner,card,'deck','destroy');game._refresh_auras()
 elif name=='historical_physical_recruit':
  card=next((card for card in p.deck if card.uid==op[1]),None)
  if card is not None and len(p.board)<7:
   p.deck.remove(card);minion=game._summon(owner,card.card_id,attack_bonus=card.attack_bonus,health_bonus=card.health_bonus,entry_source=card,entry_zone='deck',entry_origin='recruit',entry_site='physical_spell_choice')
   op[2]['minion']=deepcopy(minion);game._refresh_auras()
 elif name=='historical_physical_copy_summon':
  minion=op[1];game._summon(owner,minion.card_id,copy_from=minion,entry_origin='copy',entry_site='faithful_companions')
 elif name=='historical_physical_resurrect':
  card=game._fresh_replay_card(op[1]);game._summon(owner,card.card_id,entry_source=card,entry_zone='deck',entry_origin='resurrection',entry_keywords=('RUSH',),expires=True,entry_site='habeas_corpses')
 else:return False
 return True


def resolve_choice(game,choice,selected):
 if choice['kind']!='historical_physical_spell':return False
 owner=choice['owner'];p=game.players[owner];ctx=choice['context'];mode=choice['mode'];operations=()
 if mode=='return_policy':
  card=game._fresh_replay_card(selected['snapshot']);game._discovery_result=game._enter_hand(owner,card)
  operations=(('historical_physical_policy_trigger',game._fresh_replay_card(selected['snapshot'])),)
 elif mode=='corpses':operations=(('historical_physical_resurrect',selected['snapshot']),)
 elif mode=='copy' or mode in ('enemy_hand','enemy_deck'):
  card=game._copy_card(selected['snapshot'],source_owner=choice['recipient']);game._discovery_result=game._enter_hand(owner,card)
 else:
  values=getattr(game.players[choice['recipient']],choice['zone']);card=next((card for card in values if card.uid==selected['uid']),None)
  if card is None:return True
  if mode=='discard':game._discard_cards(owner,[card])
  elif mode=='dispose':game._shuffle_hand_card(owner,card)
  elif mode=='bell':
   identity=canonical_identity(game._card_data(card),game.cards)
   game._discovery_result=game._take_deck_draw(owner,p.deck.index(card),include_burned=True)
   operations=tuple(('historical_physical_draw_uid',other.uid) for other in p.deck if canonical_identity(game._card_data(other),game.cards)==identity)
  elif mode=='fracking':operations=(('historical_physical_draw_uid',card.uid),)+tuple(('historical_physical_destroy_uid',option['uid']) for option in choice['options'] if option is not selected)
  elif mode=='bud_spell':operations=(('cast_zone_spell','deck',card.uid,'random'),)
  elif mode in ('companions','bud_minion'):
   state=dict(double=mode=='companions' and p.max_mana>=10)
   operations=(('historical_physical_recruit',card.uid,state),('historical_physical_companion_copy',state))
 if operations:game._rule_events.append(('captured_effects',dict(operations=operations,context=dict(ctx)),[]))
 return True
