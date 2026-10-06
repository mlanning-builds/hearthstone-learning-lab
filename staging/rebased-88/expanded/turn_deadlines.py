"""Staged owner-turn deadlines, independent of end-trigger multipliers."""
from engine.cards import UnsupportedCard
RULES={'JAIL_860':('none',[]),'TLC_602':('none',[('lost_city_start',)])}
class TurnDeadlines:
 def _deadline_start_game(self):
  for owner,p in enumerate(self.players):
   if 'JAIL_860' in self._opening_effect_ids(owner) and all(self.cards[cid]['cost']<=3 for cid in p.starting_deck):
    self._schedule_turn_effect(owner,'end',5,1,(('chef_set_mana',),),source_card_id='JAIL_860')
 def _deadline_turn_entries(self,phase):
  if phase!='end':return []
  p=self.players[self.current];q=p.quest
  if q and q.get('lost_city') and q['progress']<10:
   return [dict(source=None,order=q['uid'],operations=(('lost_city_tick',q['uid'],self.turn),))]
  return []
 def _deadline_effect(self,op,ctx):
  owner=ctx['owner'];p=self.players[owner]
  if op[0]=='chef_set_mana':
   p.max_mana=min(10,p.mana_capacity);p.mana=max(0,p.max_mana-p.locked_mana)
  elif op[0]=='lost_city_start':
   if p.quest is not None or len(p.secrets)>=5:return True
   if 'TLC_602t' not in self.cards:raise UnsupportedCard('Missing Lost City reward')
   p.quest=dict(card_id='TLC_602',progress=0,total=10,lost_city=True,uid=self._new_id(),last_tick=-1)
  elif op[0]=='lost_city_tick':
   q=p.quest
   if q and q.get('lost_city') and q['uid']==op[1] and q['last_tick']!=op[2] and p.health>0:
    q['last_tick']=op[2];q['progress']=min(10,q['progress']+1)
    self._log('quest_progress',player=owner,card='TLC_602',progress=q['progress'])
    self._quest_deliver_ready(owner)
  else:return False
  return True
