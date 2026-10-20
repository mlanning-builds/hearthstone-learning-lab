"""Generated numeric spell effects with captured physical draw/damage state."""
from .selectors import has_class
from .historical_saidan import add as add_stat
TOKEN_RULES={
 'RLK_206':('none',[('historical_numeric_mark',)]),
 'RLK_553':('none',[('historical_numeric_prescience',)]),
 'RLK_553t':('none',[]),
 'RLK_601':('none',[('historical_numeric_last_stand',)]),
 'RLK_804':('minion',[('historical_numeric_arrow',)]),
 'RLK_819':('none',[('historical_numeric_eversong',)]),
 'RLK_819t':('none',[]),
 'TSC_702':('none',[('historical_numeric_switcheroo',)]),
 'TSC_211':('friendly_minion',[('historical_numeric_whispers',)]),
 'TSC_923':('none',[('historical_numeric_bioluminescence',)]),
 'TOY_800':('character',[('historical_numeric_phial',)]),
 'REV_939':('minion',[('historical_damage_then',3,'dead',(('historical_copy_coolant',),))]),
 'NX2_004':('minion',[('historical_numeric_ransack',)]),
 'JAM_013':('friendly_minion',[('buff',3,3),('historical_numeric_jam_damage',)]),
 'NX2_020':('minion',[('historical_numeric_cannibalize',)]),
}
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)


def split(game,op,ctx):
 name=op[0];p=game.players[ctx['owner']]
 if name in ('historical_numeric_mark','historical_numeric_last_stand'):
  state={};filters=None if name=='historical_numeric_mark' else (('type','eq','MINION'),('mechanic','eq','TAUNT'))
  return ('historical_draw_capture',filters,'random',state),(('historical_numeric_draw_finish',name,state),)
 if name=='historical_numeric_prescience':
  states=({},{});operations=tuple(operation for state in states for operation in (('historical_draw_capture',(('type','eq','MINION'),),'random',state),('historical_numeric_spirit',state)))
  return operations[0],operations[1:]
 if name in ('historical_numeric_arrow','historical_numeric_phial'):
  state=dict(manathirst=p.max_mana>=6)
  return ('historical_numeric_damage_capture',2,state),(('historical_numeric_damage_finish',name,state),)
 if name=='historical_numeric_switcheroo':
  a={};b={}
  return ('historical_draw_capture',(('type','eq','MINION'),),'random',a),(('historical_draw_capture',(('type','eq','MINION'),),'random',b),('historical_numeric_swap_health',a,b))
 if name=='historical_numeric_whispers':
  state={}
  return ('historical_numeric_silence_snapshot',state),(('historical_numeric_attack_missiles',state),)
 if name=='historical_numeric_attack_missiles':return game._split_fixed_summon(('missiles','enemy_minions',op[1].get('attack',0)),ctx)
 if name=='historical_numeric_eversong':return game._split_fixed_summon(('summon','RLK_819t',max(0,1+ctx.get('bonus',0))),ctx)
 if name=='historical_numeric_cannibalize':
  target=next((m for player in game.players for m in player.minions if m.uid==ctx.get('target') and m.health>0),None)
  return (('destroy',),(('historical_numeric_heal_friendly',target.health),)) if target is not None else (('batch30_noop',),())
 return None


def execute(game,op,ctx):
 owner=ctx['owner'];p=game.players[owner];name=op[0]
 target=next((m for player in game.players for m in player.minions if m.uid==ctx.get('target') and m.health>0),None)
 if name=='historical_numeric_damage_capture':op[2]['damage']=game._deal_effect(ctx.get('target',0),op[1],ctx)
 elif name=='historical_numeric_damage_finish':
  amount=op[2].get('damage',0)
  if op[1]=='historical_numeric_arrow':
   if op[2]['manathirst']:game._effect(('draw',amount),ctx)
  elif amount:p.cost_effects.append(dict(selector='ALL',amount=amount,remaining_uses=1,expires=game.turn))
 elif name=='historical_numeric_draw_finish':
  card=op[2].get('card')
  if card is None:return True
  if op[1]=='historical_numeric_mark' and game._card_data(card)['type']!='MINION':
   values=[(game.hero_id(1-owner),game.players[1-owner].health)]+[(m.uid,m.health) for m in game.players[1-owner].minions if m.health>0]
   if values:
    low=min(health for _,health in values);uid=game.rng.choice([uid for uid,health in values if health==low]);game._deal_effect(uid,4,ctx)
  elif op[1]=='historical_numeric_last_stand' and p.max_mana>=7:
   attack=game._card_stat(card,'attack',owner);health=game._card_stat(card,'health',owner)
   add_stat(card,'attack_bonus',attack);add_stat(card,'health_bonus',health)
 elif name=='historical_numeric_spirit':
  if op[1].get('card') is not None and op[1].get('cost',0)>=5:game._summon(owner,'RLK_553t',entry_origin='effect',entry_site='prescience')
 elif name=='historical_numeric_swap_health':
  a=op[1].get('card');b=op[2].get('card')
  if a is not None and b is not None:
   ah=game._card_stat(a,'health',owner);bh=game._card_stat(b,'health',owner)
   game._mutation_set_stats(a,owner,game._card_stat(a,'attack',owner),bh)
   game._mutation_set_stats(b,owner,game._card_stat(b,'attack',owner),ah)
 elif name=='historical_numeric_silence_snapshot':
  if target is not None:game._silence(target);op[1]['attack']=target.attack
 elif name=='historical_numeric_bioluminescence':
  for minion in p.minions:minion.rule_state['historical_spell_damage']=minion.rule_state.get('historical_spell_damage',0)+1
 elif name=='historical_numeric_ransack':
  records=[r for r in getattr(p,'_historical_paid_card_records',()) if r['turn']==game.turn]
  foreign=any(not has_class(game.cards[r['card_id']],p.hero_class) and not has_class(game.cards[r['card_id']],'NEUTRAL') for r in records)
  game._deal_effect(ctx.get('target',0),4 if foreign else 1,ctx)
 elif name=='historical_numeric_jam_damage':
  if target is not None:
   with game._damage_batch():
    for player in game.players:
     for minion in tuple(player.minions):
      if minion is not target:game._deal_effect(minion.uid,1,ctx)
 elif name=='historical_numeric_heal_friendly':
  for uid in (game.hero_id(owner),)+tuple(m.uid for m in p.minions):game._heal(uid,op[1],healer=owner,spell=ctx.get('spell',False))
 else:return False
 return True
