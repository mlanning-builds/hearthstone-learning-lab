"""Historical Finale, Outcast and physical Trade recipes; unvalidated."""
from .historical_saidan import add as _saidan_add
from copy import deepcopy
from engine.game import Card
from .generation_cards import pool,random_cards,discover
from .selectors import has_tribe


def finale(*operations):return ('historical_play_finale',tuple(operations))

RULES={
 'DEEP_029':('none',[finale(('historical_play_mana_shots',))]),
 'ETC_088':('none',[discover(pool(card_type='SPELL',classes='own_or_neutral'))]),
 'ETC_099':('enemy_minion',[finale(('destroy',))]),
 'ETC_209':('character',[('historical_play_finale_damage',2)]),
 'ETC_325':('none',[finale(('keyword_self','LIFESTEAL'))]),
 'ETC_376':('none',[('historical_play_big_draw',)]*2),
 'ETC_541':('none',[('historical_play_copy_enemy_deck',)]),
 'ETC_542':('none',[finale(('force_enemies_into_source',))]),
 'ETC_543':('none',[finale(('historic_board_keyword','adjacent','DIVINE_SHIELD','permanent'))]),
 'ETC_831':('none',[finale(('historical_play_next_beast',))]),
 'JAM_024':('none',[finale(('buff_random_other',2,2))]),
 'JAM_034':('none',[('opponent_next_turn_cost','SPELL',2)]),
 'BT_814':('none',[('outcast_operation',('temporary_keyword_self','IMMUNE','end'))]),
 'LEG_CS3_017':('none',[('outcast_operation',('hero_attack',3))]),
 'JAM_020':('minion',[('outcast_operation',('bounce',))]),
 'RLK_207':('none',[('outcast_operation',('next_discount','OUTCAST',1,'game'))]),
 'RLK_210':('none',[]),'CS3_019':('none',[]),
 'RLK_215':('none',[('historical_play_outcast_edges',)]),
 'SCH_705':('none',[('outcast_operation',('summon','SCH_705t',2))]),
 'TSC_217':('none',[('outcast_operation',('historical_play_discount_edges',1))]),
 'GDB_116':('none',[('outcast_operation',('historical_play_shuffle_hand',))]),
 'SW_042':('none',[]),'SW_055':('none',[]),
 'TOY_509':('none',[('historical_play_windup','damage')]),
 'TOY_802':('none',[('historical_play_windup','refresh')]),
 'TOY_880':('none',[('historical_play_windup','copies')]),
 'RLK_222':('historical_play_manathirst',[('add','RLK_222t1',1)]),
}
TOKEN_RULES={
 'SCH_705t':('none',[]),
 'RLK_222t1':('none',[('add','RLK_222t2',1)]),
 'RLK_222t2':('none',[('historical_play_astalor_shots',)]),
}
DEATH_EFFECTS={'SW_042':[('historical_play_recruit_self',)]}
TRIGGERS={
 'RLK_210':(('historical_event','outcast_card_played'),[random_cards(pool(mechanic='OUTCAST'))]),
 'CS3_019':(('historical_event','outcast_card_played'),[('historic_bounce_source',)]),
}
# These keyword effects are not duplicated with their separate Battlecry.
SINGLE_PLAY_EFFECTS={
 'WW_360':[('historical_copy_quickdraw_self',)],
 'RLK_222':[('historical_batch_mana_branch',5,(('damage',2),),(('batch30_noop',),))],
 'RLK_222t1':[('historical_batch_mana_branch',8,(('armor',5),),(('batch30_noop',),))],
 'ETC_088':[finale(discover(pool(card_type='SPELL',classes='own_or_neutral')))],
 'ETC_541':[finale(('draw',1))],
}
RULES['BAR_333']=('none',[('outcast_operation',('temporary_keyword_self','IMMUNE','end')),('historical_play_attack_edges',)])
def zone_offer(side,zone,filters,mode,limit=3,discovering=True):
 return ('historical_play_zone_offer',side,zone,tuple(filters),mode,limit,discovering)

RULES.update({
 'AV_308':('none',[zone_offer('own','hand',(('type','eq','SPELL'),('school','eq','FEL')),'copy',0,False)]),
 'DAL_729':('none',[zone_offer('enemy','hand',(),'copy')]),
 'BAR_081':('none',[zone_offer('enemy','deck',(),'copy_draw_other')]),
 'SCH_603':('none',[('outcast_operation',zone_offer('enemy','hand',(),'shuffle',3,False))]),
})
RULES.update({cid:('none',[]) for cid in ('BAR_048','TSC_635','TTN_071','BOT_236','WW_003')})
SCHOOL_DAMAGE={'BAR_048':('NATURE',3),'TSC_635':('FIRE',2)}
TRIGGERS['TSC_635']=(('spell_school_cast','FROST'),[('armor',3)])
SPELL_DAMAGE_VALUES={cid:0 for cid in tuple(SCHOOL_DAMAGE)+('TTN_071',)}
from .historical_infuse_batches import SINGLE_PLAY_EFFECTS as INFUSE_SINGLE_PLAY
SINGLE_PLAY_EFFECTS.update(INFUSE_SINGLE_PLAY)
SI7_IDS=frozenset(('CAP_000','CAP_003','CORE_EX1_134','CORE_EX1_186','EX1_134','EX1_186','ONY_030','SW_411','SW_412','SW_413','SW_417','SW_418','VAN_EX1_134'))
RULES.update({
 'BAR_552':('none',[('historical_if_combo',('historical_play_two_discounts',))]),
 'ETC_073':('none',[('historical_if_combo',('historical_play_combo_history_buff',))]),
 'SW_417':('historical_play_combo_enemy',[('historical_if_combo',('destroy',))]),
 'TSC_933':('historical_play_combo_enemy',[('historical_if_combo',('historical_play_bottom_enemy',))]),
 'ULD_231':('none',[]),
 'WON_079':('none',[('summon_opponent','WON_079t',1),('historical_if_combo',('keyword_self','RUSH'))]),
 'WW_363':('none',[('historical_play_quick_or_combo_coin',)]),
 'GDB_472':('none',[('historical_if_combo',('add','CORE_CS2_072',1))]),
})
TRIGGERS['ULD_231']=(('historical_event','combo_card_played'),[random_cards(pool(mechanic='COMBO'))])
TRIGGERS['WON_079t']=('damaged_self',[('historical_play_gong',)])
TOKEN_RULES.update({'WON_079t':('none',[]),'WON_079t2':('none',[])})
RULES['BT_323']=('none',[zone_offer('own','deck',(),'top',3,False)])
RULES['GDB_443']=('none',[zone_offer('own','deck',(('type','eq','SPELL'),),'draw_discount5')])
RULES.update({
 'BAR_037':('none',[zone_offer('own','deck',(('type','eq','MINION'),('tribe','eq','BEAST')),'wrangler')]),
 'DMF_516':('none',[zone_offer('own','deck',(),'draw_all')]),
 'ULD_236':('none',[zone_offer('own','deck',(('type','eq','SPELL'),),'cast_copy')]),
 'TTN_487':('none',[zone_offer('own','deck',(('type','eq','MINION'),),'tentacle')]),
 'WW_384':('none',[('historical_play_banker',)]),
})
TOKEN_RULES['TTN_487t']=('none',[])
GENERATED_IDS=frozenset(RULES)
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)
WINDUPS=frozenset(('TOY_509','TOY_802','TOY_880'))


def targets(game,cid,owner,mode):
 if mode=='historical_play_combo_enemy':return game._targets_for(cid,owner,'enemy_minion') if game.players[owner].cards_played else [0]
 if mode!='historical_play_manathirst':return None
 return game._targets_for(cid,owner,'character') if game.players[owner].max_mana>=5 else [0]


def physical_targets(game,card,owner,current):
 p=game.players[owner];cost=game._cost(card,owner)
 is_finale=p.mana==(cost if game._payment_kind(card,owner,cost)=='mana' else 0)
 if card.card_id=='ETC_209' and is_finale:return [0]
 if card.card_id=='ETC_099' and not is_finale:return [0]
 if card.card_id=='JAM_020' and (not p.hand or card.uid not in (p.hand[0].uid,p.hand[-1].uid)):return [0]
 return current


def split(game,op,ctx):
 if op[0]=='historical_play_gong':return game._split_fixed_summon(('summon_opponent','WON_079t2',max(0,7-len(game.players[1-ctx['owner']].board))),ctx)
 name=op[0];owner=ctx['owner'];p=game.players[owner]
 if name=='historical_play_attack_edges':
  source=ctx.get('source');minions=game.players[1-owner].minions
  if source is None or not minions:return ('batch30_noop',),()
  operations=(('force_pair',source.uid,minions[0].uid),('force_pair',source.uid,minions[-1].uid))
  first,tail=game._force_split(operations[0],ctx)
  return first,tuple(tail)+(operations[1],)
 if name=='historical_play_finale':
  operations=op[1] if ctx.get('finale') else ()
  if not operations:return ('batch30_noop',),()
  first,tail=game._split_fixed_summon(operations[0],ctx)
  return first,tuple(tail)+tuple(operations[1:])
 if name=='historical_play_mana_shots':return game._split_fixed_summon(('missiles','enemies',p.max_mana),ctx)
 if name=='historical_play_big_draw':
  from .historical_draw_batches import draw,split as split_draw
  return split_draw(game,draw((('cost','ge',6),),'discount' if ctx.get('finale') else 'none',(1,) if ctx.get('finale') else ()),ctx)
 if name=='historical_play_astalor_shots':return game._split_fixed_summon(('missiles','enemies',14 if p.max_mana>=10 else 7),ctx)
 if name=='historical_play_windup' and op[1]=='copies':
  n=1+getattr(ctx.get('physical_card'),'rule_state',{}).get('historical_windup',0)
  return game._split_fixed_summon(('copy_self_right',n),ctx)
 return None


def execute(game,op,ctx):
 name=op[0]
 if not name.startswith('historical_play_'):return False
 owner=ctx['owner'];p=game.players[owner];source=ctx.get('source')
 if name=='historical_play_two_discounts':
  p.cost_effects.append(dict(selector='ALL',amount=2,remaining_uses=2,expires=game.turn))
  return True
 if name=='historical_play_combo_history_buff':
  count=sum('COMBO' in game._card_data(r.card).get('mechanics',()) for r in p.replay_history)
  if source is not None:game._buff(source,count,count)
  return True
 if name=='historical_play_bottom_enemy':
  victim=next((m for m in game.players[1-owner].minions if m.uid==ctx.get('target') and m.health>0),None)
  if victim is not None:
   card=game._fresh_replay_card(victim);game.players[1-owner].board.remove(victim);game.players[1-owner].deck.insert(0,card)
   game._record_deck_insertion(1-owner,owner,1,'bottom',cards=(card,));game._refresh_auras()
  return True
 if name=='historical_play_quick_or_combo_coin':
  card=ctx.get('physical_card')
  if ctx.get('combo') or getattr(card,'_hand_entry_turn',None)==game.turn:game._add(owner,'TOKEN_COIN')
  return True
 if name=='historical_play_banker':
  card=ctx.get('physical_card');side='enemy' if getattr(card,'_hand_entry_turn',None)==game.turn else 'own'
  return execute(game,zone_offer(side,'deck',(('type','eq','SPELL'),),'draw'),ctx)
 if name=='historical_play_draw_uid':
  zone_owner,uid=op[1:];deck=game.players[zone_owner].deck
  index=next((i for i,c in enumerate(deck) if c.uid==uid),None)
  if index is not None:game._take_deck_draw(zone_owner,index,include_burned=True,recipient=owner)
  return True
 if name=='historical_play_zone_offer':
  from engine.cards import UnsupportedCard
  if game.pending_choice is not None:raise UnsupportedCard('Cannot overwrite physical-zone choice')
  side,zone,filters,mode,limit,discovering=op[1:];zone_owner=owner if side=='own' else 1-owner
  values=getattr(game.players[zone_owner],zone)
  indices=[i for i,c in enumerate(values) if game._matches_filter(c,filters,zone_owner=zone_owner)]
  if discovering:
   unique={}
   for i in indices:unique.setdefault(game._card_data(values[i])['id'],i)
   indices=game.rng.sample(list(unique.values()),min(limit,len(unique)))
  elif limit:indices=game.rng.sample(indices,min(limit,len(indices)))
  if indices:
   game.pending_choice=dict(owner=owner,kind='historical_play_zone',zone_owner=zone_owner,zone=zone,mode=mode,discovering=discovering,context=dict(ctx),snapshots=tuple(deepcopy(values[i]) for i in indices),options=[dict(card_id=game._card_data(values[index])['id'],index=index,snapshot=position) for position,index in enumerate(indices)])
   game.phase='choice'
 elif name=='historical_play_finale_damage':game._effect(('area_damage','enemies',op[1]) if ctx.get('finale') else ('damage',op[1]),ctx)
 elif name=='historical_play_copy_enemy_deck':p.deck=[game._copy_card(card,source_owner=1-owner) for card in game.players[1-owner].deck]
 elif name=='historical_play_next_beast':
  effects=getattr(p,'historical_next_beast',[]);effects.append((1,1));p.historical_next_beast=effects
 elif name=='historical_play_outcast_edges':
  values=game._generation_candidates(pool(mechanic='OUTCAST'),owner)
  if values:
   for left in (True,False):
    card=Card(game._new_id(),game.rng.choice(values));card.cost_delta=-2
    result=game._enter_hand(owner,card)
    if result is not None and left:p.hand.remove(card);p.hand.insert(0,card)
 elif name=='historical_play_discount_edges':
  if p.hand:
   for card in (p.hand[0],p.hand[-1]):card.cost_delta-=op[1]
 elif name=='historical_play_shuffle_hand':game.rng.shuffle(p.hand)
 elif name=='historical_play_windup':
  n=1+getattr(ctx.get('physical_card'),'rule_state',{}).get('historical_windup',0)
  if op[1]=='damage':game._effect(('area_damage','enemy_minions',n),ctx)
  elif op[1]=='refresh':game._effect(('refresh_mana',n),ctx)
  else:return False
 elif name=='historical_play_recruit_self':
  indices=[i for i,c in enumerate(p.deck) if game._card_data(c)['id']=='SW_042']
  if indices and len(p.board)<7:
   card=p.deck.pop(game.rng.choice(indices));cid=game._card_data(card)['id']
   game._summon(owner,cid,attack_bonus=getattr(card,'attack_bonus',0),health_bonus=getattr(card,'health_bonus',0),entry_origin='recruit',entry_zone='deck',entry_source=card,entry_site='persistent_peddler')
 else:return False
 return True


def summon_bonus(game,minion):
 p=game.players[minion.owner];effects=getattr(p,'historical_next_beast',())
 if effects and has_tribe(game._card_data(minion),'BEAST'):
  p.historical_next_beast=[];game._buff(minion,sum(e[0] for e in effects),sum(e[1] for e in effects))


def resolve_zone_choice(game,choice,selected):
 if choice['kind']!='historical_play_zone':return False
 owner=choice['owner'];zone_owner=choice['zone_owner'];zone=getattr(game.players[zone_owner],choice['zone']);index=selected['index'];snapshot=choice['snapshots'][selected['snapshot']]
 if choice['mode'] in ('wrangler','draw_all','cast_copy','tentacle'):
  from .identities import canonical_identity
  identity=canonical_identity(game._card_data(snapshot),game.cards)
  def same(card):return canonical_identity(game._card_data(card),game.cards)==identity
  context=choice['context']
  if choice['mode']=='wrangler':
   # Physical copies retain their own enchantments; apply a new permanent buff.
   for player in (game.players[owner],):
    for minion in player.minions:
     if same(minion):game._buff(minion,2,1)
    for card in player.hand+player.deck:
     if same(card):_saidan_add(card,'attack_bonus',2);_saidan_add(card,'health_bonus',1)
   game._rule_events.append(('captured_effects',dict(operations=(('historical_play_draw_uid',zone_owner,snapshot.uid),),context=context),[]))
  elif choice['mode']=='draw_all':
   operations=tuple(('historical_play_draw_uid',zone_owner,card.uid) for card in reversed(zone) if same(card))
   game._rule_events.append(('captured_effects',dict(operations=operations,context=context),[]))
  elif choice['mode']=='cast_copy':
   operations=(('cast_physical_spell',game._copy_card(snapshot,source_owner=zone_owner),'random'),)
   game._rule_events.append(('captured_effects',dict(operations=operations,context=context),[]))
  else:
   attack=game._card_stat(snapshot,'attack',zone_owner);health=game._card_stat(snapshot,'health',zone_owner)
   game._summon(owner,'TTN_487t',attack_bonus=attack-1,health_bonus=health-1,entry_origin='effect',entry_site='loken',entry_source=context.get('source'))
 elif choice['mode'] in ('copy','copy_draw_other'):

  game._discovery_result=game._enter_hand(owner,game._copy_card(snapshot,source_owner=zone_owner))
  if choice['mode']=='copy_draw_other' and 0<=index<len(zone):game._take_deck_draw(zone_owner,index,include_burned=True)
 elif choice['mode']=='draw':game._discovery_result=game._take_deck_draw(zone_owner,index,include_burned=True,recipient=owner)
 elif choice['mode'] in ('top','draw_discount5'):
  actual=next((i for i,card in enumerate(zone) if card.uid==snapshot.uid),None)
  if actual is not None:
   if choice['mode']=='top':zone.append(zone.pop(actual));game._log('deck_top_chosen',player=zone_owner)
   else:
    card=game._take_deck_draw(zone_owner,actual,include_burned=True,recipient=owner);game._discovery_result=card
    if card is not None and any(card is held for held in game.players[owner].hand):card.cost_delta-=5
 elif choice['mode']=='shuffle':
  if 0<=index<len(zone):game._shuffle_hand_card(zone_owner,zone[index],actor=owner)
 else:raise ValueError('Unknown physical choice destination: '+choice['mode'])
 return True


def spell_damage_bonus(game,owner,cid=None):
 school=game.cards.get(cid,{}).get('spellSchool');total=sum(e['amount'] for e in getattr(game.players[owner],'historical_weapon_spell_bonuses',()) if e['turn']==game.turn)
 for minion in game.players[owner].minions:
  if minion.silenced or minion.dormant or minion.health<=0:continue
  if minion.card_id=='TTN_071':total+=1+len(getattr(game.players[owner],'historical_spell_schools',()))
  if school=='FIRE':total+=minion.rule_state.get('historical_fire_spell_damage',0)
  rule=SCHOOL_DAMAGE.get(minion.card_id)
  if rule and rule[0]==school:total+=rule[1]
 return total


def consume_discounts(game,owner,card):
 remaining=[]
 for effect in game.players[owner].cost_effects:
  if not effect.get('consume_on_play',True) or not game._discount_matches(effect,card):remaining.append(effect);continue
  uses=effect.get('remaining_uses',1)-1
  if uses>0:effect['remaining_uses']=uses;remaining.append(effect)
 game.players[owner].cost_effects[:]=remaining

# Quickdraw is separate from Drilly's repeatable Battlecry.
SINGLE_PLAY_EFFECTS['WW_417']=[('historical_copy_quickdraw_operation',('historical_excavate_dig',False))]
