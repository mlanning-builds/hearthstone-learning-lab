"""Mage Sidequests and the three-stage Gambit; behavior unvalidated."""
from .generation_cards import pool
from .selectors import has_tribe
from engine.cards import UnsupportedCard
SCHOOLS=('FIRE','FROST','ARCANE')
STAGES=('SW_450','SW_450t','SW_450t2')
def op(name,*args):return ('historical_utility_mage_quest_'+name,)+args
TOKEN_RULES={
 'DRG_323':('none',[op('sidequest','DRG_323')]),
 'DRG_324':('none',[op('sidequest','DRG_324')]),
 'DRG_323t':('none',[]),
 'SW_450':('none',[op('gambit',0)]),
 'SW_450t':('none',[op('gambit',1)]),
 'SW_450t2':('none',[op('gambit',2)]),
 'SW_450t4':('none',[op('dawngrasp')]),
}
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

def enqueue(game,owner,operations,cid):
 game._rule_events.append(('captured_effects',dict(operations=tuple(operations),context=dict(owner=owner,source=None,target=0,bonus=0,lifesteal=False,card_id=cid)),[]))

def event(game,kind,data):
 owner=data.get('owner')
 if owner not in (0,1):return
 p=game.players[owner]
 if kind=='spell_played' and data.get('cost',0)>0:
  for quest in tuple(getattr(p,'historical_mage_sidequests',())):
   if quest['card_id']!='DRG_323':continue
   quest['progress']=min(8,quest['progress']+data['cost'])
   game._log('quest_progress',player=owner,card=quest['card_id'],progress=quest['progress'])
   if quest['progress']==8:
    p.historical_mage_sidequests.remove(quest);game._log('quest_complete',player=owner,card='DRG_323')
    enqueue(game,owner,(('summon','DRG_323t',1),),'DRG_323')
 if kind=='minion_played' and game.current==owner and has_tribe(game._event_card_data(data),'ELEMENTAL'):
  for quest in tuple(getattr(p,'historical_mage_sidequests',())):
   if quest['card_id']!='DRG_324':continue
   previous=quest.get('last_elemental_turn')
   if previous==p.turns_taken-1:
    p.historical_mage_sidequests.remove(quest);game._log('quest_complete',player=owner,card='DRG_324')
    enqueue(game,owner,(('filtered_draw',(('type','eq','SPELL'),),3),),'DRG_324')
   else:
    quest['progress']=1;quest['last_elemental_turn']=p.turns_taken
    game._log('quest_progress',player=owner,card='DRG_324',progress=1)
 if kind!='spell_cast':return
 quest=p.quest
 if not quest or not quest.get('mage_gambit'):return
 school=game.cards[data['card_id']].get('spellSchool')
 if school not in SCHOOLS or school in quest['seen']:return
 quest['seen'].append(school);quest['progress']=len(quest['seen'])
 game._log('quest_progress',player=owner,card=quest['card_id'],progress=quest['progress'])
 if quest['progress']<3:return
 stage=quest['stage'];cid=quest['card_id'];game._log('quest_complete',player=owner,card=cid)
 if stage<2:
  quest.update(stage=stage+1,card_id=STAGES[stage+1],progress=0,seen=[])
  reward=(('filtered_draw',(('type','eq','SPELL'),),1),) if stage==0 else (op('school_offer'),)
 else:p.quest=None;reward=(('add','SW_450t4',1),)
 enqueue(game,owner,reward,cid)

def turn_entries(game,phase):
 if phase!='start':return []
 owner=game.current
 if not any(q['card_id']=='DRG_324' for q in getattr(game.players[owner],'historical_mage_sidequests',())):return []
 return [dict(source=None,order=0,card_id='DRG_324',operations=(op('allies_reset'),))]

def execute(game,operation,ctx):
 prefix='historical_utility_mage_quest_'
 if not operation[0].startswith(prefix):return False
 name=operation[0][len(prefix):];owner=ctx['owner'];p=game.players[owner]
 if name=='sidequest':
  cid=operation[1];quests=getattr(p,'historical_mage_sidequests',[])
  if any(q['card_id']==cid for q in quests) or len(p.secrets)+game._quest_slots(owner)>=5:
   game._log('quest_fizzle',player=owner,card=cid,reason='duplicate_or_capacity');return True
  quests.append(dict(card_id=cid,progress=0,total=8 if cid=='DRG_323' else 2));p.historical_mage_sidequests=quests
  game._log('quest_start',player=owner,card=cid)
 elif name=='gambit':
  if p.quest is not None or len(p.secrets)+game._quest_slots(owner)>=5:
   game._log('quest_fizzle',player=owner,card=STAGES[operation[1]],reason='active_quest_or_capacity');return True
  p.quest=dict(card_id=STAGES[operation[1]],stage=operation[1],progress=0,total=3,seen=[],mage_gambit=True)
  game._log('quest_start',player=owner,card=p.quest['card_id'])
 elif name=='allies_reset':
  for quest in getattr(p,'historical_mage_sidequests',()):
   if quest['card_id']=='DRG_324' and quest.get('last_elemental_turn',-100)<p.turns_taken-1:quest['progress']=0
 elif name=='dawngrasp':p.historical_mage_spell_damage=getattr(p,'historical_mage_spell_damage',0)+3
 elif name=='school_offer':
  if game.pending_choice is not None:raise UnsupportedCard('Cannot overwrite Gambit Discover')
  requests=[pool(card_type='SPELL',school=school,classes='own_or_neutral') for school in SCHOOLS]
  pools=[game._generation_discover_candidates(request,ctx) for request in requests]
  ids=[game.rng.choice(list(values)) for values in pools if values]
  if ids:
   # One option from each eligible school, rather than three from their union.
   game.pending_choice=dict(owner=owner,kind='historical_mage_offer',mode='gambit',context=dict(ctx),options=[dict(card_id=cid) for cid in ids])
   game.phase='choice'
 else:return False
 return True
