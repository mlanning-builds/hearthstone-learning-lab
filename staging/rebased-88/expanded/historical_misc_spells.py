"""Explicit generated conditional spell programs and destruction consumers."""
from copy import deepcopy
from .selectors import effective_tribes as tribes
TOKEN_RULES={
 'WW_009':('enemy_character',[('freeze',),('historical_excavate_dig',False)]),
 'WW_334':('none',[('armor',6),('historical_excavate_dig',False)]),
 'TTN_853':('enemy_minion',[('historical_misc_health_one',),('area_damage','enemies',1)]),
 'WW_027':('minion',[('buff',2,3),('historical_misc_tribe_draw',)]),
 'WW_051':('none',[('historical_misc_showdown',)]),
 'YOG_513':('friendly_undead',[('buff',2,2),('historical_misc_soulcage',)]),
 'WW_403':('character',[('damage',3),('historical_copy_quickdraw_operation',('historical_misc_enemy_next_cost',))]),
 'WW_409':('character',[('damage',2),('historical_misc_load_chamber',)]),
 'WW_436':('none',[('historical_misc_trolley_discard',),('summon','WW_437t',2)]),
 'WW_441':('none',[('draw',2)]),
 'YOG_301':('none',[('historical_misc_fatigue_both',)]),
 'WW_051t':('none',[]),
}
DISCARD_EFFECTS={'WW_441':[('draw',2)]}
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)


def split(game,op,ctx):
 owner=ctx['owner'];p=game.players[owner];name=op[0]
 if name=='historical_misc_showdown':
  operations=tuple(('historical_misc_outlaw',recipient,recipient==owner) for recipient in (owner,1-owner) for _ in range(3))
  return operations[0],operations[1:]
 if name=='historical_misc_soulcage':
  target=next((m for m in p.minions if m.uid==ctx.get('target') and m.health>0),None)
  if p.corpses<5 or target is None:return ('batch30_noop',),()
  return ('historical_misc_pay_five',),(('historical_misc_cage_copy',target.uid),)
 if name=='historical_misc_fatigue_both':
  operations=tuple(('historical_misc_fatigue_hit',recipient) for _ in range(2) for recipient in (owner,1-owner))
  return operations[0],operations[1:]
 return None


def execute(game,op,ctx):
 owner=ctx['owner'];p=game.players[owner];name=op[0]
 target=next((m for player in game.players for m in player.minions if m.uid==ctx.get('target') and m.health>0),None)
 if name=='historical_misc_health_one':
  if target is not None:target.health=target.max_health=1
 elif name=='historical_misc_tribe_draw':
  if target is not None:
   types=tribes(game._card_data(target))
   if types:game._draw(owner,predicate=lambda data:bool(types & tribes(data)))
 elif name=='historical_misc_outlaw':game._summon(op[1],'WW_051t',entry_keywords=('RUSH',) if op[2] else (),entry_origin='effect',entry_site='showdown')
 elif name=='historical_misc_pay_five':game._spend_corpses(owner,5)
 elif name=='historical_misc_cage_copy':
  original=next((m for m in p.minions if m.uid==op[1] and m.health>0),None)
  if original is not None:game._summon(owner,original.card_id,copy_from=original,entry_origin='copy',entry_site='sinister_soulcage')
 elif name=='historical_misc_enemy_next_cost':game.players[1-owner].cost_effects.append(dict(selector='ALL',amount=-1,remaining_uses=1,expires=None))
 elif name=='historical_misc_load_chamber':
  for selector in ('NAGA','FEL','WEAPON'):p.cost_effects.append(dict(selector=selector,amount=1,remaining_uses=1,expires=None))
 elif name=='historical_misc_trolley_discard':
  if getattr(ctx.get('physical_card'),'_hand_entry_turn',None)!=game.turn:
   cards=[card for card in p.hand if game._card_data(card)['type']=='SPELL']
   if cards:
    cost=min(game._cost(card,owner) for card in cards)
    game._discard_cards(owner,[game.rng.choice([card for card in cards if game._cost(card,owner)==cost])])
 elif name=='historical_misc_fatigue_hit':
  recipient=op[1];player=game.players[recipient];player.fatigue+=1
  game._damage(game.hero_id(recipient),player.fatigue,damage_source=None,damage_owner=recipient,damage_cause='fatigue')
 else:return False
 return True
