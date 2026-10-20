"""Historical Overload resources and spell-keyword consumers; unvalidated."""
from .selectors import has_tribe,has_school
from .generation_cards import pool,random_cards

# These bodies have only printed keywords and the explicit paid-play Overload.
INTRINSIC=('EX1_243','ICC_081','MIS_306','OG_024','SW_033')
RULES={cid:('none',[]) for cid in INTRINSIC}
RULES.update({
 'BOT_543':('none',[('historical_resource_omega_lifesteal',)]),
 'OG_209':('none',[]),'WON_336':('none',[]),'TOY_807':('none',[]),
 'RLK_218':('none',[('historical_resource_no_hero_targets',)]),
 'GDB_135':('none',[('historical_resource_next_refresh',)]),
 'TSC_828':('none',[('historical_resource_refresh_spells',)]),
 'TSC_620':('none',[]),
 'ETC_371':('none',[('historical_resource_inzah',)]),
 'OG_026':('none',[('unlock_mana',)]),
 'WON_090':('none',[('historical_resource_prevent',),('filtered_draw',(('mechanic','eq','OVERLOAD'),),1)]),
 'WW_326':('none',[]),
 'GDB_444':('none',[('historical_resource_next_draenei',)]),
 'EX1_258':('none',[]),'BOT_407':('none',[]),'SW_026':('none',[]),
 'LOE_018':('none',[]),'GVG_040':('none',[]),
 'GDB_434':('none',[('historical_resource_asteroid_bonus',1)]),
 'GDB_728':('none',[('historical_resource_draw_libram',)]),
 'SCH_120':('none',[]),'GDB_127':('none',[]),'GDB_442':('none',[]),
 'GDB_441':('none',[]),
 'ETC_332':('none',[('historical_resource_dreamboat',)]),
})
TRIGGERS={
 'TSC_620':(('historical_event','siren_alternating'),[('refresh_mana',2)]),
 'EX1_258':(('historical_event','overload_card_played'),[('buff_self',1,1)]),
 'BOT_407':(('historical_event','overload_card_played'),[('summon','BOT_102t',2)]),
 'SW_026':(('historical_event','overload_card_played'),[('summon','EX1_tk11',1)]),
 'LOE_018':(('historical_event','mana_overloaded'),[('historical_resource_trogg',)]),
 'GVG_040':(('historical_event','other_friendly_murloc_died'),[('draw',1)]),
 'GDB_441':(('historical_event','another_overhealed'),[('historical_resource_anchorite',)]),
}
SPELLBURST={
 'SCH_120':[('historical_resource_acolyte',)],
 'GDB_127':[('historical_resource_steal_health',2)],
 'GDB_442':[random_cards(pool(card_type='MINION',minimum=3,maximum=3),destination='board')],
 'GDB_434':[('on_draw_shuffle','GDB_430',3,0)],
 'GDB_728':[('historical_resource_draw_libram',)],
}
TOKEN_RULES={'BOT_102t':('none',[]),'EX1_tk11':('none',[])}
SPELL_DAMAGE_VALUES={'TOY_807':1,'RLK_218':2}
GENERATED_IDS=frozenset(RULES)
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)|{'GDB_430'}


def add_overload(game,owner,amount):
 if type(amount) is not int or amount<0:raise ValueError('Invalid explicit Overload amount')
 p=game.players[owner]
 if not amount or getattr(p,'historical_no_overload_turn',None)==game.turn:return 0
 p.overload_next+=amount;p.overloaded_total+=amount
 from .historical_held_upgrades import progress
 progress(game,owner,'sapphire',amount)
 game._queue_event('historical_overloaded',owner=owner,amount=amount)
 return amount


def played_overload(game,owner,card,amount):
 if card.card_id=='WW_326' and {'ELEMENTAL','ALL'} & game.players[owner].previous_tribes:return 0
 return amount


def split(game,op,ctx):
 if op[0]!='historical_resource_dreamboat':return None
 source=ctx.get('source');values=[m.uid for m in game.players[ctx['owner']].minions if m is not source and m.health>0];state={'overhealed':0}
 operations=tuple(('historical_resource_heal_boat',uid,state) for uid in values)+(('historical_resource_boat_finish',state),)
 return operations[0],operations[1:]


def execute(game,op,ctx):
 name=op[0]
 if not name.startswith('historical_resource_'):return False
 owner=ctx['owner'];p=game.players[owner];q=game.players[1-owner];source=ctx.get('source')
 if name=='historical_resource_omega_lifesteal':
  if p.max_mana>=10:p.historical_spell_lifesteal_turn=game.turn
 elif name=='historical_resource_no_hero_targets':p.historical_spell_no_heroes_turn=game.turn
 elif name=='historical_resource_next_refresh':p.cost_effects.append(dict(selector='DRAENEI',amount=0,grant_refresh_attack=True,expires=None))
 elif name=='historical_resource_refresh_attack':
  if source is not None:game._effect(('refresh_mana',max(0,source.attack)*op[1]),ctx)
 elif name=='historical_resource_refresh_spells':game._effect(('refresh_mana',p.spells_cast_turn),ctx)
 elif name=='historical_resource_inzah':p.historical_overload_discount=getattr(p,'historical_overload_discount',0)+1
 elif name=='historical_resource_prevent':p.historical_no_overload_turn=game.turn
 elif name=='historical_resource_next_draenei':p.cost_effects.append(dict(selector='DRAENEI',amount=2,grant_overload=2,expires=None))
 elif name=='historical_resource_trogg':
  if source is not None:game._buff(source,ctx['event']['amount'],0)
 elif name=='historical_resource_asteroid_bonus':p.historical_asteroid_bonus=getattr(p,'historical_asteroid_bonus',0)+op[1]
 elif name=='historical_resource_asteroid_damage':game._effect(('damage_random_enemy',2+getattr(p,'historical_asteroid_bonus',0)),ctx)
 elif name=='historical_resource_draw_libram':
  from .historical_family_batches import LIBRAMS
  game._draw(owner,lambda data:data['id'] in LIBRAMS)
 elif name=='historical_resource_acolyte':
  values=[m for m in q.minions if m.health>0 and m.attack<=2]
  if values and len(p.board)<7:
   m=game.rng.choice(values);q.board.remove(m);m.owner=owner;m.summoned_turn=game.turn;m.attacks=0;p.board.append(m);game._refresh_auras()
 elif name=='historical_resource_steal_health':
  values=[game.hero_id(1-owner)]+[m.uid for m in q.minions if m.health>0]
  if source is not None and source.health>0 and values:
   target=game.rng.choice(values)
   if target<0:q.health-=op[1];q.max_health-=op[1];q.hero_health_changed_turn=True
   else:game._buff(game._find(target),0,-op[1])
   game._buff(source,0,op[1])
 elif name=='historical_resource_anchorite':
  target=next((m for player in game.players for m in player.minions if m.uid==ctx['event']['target'] and m.health>0),None)
  if target is not None:game._buff(target,0,ctx['event']['overheal'])
 elif name=='historical_resource_heal_boat':
  target=next((m for m in p.minions if m.uid==op[1] and m.health>0),None)
  if target is not None:
   receipt={};game._heal(target.uid,3,healer=owner,_receipt=receipt)
   if receipt.get('overheal',0)>0:op[2]['overhealed']+=1
 elif name=='historical_resource_boat_finish':
  if source is not None:game._buff(source,op[1]['overhealed'],op[1]['overhealed'])
 else:return False
 return True


def spell_lifesteal(game,owner,cid=None):
 p=game.players[owner]
 if cid is not None and has_school(game.cards[cid],'FEL') and game._active('WW_091',owner):return True
 return getattr(p,'historical_spell_lifesteal_turn',None)==game.turn or any(m.card_id in ('OG_209','WON_336') and m.health>0 and not m.silenced and not m.dormant for m in p.minions)
