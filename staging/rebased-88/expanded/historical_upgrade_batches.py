"""Explicit Corrupt/Forge/Miniaturize recipes and private continuations.

Implementation-only. No gameplay/regression validation is claimed. Upgrades are
physical card transitions; they do not play the held card or narrow any pool.
"""
from .historical_saidan import add as _saidan_add
from copy import deepcopy
from engine.game import Card
from .generation_cards import pool,random_cards,discover
from .selectors import has_tribe
from .pools import require_fixed_cards

CORRUPT_FORMS={
 'YOP_011':('YOP_011t',0,0),
 'DMF_061':('DMF_061t',0,0),'DMF_073':('DMF_073t',0,0),
 'DMF_078':('DMF_078t',0,0),'DMF_080':('DMF_080t',4,4),
 'DMF_082':('DMF_082t',4,0),'DMF_083':('DMF_083t',0,0),
 'DMF_101':('DMF_101t',0,0),'DMF_118':('DMF_118t',0,0),
 'DMF_124':('DMF_124t',1,1),'DMF_124t':('DMF_124t',1,1),
 'DMF_163':('DMF_163t',0,0),'DMF_174':('DMF_174t',0,0),
 'DMF_184':('DMF_184t',0,4),'DMF_247':('DMF_247t',1,1),
 'DMF_248':('DMF_248t',0,0),'DMF_517':('DMF_517a',2,0),
 'DMF_703':('DMF_703t',0,0),'YOP_025':('YOP_025t',2,2),
}
FORGE_FORMS={
 'DEEP_024':'DEEP_024t','DEEP_027':'DEEP_027t',
 'TTN_039':'TTN_039t','TTN_042':'TTN_042t','TTN_076':'TTN_076t',
 'TTN_457':'TTN_457t','TTN_458':'TTN_458t',
 'TTN_724':'TTN_724t','TTN_724t':'TTN_724t',
 'TTN_730':'TTN_730t','TTN_801':'TTN_801t',
}
MINI_FORMS={
 'TOY_341':('TOY_341t',),
 'TOY_307':('TOY_307t',),'TOY_312':('TOY_312t',),
 'TOY_340':('TOY_340t1',),'TOY_351':('TOY_351t',),
 'TOY_375':('TOY_375t',),'TOY_380':('TOY_380t',),
 'TOY_521':('TOY_521t1',),'TOY_601':('TOY_601t',),
 'TOY_801':('TOY_801t',),'TOY_811':('TOY_811t',),
 'TOY_813':('TOY_813t',),'TOY_828':('TOY_828t',),
 'TOY_915':('TOY_915t',),'MIS_025':('MIS_025t','MIS_025t1'),
}
RULES={cid:('none',[]) for cid in set(CORRUPT_FORMS)|set(FORGE_FORMS)|set(MINI_FORMS)}
# Noncollectible upgraded roots are registered only as playable tokens below.
for cid in ('DMF_124t','TTN_724t'):RULES.pop(cid)
RULES.update({
 'DMF_061':('none',[]),
 'DMF_101':('minion',[('damage',3)]),
 'DMF_118':('none',[('historical_upgrade_remove_top',False,5)]),
 'DMF_163':('none',[('copy_self_right',2)]),
 'DMF_174':('character',[('heal',4)]),
 'DMF_703':('none',[('summon','DMF_703t2',1)]),
 'DEEP_024':('none',[('historical_upgrade_quickdraw_damage',5)]),
 'DEEP_027':('none',[]),
 'TTN_039':('none',[random_cards(pool(card_type='SPELL',school='HOLY'))]),
 'TTN_076':('none',[discover(pool(card_type='SPELL',classes='own_or_neutral'))]),
 'TTN_457':('historical_upgrade_corpses',[('historical_upgrade_corpse_damage',3,3)]),
 'TTN_458':('none',[('missiles','enemy_minions',5)]),
 'TTN_729':('none',[]),
 'TOY_307':('none',[random_cards(pool(card_type='SPELL',school='FROST'),2,temporary=True)]),
 'TOY_351':('none',[]),
 'TOY_375':('enemy_minion',[('historical_upgrade_freeze_armor',)]),
 'TOY_521':('none',[('next_discount','ALL',2,'turn')]),
 'TOY_813':('minion',[('historical_upgrade_source_stats',)]),
 'TOY_828':('none',[]),
 'TOY_915':('historic_friendly_demon',[('historic_temporary_attack','target',2,'end'),('temporary_keyword_target','IMMUNE','end')]),
})
TOKEN_RULES={spec[0]:('none',[]) for spec in CORRUPT_FORMS.values()}
TOKEN_RULES.update({cid:('none',[]) for cid in FORGE_FORMS.values()})
TOKEN_RULES.update({cid:('none',[]) for ids in MINI_FORMS.values() for cid in ids})
TOKEN_RULES.update({
 'DMF_061t':('none',[('summon','DMF_061t2',1),('draw',1)]),
 'DMF_101t':('minion',[('damage',12)]),
 'DMF_118t':('none',[('historical_upgrade_remove_top',True,5)]),
 'DMF_163t':('none',[('historical_upgrade_fill_source',)]),
 'DMF_174t':('character',[('damage',4)]),
 'DMF_703t':('none',[('summon','DMF_703t2',2)]),
 'DEEP_024t':('character',[('damage',5)]),
 'TTN_039t':('none',[random_cards(pool(card_type='SPELL',school='HOLY')),('heal_own_hero',6)]),
 'TTN_076t':('none',[discover(pool(card_type='SPELL',classes='own_or_neutral'),cost_delta=-3)]),
 'TTN_457t':('character',[('gain_corpses',3),('damage',3)]),
 'TTN_458t':('none',[('missiles','enemy_minions',5)]),
 'DMF_061t2':('none',[]),'DMF_703t2':('none',[]),
 'TOY_380t2':('none',[]),'TOY_601t2':('none',[]),
 'TTN_801t1':('none',[]),'TTN_801t2':('none',[]),
})
for base in MINI_FORMS:
 if base in ('TOY_312','TOY_340','TOY_341','TOY_380','TOY_601','TOY_801','TOY_811','MIS_025'):continue
 for cid in MINI_FORMS[base]:TOKEN_RULES[cid]=deepcopy(RULES[base])
CHOICES={
 'DMF_061':[('Prune the Fruit','none',[('draw',1)]),('Dig It Up','none',[('summon','DMF_061t2',1)])],
 'DEEP_027':[('Splintered Form','none',[('discard',2)]),('Mana Disintegration','none',[('destroy_crystals',1)])],
}
for cid in ('TOY_801','TOY_801t'):
 CHOICES[cid]=[('Seedling Growth','none',[('historical_event_spell_damage','self',1)]),('Cultivate','none',[('filtered_draw',(('type','eq','SPELL'),),1)])]
DEATH_EFFECTS={}
# The hand filter is an explicit tribe predicate, not a mechanic named UNDEAD.
for cid in ('TOY_828','TOY_828t'):DEATH_EFFECTS[cid]=[('historical_upgrade_undead_hand',2,2)]
for cid in ('TOY_351','TOY_351t'):DEATH_EFFECTS[cid]=[('historical_upgrade_copy_beast_deck',3)]
for cid in ('TOY_380','TOY_380t'):DEATH_EFFECTS[cid]=[('summon','TOY_380t2',1)]
END_EFFECTS={cid:[('copy_self_right',1)] for cid in ('TTN_730','TTN_730t')}
END_EFFECTS.update({cid:[('historical_upgrade_summon_attack','TOY_601t2')] for cid in ('TOY_601','TOY_601t')})
TRIGGERS={
 'TTN_801':(('spell_school_cast','NATURE'),[('summon','TTN_801t1',1)]),
 'TTN_801t':(('spell_school_cast','NATURE'),[('summon','TTN_801t2',1)]),
 'TTN_729':(('historical_upgrade_event','forged'),[('historical_upgrade_copy_forged',)]),
}
for cid in ('MIS_025','MIS_025t','MIS_025t1'):
 TRIGGERS[cid]=(('historical_upgrade_event','same_attack_play'),[('historical_copy_played','summon',None,None)])
AURAS={'DMF_082':('others',1,0),'DMF_082t':('others',1,0)}
# Echo's fresh generated copy has its own one-mana minimum and lifetime.
ECHO_IDS=frozenset(('BOT_700','GIL_207','GIL_607t','GIL_677','GIL_678','GIL_680','GIL_835'))
RULES.update({cid:('none',[]) for cid in ECHO_IDS|{'GIL_618','GIL_510','BOT_107'}})
RULES['GIL_677']=('none',[random_cards(pool(card_type='MINION',rarity='LEGENDARY'))])
RULES['GIL_835']=('character',[('heal',2)])
DEATH_EFFECTS['BOT_700']=[('summon','BOT_312t',2)]
END_EFFECTS['BOT_107']=[('area_damage','other_characters',1)]
TRIGGERS['GIL_510']=(('historical_upgrade_event','echo_played'),[('buff_self',1,1)])
TOKEN_RULES['BOT_312t']=('none',[])
from .adapt import ADAPTATIONS,PLANT
RULES.update({cid:('none',[('historical_upgrade_adapt','self')]) for cid in ('UNG_001','UNG_100','UNG_925')})
RULES.update({
 'UNG_002':('none',[('historical_upgrade_adapt','self')]*2),
 'UNG_047':('friendly_minion',[('historical_upgrade_adapt_sacrifice',)]),
 'UNG_075':('none',[]),
 'UNG_089':('none',[('historical_upgrade_adapt','murlocs')]),
 'UNG_915':('friendly_beast',[('historical_upgrade_adapt','target')]),
 'UNG_962':('none',[('historical_upgrade_adapt','recruits')]),
 'WON_027':('none',[('historical_upgrade_adapt','raptors')]),
})
TRIGGERS['UNG_075']=(('historical_event','source_attacked_hero'),[('historical_upgrade_adapt','self')])
ECHO_IDS=ECHO_IDS|{'WON_027'}
TOKEN_RULES.update({cid:('minion',[('historical_upgrade_apply_adaptation',cid)]) for cid in ADAPTATIONS})
TOKEN_RULES[PLANT]=('none',[])
MINI_FORMS.update({'MIS_006':('MIS_006t',),'MIS_300':('MIS_300t',),'MIS_307':('MIS_307t1',),'MIS_918':('MIS_918t',),'TOY_513':('TOY_513t',),'TOY_652':('TOY_652t',)})
RULES.update({
 'MIS_006':('none',[('historical_upgrade_discover_undead',)]),
 'MIS_300':('none',[]),
 'MIS_307':('none',[('historical_upgrade_tinyfin',)]),
 'MIS_918':('none',[]),
 'TOY_513':('none',[('hero_attack',1),('historical_upgrade_hero_windfury',)]),
 'TOY_652':('none',[('historical_upgrade_shopper',)]),
})
for cid in ('MIS_006','MIS_300','MIS_307','MIS_918','TOY_513','TOY_652'):
 for token in MINI_FORMS[cid]:TOKEN_RULES[token]=deepcopy(RULES[cid])
TOKEN_RULES['MIS_307t']=('none',[])
GENERATED_IDS=frozenset(RULES)
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)
# Spell definitions live with Helbrim's complete generated family.
CORRUPT_FORMS['YOP_015']=('YOP_015t',0,0)


def targets(game,cid,owner,mode):
 if mode!='historical_upgrade_corpses':return None
 return game._targets_for(cid,owner,'character') if game.players[owner].corpses>=3 else [0]


def card_targets(game,card,owner,targets):
 if card.card_id!='DEEP_024':return targets
 return game._targets_for(card.card_id,owner,'character') if getattr(card,'_hand_entry_turn',None)==game.turn else [0]


def matches(game,wanted,kind,data,minion):
 if not isinstance(wanted,tuple) or len(wanted)!=2 or wanted[0]!='historical_upgrade_event':return None
 if wanted[1]=='forged':return kind=='historical_forged' and data['owner']==minion.owner
 if wanted[1]=='echo_played':return kind=='historical_echo_played' and minion.uid in data['listeners']
 if wanted[1]=='same_attack_play':
  return kind=='minion_played' and data['owner']==minion.owner and data.get('source')!=minion.uid and data.get('entry_attack')==minion.attack
 return False


def split(game,op,ctx):
 if op[0]=='historical_upgrade_adapt_sacrifice':
  victim=next((m for m in game.players[ctx['owner']].minions if m.uid==ctx.get('target') and m.health>0),None)
  if victim is None:return ('batch30_noop',),()
  return ('destroy',),(('historical_upgrade_adapt_after_destroy',{'victim':victim}),)
 if op[0]=='historical_upgrade_adapt_after_destroy':
  if op[1]['victim'].health>0:return ('batch30_noop',),()
  return ('historical_upgrade_adapt','self'),(('historical_upgrade_adapt','self'),)
 if op[0]=='historical_upgrade_fill_source':return game._split_fixed_summon(('copy_self_right',max(0,7-len(game.players[ctx['owner']].board))),ctx)
 if op[0]=='historical_upgrade_summon_attack':
  state={}
  return ('historical_upgrade_capture_summon',op[1],state),(('historical_upgrade_attack_summoned',state),)
 return None


def execute(game,op,ctx):
 name=op[0]
 if not name.startswith('historical_upgrade_'):return False
 owner=ctx['owner'];p=game.players[owner];source=ctx.get('source');uid=ctx.get('target',0)
 target=next((m for player in game.players for m in player.minions if m.uid==uid and m.health>0),None)
 if name=='historical_upgrade_discover_undead':
  if source is not None:game._effect(discover(pool(card_type='MINION',tribe='UNDEAD',classes='own_or_neutral'),cost_delta=-source.attack),ctx)
 elif name=='historical_upgrade_shopper':
  if source is not None:
   game._effect(discover(pool(card_type='MINION',tribe='DEMON',classes='own_or_neutral'),stats=(source.attack,source.health),set_cost=game._card_stat(source,'cost',owner)),ctx)
 elif name=='historical_upgrade_tinyfin':
  if source is not None:game._summon(owner,'MIS_307t',entry_stats=(source.attack,source.health),entry_origin='effect',entry_site='growfin_tinyfin')
 elif name=='historical_upgrade_hero_windfury':p.historical_hero_windfury_turn=game.turn
 elif name=='historical_upgrade_adapt':
  from engine.cards import UnsupportedCard
  if game.pending_choice is not None:raise UnsupportedCard('Cannot overwrite Adapt choice')
  group=op[1];minions=[m for m in p.minions if m.health>0 and not m.dormant]
  if group=='self':values=[source] if source in minions else []
  elif group=='target':values=[target] if target in minions else []
  elif group=='friendly':values=minions
  elif group=='murlocs':values=[m for m in minions if has_tribe(game._card_data(m),'MURLOC')]
  elif group=='recruits':values=[m for m in minions if m.card_id in ('CS2_101t','CORE_CS2_101t')]
  elif group=='raptors':values=[m for m in minions if m.card_id=='WON_027']
  else:raise ValueError('Unknown explicit Adapt group: '+group)
  if values:
   require_fixed_cards(tuple(ADAPTATIONS)+(PLANT,),game.cards)
   options=game.rng.sample(sorted(ADAPTATIONS),3)
   game.pending_choice=dict(owner=owner,kind='historical_adapt',targets=tuple(m.uid for m in values),options=[dict(card_id=cid) for cid in options])
   game.phase='choice'
 elif name=='historical_upgrade_apply_adaptation':
  from .adapt import apply_adaptation
  if target is not None:apply_adaptation(game,target,op[1])
 elif name=='historical_upgrade_echo':
  require_fixed_cards((op[1],),game.cards)
  card=Card(game._new_id(),op[1]);game._make_temporary(card)
  game._b60_state(card)['historical_echo_copy']=True
  game._enter_hand(owner,card)
  game._queue_event('historical_echo_played',owner=owner,card_id=op[1],listeners=op[2])
 elif name=='historical_upgrade_remove_top':
  recipient=1-owner if op[1] else owner;deck=game.players[recipient].deck
  for _ in range(min(op[2],len(deck))):game._log('destroy_deck_card',player=recipient,card=game._card_data(deck.pop())['id'])
 elif name=='historical_upgrade_quickdraw_damage':
  if getattr(ctx.get('physical_card'),'_hand_entry_turn',None)==game.turn:game._deal_effect(uid,op[1],ctx)
 elif name=='historical_upgrade_corpse_damage':
  if p.corpses>=op[1]:game._spend_corpses(owner,op[1]);game._deal_effect(uid,op[2],ctx)
 elif name=='historical_upgrade_freeze_armor':
  if target is not None:
   amount=target.attack;game._freeze(uid);game._gain_armor(owner,amount)
 elif name=='historical_upgrade_source_stats':
  if source is not None and target is not None:game._set_entity_stats(target,source.attack,source.health)
 elif name=='historical_upgrade_undead_hand':
  for card in p.hand:
   if game._card_data(card)['type']=='MINION' and has_tribe(game._card_data(card),'UNDEAD'):_saidan_add(card,'attack_bonus',op[1]);_saidan_add(card,'health_bonus',op[2])
 elif name=='historical_upgrade_copy_beast_deck':
  candidates=[c for c in p.deck if game._card_data(c)['type']=='MINION' and has_tribe(game._card_data(c),'BEAST')]
  if candidates:
   card=game._copy_card(game.rng.choice(candidates),source_owner=owner);card.cost_delta-=op[1];game._enter_hand(owner,card)
 elif name=='historical_upgrade_capture_summon':
  m=game._summon(owner,op[1],entry_origin='effect',entry_source=source,entry_site='historical_upgrade_summon_attack')
  if m is not None:op[2]['uid']=m.uid
 elif name=='historical_upgrade_attack_summoned':
  m=game._force_live(op[1].get('uid',0))
  if m is not None:
   target_id=game._force_target(m.owner,'random_enemy_character')
   if target_id:game._force_attack(m.uid,target_id)
 elif name=='historical_upgrade_copy_forged':game._enter_hand(owner,game._copy_card(ctx['event']['card'],source_owner=owner))
 else:return False
 return True


def resolve_adapt(game,choice,selected):
 from .adapt import apply_adaptation
 if choice['kind']!='historical_adapt':return False
 for uid in choice['targets']:
  target=next((m for player in game.players for m in player.minions if m.uid==uid and m.health>0),None)
  if target is not None:apply_adaptation(game,target,selected['card_id'])
 game._refresh_auras()
 return True

FORGE_FORMS['TTN_490']='TTN_490t'

MINI_FORMS['TOY_501']=('TOY_501t',)

MINI_FORMS['TOY_604']=('TOY_604t',)

# Darkmoon board Student's physical Corrupt upgrade.
CORRUPT_FORMS['SCH_199t26']=('SCH_199t26t',2,2)

from .historical_forge_spells import FORMS as SPELL_FORGE_FORMS
FORGE_FORMS.update(SPELL_FORGE_FORMS)

FORGE_FORMS['TTN_430']='TTN_430t'

FORGE_FORMS['TTN_855t']='TTN_855'

from .historical_offer_spells import FORMS as OFFER_FORGE_FORMS
FORGE_FORMS.update(OFFER_FORGE_FORMS)

# Native Corrupt conversion for generated Dunk Tank.
CORRUPT_FORMS['DMF_701']=('DMF_701t',0,0)

CORRUPT_FORMS['DMF_105']=('DMF_105t',0,0)

from .historical_spell_archive_batch import CORRUPT_FORMS as ARCHIVE_CORRUPT_FORMS
CORRUPT_FORMS.update(ARCHIVE_CORRUPT_FORMS)

CORRUPT_FORMS['WON_064']=('WON_064ts',0,0)
