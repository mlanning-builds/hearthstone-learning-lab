"""Historical Sidequests sharing the existing public quest-zone list."""
def op(name,*args):return ('historical_utility_sidequest_batch_'+name,)+args
TOTALS={'DRG_008':5,'DRG_051':10,'DRG_251':3,'DRG_255':3,'DRG_258':1,'DRG_317':2}
REWARDS={
 'DRG_008':(('board_buff',1,1),),
 'DRG_051':(('historical_copy_recruit_one','deck',(('type','eq','MINION'),),None,None),),
 'DRG_251':(('summon','DRG_251t',1),),
 'DRG_255':(('summon','DRG_255t2',3),),
 'DRG_258':(('summon','DRG_258t',1),),
 'DRG_317':(('add','CS2_005',3),),
}
TOKEN_RULES={cid:('none',[op('start',cid)]) for cid in TOTALS}
TOKEN_RULES.update({cid:('none',[]) for cid in ('DRG_251t','DRG_255t2','DRG_258t')})
DEATH_EFFECTS={'DRG_255t2':[('damage_enemy_hero',2)]}
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

def summon_listener(game,owner):return any(q['card_id'] in ('DRG_008','DRG_251') for q in getattr(game.players[owner],'historical_mage_sidequests',()))

def complete(game,owner,quest):
 p=game.players[owner];quests=p.historical_mage_sidequests
 if quest not in quests:return
 quests.remove(quest);cid=quest['card_id'];game._log('quest_complete',player=owner,card=cid)
 game._rule_events.append(('captured_effects',dict(operations=REWARDS[cid],context=dict(owner=owner,source=None,target=0,bonus=0,lifesteal=False,card_id=cid)),[]))

def event(game,kind,data):
 if kind=='damage' and data.get('target',0)<0 and data.get('amount',0)>0:
  side=-data['target']-1
  for quest in getattr(game.players[side],'historical_mage_sidequests',()):
   if quest['card_id']=='DRG_258':quest['damaged']=True;quest['progress']=0
 owner=data.get('owner')
 if owner not in (0,1):return
 p=game.players[owner]
 for quest in tuple(getattr(p,'historical_mage_sidequests',())):
  cid=quest['card_id'];amount=0
  if cid=='DRG_008' and kind=='minion_summoned':amount=1
  elif cid=='DRG_051' and kind=='minion_played':amount=max(0,data.get('cost',0))
  elif cid=='DRG_251' and kind=='minion_summoned' and 'RUSH' in data.get('entry_keywords',()):amount=1
  elif cid=='DRG_255' and kind=='hero_power_used':amount=1
  elif cid=='DRG_317' and kind=='hero_attack':amount=1
  if not amount:continue
  quest['progress']=min(quest['total'],quest['progress']+amount);game._log('quest_progress',player=owner,card=cid,progress=quest['progress'])
  if quest['progress']>=quest['total']:complete(game,owner,quest)

def turn_entries(game,phase):
 if phase!='start':return []
 return [dict(source=None,order=quest['uid'],card_id='DRG_258',operations=(op('sanctuary',quest['uid']),)) for quest in getattr(game.players[game.current],'historical_mage_sidequests',()) if quest['card_id']=='DRG_258']

def execute(game,operation,ctx):
 name=operation[0];owner=ctx['owner'];p=game.players[owner]
 if name==op('start')[0]:
  cid=operation[1];quests=getattr(p,'historical_mage_sidequests',[])
  if any(q['card_id']==cid for q in quests) or len(p.secrets)+game._quest_slots(owner)>=5:
   game._log('quest_fizzle',player=owner,card=cid,reason='duplicate_or_capacity');return True
  quests.append(dict(card_id=cid,progress=0,total=TOTALS[cid],uid=game._new_id(),damaged=False));p.historical_mage_sidequests=quests
  game._log('quest_start',player=owner,card=cid);return True
 if name==op('sanctuary')[0]:
  quest=next((q for q in getattr(p,'historical_mage_sidequests',()) if q.get('uid')==operation[1]),None)
  if quest is not None:
   if not quest['damaged']:quest['progress']=1;complete(game,owner,quest)
   else:quest['damaged']=False
  return True
 return False
