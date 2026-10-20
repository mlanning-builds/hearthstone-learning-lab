"""Complete Spellstone and Remixed held-card families; behavior unvalidated."""
from .generation_cards import pool,discover
from .selectors import has_tribe
from .historical_saidan import add as add_stat
REMIXED_FORMS={
 'JAM_015':('JAM_015t','JAM_015t2','JAM_015t3','JAM_015t4'),
 'JAM_018':('JAM_018t','JAM_018t2','JAM_018t3','JAM_018t4'),
}
OPAL={'TOY_645':'TOY_645t','TOY_645t':'TOY_645t1'}
SPINEL={'TOY_825':'TOY_825t','TOY_825t':'TOY_825t2'}
TOKEN_RULES={
 'JAM_015':('none',[]),
 'JAM_015t':('none',[('weapon_buff',2,0)]),
 'JAM_015t2':('none',[('armor',5)]),
 'JAM_015t3':('none',[]),
 'JAM_015t4':('none',[discover(pool(card_type='MINION',mechanic='TAUNT',classes='own_or_neutral'))]),
 'JAM_018':('none',[('area_damage','all_minions',3)]),
 'JAM_018t':('none',[('area_damage','all_minions',3),('draw',3)]),
 'JAM_018t2':('none',[('area_damage','all_minions',3),('area_damage','all_minions',3)]),
 'JAM_018t3':('none',[('area_damage','all_minions',3),('hero_attack',5)]),
 'JAM_018t4':('none',[('area_damage','all_minions',3),('summon','JAM_018t5',1)]),
 'JAM_018t5':('none',[]),
 'TOY_645':('none',[('draw',1)]),
 'TOY_645t':('none',[('draw',2)]),
 'TOY_645t1':('none',[('draw',3)]),
 'TOY_825':('none',[('historical_held_spellstone_buff',1)]),
 'TOY_825t':('none',[('historical_held_spellstone_buff',2)]),
 'TOY_825t2':('none',[('historical_held_spellstone_buff',3)]),
}
SEEDLINGS={'TTN_930':(3,'TTN_930t'),'TTN_950':(2,'TTN_950t3')}
TOKEN_RULES.update({
 'TTN_930':('none',[('draw',1),('armor',5)]),
 'TTN_930t':('none',[('draw',2),('armor',10)]),
 'TTN_950':('none',[('summon','TTN_950t',2)]),
 'TTN_950t':('none',[]),
 'TTN_950t3':('none',[('summon','TTN_950t2',2)]),
})
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)


def progress(game,owner,family,amount):
 if amount<=0:return
 from .historical_iconic_followups import JASPER,EMERALD
 families={'ruby':({'LOOT_103':'LOOT_103t1','LOOT_103t1':'LOOT_103t2'},2),'sapphire':({'LOOT_064':'LOOT_064t1','LOOT_064t1':'LOOT_064t2'},3),'opal':(OPAL,2),'spinel':(SPINEL,5),'jasper':(JASPER,3),'emerald':(EMERALD,1)}
 forms,threshold=families[family];key='historical_'+family+'_progress'
 for card in tuple(game.players[owner].hand):
  if card.card_id not in forms:continue
  state=game._b60_state(card);value=state.get(key,0)+amount
  if card.card_id in forms and value>=threshold:
   value=0;card.card_id=forms[card.card_id]
  state[key]=value if card.card_id in forms else 0


def execute(game,op,ctx):
 if op[0]=='historical_held_seedling_tick':
  owner=ctx['owner'];card=next((c for c in game.players[owner].hand if c.uid==op[1] and c.card_id in SEEDLINGS),None)
  if card is not None:
   needed,destination=SEEDLINGS[card.card_id];state=game._b60_state(card)
   state['historical_seedling_progress']=state.get('historical_seedling_progress',0)+1
   if state['historical_seedling_progress']>=needed:
    game._b60_transform_card(card,destination);game._log('hand_transformed',player=owner,entity=card.uid)
  return True
 if op[0]!='historical_held_spellstone_buff':return False
 owner=ctx['owner']
 for card in game.players[owner].hand:
  if game._card_data(card)['type']=='MINION' and has_tribe(game._card_data(card),'UNDEAD'):
   add_stat(card,'attack_bonus',op[1]);add_stat(card,'health_bonus',op[1])
 return True
