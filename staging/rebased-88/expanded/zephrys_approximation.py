"""Owner-authorized Zephrys/Wish approximation, NOT Blizzard's exact evaluator.

Pure public-state scoring; no game rollout, training, hidden-card access or
implemented-only filtering. Coefficients and category diversity are our design.
The complete 139-card researched historical candidate list is retained.
"""
from copy import deepcopy
from .pools import require_fixed_cards
POOL=('CS2_008', 'CS2_072', 'EX1_332', 'CS2_004', 'EX1_607', 'NEW1_003', 'NEW1_022', 'EX1_586', 'EX1_302', 'CS2_037', 'DS1_185', 'CS1_130', 'EX1_238', 'EX1_308', 'EX1_245', 'EX1_400', 'EX1_251', 'NEW1_017', 'NEW1_025', 'EX1_360', 'EX1_578', 'EX1_410', 'EX1_192', 'CS1_129', 'EX1_319', 'CS2_065', 'EX1_124', 'EX1_581', 'CS2_108', 'EX1_126', 'CS2_114', 'CS2_234', 'EX1_622', 'CS2_073', 'BT_035', 'CS2_025', 'CS2_105', 'CS2_039', 'CS2_009', 'EX1_160', 'EX1_195', 'EX1_059', 'EX1_066', 'EX1_544', 'EX1_096', 'EX1_339', 'EX1_392', 'CS2_089', 'EX1_539', 'EX1_134', 'EX1_241', 'EX1_617', 'EX1_259', 'BT_740', 'BT_036', 'BT_921', 'EX1_536', 'EX1_129', 'EX1_334', 'CS2_203', 'CS2_011', 'CS2_013', 'CS2_026', 'CS2_007', 'EX1_189', 'NEW1_031', 'EX1_613', 'EX1_590', 'EX1_014', 'CS2_023', 'BT_352', 'NEW1_027', 'EX1_507', 'EX1_103', 'EX1_197', 'EX1_246', 'CS1_112', 'EX1_303', 'CS2_062', 'CS2_029', 'DS1_183', 'CS2_012', 'CS2_097', 'EX1_626', 'EX1_158', 'EX1_093', 'CS2_092', 'EX1_043', 'EX1_186', 'EX1_194', 'CS2_033', 'DS1_070', 'EX1_407', 'BT_235', 'CS2_076', 'EX1_537', 'NEW1_007', 'BT_495', 'EX1_165', 'NEW1_041', 'EX1_005', 'CS2_046', 'CS2_080', 'CS2_112', 'EX1_567', 'EX1_623', 'EX1_564', 'EX1_558', 'EX1_355', 'EX1_250', 'EX1_309', 'CS2_028', 'EX1_384', 'CS2_042', 'EX1_002', 'EX1_091', 'CS2_064', 'EX1_534', 'EX1_164', 'CS2_032', 'EX1_249', 'CS2_088', 'EX1_411', 'DS1_188', 'EX1_190', 'EX1_178', 'CS2_077', 'EX1_312', 'EX1_198', 'EX1_383', 'EX1_354', 'BT_512', 'EX1_561', 'EX1_323', 'EX1_572', 'EX1_543', 'NEW1_030', 'CS1_113', 'EX1_279')
DIRECT={'CS2_008':1,'DS1_185':2,'EX1_238':3,'EX1_308':4,'CS2_029':6,'EX1_241':5,'EX1_279':10,'EX1_539':3,'EX1_124':2}
AREA={'CS2_032':4,'CS2_028':2,'CS2_062':3,'CS1_112':2,'EX1_259':3,'CS2_025':1,'CS2_012':1,'BT_235':4}
DESTROY_ALL={'EX1_312','EX1_407'}
SINGLE={'CS2_234','EX1_622','CS2_108','CS2_076','EX1_617','EX1_005','EX1_002','EX1_198','EX1_309','EX1_246','EX1_581'}
SILENCE={'EX1_332','EX1_245','CS2_203','EX1_626'}
WEAPON_REMOVAL={'EX1_066','EX1_558','NEW1_025'}
HEAL={'CS2_089':8,'CS2_007':8,'EX1_192':5,'CS2_088':6,'EX1_354':8}
DRAW={'CS2_023':2,'CS2_077':4,'EX1_354':3,'CS2_004':1,'EX1_278':1,'EX1_391':1,'EX1_339':2,'EX1_392':2}

def _ready(row,turn):
 keys=set(row.get('keywords',()))
 limit=4 if 'MEGA_WINDFURY' in keys else 2 if 'WINDFURY' in keys else 1
 return row.get('kind')=='MINION' and not row.get('dormant') and row.get('frozen_until',-1)<0 and row.get('attacks',0)<limit and (row.get('summoned_turn')!=turn or 'CHARGE' in keys or 'RUSH' in keys)

def evaluate(state,metadata):
 """Return three distinct offers. This entire ranking is approximate."""
 owner=state['owner'];p=state['players'][owner];q=state['players'][1-owner]
 own=[m for m in p['board'] if m['kind']=='MINION' and not m.get('dormant')]
 enemy=[m for m in q['board'] if m['kind']=='MINION' and not m.get('dormant')]
 mana=p['mana'];future=p.get('next_turn_mana_baseline',min(10,p['max_mana']+1))
 enemy_life=q['health']+q['armor'];life=p['health']+p['armor']
 pressure=sum(max(0,m['attack']) for m in enemy)
 threat=max((m['attack']+.45*m['health'] for m in enemy),default=0)
 taunts=[m for m in enemy if 'TAUNT' in m.get('keywords',()) and 'STEALTH' not in m.get('keywords',())]
 ready=[m for m in own if _ready(m,state['turn'])]
 face=sum(max(0,m['attack']) for m in ready if m.get('summoned_turn')!=state['turn'] or 'CHARGE' in m.get('keywords',())) if not taunts else 0
 if not taunts and not p.get('frozen') and p['hero_attacks']<p.get('hero_attack_limit',1):face+=p['hero_attack']
 scores=[]
 for cid in POOL:
  data=metadata[cid];cost=data['cost'];text=data.get('text','').lower();kind=data['type']
  # Giant discounts depend on public counts. Other cost modifiers deliberately
  # do not alter the printed-cost planning heuristic.
  if cid=='EX1_586':cost=max(0,cost-len(own)-len(enemy))
  if cid=='NEW1_022':cost=max(0,cost-(p['weapon']['attack'] if p.get('weapon') else 0))
  now=cost<=mana;soon=cost<=future
  score=0.;category='proactive'
  if kind=='MINION':
   score=data.get('attack',0)+.6*data.get('health',0)
   if len(p['board'])>=7:score-=40
   if 'TAUNT' in data.get('mechanics',()):score+=min(pressure,max(0,pressure-life+1))*1.5
   if 'CHARGE' in data.get('mechanics',()) and now and not taunts:score+=data.get('attack',0)*2
  elif kind=='WEAPON':
   score=data.get('attack',0)*min(2,data.get('durability',0))
   if p.get('weapon'):score-=p['weapon']['attack']*min(2,p['weapon']['durability'])
  else:score=1
  if cid in DIRECT:
   category='damage';damage=DIRECT[cid]+p.get('spell_damage',0)
   if cid=='EX1_539' and any('BEAST' in m.get('tribes',()) for m in own):damage+=2
   score=max(score,damage*1.5+min(damage,threat))
   if now and not q.get('immune') and not q.get('divine_shield') and damage+face>=enemy_life:
    score=100000+damage+face-enemy_life
  if cid in AREA or cid in DESTROY_ALL:
   category='area';damage=AREA.get(cid,100)+p.get('spell_damage',0)
   score=sum(m['attack']+m['health']*.4 for m in enemy if m['health']<=damage and 'DIVINE_SHIELD' not in m.get('keywords',()))
   score+=len(enemy)*1.5
   if cid in DESTROY_ALL or cid=='CS2_062':score-=sum(m['attack']+m['health']*.4 for m in own if m['health']<=damage)*.7
  if cid in SINGLE:
   category='removal';eligible=list(enemy)
   if cid=='CS2_234':eligible=[m for m in enemy if m['attack']<=3]
   if cid=='EX1_622':eligible=[m for m in enemy if m['attack']>=5]
   if cid=='EX1_005':eligible=[m for m in enemy if m['attack']>=7]
   if cid=='EX1_002':eligible=taunts
   if cid=='CS2_108':eligible=[m for m in enemy if m['health']<m['max_health']]
   score=max((m['attack']+.6*m['health'] for m in eligible),default=-15)
  if cid in SILENCE:
   category='silence';score=sum(5+max(0,m['attack']-3) for m in enemy if set(m.get('keywords',()))&{'TAUNT','DEATHRATTLE','DIVINE_SHIELD','REBORN','LIFESTEAL'})
   if cid!='EX1_626':score=min(score,threat+5)
   if now and taunts and sum(m['attack'] for m in ready)>=enemy_life:score+=50
  if cid in WEAPON_REMOVAL:
   category='weapon_removal';weapon=q.get('weapon');score=2 if not weapon else 5+weapon['attack']*min(2,weapon['durability'])
  if cid=='EX1_544':category='secret_removal';score=2+q.get('secret_count',0)*10
  if cid in HEAL:
   category='survival';healing=min(HEAL[cid],p['max_health']-p['health']);score=healing*(3 if pressure>=life else 1.1)
  if cid=='EX1_561':category='survival';score=max(p['max_health']-p['health'],q['health']-15)
  if cid in DRAW:
   category='draw';score+=DRAW[cid]*max(.2,4-p['hand_count']*.45)
   if not p['deck_count']:score-=30
  if cid in ('CS2_046','CS2_011'):
   category='buff';gain=3 if cid=='CS2_046' else 2;score=len(own)*gain
   if now and not q.get('immune') and not taunts and face+len(ready)*gain>=enemy_life:score+=100000
  if not now:score-=12 if soon else 35+max(0,cost-future)*3
  else:score+=4
  scores.append((score,category,cid))
 scores.sort(key=lambda row:(-row[0],POOL.index(row[2])))
 # Prefer different purposes unless another same-purpose option is markedly
 # better. The diversity margin is a local heuristic, not a Blizzard constant.
 selected=[];categories=set()
 while len(selected)<3:
  remaining=[row for row in scores if row[2] not in selected]
  best=remaining[0]
  distinct=next((row for row in remaining if row[1] not in categories),None)
  pick=distinct if distinct is not None and distinct[0]>=best[0]-8 else best
  selected.append(pick[2]);categories.add(pick[1])
 return tuple(selected)

def policy(cards):
 require_fixed_cards(POOL,cards)
 metadata={cid:deepcopy(cards[cid]) for cid in POOL}
 from .historical_zephrys import ZephrysPolicy
 return ZephrysPolicy(source='Owner-authorized local approximation v1; historical offer-list candidate bf6ae0699b375ff9d4dca3a072f0e8aa9080dbac',build='36.6.0.251952',pool=POOL,evaluator=lambda snapshot:evaluate(snapshot,metadata),complete=False,approximate=True)
