"""Explicit conditional-cost generated spells and physical held history."""
from .generation_cards import pool,random_cards,discover
from .selectors import has_school,has_tribe
TOKEN_RULES={
 'DEEP_010':('none',[('area_damage','all_minions',1)]*3),
 'ETC_356':('minion',[('damage',6)]),
 'ETC_384':('none',[('draw',2)]),
 'MIS_709':('minion',[('damage',4)]),
 'RLK_590':('none',[('generation_fill_plain_hand',pool(card_type='SPELL',classes='any'))]),
 'RLK_603':('none',[('draw',2)]),'RLK_829':('none',[('draw',2)]),
 'TOY_519':('none',[random_cards(pool(card_type='MINION',minimum=4,maximum=4),2,'board')]),
 'TOY_804':('none',[('summon','TOY_804t',2)]),'TOY_804t':('none',[]),
 'TOY_883':('none',[('area_damage','enemy_minions',3)]),
 'TOY_907':('none',[('armor',6)]),
 'TSC_058':('character',[('damage',2)]),
 'TSC_061':('minion',[('buff',4,4),('keyword','DIVINE_SHIELD')]),
 'TTN_085':('none',[('draw',2)]),
 'TTN_831':('none',[('area_damage','enemies',3)]),
 'TTN_841':('none',[('hero_attack',4)]),
 'TTN_954':('none',[('board_buff',2,2)]),
 'WW_325':('minion',[('damage',4)]),
 'WW_336':('none',[('area_damage','enemies',3)]),
 'WW_365':('minion',[('set_target_stats',1,1),('historical_copy_quickdraw_operation',('damage',1))]),
 'WW_411':('none',[discover(pool(mechanic='QUICKDRAW',classes='other'))]),
 'WW_823':('character',[('heal',7),('historical_copy_quickdraw_operation',('refresh_mana',2))]),
}
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)


def cost(game,card,owner,value):
 cid=card.card_id;p=game.players[owner]
 if cid=='GDB_439' and getattr(card,'rule_state',{}).get('historical_orbital_adjacent_turn')==game.turn:value=0
 if cid in ('ONY_005tc2','VAC_464t24'):value-=sum(len(player.death_records) for player in game.players)
 elif cid=='TTN_088':value-=len(getattr(p,'historical_triggered_secrets',()))
 draw_state=getattr(p,'historical_draw_turn',{})
 draws=draw_state.get('count',0) if draw_state.get('turn')==game.turn else 0
 records=getattr(p,'_historical_cast_records',())
 if cid=='DEEP_010' and any(record['owner_turn']==p.turns_taken-1 for record in records):value-=2
 elif cid=='ETC_356' and (p.locked_mana or p.overload_next):value-=3
 elif cid=='ETC_384':value-=game._hero_attack(owner)
 elif cid=='MIS_709' and any(record['turn']==game.turn and has_school(game._card_data(record['card']),'HOLY') for record in records):value=1
 elif cid in ('RLK_590','TOY_883'):value-=sum(held is not card for held in p.hand)
 elif cid=='RLK_603':value-=sum(m.health<m.max_health for m in p.minions)+int(p.health<p.max_health)
 elif cid=='RLK_829' and game._choicegen_undead_died(owner):value=1
 elif cid in ('TOY_519','TTN_841'):value-=draws
 elif cid=='TOY_804' and game._spell_damage(owner)>0:value-=3
 elif cid=='TOY_907' and p.armor==0:value=0
 elif cid=='TSC_058' and getattr(card,'rule_state',{}).get('historical_cost_naga_played'):value=0
 elif cid=='TSC_061':value-=getattr(p,'historical_holy_mana_paid',0)
 elif cid=='TTN_085':value-=len(getattr(p,'historical_spell_schools',()))
 elif cid=='TTN_831':value-=sum(record['turn']==game.turn and has_school(game._card_data(record['card']),'NATURE') for record in records)
 elif cid=='TTN_954':
  from .historical_tribal_batches import TREANTS
  counts=getattr(p,'historical_summoned_ids',{})
  value-=sum(counts.get(cid,0) for cid in TREANTS)
 elif cid=='WW_325' and getattr(card,'_hand_entry_turn',None)==game.turn:value=1
 elif cid=='WW_336':value-=len(game.players[1-owner].minions)
 return value


def paid(game,owner,card,mana_spent):
 data=game._card_data(card);player=game.players[owner]
 player._historical_paid_card_records=getattr(player,'_historical_paid_card_records',[])+[dict(card_id=card.card_id,turn=game.turn)]
 if data['type']=='SPELL' and has_school(data,'HOLY'):
  player.historical_holy_mana_paid=getattr(player,'historical_holy_mana_paid',0)+max(0,mana_spent)
 if data['type']=='MINION' and has_tribe(data,'NAGA'):
  for held in player.hand:
   if held.card_id in ('TSC_058','TSC_948','TSC_947','TSC_651','TSC_215','WW_404','TSC_023'):game._b60_state(held)['historical_cost_naga_played']=True
