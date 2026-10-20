"""Complete literal Portal/Plague/Ranked dependencies for Transfer Student.

All new bodies and shared rank transitions are unvalidated. Broad random
summons/transforms retain full generation contracts and admission checks.
"""
from .generation_cards import pool,random_cards,board_pool
from .pools import require_fixed_cards

BASES=('BAR_034','BAR_044','BAR_305','BAR_314','BAR_319','BAR_536','BAR_842','BAR_880','BAR_891','BAR_914')
RANKS={base:(base,base+'t',base+'t2') for base in BASES}
RANK_INDEX={cid:(base,index) for base,forms in RANKS.items() for index,cid in enumerate(forms)}
TOKEN_RULES={
 'KAR_073':('none',[('area_damage','enemy_minions',1),random_cards(pool(card_type='MINION',minimum=1,maximum=1),destination='board')]),
 'KAR_075':('character',[('heal',6),random_cards(pool(card_type='MINION',minimum=6,maximum=6),destination='board')]),
 'KAR_076':('character',[('damage',6),random_cards(pool(card_type='MINION',minimum=6,maximum=6),destination='board')]),
 'KAR_077':('minion',[('buff',2,2),random_cards(pool(card_type='MINION',minimum=2,maximum=2),destination='board')]),
 'KAR_091':('none',[('armor',4),random_cards(pool(card_type='MINION',minimum=4,maximum=4),destination='board')]),
 'ULD_172':('none',[('historical_student_spell_murlocs',)]),
 'ULD_707':('none',[('historical_student_spell_wrath',)]),
 'ULD_715':('none',[('equip','ULD_715t'),('historical_student_spell_other_knife',)]),
 'ULD_717':('none',[('historical_student_spell_flames',)]),
 'ULD_718':('none',[('historical_student_spell_death',)]),
 'ULD_715t':('none',[]), # Printed Poisonous weapon.
 'BAR_034t3':('none',[]),'BAR_034t4':('none',[]),'BAR_034t5':('none',[]),
 'BAR_914t3':('none',[]),
}
for rank in range(3):
 suffix=('','t','t2')[rank];n=rank+1
 TOKEN_RULES.update({
  'BAR_034'+suffix:('none',[('summon',('BAR_034t3','BAR_034t4','BAR_034t5')[rank],1)]),
  'BAR_044'+suffix:('minion',[('historical_student_spell_chain',rank+2)]),
  'BAR_305'+suffix:('none',[('historical_student_spell_freeze',n)]),
  'BAR_314'+suffix:('none',[('area_damage','enemy_minions',n)]),
  'BAR_319'+suffix:('character',[('damage',2*n)]),
  'BAR_536'+suffix:('none',[('historical_draw_batch',(('type','eq','MINION'),('tribe','eq','BEAST')),'discount',(n,),'random')]),
  'BAR_842'+suffix:('none',[('historic_zone_buff','hand',None,n,n)]),
  'BAR_880'+suffix:('none',[('historical_student_spell_conviction',n)]),
  'BAR_891'+suffix:('none',[('hero_attack',rank+2)]),
  'BAR_914'+suffix:('none',[('summon','BAR_914t3',n)]),
 })
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)


def upgrade_card(game,owner,card):
 spec=RANK_INDEX.get(card.card_id)
 if spec is None:return
 base,current=spec;mana=game.players[owner].max_mana
 rank=max(current,2 if mana>=10 else 1 if mana>=5 else 0)
 target=RANKS[base][rank]
 require_fixed_cards((target,),game.cards)
 # Preserve actual physical discounts, enchantments and provenance. Ranked
 # upgrades are permanent and never downgrade after losing Mana Crystals.
 card.card_id=target


def refresh_hand_ranks(game):
 for owner,player in enumerate(game.players):
  for card in tuple(player.hand):upgrade_card(game,owner,card)


def split(game,op,ctx):
 if op[0]=='historical_student_spell_other_knife':
  return game._split_fixed_summon(('replay_context',(('equip','ULD_715t'),),dict(ctx,owner=1-ctx['owner'])),ctx)
 if op[0]=='historical_student_spell_flames':
  state={}
  return ('historical_student_spell_sacrifice',state),(('historical_student_spell_flames_finish',state),)
 return None


def execute(game,op,ctx):
 name=op[0];owner=ctx['owner'];p=game.players[owner]
 if name=='historical_student_spell_chain':
  target=next((m for player in game.players for m in player.minions if m.uid==ctx.get('target') and m.health>0),None)
  if target is not None:
   board=game.players[target.owner].board;index=board.index(target)
   adjacent=[m for i,m in enumerate(board) if abs(i-index)==1 and m in game.players[target.owner].minions and m.health>0]
   chosen=game.rng.choice(adjacent) if adjacent else None
   with game._damage_batch():
    game._deal_effect(target.uid,op[1],ctx)
    if chosen is not None:game._deal_effect(chosen.uid,op[1],ctx)
 elif name=='historical_student_spell_freeze':
  targets=[m for m in game.players[1-owner].minions if m.health>0]
  for target in game.rng.sample(targets,min(op[1],len(targets))):game._freeze(target.uid)
 elif name=='historical_student_spell_conviction':
  targets=[m for m in p.minions if m.health>0]
  for target in game.rng.sample(targets,min(op[1],len(targets))):game._buff(target,3,0)
 elif name=='historical_student_spell_murlocs':
  request=board_pool(pool(card_type='MINION',tribe='MURLOC'))
  values=game._generation_created_candidates(request,ctx)
  if values:
   targets=[m for player in game.players for m in player.minions if m.health>0]
   replacements=[(m,game.rng.choice(values)) for m in targets]
   for target,cid in replacements:
    if target in game.players[target.owner].minions:game._transform(target,cid)
 elif name=='historical_student_spell_wrath':
  for player in game.players:
   for target in player.minions:
    if 0<target.health<target.max_health and not game._fire_immune_target(target.uid,ctx):target.health=0
 elif name=='historical_student_spell_death':
  targets=[m for player in game.players for m in player.minions if m.health>0]
  for target in targets:game._silence(target)
  for target in targets:
   if target in game.players[target.owner].minions and not game._fire_immune_target(target.uid,ctx):target.health=0
 elif name=='historical_student_spell_sacrifice':
  targets=[m for m in p.minions if m.health>0 and not game._fire_immune_target(m.uid,ctx)]
  op[1]['destroyed']=len(targets)
  for target in targets:target.health=0
 elif name=='historical_student_spell_flames_finish':
  targets=[m for m in game.players[1-owner].minions if m.health>0 and not game._fire_immune_target(m.uid,ctx)]
  chosen=game.rng.sample(targets,min(op[1].get('destroyed',0),len(targets)))
  for target in chosen:target.health=0
 else:return False
 return True

RANKS['ONY_016']=('ONY_016','ONY_016t','ONY_016t2')
RANK_INDEX.update({cid:('ONY_016',index) for index,cid in enumerate(RANKS['ONY_016'])})
