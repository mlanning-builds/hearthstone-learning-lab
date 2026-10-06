"""Staged Tiny Pal ammunition choices and post-attack effects."""
from engine.cards import UnsupportedCard
from .generation_cards import pool,random_cards
AMMUNITION=tuple('JAIL_458t'+str(i) for i in range(1,5))
THREES=pool(card_type='MINION',minimum=3,maximum=3)
BATTLECRIES=pool(card_type='MINION',mechanic='BATTLECRY')
RULES={'JAIL_458':('none',[('tiny_choose',None)])}
TOKEN_RULES={cid:('none',[('tiny_choose',None)]) for cid in AMMUNITION}
WEAPON_TRIGGERS={cid:[('tiny_after_attack',cid)] for cid in AMMUNITION}
def requests_for(cid):return {THREES,BATTLECRIES} if cid=='JAIL_458' else set()
class TinyPal:
 def _tiny_effect(self,op,ctx):
  owner=ctx['owner'];p=self.players[owner]
  if op[0]=='tiny_choose':
   if not p.weapon:return True
   if len(op)>2 and getattr(p.equipped_card,'uid',None)!=op[2]:return True
   choices=[cid for cid in AMMUNITION if cid!=op[1]]
   if any(cid not in self.cards for cid in choices):raise UnsupportedCard('Missing Tiny Pal ammunition')
   self.pending_choice=dict(owner=owner,kind='tiny_ammunition',weapon_uid=getattr(p.equipped_card,'uid',None),options=[dict(card_id=cid) for cid in choices]);self.phase='choice'
  elif op[0]=='tiny_after_attack':
   cid=op[1]
   operations={AMMUNITION[0]:(('tiny_freeze',ctx['target']),),AMMUNITION[1]:(('area_damage','enemies',1),),AMMUNITION[2]:(random_cards(THREES,destination='board',keyword='TAUNT'),),AMMUNITION[3]:(random_cards(BATTLECRIES,cost_delta=-2),)}[cid]
   self._rule_events.append(('captured_effects',dict(operations=operations+(('tiny_choose',cid,ctx.get('weapon_uid')),),context=dict(owner=owner,source=None,target=0,bonus=0,lifesteal=False)),[]))
  elif op[0]=='tiny_freeze':
   targets=[self.hero_id(1-owner)]+[m.uid for m in self.players[1-owner].minions]
   targets=[uid for uid in targets if uid!=op[1]]
   for uid in self.rng.sample(targets,min(2,len(targets))):self._freeze(uid)
  else:return False
  return True
 def _tiny_choice(self,choice,selected):
  if choice['kind']!='tiny_ammunition':return False
  p=self.players[choice['owner']]
  if p.weapon and getattr(p.equipped_card,'uid',None)==choice['weapon_uid']:
   p.weapon['card_id']=selected['card_id'];p.equipped_card.card_id=selected['card_id']
  return True
