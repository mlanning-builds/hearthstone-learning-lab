"""Aya setup and physical counterfeit replacement, with explicit potion parts."""
from engine.game import Card
from engine.cards import UnsupportedCard
from .generation_cards import pool,random_cards
COINS=('JAIL_504t','JAIL_504t2','JAIL_504t3')
POTION='JAIL_504t3p'
DEMONS=pool(card_type='MINION',tribe='DEMON')
# Effect resolution order is explicit, distinct from randomized ingredient picks.
INGREDIENTS=(('damage',3),('area_damage','all_minions',2),('freeze_random_enemies',1),
 ('summon','CFM_621_m2',1),('counterfeit_resurrect',),('board_buff',0,2),
 ('draw',1),random_cards(DEMONS),('armor',4))
RULES={'JAIL_504':('none',[('counterfeit_choose',)])}
TOKEN_RULES={COINS[0]:('none',[('temporary_mana',1),('counterfeit_jade',)]),
 COINS[1]:('none',[('temporary_mana',1),('damage_random_enemy_minion',2)]),
 COINS[2]:('none',[('temporary_mana',1),('counterfeit_potion',)]),
 POTION:('none',[('crafted_spell',)])}
def requests_for(cid):return {DEMONS} if cid=='JAIL_504' else set()
class Counterfeits:
 def _aya_setup(self):
  players=[i for i in range(2) if 'JAIL_504' in self._opening_effect_ids(i)]
  if len(players)==1:self.first_player=1-players[0]
  elif len(players)==2:self.first_player=self.rng.randrange(2)
  self.current=self.first_player
  return self.first_player
 def _replace_coin(self,owner,card):
  from .cards import COIN_IDS
  identity=getattr(self.players[owner],'counterfeit_coin',None)
  if identity and card.card_id in COIN_IDS|set(COINS):card.card_id=identity
 def _crafted_rule(self,card):
  state=getattr(card,'rule_state',{})
  if 'crafted_ops' not in state:return None
  return state.get('crafted_target','none'),state['crafted_ops']
 def _counterfeit_effect(self,op,ctx):
  owner=ctx['owner'];p=self.players[owner];name=op[0]
  if name=='counterfeit_choose':
   if any(cid not in self.cards for cid in COINS):raise UnsupportedCard('Missing counterfeit Coins')
   self.pending_choice=dict(owner=owner,kind='counterfeit',options=[dict(card_id=cid) for cid in COINS]);self.phase='choice'
  elif name=='counterfeit_potion':
   self._generation_candidates(DEMONS,owner)
   if POTION not in self.cards or 'CFM_621_m2' not in self.cards:raise UnsupportedCard('Missing Kazakus potion dependencies')
   selected=sorted(self.rng.sample(range(len(INGREDIENTS)),2))
   card=Card(self._new_id(),POTION)
   card.rule_state=dict(crafted_ops=tuple(INGREDIENTS[i] for i in selected),crafted_target='character' if 0 in selected else 'none')
   self._enter_hand(owner,card)
  elif name=='counterfeit_jade':
   size=min(30,getattr(p,'jade_size',0)+1);p.jade_size=size
   m=self._summon(owner,'JAIL_504tt01',attack_bonus=size-1,health_bonus=size-1,entry_origin='effect',entry_site='counterfeit_jade')
   if m:m.base_stat_override=(size,size)
  elif name=='counterfeit_resurrect':
   if p.death_history:self._summon(owner,self.rng.choice(p.death_history),entry_origin='resurrection',entry_site='counterfeit_potion')
  elif name=='crafted_spell':
   raise UnsupportedCard('Custom spell has no physical crafted payload')
  else:return False
  return True
 def _counterfeit_choice(self,choice,selected):
  if choice['kind']!='counterfeit':return False
  owner=choice['owner'];p=self.players[owner];p.counterfeit_coin=selected['card_id']
  for c in p.hand+p.deck:
   if isinstance(c,Card):self._replace_coin(owner,c)
  for _ in range(3):self._add(owner,selected['card_id'])
  return True
