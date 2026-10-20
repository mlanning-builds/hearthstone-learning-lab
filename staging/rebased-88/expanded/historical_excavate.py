"""Pinned Excavate recipes and physical rewards; gameplay validation deferred."""
from .historical_saidan import add as _saidan_add
from .generation_cards import pool, random_cards, discover

COMMON=('WW_001t','WW_001t2','WW_001t3','WW_001t4','WW_001t18','DEEP_999t1')
RARE=('WW_001t5','WW_001t7','WW_001t8','WW_001t9','WW_001t16','DEEP_999t2')
EPIC=('WW_001t11','WW_001t12','WW_001t13','WW_001t14','WW_001t17','DEEP_999t3')
CLASS_REWARDS={'ROGUE':'WW_001t23','MAGE':'WW_001t24','WARLOCK':'WW_001t25',
 'DEATHKNIGHT':'WW_001t26','WARRIOR':'WW_001t27','PALADIN':'DEEP_999t4','SHAMAN':'DEEP_999t5'}
DIG=('historical_excavate_dig',False)
RULES={cid:('none',[DIG]) for cid in ('WW_001','WW_002')}
RULES.update({'WW_322':('none',[('historical_excavate_dig',True)]),
 'WW_442':('none',[]),
 'DEEP_033':('none',[('historical_excavate_bonus',),DIG]),
 'WW_417':('none',[DIG])})
RULES.update({'WW_324':('none',[]),'WW_375':('none',[]),'DEEP_007':('none',[('historical_excavate_finley',)]),'WW_349':('none',[('historical_excavate_brawl',)]),'WW_356':('none',[('historical_excavate_discount',)]),'WW_413':('historical_excavate_enemy',[('historical_excavate_flinger',)]),'WW_426':('none',[DIG,('historical_excavate_miner',)]),'WW_432':('none',[('historical_excavate_secrets',)]),'WW_437':('none',[('historical_excavate_trams',)])})
DEATH_EFFECTS={'WW_442':[DIG],'WW_417':[DIG],'WW_324':[('historical_excavate_pile_wait',)]}
TOKEN_RULES={
 'WW_001t23':('none',[('historical_excavate_scorpion',)]),
 'WW_001t24':('none',[random_cards(pool(card_type='MINION',mechanic='TITAN'),set_cost=1)]),
 'WW_001t25':('none',[('historical_excavate_snake',)]),
 'WW_001t26':('none',[('historical_excavate_rat',)]),
 'WW_001t27':('none',[discover(pool(card_type='MINION',minimum=8,maximum=8,classes='own_or_neutral'),destination='board')]*2),
 'DEEP_999t4':('none',[('historical_excavate_dragon',)]),
 'DEEP_999t5':('none',[('historical_excavate_murloc',)]),
}
TOKEN_RULES['WW_437t']=('none',[])
FIXED_TOKEN_IDS=frozenset(CLASS_REWARDS.values())|{'WW_437t','PRO_001at'}

def targets(game,cid,owner,mode):
 if mode!='historical_excavate_enemy':return None
 return game._targets_for(cid,owner,'enemy_minion') if getattr(game.players[owner],'historical_excavations',0)>=2 else [0]

def split(game,op,ctx):
 if op[0]=='historical_excavate_miner':return game._split_fixed_summon(('missiles','enemies',len(game.players[ctx['owner']].hand)),ctx)
 if op[0]=='historical_excavate_trams':return game._split_fixed_summon(('summon','WW_437t',6),ctx) if getattr(game.players[ctx['owner']],'historical_excavations',0)>=2 else (('batch30_noop',),())
 if op[0]=='historical_excavate_secrets':
  if getattr(game.players[ctx['owner']],'historical_excavations',0)<2:return ('batch30_noop',),()
  from .automatic_casting import MAGE_SECRETS
  return game._split_fixed_summon(('autocast_random',MAGE_SECRETS,2),ctx)
 if op[0]!='historical_excavate_murloc':return None
 owner=ctx['owner'];p=game.players[owner];source=ctx.get('source');operations=[]
 for zone in ('hand','deck','board'):
  values=list(p.minions) if zone=='board' else list(getattr(p,zone))
  for card in values:
   if card is source or game._card_data(card)['type']!='MINION':continue
   cost=game._cost(card,owner) if zone=='hand' else game._card_stat(card,'cost',owner)
   request=pool(card_type='MINION',minimum=cost+3,maximum=cost+3)
   from .generation_cards import board_pool
   outcomes=game._generation_candidates(board_pool(request) if zone=='board' else request,owner)
   if outcomes:operations.append(('historical_excavate_transform',zone,card.uid,cost,game.rng.choice(outcomes)))
 return (operations[0],tuple(operations[1:])) if operations else (('batch30_noop',),())

def execute(game,op,ctx):
 name=op[0]
 if not name.startswith('historical_excavate_'):return False
 owner=ctx['owner'];p=game.players[owner];q=game.players[1-owner];source=ctx.get('source')
 if name=='historical_excavate_dig':
  from .pools import require_fixed_cards
  require_fixed_cards(COMMON+RARE+EPIC+tuple(CLASS_REWARDS.values()),game.cards)
  p.historical_excavations=getattr(p,'historical_excavations',0)+1
  maximum=4 if p.hero_class in CLASS_REWARDS else 3
  # Normalize the previous cycle to the current hero's maximum rarity.
  # A class without a Legendary loops Common/Rare/Epic, including after
  # changing class while the previous class was waiting for tier four.
  tier=getattr(p,'historical_excavate_tier',0)%maximum+1
  if tier==4:
   reward=CLASS_REWARDS[p.hero_class];tier=0
  else:
   reward=game.rng.choice((COMMON,RARE,EPIC)[tier-1])
   if tier==3 and p.hero_class not in CLASS_REWARDS:tier=0
  p.historical_excavate_tier=tier
  card=game._add(owner,reward)
  if card is not None and op[1]:game._set_card_cost(card,0)
  game._log('excavate',player=owner,total=p.historical_excavations,reward=reward)
  pending=getattr(p,'historical_piles_waiting',[]);p.historical_piles_waiting=[]
  if pending:game._rule_events.append(('captured_effects',dict(operations=tuple(('historical_excavate_pile_summon',card) for card in pending),context=dict(owner=owner,source=None,target=0,bonus=0,lifesteal=False)),[]))
  for minion in list(p.all_minions):
   if minion.card_id=='WW_375' and minion.dormant>0 and not minion.silenced:
    if minion.dormant<=2:game._awaken(minion)
    else:minion.dormant-=2
 elif name=='historical_excavate_pile_wait':
  if source is not None:
   pending=getattr(p,'historical_piles_waiting',[]);pending.append(game._fresh_replay_card(source));p.historical_piles_waiting=pending
 elif name=='historical_excavate_pile_summon':
  card=op[1];game._summon(owner,card.card_id,entry_origin='resurrection',entry_source=card,entry_site='pile_of_bones')
 elif name=='historical_excavate_finley':
  if getattr(p,'historical_excavations',0)>=2:
   for minion in list(q.minions):
    if minion.health>0:game._transform(minion,'PRO_001at')
 elif name=='historical_excavate_brawl':
  values=[m for player in game.players for m in player.minions if m.health>0]
  if values:
   survivor=source if getattr(p,'historical_excavations',0)>=2 and source in values else game.rng.choice(values)
   for minion in values:
    if minion is not survivor:minion.health=0
 elif name=='historical_excavate_discount':
  if getattr(p,'historical_excavations',0)>=2:p.cost_effects.append(dict(selector='ALL',amount=7,remaining_uses=1,expires=game.turn))
 elif name=='historical_excavate_flinger':
  if getattr(p,'historical_excavations',0)>=2:game._effect(('destroy',),ctx)
 elif name=='historical_excavate_bonus':
  if source in p.minions:game._grant_bonus_effects(source,2)
 elif name=='historical_excavate_scorpion':
  outcomes=game._generation_candidates(pool(card_type='SPELL'),owner)
  count=getattr(p,'historical_excavations',0)
  if outcomes:
   for _ in range(4):
    card=game._add(owner,game.rng.choice(outcomes))
    if card is not None:game._set_card_cost(card,max(1,game._card_stat(card,'cost',owner)-count))
 elif name=='historical_excavate_snake':
  q.max_health=max(0,q.max_health-10);q.health-=10;p.max_health+=10;p.health+=10
  game._log('steal_hero_health',player=owner,opponent=1-owner,amount=10)
 elif name=='historical_excavate_rat':
  records=list(p.death_records)
  if records:
   highest=max(game._card_stat(r['entity'],'cost',owner) for r in records)
   record=game.rng.choice([r for r in records if game._card_stat(r['entity'],'cost',owner)==highest])
   card=game._fresh_replay_card(record['entity'])
   game._summon(owner,card.card_id,attack_bonus=2,health_bonus=2,entry_keywords=('REBORN','LIFESTEAL'),entry_origin='resurrection',entry_source=card,entry_site='azerite_rat')
 elif name=='historical_excavate_dragon':
  for zone in ('hand','deck'):
   for card in getattr(p,zone):
    if game._card_data(card)['type']=='MINION':_saidan_add(card,'attack_bonus',3);_saidan_add(card,'health_bonus',3)
  for minion in list(p.minions):
   if minion is not source:game._buff(minion,3,3)
 elif name=='historical_excavate_transform':
  zone,uid,cost,cid=op[1:];values=p.minions if zone=='board' else getattr(p,zone)
  card=next((c for c in values if c.uid==uid),None)
  if card is not None:
   if zone=='board':card=game._transform(card,cid)
   else:game._b60_transform_card(card,cid)
   if card is not None:game._set_card_cost(card,cost)
 else:return False
 return True
