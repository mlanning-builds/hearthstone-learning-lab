"""Historical armor and physical weapon consumers; unvalidated."""
from copy import deepcopy
from .generation_cards import pool,random_cards
from .selectors import has_tribe

RULES={
 'LOOT_367':('none',[('historical_arsenal_enemy_armor',2)]),
 'TRL_308':('none',[('historical_arsenal_convert_health',)]),
 'TTN_811':('none',[('historical_arsenal_odyn',)]),
 'AV_145':('none',[('historical_arsenal_armor_gate',15)]),
 'TTN_469':('none',[('historical_arsenal_changed_draw',2)]),
 'EX1_398':('none',[('equip','EX1_398t')]),
 'NEW1_025':('none',[('historic_weapon_wear',1)]),
 'OG_220':('none',[('historical_arsenal_random_weapon','any')]),
 'GVG_119':('none',[('historical_arsenal_both_weapons',)]),
 'WC_029':('none',[('historical_arsenal_deck_weapon',)]),
 'VAC_924':('none',[('historical_arsenal_pirate_weapon',)]),
 'DRG_055':('none',[('historical_arsenal_old_weapon','equip')]),
 'LOOT_389':('none',[('historical_arsenal_old_weapon','hand')]),
 'ETC_098':('none',[('summon_opponent','ETC_098t',1)]),
 'JAM_035':('none',[('historical_arsenal_discard_draw',)]),
 'ICC_096':('none',[('historical_arsenal_eat_weapons',)]),
}
PASSIVES=('ETC_355','CS2_146','CS2_221','SCH_519','ICC_240','JAM_016')
RULES.update({cid:('none',[]) for cid in PASSIVES})
DEATH_EFFECTS={'ICC_062':[('historical_arsenal_enemy_turn_armor',6)]}
END_EFFECTS={'LOOT_519':[('historical_arsenal_armor_minion',)]}
TRIGGERS={
 'GVG_086':('friendly_armor_gained',[('buff_self',1,0)]),
 'EX1_402':(('historical_event','friendly_minion_damaged'),[('armor',1)]),
 'ICC_097':(('historical_event','own_weapon_broken'),[('buff_self',1,1)]),
 'ETC_400':(('historical_event','own_weapon_broken'),[('historical_arsenal_random_weapon','DEMONHUNTER')]),
 'TOY_651':(('historical_event','armor_patron'),[('summon','TOY_651',1)]),
}
for cid in DEATH_EFFECTS.keys()|END_EFFECTS.keys()|TRIGGERS.keys():RULES.setdefault(cid,('none',[]))
TOKEN_RULES={'EX1_398t':('none',[]),'ETC_098t':('none',[])}
DEATH_EFFECTS['ETC_098t']=[('historical_arsenal_enemy_weapon_card',)]
GENERATED_IDS=frozenset(RULES)
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)


def weapon_aura(game,owner):
 return 2*sum(not m.silenced and not m.dormant and m.health>0 and (m.card_id=='SCH_519' or m.card_id=='CS2_221' and m.health<m.max_health) for m in game.players[owner].minions)


def lose_durability(game,owner,amount):
 p=game.players[owner]
 if not p.weapon or amount<=0:return
 if p.weapon['card_id']=='AV_146':return
 if game.current==owner and any(m.card_id=='ICC_240' and not m.silenced and not m.dormant and m.health>0 for m in p.minions):return
 p.weapon['durability']-=amount
 if p.weapon['durability']<=0:game._break_weapon(owner)


def split(game,op,ctx):
 owner=ctx['owner'];p=game.players[owner]
 if op[0]=='historical_arsenal_enemy_weapon_card':
  return game._split_fixed_summon(('replay_context',(random_cards(pool(card_type='WEAPON')),),dict(ctx,owner=1-owner)),ctx)
 if op[0]=='historical_arsenal_both_weapons':
  game._generation_candidates(pool(card_type='WEAPON'),owner);game._generation_candidates(pool(card_type='WEAPON'),1-owner)
  return ('historical_arsenal_random_weapon','any'),(('replay_context',(('historical_arsenal_random_weapon','any'),),dict(ctx,owner=1-owner)),)
 if op[0]=='historical_arsenal_discard_draw':
  state={}
  return ('historical_arsenal_discard_one',state),(('historical_arsenal_discard_finish',state),)
 if op[0]=='historical_arsenal_discard_finish':return game._split_fixed_summon(('draw',3 if op[1].get('discarded') else 0),ctx)
 if op[0]=='historical_arsenal_eat_weapons':
  state={}
  return ('historical_arsenal_discard_all',state),(('historical_arsenal_eat_finish',state),)
 return None


def execute(game,op,ctx):
 name=op[0]
 if not name.startswith('historical_arsenal_'):return False
 owner=ctx['owner'];p=game.players[owner];source=ctx.get('source')
 if name=='historical_arsenal_enemy_armor':game._gain_armor(owner,op[1]*len(game.players[1-owner].minions))
 elif name=='historical_arsenal_convert_health':
  amount=max(0,p.health-1)
  if amount:p.health=1;p.hero_health_changed_turn=True;game._gain_armor(owner,amount)
 elif name=='historical_arsenal_odyn':p.historical_odyn=getattr(p,'historical_odyn',0)+1
 elif name=='historical_arsenal_armor_gate':
  if getattr(p,'historical_armor_gained',0)>=op[1]:game._effect(('buff_self',3,3),ctx);game._effect(('keyword_self','CHARGE'),ctx)
 elif name=='historical_arsenal_changed_draw':
  if getattr(p,'historical_armor_changed_turn',None)==game.turn:game._effect(('draw',op[1]),ctx)
 elif name=='historical_arsenal_enemy_turn_armor':
  if game.current!=owner:game._gain_armor(owner,op[1])
 elif name=='historical_arsenal_random_weapon':
  request=pool(card_type='WEAPON',classes=op[1]);values=game._generation_candidates(request,owner)
  if values:game._equip(owner,game.rng.choice(values))
 elif name=='historical_arsenal_deck_weapon' or name=='historical_arsenal_pirate_weapon':
  if name=='historical_arsenal_pirate_weapon' and not any(m is not source and has_tribe(game._card_data(m),'PIRATE') for m in p.minions):return True
  choices=[i for i,c in enumerate(p.deck) if game._card_data(c)['type']=='WEAPON']
  if choices:
   from engine.game import Card
   value=p.deck.pop(game.rng.choice(choices));card=value if isinstance(value,Card) else Card(game._new_id(),value)
   game._equip(owner,card.card_id,attack_bonus=card.attack_bonus,physical_card=card)
 elif name=='historical_arsenal_old_weapon':
  values=getattr(p,'historical_broken_weapons',())
  if values:
   card=game._fresh_replay_card(game.rng.choice(values))
   if op[1]=='hand':game._enter_hand(owner,card)
   else:game._equip(owner,card.card_id,attack_bonus=card.attack_bonus,physical_card=card)
 elif name=='historical_arsenal_enemy_weapon_card':
  game._effect(random_cards(pool(card_type='WEAPON')),dict(ctx,owner=1-owner))
 elif name=='historical_arsenal_armor_minion':game._effect(random_cards(pool(card_type='MINION',minimum=min(10,p.armor),maximum=min(10,p.armor)),destination='board'),ctx)
 elif name=='historical_arsenal_discard_one':
  values=[c for c in p.hand if game._card_data(c)['type']=='WEAPON']
  if values:game._discard_card(owner,game.rng.choice(values));op[1]['discarded']=True
 elif name=='historical_arsenal_discard_all':
  values=[c for c in p.hand if game._card_data(c)['type']=='WEAPON']
  op[1]['attack']=sum(game._card_stat(c,'attack',owner) for c in values)
  op[1]['health']=sum((game._card_data(c).get('durability') or game._card_data(c).get('health',0))+c.health_bonus for c in values)
  if values:game._discard_cards(owner,values)
 elif name=='historical_arsenal_eat_finish':
  if source is not None and source in p.minions:game._buff(source,op[1].get('attack',0),op[1].get('health',0))
 else:return False
 return True
