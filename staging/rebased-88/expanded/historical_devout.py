"""Base-definition Deathrattle replay and alternating Xyrella powers."""
ROOT_RULES={
 'AV_207':('none',[('historical_devout_replay',)]),
 'EX1_323':('none',[('equip','EX1_323w')]),
}
FIXED_TOKEN_IDS=frozenset(('AV_207p','AV_207p2','EX1_tk33','EX1_tk34','EX1_323w'))


def flip(game,owner):
 power=game.players[owner].primary_power
 if power is not None and power['card_id'] in ('AV_207p','AV_207p2'):
  power['card_id']='AV_207p2' if power['card_id']=='AV_207p' else 'AV_207p'
  game._log('xyrella_power_flipped',player=owner,card=power['card_id'])


def base_source(game,owner,entity):
 from .game import Minion
 card=game._fresh_replay_card(entity);data=game._card_data(card)
 stats=getattr(card,'base_stat_override',None) or (data['attack'],data['health'])
 source=Minion(game._new_id(),card.card_id,owner,stats[0],stats[1],stats[1],set(data.get('mechanics',())),summoned_turn=game.turn)
 if getattr(card,'rule_state',{}).get('forge_parts') is not None:game._forge_entry(source,card)
 return source,card


def split(game,op,ctx):
 owner=ctx['owner']
 if op[0]=='historical_devout_replay':
  # Freeze the eligible death history before any replay can kill new minions.
  entities=[]
  for record in tuple(game.players[owner].death_records):
   entity=record['entity']
   source,card=base_source(game,owner,entity)
   if game._unrepeated_death_operations(source):entities.append(entity)
  game.rng.shuffle(entities)
  operations=tuple(('historical_devout_death',entity) for entity in entities)
  if not operations:return ('batch30_noop',),()
  first,tail=game._split_fixed_summon(operations[0],ctx)
  return first,tuple(tail)+operations[1:]
 if op[0]=='historical_devout_death':
  source,card=base_source(game,owner,op[1])
  operations=game._death_operations(source)
  context=dict(ctx,owner=owner,source=source,physical_card=card,card_id=card.card_id,target=0,spell=False,bonus=0,lifesteal='LIFESTEAL' in game._effective_keywords(source),automatic_choices=True,death_position=len(game.players[owner].board))
  return game._split_fixed_summon(('replay_context',operations,context),ctx)
 return None


def execute(game,op,ctx):
 if op[0]!='historical_devout_heal':return False
 if ctx.get('target',0):game._heal(ctx['target'],5,healer=ctx['owner'],power=True)
 return True
