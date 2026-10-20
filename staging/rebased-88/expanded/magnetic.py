"""Explicit Constructed Magnetic attachments; no inferred card admission."""
from .historical_saidan import add as _saidan_add
from copy import deepcopy
from engine.cards import UnsupportedCard
from .selectors import has_tribe
MAGNETIC_IDS=frozenset(('BOT_906','BOT_911','DEEP_015','TTN_852','BOT_020','BOT_021','BOT_035','BOT_237','BOT_548','BOT_563','TTN_087','BOT_251','BOT_312','TTN_921','TTN_734','TTN_730t','BOT_107','BOT_700','TTN_077'))
MAGNETIC_IDS=MAGNETIC_IDS|frozenset(('TTN_471','TTN_700','TTN_923'))
MAGNETIC_IDS=MAGNETIC_IDS|frozenset(('TTN_719t',)+tuple('TTN_719t'+str(i) for i in range(1,8)))
RULES={cid:('none',[]) for cid in MAGNETIC_IDS|{'TTN_906'}}
ATTACK_EFFECTS={'TTN_852':[('magnetic_hand_buff',)],'TTN_921':[('add','TOKEN_COIN',1)]}
TRIGGERS={cid:('attacked_self',ops) for cid,ops in ATTACK_EFFECTS.items()}
from .generation_cards import pool,random_cards
DEATH_EFFECTS={'TTN_700':[random_cards(pool(card_type='MINION',minimum=8,maximum=8),destination='board')],'BOT_700':[('summon','BOT_312t',2)],'TTN_734':[('historical_event_transfer_buff','MECHANICAL',2,2)],'TTN_906':[('magnetic_return',)],'BOT_251':[('destroy_random_enemy',)],'BOT_312':[('summon','BOT_312t',3)]}
FIXED_TOKEN_IDS=frozenset(('BOT_312t',))
RULES['BOT_312t']=('none',[])
class Magnetic:
 def _magnetic_target(self,card,owner,position):
  if card.card_id not in MAGNETIC_IDS:return None
  board=self.players[owner].board
  if not 0<=position<len(board):return None
  m=board[position]
  if m not in self.players[owner].minions or m.health<=0 or m.dormant:return None
  d=self._card_data(m)
  return m if has_tribe(d,'MECHANICAL') or card.card_id=='DEEP_015' and has_tribe(d,'UNDEAD') or card.card_id=='TTN_087' and has_tribe(d,'BEAST') else None
 def _magnetic_attach(self,card,owner,position,grants,*,notify=True):
  m=self._magnetic_target(card,owner,position)
  if m is None:return False
  if self._dark_list(card):raise UnsupportedCard('Magnetic Dark Gift transfer needs an explicit attachment contract')
  state=getattr(card,'rule_state',{})
  if any(key in state for key in ('forge_parts','crafted_ops','stored_spell','shatter_combined')):raise UnsupportedCard('Composite Magnetic transfer needs an explicit attachment contract')
  self._buff(m,self._card_stat(card,'attack',owner),self._card_stat(card,'health',owner))
  keywords=set(self.cards[card.card_id].get('mechanics',()))-{'MAGNETIC','TRIGGER_VISUAL','BATTLECRY'}
  keywords.update(state.get('extra_keywords',()));keywords.update(k for k in grants if k)
  if card.card_id=='TTN_923':
   keywords.discard('STEALTH');self._temporary_keyword(m,'STEALTH','next_start')
  m.keywords.update(keywords)
  m.attached_death_effects.extend(DEATH_EFFECTS.get(card.card_id,()))
  m.rule_state.setdefault('magnetic_parts',[]).append(dict(uid=card.uid,card_id=card.card_id))
  upgrades=getattr(m,'_magnetic_upgrades',[]);upgrades.append((deepcopy(card),tuple(grants)));m._magnetic_upgrades=upgrades
  if notify:
   self._queue_event('historical_magnetized',owner=owner,target=m.uid,card_id=card.card_id)
   self._log('magnetize',player=owner,card=card.card_id,target=m.uid)
  return True
 def _magnetic_listeners(self):
  return [(m,(('magnetic_attack',part['uid'],part['card_id']),ATTACK_EFFECTS[part['card_id']]))
    for p in self.players for m in p.minions if m.health>0
    for part in m.rule_state.get('magnetic_parts',()) if part['card_id'] in ATTACK_EFFECTS]
 def _magnetic_trigger_matches(self,wanted,kind,data,m):
  if not isinstance(wanted,tuple) or wanted[0]!='magnetic_attack':return None
  return (not m.dormant and kind=='minion_attack' and data['source']==m.uid and any(part['uid']==wanted[1] and part['card_id']==wanted[2] for part in m.rule_state.get('magnetic_parts',())))
 def _magnetic_effect(self,op,ctx):
  owner=ctx['owner'];p=self.players[owner]
  if op[0]=='magnetic_hand_buff':
   choices=[c for c in p.hand if self.cards[c.card_id]['type']=='MINION']
   if choices:
    c=self.rng.choice(choices);_saidan_add(c,'attack_bonus',1);_saidan_add(c,'health_bonus',1)
  elif op[0]=='magnetic_return':
   source=ctx.get('source')
   for part in source.rule_state.get('magnetic_parts',()) if source is not None else ():
    self._add(owner,part['card_id'])
  else:return False
  return True
