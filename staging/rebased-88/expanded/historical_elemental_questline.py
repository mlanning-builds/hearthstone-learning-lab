"""Pinned Command the Elements stages and permanent Bru'kan reward, unvalidated."""
STAGES={'SW_031':(3,'SW_031t'),'SW_031t':(3,'SW_031t2'),'SW_031t2':(2,'SW_031t7')}
def played(game,owner):
 quest=game.players[owner].quest
 if quest and quest['card_id'] in STAGES:game._quest_progress(owner,1)
def deliver(game,owner):
 player=game.players[owner];quest=player.quest
 if not quest or quest['card_id'] not in STAGES:return False
 cid=quest['card_id'];total,reward=STAGES[cid]
 if quest['progress']<total:return True
 if cid=='SW_031t2':
  if len(player.hand)>=getattr(player,'hand_capacity',10):return True
  player.quest=None;game._add(owner,reward)
 else:
  player.quest=dict(card_id=reward,progress=0,total=STAGES[reward][0])
  operations=(('unlock_mana',),) if cid=='SW_031' else (('summon','SW_031t8',1),)
  context=dict(owner=owner,source=None,target=0,bonus=0,lifesteal=False,card_id=cid)
  game._rule_events.append(('captured_effects',dict(operations=operations,context=context),[]))
 game._log('quest_reward_delivered',player=owner,card=reward)
 return True
