"""Additional native Secret event programs; fidelity review deferred."""
from .generation_cards import pool,board_pool
SECRETS={
 'UNG_024':'mana_bind',
 'LOOT_079':'wandering_monster','CORE_LOOT_079':'wandering_monster','EX1_533':'misdirection','VAN_EX1_533':'misdirection',
 'EX1_295':'ice_block','VAN_EX1_295':'ice_block',
 'KAR_004':'cat_trick','CORE_KAR_004':'cat_trick',
 'JAM_003':'hidden_meaning','MAW_006':'objection','MAW_010':'motion_denied',
 'MIS_105':'bait_switch','REV_827':'sticky_situation','TTN_504':'bait_arrow',
 'DEEP_000':'summoning_ward','MAW_018':'perjury','REV_825':'double_cross',
}
SECRETS.update({'AT_002':'effigy','FP1_018':'duplicate','tt_010':'spellbender'})
SECRETS.update({'BT_003':'netherwind_portal','DMF_107':'rigged_faire_game','EX1_294':'mirror_entity','EX1_594':'vaporize','ICC_082':'frozen_clone','TRL_400':'splitting_image','ULD_239':'flame_ward'})
PROGRAMS={
 'motion':(('damage_enemy_hero',6),),'sticky':(('summon','REV_827t',1),),
 'cross':(('draw',2),),'hidden':(('historical_secret_v2_random_three',),),
 'ward':(('historical_secret_v2_highest_copy',),),
 'perjury':(('historical_secret_discover',pool(card_type='SPELL',mechanic='SECRET',classes='other'),'cast'),),
}
TOKEN_RULES={cid:('none',[('secret',cid)]) for cid in SECRETS}
TOKEN_RULES['REV_827t']=('none',[])
TOKEN_RULES['tt_010a']=('none',[])
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)


def event_program(game,secret,event,owner,actor,data):
 from .historical_secret_archive import event_program as archive_program
 result=archive_program(game,secret,event,owner,actor,data)
 if result is not None:return result
 cid=secret.card_id;p=game.players[owner];q=game.players[actor]
 if cid in ('EX1_294','ICC_082') and event=='after_card':
  target=next((m for m in q.minions if m.uid==data.get('source') and m.health>0 and not m.dormant),None)
  if target is not None and (cid=='ICC_082' or len(p.board)<7):
   from copy import deepcopy
   if cid=='ICC_082':return (('historical_copy_target_snapshot',deepcopy(target),'hand',2,None,None,None,False),)
   return (('historical_secret_v2_mirror',deepcopy(target)),)
 if cid=='BT_003' and event=='after_spell' and len(p.board)<7:
  request=board_pool(pool(card_type='MINION',minimum=4,maximum=4))
  game._generation_created_candidates(request,dict(owner=owner))
  return (('historical_secret_v2_portal',),)
 if cid=='TRL_400' and event=='attack' and len(p.board)<7:
  target=next((m for m in p.minions if m.uid==data.get('target') and m.health>0),None)
  if target is not None:
   from copy import deepcopy
   return (('historical_secret_v2_mirror',deepcopy(target)),)
 if cid=='EX1_594' and event=='attack' and data.get('target')==game.hero_id(owner):
  target=next((m for m in q.minions if m.uid==data.get('source') and m.health>0),None)
  if target is not None:return (('historical_secret_v2_vaporize',target.uid),)
 if cid=='ULD_239' and event=='after_attack' and data.get('source_snapshot') is not None and data.get('target')==game.hero_id(owner):return (('area_damage','enemy_minions',3),)
 if cid=='UNG_024' and event=='before_spell' and data.get('physical_card') is not None:
  from copy import deepcopy
  return (('historical_ungoro_mana_bind',deepcopy(data['physical_card'])),)
 if cid in ('KAR_004','CORE_KAR_004') and event=='after_spell' and len(p.board)<7:return (('summon','KAR_004a',1),)
 if cid=='MAW_010' and event=='after_card' and q.cards_played==3:return PROGRAMS['motion']
 if cid=='MIS_105' and event=='after_card':
  kind=game.cards.get(data.get('card_id'),{}).get('type')
  if kind in ('MINION','SPELL','WEAPON'):
   return tuple(('filtered_draw',(('type','eq',other),),1) for other in ('MINION','SPELL','WEAPON') if other!=kind)
 if cid=='REV_827' and event=='after_spell' and len(p.board)<7:return PROGRAMS['sticky']
 if cid=='REV_825' and event=='spent_all' and data.get('amount',0)>0 and q.mana==0:return PROGRAMS['cross']
 if cid=='TTN_504' and event=='attack':
  target=next((m for m in p.minions if m.uid==data.get('target') and m.health>0),None)
  if target is not None:return (('historical_secret_v2_buff_uid',target.uid),)
 return None


def turn_entries(game,phase):
 from .historical_secret_archive import turn_entries as archive_entries
 entries=archive_entries(game,phase)
 for owner in (game.current,1-game.current):
  for secret in game.players[owner].secrets:
   due=(phase=='start' and owner==game.current and secret.card_id in ('DEEP_000','MAW_018') or phase=='end' and owner!=game.current and secret.card_id in ('JAM_003','DMF_107'))
   if due:entries.append(dict(source=None,order=getattr(secret,'_secret_entry_order',secret.uid),operations=(('historical_secret_v2_turn',owner,secret.uid),)))
 return entries


def execute(game,op,ctx):
 from .historical_secret_archive import execute as archive_execute
 if archive_execute(game,op,ctx):return True
 owner=ctx['owner'];p=game.players[owner];name=op[0]
 if name=='historical_secret_v2_bender_summon':
  body=game._summon(owner,'tt_010a',entry_origin='secret',entry_site='spellbender')
  if body is not None:op[1]['target']=body.uid
 elif name=='historical_secret_v2_death':
  from .historical_secret_batches import blocked
  secret=next((s for s in p.secrets if s.uid==op[1]),None)
  if secret is None or owner==game.current or blocked(game):return True
  context=dict(ctx,secret_card=secret,card_id=secret.card_id,bonus=game._spell_damage(owner,secret.card_id))
  if secret.card_id=='FP1_018':program=(('historical_copy_target_snapshot',op[2],'hand',2,None,None,None,False),)
  elif secret.card_id=='AT_002' and len(p.board)<7:
   request=board_pool(pool(card_type='MINION',minimum=op[3],maximum=op[3]))
   game._generation_created_candidates(request,context)
   program=(('historical_secret_v2_effigy',op[3]),)
  else:return True
  game._trigger_secret_program(owner,secret,program,context)
 elif name=='historical_secret_v2_effigy':
  if len(p.board)<7:
   values=game._generation_created_candidates(board_pool(pool(card_type='MINION',minimum=op[1],maximum=op[1])),ctx)
   if values:game._summon(owner,game.rng.choice(values),entry_origin='secret',entry_site='effigy')
 elif name=='historical_secret_v2_mirror':
  target=op[1]
  if len(p.board)<7:game._summon(owner,target.card_id,copy_from=target,entry_origin='secret',entry_site='mirror_entity')
 elif name=='historical_secret_v2_vaporize':
  target=game._force_live(op[1])
  if target is not None:target.health=0
 elif name=='historical_secret_v2_portal':
  values=game._generation_created_candidates(board_pool(pool(card_type='MINION',minimum=4,maximum=4)),ctx)
  if values and len(p.board)<7:game._summon(owner,game.rng.choice(values),entry_origin='secret',entry_site='netherwind_portal')
 elif name=='historical_secret_v2_buff_uid':
  target=next((m for m in p.minions if m.uid==op[1] and m.health>0),None)
  if target is not None:game._buff(target,3,3)
 elif name=='historical_secret_v2_random_three':
  values=game._generation_created_candidates(board_pool(pool(card_type='MINION',minimum=3,maximum=3)),ctx)
  if values:game._summon(owner,game.rng.choice(values),entry_origin='secret',entry_site='hidden_meaning')
 elif name=='historical_secret_v2_highest_copy':
  targets=[m for m in p.minions if m.health>0]
  if targets:
   cost=max(game._card_stat(m,'cost',owner) for m in targets)
   target=game.rng.choice([m for m in targets if game._card_stat(m,'cost',owner)==cost])
   game._summon(owner,target.card_id,copy_from=target,entry_origin='secret',entry_site='summoning_ward')
 elif name=='historical_secret_v2_turn':
  owner=op[1];p=game.players[owner]
  from .historical_secret_batches import blocked
  if blocked(game):return True
  secret=next((secret for secret in p.secrets if secret.uid==op[2]),None)
  if secret is None:return True
  context=dict(owner=owner,source=None,target=0,card_id=secret.card_id,secret_card=secret,bonus=game._spell_damage(owner,secret.card_id),lifesteal=False)
  if secret.card_id=='DMF_107':
   damage=getattr(p,'historical_opponent_turn_damage',{})
   if damage.get('turn')==game.turn and damage.get('amount',0)>0:return True
   if owner==game.current:return True
   operations=(('draw',3),)
  elif secret.card_id=='DEEP_000':
   if not p.minions or len(p.board)>=7:return True
   operations=PROGRAMS['ward']
  elif secret.card_id=='JAM_003':
   if game.players[game.current].mana!=0 or len(p.board)>=7:return True
   game._generation_created_candidates(board_pool(pool(card_type='MINION',minimum=3,maximum=3)),context)
   operations=PROGRAMS['hidden']
  elif secret.card_id=='MAW_018':
   request=pool(card_type='SPELL',mechanic='SECRET',classes='other')
   game._generation_discover_candidates(request,context)
   operations=PROGRAMS['perjury']
  else:return True
  game._trigger_secret_program(owner,secret,operations,context)
 else:return False
 return True


def redirect_spellbender(game,actor,target):
 """Only player-selected spells reach this hook, after counter resolution."""
 from .historical_secret_batches import blocked
 owner=1-actor;p=game.players[owner]
 if target<=0 or game.current==owner or blocked(game) or len(p.board)>=7 or game._force_live(target) is None:return target
 secret=next((s for s in p.secrets if s.card_id=='tt_010'),None)
 if secret is None:return target
 from .pools import require_fixed_cards
 require_fixed_cards(('tt_010a',),game.cards)
 state={}
 context=dict(owner=owner,source=None,target=0,bonus=0,lifesteal=False,card_id=secret.card_id,secret_card=secret)
 game._trigger_secret_program(owner,secret,(('historical_secret_v2_bender_summon',state),),context)
 game._settle(allow_event_choices=True)
 return state.get('target',target)

from .historical_secret_archive import SECRETS as ARCHIVE_SECRETS,TOKEN_RULES as ARCHIVE_RULES
SECRETS.update(ARCHIVE_SECRETS)
TOKEN_RULES.update(ARCHIVE_RULES)
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)
