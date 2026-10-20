"""Explicit historical drawn-card families; implementation only, unvalidated.

Draw-triggered minions remain in hand. Casts/Summons When Drawn are separate
physical transitions, and complete generation requests are never narrowed.
"""
from engine.game import Card
from .generation_cards import pool,random_cards
from .pools import require_fixed_cards
from .selectors import has_tribe

SOUL='SCH_307t'
BOMB='BOT_511t'
MINE='GVG_056t'
CAST_EFFECTS={
 'VAC_321t':(('historical_drawn_eruption',),),
 'VAC_933t':(('summon','VAC_926t',1),),
 'BAR_721t':(('historical_copy_mankrik',),),
 BOMB:(('on_draw_hurt_owner',5),),MINE:(('on_draw_hurt_owner',10),),
 'DAL_582t':(('summon','DAL_582t2',1),),
 'DMF_514t':(('summon','DMF_514t2',1),),
 'DRG_036t':(('summon','DRG_036',1),),
 'DRG_320t':(random_cards(pool(card_type='MINION',tribe='DRAGON'),destination='board'),),
 'GDB_430':(('historical_resource_asteroid_damage',),),
 'LOE_110t':(('on_draw_hurt_owner',7),),
 'LOOT_026e':(('summon','LOOT_026t',1),),
 'MAW_005t':(('historical_drawn_overload',2),),
 'ONY_028t':(('summon','ONY_028',1),),
 SOUL:(('heal_own_hero',2),),
 'SW_097t':(('summon','skele21',1),),
}
SUMMON_DRAW={'TTN_083t':0}
RULES={
 'BOT_511':('none',[('on_draw_shuffle',BOMB,1,1)]),
 'DAL_060':('none',[('on_draw_shuffle',BOMB,1,1)]),
 'DAL_064':('none',[('historical_drawn_boom_bots',)]),
 'DAL_565':('none',[('on_draw_shuffle','DAL_582t',3,0)]),
 'DAL_582':('none',[('on_draw_shuffle','DAL_582t',3,0)]),
 'DRG_320':('none',[('on_draw_shuffle','DRG_320t',7,0)]),
 'GDB_435':('none',[('on_draw_shuffle','GDB_430',3,0)]),
 'GDB_901':('enemy_minion',[('damage',3),('on_draw_shuffle','GDB_430',3,0)]),
 'GVG_056':('none',[('on_draw_shuffle',MINE,1,1)]),
 'WON_114':('none',[('on_draw_shuffle',MINE,1,1)]),
 'LOE_110':('none',[('on_draw_shuffle','LOE_110t',1,0)]),
 'LOOT_026':('none',[('on_draw_shuffle','LOOT_026e',3,0)]),
 'MAW_005':('none',[('on_draw_shuffle','MAW_005t',3,1)]),
 'SCH_700':('none',[('on_draw_shuffle',SOUL,2,0)]),
 'SCH_343':('none',[('historical_drawn_consume_soul',( ('buff_self',3,3), ))]),
 'SCH_355':('none',[('historical_drawn_consume_soul',( ('area_damage','other_minions',3), ))]),
 'SCH_517':('historical_soul_target',[('historical_drawn_consume_soul',( ('damage',3), ))]),
 'SCH_704':('none',[('historical_drawn_consume_soul',( ('hero_attack',5), ))]),
 'SCH_703':('none',[('historical_drawn_souls',)]),
 'TTN_083':('none',[('on_draw_shuffle','TTN_083t',4,0)]),
 'YOP_003':('none',[('on_draw_shuffle',SOUL,2,0)]),
}
for cid in ('TTN_450t','TTN_450t2','TTN_450t3'):
 CAST_EFFECTS[cid]=(('on_draw_hurt_owner',2),('historical_copy_plague_effect',cid),('historical_copy_unending_plague',))
CAST_EFFECTS['TRL_541t']=(('on_draw_hurt_owner',3),)
TOKEN_RULES={cid:('none',list(operations)) for cid,operations in CAST_EFFECTS.items()}
TOKEN_RULES.update({cid:('none',[]) for cid in ('DAL_582t2','DMF_514t2','LOOT_026t','skele21','SCH_703t','TTN_083t')})
# Ordinary hand casts receive printed Overload through the play boundary.
TOKEN_RULES['MAW_005t']=('none',[])
TOKEN_RULES['YOP_003t']=('none',[('on_draw_shuffle',SOUL,2,0),('draw',1)])
DEATH_EFFECTS={
 'DMF_514':[('on_draw_shuffle','DMF_514t',3,0)],
 'DRG_036':[('on_draw_shuffle','DRG_036t',1,0)],
 'GVG_056':RULES['GVG_056'][1],
 'WON_114':RULES['WON_114'][1],
 'MIS_711':[('on_draw_shuffle',BOMB,3,1)],
 'ONY_028':[('on_draw_shuffle','ONY_028t',1,0)],
}
END_EFFECTS={'MIS_308':[('on_draw_shuffle',BOMB,1,1)]}
TRIGGERS={'SW_097':('damaged_self',[('on_draw_shuffle','SW_097t',2,0)])}
REGULAR_EFFECTS={
 'AT_130':(('area_damage','friendly_minions',1),),
 'DAL_185':(('heal_own_hero',4),),
 'GVG_007':(('historical_drawn_non_mech_damage',2),),
 'WON_038':(('historical_drawn_non_mech_damage',2),),
 'SC_012':(('historical_drawn_copy_received',),),
 'SW_306':(('historical_drawn_copy_received',),),
 'VAC_337':(('historical_drawn_copy_received',),),
 'TTN_715':(random_cards(pool(card_type='MINION',tribe='DRAGON')),),
}
for cid in DEATH_EFFECTS.keys()|END_EFFECTS.keys()|TRIGGERS.keys()|REGULAR_EFFECTS.keys():RULES.setdefault(cid,('none',[]))
GENERATED_IDS=frozenset(RULES)
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)


def targets(game,cid,owner,mode):
 if mode!='historical_soul_target':return None
 return game._targets_for(cid,owner,'character') if any(game._card_data(c)['id']==SOUL for c in game.players[owner].deck) else [0]


def split(game,op,ctx):
 owner=ctx['owner'];p=game.players[owner]
 if op[0]=='historical_drawn_consume_soul':
  choices=[i for i,card in enumerate(p.deck) if game._card_data(card)['id']==SOUL]
  if not choices:return ('batch30_noop',),()
  value=p.deck.pop(game.rng.choice(choices));game._zone_card_removed(owner,value,'deck','destroy');game._log('destroy_deck_card',player=owner,card=SOUL)
  return op[1][0],tuple(op[1][1:])
 if op[0]=='historical_drawn_souls':
  count=sum(game._card_data(c)['id']==SOUL for c in p.deck)
  return game._split_fixed_summon(('summon','SCH_703t',count),ctx)
 if op[0]=='historical_drawn_boom_bots':
  count=2*sum(game._card_data(c)['id']==BOMB for c in game.players[1-owner].deck)
  return game._split_fixed_summon(('summon','BOT_218t',count),ctx)
 return None


def received(game,owner,card):
 operations=REGULAR_EFFECTS.get(card.card_id,())
 if operations:
  from copy import deepcopy
  game._rule_events.append(('captured_effects',dict(operations=operations,context=dict(owner=owner,source=None,physical_card=deepcopy(card),target=0,bonus=0,lifesteal=False)),[]))


def execute(game,op,ctx):
 if not op[0].startswith('historical_drawn_'):return False
 owner=ctx['owner'];p=game.players[owner]
 if op[0]=='historical_drawn_eruption':
  amount=1+getattr(ctx.get('physical_card'),'rule_state',{}).get('historical_eruption_bonus',0)
  game._effect(('area_damage','enemies',amount),ctx)
 elif op[0]=='historical_drawn_overload':
  from .historical_resource_batches import add_overload
  add_overload(game,owner,op[1])
 elif op[0]=='historical_drawn_copy_received':
  card=ctx.get('physical_card')
  if card is not None:game._clone_hand_card(owner,card,source_owner=owner)
 elif op[0]=='historical_drawn_non_mech_damage':
  targets=[game.hero_id(i) for i in (0,1)]+[m.uid for player in game.players for m in player.minions if not has_tribe(game._card_data(m),'MECHANICAL')]
  with game._damage_batch():
   for uid in targets:game._deal_effect(uid,op[1],ctx)
 else:return False
 return True
