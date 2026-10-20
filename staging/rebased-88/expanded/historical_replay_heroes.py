"""Historical Hero spell replay and power programs; fidelity review deferred."""
ROOT_RULES={
 'AV_200':('none',[('historical_replay_hero','schools')]),
 'TRL_065':('none',[('historical_replay_hero','played')]),
}
FIXED_TOKEN_IDS=frozenset(('AV_200p2','TRL_065h'))


def split(game,op,ctx):
 owner=ctx['owner'];player=game.players[owner]
 if op[0]=='historical_replay_hero':
  if op[1]=='played':
   cards=[record.card for record in tuple(player.replay_history) if game._card_data(record.card)['type']=='SPELL']
  else:
   groups={}
   for record in tuple(getattr(player,'_historical_cast_records',())):
    card=record['card'];school=game._card_data(card).get('spellSchool')
    if school:groups.setdefault(school,[]).append(card)
   # Choose a cast instance, retaining repeated-cast weighting. No-school
   # spells are absent because they do not represent a spell school.
   cards=[game.rng.choice(groups[school]) for school in sorted(groups)]
  game.rng.shuffle(cards)
  operations=tuple(('historical_copy_replay_cast',game._fresh_replay_card(card),'random') for card in cards)
  if not operations:return ('batch30_noop',),()
  first,tail=game._split_fixed_summon(operations[0],ctx)
  return first,tuple(tail)+operations[1:]
 if op[0]=='historical_arcane_burst':
  power=player.primary_power
  bonus=power.get('historical_arcane_burst_bonus',0) if power is not None and power['card_id']=='AV_200p2' else 0
  uid=ctx.get('target',0)
  victim=next((m for other in game.players for m in other.minions if m.uid==uid and m.health>0),None)
  state=dict(victim=victim,health=getattr(victim,'health',None),prior_damage=getattr(player,'historical_power_damage_total',0),power_uid=power.get('uid') if power else None)
  return ('historical_copy_power_hit','target',2+bonus),(('historical_arcane_burst_after',state),)
 return None


def execute(game,op,ctx):
 if op[0]!='historical_arcane_burst_after':return False
 player=game.players[ctx['owner']];state=op[1];victim=state['victim'];power=player.primary_power
 dealt=getattr(player,'historical_power_damage_total',0)-state['prior_damage']
 if (victim is not None and victim.health<=0 and dealt==state['health'] and dealt>0
     and power is not None and power['card_id']=='AV_200p2' and power.get('uid')==state['power_uid']):
  power['historical_arcane_burst_bonus']=power.get('historical_arcane_burst_bonus',0)+2
 return True
