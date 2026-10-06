"""Explicit finite construction trees for Elise locations and Kazakus trials."""
from copy import deepcopy
from engine.game import Card
from engine.cards import UnsupportedCard
from .generation_cards import pool,discover,random_cards
THREES=pool(card_type='MINION',minimum=3,maximum=3)
SPELLS=pool(card_type='SPELL',classes='own_or_neutral')
RULES={'CAP_405':('none',[('craft_trial',)]),'TLC_100':('none',[('craft_location',)])}
LOCATION_IDS=tuple('TLC_100t'+str(i) for i in (1,2,3))
TRIAL_IDS=tuple('CAP_405tb'+str(i) for i in (1,2,3))
TOKEN_RULES={cid:('none',[('crafted_spell',)]) for cid in TRIAL_IDS}
TOKEN_RULES.update({cid:('none',[]) for cid in LOCATION_IDS})
TOKEN_RULES['LOOT_368']=('none',[])
DEATH_EFFECTS={'LOOT_368':[('death_summon','CS2_065',3)]}
LOCATION_RULES={cid:'none' for cid in LOCATION_IDS}
TRIAL_PARTS={
 1:(('trial_fights',),),2:(('trial_control',),),3:(('trial_steal',),('trial_steal',)),
 4:(('draw',3),),5:(('hand_buff',3,3),('board_buff',3,3)),
 6:(random_cards(THREES,3,'board'),),7:(('osk_discount_minions',2),),
 8:(('heal_own_hero',12),),9:(('summon','LOOT_368',1),),
}
def requests_for(cid):return {THREES} if cid=='CAP_405' else {SPELLS} if cid=='TLC_100' else set()
class CustomBuilders:
 def _craft_offer(self,owner,kind,ids,**state):
  if any(cid not in self.cards for cid in ids):raise UnsupportedCard('Missing custom construction option')
  self.pending_choice=dict(owner=owner,kind=kind,options=[dict(card_id=cid) for cid in ids],**state);self.phase='choice'
 def _craft_trial_parts(self,owner,picked):
  ids=['CAP_405t'+str(i) for i in range(1,10) if i not in picked]
  self._craft_offer(owner,'craft_trial_parts',self.rng.sample(ids,3),picked=picked)
 def _craft_location_parts(self,owner,tier,picked):
  ids=['TLC_100t'+str(tier)+str(i) for i in range(1,8) if i not in picked and not(tier==1 and i==7)]
  self._craft_offer(owner,'craft_location_parts',self.rng.sample(ids,3),tier=tier,picked=picked)
 def _craft_effect(self,op,ctx):
  name=op[0];owner=ctx['owner'];p=self.players[owner];q=self.players[1-owner]
  if name=='craft_trial':self._craft_trial_parts(owner,[])
  elif name=='craft_location':
   if len({self.cards[cid]['cost'] for cid in p.starting_deck})>=10:self._craft_offer(owner,'craft_location_cost',LOCATION_IDS)
  elif name=='trial_wait':
   delay,operations=op[1:]
   self._schedule_turn_effect(owner,'start',delay,1,operations,source_card_id=ctx.get('card_id'))
  elif name=='trial_control':
   if q.minions:self._osk_effect(('osk_control',),dict(ctx,target=self.rng.choice(q.minions).uid))
  elif name=='trial_steal':
   if q.hand:
    card=q.hand.pop(self.rng.randrange(len(q.hand)));self._enter_hand(owner,card)
  elif name=='location_spell_bonus':p._next_spell_bonus=getattr(p,'_next_spell_bonus',0)+op[1]
  elif name=='location_attack':
   p.temporary_attack+=op[1]
   for m in p.minions:self._adjust_minion_attack(m,op[1]);m.temporary_attack+=op[1]
  elif name=='location_copy':
   options=[dict(card_id=m.card_id,uid=m.uid) for m in p.minions if m.health>0]
   if options:self.pending_choice=dict(owner=owner,kind='location_copy',size=op[1],options=options);self.phase='choice'
  else:return False
  return True
 def _craft_split(self,op,ctx):
  if op[0]=='trial_wait' and op[1]==0:return ('batch30_noop',),tuple(op[2])
  if op[0]=='trial_fights':
   ids=[m.uid for p in self.players for m in p.minions];self.rng.shuffle(ids)
   return ('batch30_noop',),tuple(('trial_attack',uid) for uid in ids)
  if op[0]=='trial_attack':
   source=self._force_live(op[1]);targets=[m.uid for p in self.players for m in p.minions if m.uid!=op[1] and m.health>0]
   return (('batch30_noop',),(('force_pair',op[1],self.rng.choice(targets)),)) if source and targets else (('batch30_noop',),())
 def _craft_choice(self,choice,selected):
  kind=choice['kind']
  if kind not in ('craft_trial_parts','craft_trial_length','craft_location_cost','craft_location_parts','location_copy'):return False
  owner=choice['owner'];cid=selected['card_id']
  if kind=='craft_trial_parts':
   picked=choice['picked']+[int(cid.removeprefix('CAP_405t'))]
   if len(picked)<2:self._craft_trial_parts(owner,picked)
   else:self._craft_offer(owner,'craft_trial_length',tuple(c+'b' for c in TRIAL_IDS),picked=picked)
  elif kind=='craft_trial_length':
   index=int(cid[-2])-1;card=Card(self._new_id(),TRIAL_IDS[index]);ops=tuple(op for n in choice['picked'] for op in TRIAL_PARTS[n])
   card.rule_state=dict(crafted_ops=(('trial_wait',(0,1,4)[index],ops),),crafted_target='none');self._enter_hand(owner,card)
  elif kind=='craft_location_cost':self._craft_location_parts(owner,int(cid[-1]),[])
  elif kind=='craft_location_parts':
   picked=choice['picked']+[int(cid[-1])];tier=choice['tier']
   if len(picked)<2:self._craft_location_parts(owner,tier,picked)
   else:
    value=(1,2,4)[tier-1];card=Card(self._new_id(),LOCATION_IDS[tier-1]);ops=[];death=[]
    for n in picked:
     if n==1:death.append(('area_damage','enemies',(1,3,5)[tier-1]))
     elif n==2:ops.append(('location_spell_bonus',value))
     elif n==3:ops.append(discover(SPELLS,cost_delta=-(1,4,7)[tier-1]))
     elif n==4:ops.append(('location_attack',value))
     elif n==5:ops.append(('summon','DINO_136t',value))
     elif n==6:ops.append(('armor',3*value))
     elif n==7:ops.append(('location_copy',(1,3,5)[tier-1]))
    card.rule_state=dict(crafted_location_ops=tuple(ops),crafted_location_death=tuple(death));self._enter_hand(owner,card)
  elif kind=='location_copy':
   m=self._force_live(selected['uid'])
   if m and m.owner==owner:
    copy=self._summon(owner,m.card_id,copy_from=m,entry_origin='effect',entry_site='elise_location')
    if copy:self._set_entity_stats(copy,choice['size'],choice['size'])
  else:return False
  return True
 def _crafted_location_entry(self,location,card):
  state=getattr(card,'rule_state',{})
  if location is not None and 'crafted_location_ops' in state:
   location.rule_state=deepcopy(state);location.attached_death_effects.extend(deepcopy(state['crafted_location_death']))
