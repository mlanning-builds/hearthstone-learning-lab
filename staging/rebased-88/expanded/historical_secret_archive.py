"""Historical Secret outcomes; authored rules, behavioral validation deferred."""
from copy import deepcopy
from .historical_saidan import add as add_stat

SECRETS={
 'AT_060':'bear_trap','AT_073':'competitive_spirit',
 'BAR_550':'galloping_savior','BOT_908':'autodefense_matrix',
 'BT_203':'pack_tactics','BT_707':'ambush','BT_709':'dirty_tricks',
 'CFM_026':'hidden_cache','DMF_123':'open_cages','DMF_513':'shadow_clone',
 'EX1_379':'repentance','EX1_554':'snake_trap','EX1_609':'snipe',
 'WON_018':'snipe','GIL_903':'hidden_wisdom','ICC_200':'venomstrike_trap',
 'LOE_027':'sacred_trial','WC_033':'judgment_justice',
}
SECRETS.update({'CFM_800':'getaway_kodo','LOOT_204':'cheat_death','EX1_136':'redemption','FP1_020':'avenge','EX1_132':'eye_for_eye','LOOT_214':'evasion','CS3_016':'reckoning','LOE_021':'dart_trap','SCH_706':'plagiarize'})
SECRETS.update({'AV_226':'ice_trap','DAL_570':'never_surrender','BT_042':'bamboozle','EX1_130':'noble_sacrifice','LOOT_210':'sudden_betrayal'})
SECRETS['YOP_017']='shenanigans'
SECRETS['DMF_236']='oh_my_yogg'
TOKEN_RULES={cid:('none',[('secret',cid)]) for cid in SECRETS}
# Native keywords encode the entire behavior of these generated bodies.
TOKEN_RULES.update({cid:('none',[]) for cid in ('BAR_550t','BT_707t','EX1_554t','EX1_130a')})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

def op(name,*args):return ('historical_secret_v2_archive_'+name,)+args

def event_program(game,secret,event,owner,actor,data):
 cid=secret.card_id;p=game.players[owner];q=game.players[actor]
 if cid=='DAL_570' and event=='before_spell' and p.minions:return (('board_buff',0,2),)
 if event=='archive_damage':
  if data.get('amount',0)>0 and data.get('target')==game.hero_id(owner):
   if cid=='EX1_132':return (('damage_enemy_hero',data['amount']),)
   if cid=='LOOT_214':return (op('evasion'),)
  if cid=='CS3_016' and data.get('amount',0)>=3:
   source=game._force_live(data.get('source_uid'))
   if source is not None and source.owner==actor:return (op('destroy',source.uid),)
 if event=='archive_power' and cid=='LOE_021':return (('damage_random_enemy',5),)
 if cid=='BT_709' and event=='after_spell':return (('draw',2),)
 if event=='after_card':
  if q.cards_played==3:
   if cid=='BAR_550' and len(p.board)<7:return (('summon','BAR_550t',1),)
   if cid=='GIL_903':return (('draw',2),)
  if game.cards.get(data.get('card_id'),{}).get('type')=='MINION':
   if cid=='BT_707' and len(p.board)<7:return (('summon','BT_707t',1),)
   if cid=='CFM_026' and any(game._card_data(c)['type']=='MINION' for c in p.hand):return (op('cache'),)
   target=next((m for m in q.minions if m.uid==data.get('source') and m.health>0),None)
   if target is not None:
    if cid in ('EX1_609','WON_018'):return (op('hit',target.uid,6),)
    if cid=='EX1_379':return (op('repent',target.uid),)
    # Count includes the just-played minion and excludes Dormant bodies.
    if cid=='LOE_027' and len(q.minions)>=4:return (op('destroy',target.uid),)
 if event=='attack':
  target=next((m for m in p.minions if m.uid==data.get('target') and m.health>0),None)
  if target is not None:
   if cid=='BOT_908' and 'DIVINE_SHIELD' not in game._effective_keywords(target):return (op('shield',target.uid),)
   if len(p.board)<7:
    if cid=='BT_203':return (op('copy',deepcopy(target),'pack'),)
    if cid=='EX1_554':return (('summon','EX1_554t',3),)
    if cid=='ICC_200':return (('summon','EX1_170',1),)
  if cid=='WC_033':
   attacker=next((m for m in q.minions if m.uid==data.get('source') and m.health>0),None)
   if attacker is not None:return (op('justice',attacker.uid),)
 if event=='after_attack' and data.get('target')==game.hero_id(owner) and len(p.board)<7:
  if cid=='AT_060':return (('summon','CS2_125',1),)
  if cid=='DMF_513' and data.get('source_snapshot') is not None:return (op('copy',deepcopy(data['source_snapshot']),'shadow'),)
 return None

def turn_entries(game,phase):
 if phase=='end':
  owner=1-game.current;p=game.players[owner]
  state=getattr(game.players[game.current],'historical_paid_card_turn',{})
  if state.get('turn')!=game.turn or not state.get('cards'):return []
  return [dict(source=None,order=getattr(s,'_secret_entry_order',s.uid),operations=(op('plagiarize_turn',owner,s.uid,tuple(deepcopy(state['cards']))),)) for s in p.secrets if s.card_id=='SCH_706']
 if phase!='start':return []
 owner=game.current
 return [dict(source=None,order=getattr(s,'_secret_entry_order',s.uid),operations=(op('turn',owner,s.uid),)) for s in game.players[owner].secrets if s.card_id in ('AT_073','DMF_123')]

def execute(game,operation,ctx):
 prefix='historical_secret_v2_archive_'
 if not operation[0].startswith(prefix):return False
 name=operation[0][len(prefix):];owner=ctx['owner'];p=game.players[owner]
 if name=='yogg_replace':
  actor,cost=operation[1:]
  from .generation_cards import pool
  request=pool(card_type='SPELL',minimum=cost,maximum=cost)
  values=game._autocast_candidates(request,actor)
  if values:
   cid=game.rng.choice(list(values))
   context=dict(owner=actor,source=None,target=0,bonus=0,lifesteal=False,card_id='DMF_236')
   game._rule_events.append(('captured_effects',dict(operations=(('cast_fixed_spell',cid,'random'),),context=context),[]))
 elif name=='banana':
  card=operation[1]
  game._b60_transform_card(card,'EX1_014t')
  # A transformed card has Banana's program, never the old taught/on-draw or
  # Deathrattle payload. Ordinary cost enchantments follow the native transform.
  for field in ('attached_death_effects','_crafted_definition','_learned_spell','_historical_resealed_cards','_bound_minion'):
   if hasattr(card,field):delattr(card,field)
  state=getattr(card,'rule_state',{})
  for key in ('crafted_ops','crafted_target','historical_cast_when_drawn','forge_parts'):
   state.pop(key,None)
 elif name=='ice_return':
  card,recipient=operation[1:]
  card.cost_delta=getattr(card,'cost_delta',0)+1
  if not any(c is card for c in game.players[recipient].hand):game._enter_hand(recipient,card)
 elif name=='redirect':
  cid,source,target,state=operation[1:]
  if cid=='EX1_130' and len(p.board)<7:
   body=game._summon(owner,'EX1_130a',entry_origin='secret',entry_site='noble_sacrifice')
   if body is not None:state['target']=body.uid
  elif cid=='LOOT_210':
   candidates=sudden_neighbors(game,source)
   if candidates:state['target']=game.rng.choice(candidates)
  elif cid=='BT_042':
   defender=game._force_live(target)
   if defender is not None:
    from .transformations import evolve_pool
    values=game._generation_created_candidates(evolve_pool(game._card_stat(defender,'cost',defender.owner),3),ctx)
    if values:
     before={m.uid for m in p.minions};old=defender.uid
     result=game._transform(defender,game.rng.choice(values))
     if result is not None:state['target']=result.uid
     elif game._force_live(old) is not None:state['target']=old
     else:
      replacement=next((m for m in p.minions if m.uid not in before),None)
      if replacement is not None:state['target']=replacement.uid
  game._log('attack_redirected',source=source,previous=target,target=state['target'],card=cid)
 elif name=='evasion':p.historical_evasion_immune_turn=game.turn
 elif name=='dispatch':
  event,data=operation[1:]
  if event=='damage':
   for secret_owner in (0,1):game._secret_event('archive_damage',1-secret_owner,**data)
  elif event=='hero_power_used':game._secret_event('archive_power',data['owner'])
 elif name=='death':
  from .historical_secret_batches import blocked
  secret=next((s for s in p.secrets if s.uid==operation[1]),None)
  if secret is None or owner==game.current or blocked(game):return True
  source,position=operation[2:]
  if secret.card_id=='FP1_020':
   if not any(m.health>0 for m in p.minions):return True
   program=(op('avenge'),)
  elif secret.card_id in ('CFM_800','LOOT_204'):program=(op('return',source,-2 if secret.card_id=='LOOT_204' else 0),)
  elif secret.card_id=='EX1_136' and len(p.board)<7:program=(op('redemption',source,position),)
  else:return True
  context=dict(ctx,card_id=secret.card_id,secret_card=secret,bonus=game._spell_damage(owner,secret.card_id))
  game._trigger_secret_program(owner,secret,program,context)
 elif name=='return':
  card=game._fresh_replay_card(operation[1]);game._carry_origin(operation[1],card)
  card.cost_delta=getattr(card,'cost_delta',0)+operation[2];game._enter_hand(owner,card)
 elif name=='redemption':
  if len(p.board)<7:
   source=operation[1];before={m.uid for m in p.minions}
   card=game._fresh_replay_card(source)
   game._summon(owner,source.card_id,min(operation[2],len(p.board)),entry_source=card,entry_zone='hand',entry_origin='resurrection',entry_site='redemption')
   for body in p.minions:
    if body.uid not in before and body.card_id==source.card_id:body.health=1
 elif name=='avenge':
  values=[m for m in p.minions if m.health>0]
  if values:game._buff(game.rng.choice(values),3,2)
 elif name=='plagiarize_turn':
  from .historical_secret_batches import blocked
  owner=operation[1];p=game.players[owner]
  secret=next((s for s in p.secrets if s.uid==operation[2] and s.card_id=='SCH_706'),None)
  if secret is not None and owner!=game.current and not blocked(game):
   context=dict(ctx,owner=owner,source=None,card_id=secret.card_id,secret_card=secret)
   game._trigger_secret_program(owner,secret,(op('plagiarize_cards',operation[3]),),context)
 elif name=='plagiarize_cards':
  for source in operation[1]:
   card=game._fresh_replay_card(source);game._carry_origin(source,card);game._enter_hand(owner,card)
 elif name=='cache':
  cards=[c for c in p.hand if game._card_data(c)['type']=='MINION']
  if cards:
   card=game.rng.choice(cards);add_stat(card,'attack_bonus',2);add_stat(card,'health_bonus',2)
 elif name=='copy':
  source,mode=operation[1:]
  if len(p.board)<7:
   mods=dict(entry_stats=(3,3)) if mode=='pack' else dict(entry_keywords=('STEALTH',))
   game._summon(owner,source.card_id,copy_from=source,entry_origin='secret',entry_site='pack_tactics' if mode=='pack' else 'shadow_clone',**mods)
 elif name=='turn':
  from .historical_secret_batches import blocked
  owner=operation[1];p=game.players[owner]
  secret=next((s for s in p.secrets if s.uid==operation[2]),None)
  if secret is None or owner!=game.current or blocked(game):return True
  if secret.card_id=='AT_073':
   if not p.minions:return True
   program=(('board_buff',1,1),)
  elif secret.card_id=='DMF_123':
   if len(p.minions)<2 or len(p.board)>=7:return True
   from .pools import require_fixed_cards
   require_fixed_cards(('NEW1_032','NEW1_033','NEW1_034'),game.cards)
   program=(op('companion'),)
  else:return True
  context=dict(owner=owner,source=None,target=0,bonus=game._spell_damage(owner,secret.card_id),lifesteal=False,card_id=secret.card_id,secret_card=secret)
  game._trigger_secret_program(owner,secret,program,context)
 elif name=='companion':
  if len(p.board)<7:game._summon(owner,game.rng.choice(('NEW1_032','NEW1_033','NEW1_034')),entry_origin='secret',entry_site='open_cages')
 elif name in ('hit','destroy','repent','justice','shield'):
  target=game._force_live(operation[1])
  if target is None:return True
  if name=='hit':game._deal_effect(target.uid,operation[2],ctx)
  elif name=='destroy':target.health=0
  elif name=='repent':target.health=target.max_health=1;game._refresh_auras()
  elif name=='justice':game._set_entity_stats(target,1,1);game._refresh_auras()
  else:target.keywords.add('DIVINE_SHIELD')
 else:return False
 return True


def event(game,kind,data):
 if kind not in ('damage','hero_power_used'):return
 if kind=='damage' and data.get('amount',0)<=0:return
 if not any(s.card_id in ('EX1_132','LOOT_214','CS3_016','LOE_021') for p in game.players for s in p.secrets):return
 game._rule_events.append(('captured_effects',dict(operations=(op('dispatch',kind,dict(data)),),context=dict(owner=game.current,source=None,target=0,bonus=0,lifesteal=False)),[]))


def sudden_neighbors(game,source):
 attacker=game._force_live(source)
 if attacker is None:return ()
 p=game.players[attacker.owner];board=p.board;index=board.index(attacker)
 return tuple(board[i].uid for i in (index-1,index+1) if 0<=i<len(board) and board[i] in p.minions and board[i].health>0 and 'IMMUNE' not in game._effective_keywords(board[i]))

def redirect(game,owner,source,target,secret):
 cid=secret.card_id
 if cid not in ('BT_042','EX1_130','LOOT_210') or game.current==owner:return False,target
 from .historical_secret_batches import blocked
 if blocked(game):return False,target
 p=game.players[owner]
 if cid=='EX1_130':
  if len(p.board)>=7:return False,target
  from .pools import require_fixed_cards
  require_fixed_cards(('EX1_130a',),game.cards)
 elif cid=='LOOT_210':
  if target!=game.hero_id(owner) or not sudden_neighbors(game,source):return False,target
 else:
  defender=next((m for m in p.minions if m.uid==target and m.health>0),None)
  if defender is None:return False,target
  from .transformations import evolve_pool
  values=game._generation_candidates(evolve_pool(game._card_stat(defender,'cost',owner),3),owner)
  if not values:return False,target
 state=dict(target=target)
 context=dict(owner=owner,source=None,target=0,bonus=0,lifesteal=False,card_id=cid,secret_card=secret)
 game._trigger_secret_program(owner,secret,(op('redirect',cid,source,target,state),),context)
 game._settle(allow_event_choices=True)
 return True,state['target']


def before_receive_draw(game,owner,card,private=False):
 """Successful second draws transform before Casts When Drawn admission.

 The existing card_drawn tag counts intrinsic casts and replacement draws;
 overdraw and private starting-hand moves never enter this Secret window.
 """
 if private:return
 secret_owner=1-owner
 if game.current==secret_owner:return
 state=getattr(game.players[owner],'historical_draw_turn',{})
 ordinal=(state.get('count',0) if state.get('turn')==game.turn else 0)+1
 if ordinal!=2:return
 from .historical_secret_batches import blocked
 if blocked(game):return
 secret=next((s for s in game.players[secret_owner].secrets if s.card_id=='YOP_017'),None)
 if secret is None:return
 from .pools import require_fixed_cards
 require_fixed_cards(('EX1_014t',),game.cards)
 context=dict(owner=secret_owner,source=None,target=0,bonus=0,lifesteal=False,card_id=secret.card_id,secret_card=secret)
 game._trigger_secret_program(secret_owner,secret,(op('banana',card),),context)
