"""Private hand choices and next-opponent-turn exact-name watches."""
from .generation_cards import pool
RULES={'JAIL_851':('none',[('investigate_hand',)]),'TIME_041':('none',[('guess_hand',)])}
DECOYS=pool(classes='own_or_neutral')
def requests_for(cid):return {DECOYS} if cid=='TIME_041' else set()
class HandInvestigations:
 def _investigation_effect(self,op,ctx):
  name=op[0];owner=ctx['owner'];enemy=self.players[1-owner]
  if name not in ('investigate_hand','guess_hand'):return False
  if not enemy.hand:return True
  if name=='investigate_hand':
   offer=self.rng.sample(enemy.hand,min(4,len(enemy.hand)))
   self.pending_choice=dict(owner=owner,kind='investigate_hand',options=[dict(card_id=c.card_id) for c in offer])
  else:
   pool_ids=self._generation_candidates(DECOYS,1-owner)
   names={self.cards[c.card_id]['name'] for c in enemy.hand}
   decoys=[cid for cid in pool_ids if self.cards[cid]['name'] not in names]
   correct=self.rng.choice(enemy.hand).card_id
   offer=[correct]+self.rng.sample(decoys,min(2,len(decoys)));self.rng.shuffle(offer)
   self.pending_choice=dict(owner=owner,kind='guess_hand',correct=correct,source_uid=getattr(ctx.get('source'),'uid',None),options=[dict(card_id=cid) for cid in offer])
  self.phase='choice';return True
 def _investigation_choice(self,choice,selected):
  owner=choice['owner'];p=self.players[owner]
  if choice['kind']=='investigate_hand':
   watches=getattr(p,'_hand_investigations',[])
   watches.append(dict(name=self.cards[selected['card_id']]['name'],enemy=1-owner,due=self.players[1-owner].turns_taken+1))
   p._hand_investigations=watches
  elif choice['kind']=='guess_hand':
   if selected['card_id']==choice['correct']:
    m=next((m for m in p.minions if m.uid==choice['source_uid']),None)
    if m is not None:self._buff(m,0,4)
  else:return False
  return True
 def _investigation_played(self,owner,card):
  beneficiary=1-owner;p=self.players[beneficiary];name=self._card_data(card)['name'];retained=[]
  for watch in getattr(p,'_hand_investigations',[]):
   due=watch['due'];current=self.players[owner].turns_taken
   if watch['enemy']==owner and due==current and self.current==owner and watch['name']==name:
    self._rule_events.append(('captured_effects',dict(operations=(('add','TOKEN_COIN',3),),context=dict(owner=beneficiary,source=None,target=0,bonus=0,lifesteal=False)),[]))
   elif due>=self.players[watch['enemy']].turns_taken:retained.append(watch)
  p._hand_investigations=retained
