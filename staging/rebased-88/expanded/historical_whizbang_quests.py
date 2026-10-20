"""Quest Accepted's explicit three-quest exception; runtime validation deferred."""
from .pools import require_fixed_cards
from .historical_elemental_questline import STAGES
ROOTS=('UNG_942','ULD_291','SW_031')
TOTALS={'UNG_942':8,'ULD_291':6,**{cid:row[0] for cid,row in STAGES.items()}}
def active(player):return getattr(player,'whizbang_quests',[])
def begin(game,owner):
 require_fixed_cards(ROOTS+('UNG_942t','ULD_291p','SW_031t','SW_031t2','SW_031t7','SW_031t8'),game.cards)
 player=game.players[owner];quests=active(player)
 player.whizbang_quests=quests
 existing={q['card_id'] for q in quests}
 if player.quest:existing.add(player.quest['card_id'])
 if existing.intersection(STAGES):existing.add('SW_031')
 for cid in ROOTS:
  if cid in existing or len(player.secrets)+game._quest_slots(owner)>=5:continue
  quests.append(dict(card_id=cid,progress=0,total=TOTALS[cid]))
  player.quests_played+=1
  game._log('quest_started',player=owner,card=cid)
def progress(game,owner,kind):
 for quest in tuple(active(game.players[owner])):
  cid=quest['card_id']
  matches=(kind=='murloc' and cid=='UNG_942') or (kind=='battlecry' and cid=='ULD_291') or (kind=='overload' and cid in STAGES)
  if matches:
   quest['progress']=min(quest['total'],quest['progress']+1)
   game._log('quest_progress',player=owner,card=cid,progress=quest['progress'])
 game._quest_deliver_ready(owner)
def deliver(game,owner):
 player=game.players[owner];quests=active(player)
 for quest in tuple(quests):
  if quest['progress']<quest['total']:continue
  cid=quest['card_id'];operations=()
  if cid=='ULD_291':
   quests.remove(quest);game._replace_primary_power(owner,dict(card_id='ULD_291p'))
  elif cid in ('UNG_942','SW_031t2'):
   if len(player.hand)>=getattr(player,'hand_capacity',10):continue
   quests.remove(quest);game._add(owner,'UNG_942t' if cid=='UNG_942' else 'SW_031t7')
  elif cid in STAGES:
   following=STAGES[cid][1]
   quest.update(card_id=following,progress=0,total=TOTALS[following])
   operations=(('unlock_mana',),) if cid=='SW_031' else (('summon','SW_031t8',1),)
  if operations:
   context=dict(owner=owner,source=None,target=0,bonus=0,lifesteal=False,card_id=cid)
   game._rule_events.append(('captured_effects',dict(operations=operations,context=context),[]))
  game._log('quest_complete',player=owner,card=cid)
