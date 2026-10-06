"""Staged Fabled effects; bundle membership does not imply live support.

Windrunner repetitions snapshot distinct other sisters already played, then
use ordinary effect frames so each Discover and damage wave can settle.
"""
from .generation_cards import pool,discover
from . import azshara
from .selectors import has_tribe,has_school
from engine.cards import UnsupportedCard

BLOOD_FIGHTERS=('TIME_850','TIME_850t','TIME_850t1')
BOONS={'TIME_619t3':'TAUNT','TIME_619t4':'LIFESTEAL','TIME_619t5':'RUSH'}
SISTERS=('TIME_609','TIME_609t1','TIME_609t2')
SPELLS=pool(card_type='SPELL',classes='own_or_neutral')
RULES={'TIME_609':('none',[('fabled_sisters','TIME_609')]),'TIME_850':('none',[]),'TIME_852':('none',[]),'TIME_619':('none',[('talanji_find',),('choose_boon',)]),'TIME_890':('none',[('medivh_clear',)])}
TOKEN_RULES={cid:('none',[('fabled_sisters',cid)]) for cid in SISTERS[1:]}
TOKEN_RULES.update({cid:('none',[]) for cid in BLOOD_FIGHTERS[1:]})
TOKEN_RULES.update({'TIME_852t1':('none',[]),'TIME_852t3':('none',[('fabled_resurrect_dragons',)])})
TOKEN_RULES.update({'TIME_619t':('none',[]),'TIME_619t2':('none',[('area_damage','enemies',2),('choose_boon',)])})
DEATH_EFFECTS={cid:[('fabled_blood_fighter',cid)] for cid in BLOOD_FIGHTERS}

TOKEN_RULES['TIME_890t']=('none',[])
LOCATION_RULES={'TIME_890t2':'none'}
KARAZHAN_POOL=pool(card_type='MINION',minimum=8,maximum=8)
LOCATION_EFFECTS={'TIME_890t2':[('generate_random',KARAZHAN_POOL,2,'board',())]}
DEATH_EFFECTS['TIME_619t']=[('bwonsamdi_summon',)]

CHOICES=azshara.CHOICES
RULES.update(azshara.RULES)
LOCATION_RULES.update(azshara.LOCATION_RULES)
LOCATION_EFFECTS.update(azshara.LOCATION_EFFECTS)

def requests_for(cid):
 if azshara.requests_for(cid):return azshara.requests_for(cid)
 if cid in ('TIME_890','TIME_890t2'):return {KARAZHAN_POOL}
 if cid in ('TIME_619','TIME_619t'):return {pool(card_type='MINION',minimum=n,maximum=n) for n in (4,6,8,10)}
 return {SPELLS} if cid in SISTERS else set()

class FabledEffects:
 def _spell_multiplier(self,owner):
  weapon=self.players[owner].weapon
  return 2 if weapon and weapon['card_id']=='TIME_890t' else 1

 def _medivh_free(self,cid,owner):
  p=self.players[owner]
  if cid=='TIME_890':return any(v.card_id=='TIME_890t2' for v in p.locations)
  if cid=='TIME_890t':return any(m.card_id=='TIME_890' and m.health>0 for m in p.minions)
  if cid=='TIME_890t2':return bool(p.weapon and p.weapon['card_id']=='TIME_890t')
  return False

 def _fabled_choice(self,choice,selected):
  if choice['kind']!='fabled_boon':return False
  cid=selected['card_id'];p=self.players[choice['owner']]
  if cid not in BOONS or cid in p.bwonsamdi_boons:raise UnsupportedCard('Invalid or repeated Boon')
  p.bwonsamdi_boons.append(cid)
  self._refresh_auras()
  self._log('boon',player=choice['owner'],card=cid)
  return True

 def _azure_sources(self,owner,cid):
  dragons=[m for m in self.players[owner].minions if m.health>0 and has_tribe(self.cards[m.card_id],'DRAGON')]
  return [m for m in dragons if m.card_id==cid and not m.silenced and any(other is not m for other in dragons)]

 def _azure_discount(self,owner,cid):
  return 2*len(self._azure_sources(owner,'TIME_852')) if has_school(self.cards[cid],'ARCANE') else 0

 def _azure_repeats_spell(self,owner,cid,other_repeat=False):
  if not has_school(self.cards[cid],'ARCANE'):return False
  sources=self._azure_sources(owner,'TIME_852t1')
  if sources and (len(sources)>1 or other_repeat):
   raise UnsupportedCard('Malygos repetition stacking needs reviewed semantics')
  return bool(sources)

 def _fabled_split(self,op,ctx):
  if op[0]=='fabled_resurrect_dragons':
   # Preserve death multiplicity, not distinct identities. Snapshot before
   # summons so deaths caused during this effect cannot grow its own list.
   ids=[cid for cid in self.players[ctx['owner']].death_history if has_tribe(self.cards[cid],'DRAGON')]
   self.rng.shuffle(ids)
   ops=[('fabled_resurrect',cid) for cid in ids]
   return (ops[0],tuple(ops[1:])) if ops else (('batch30_noop',),())
  if op[0]=='fabled_blood_fighter':
   state={}
   return ('fabled_recruit_fighter',op[1],state),(('fabled_fighter_attack',op[1],state),)
  if op[0]!='fabled_sisters':return None
  cid=op[1]
  if cid not in SISTERS:raise ValueError('Unknown Windrunner sister: '+cid)
  played={entry['card_id'] for entry in self.players[ctx['owner']].played_history}
  count=1+len((set(SISTERS)-{cid})&played)
  effect={'TIME_609':('area_damage','enemies',2),
          'TIME_609t1':discover(SPELLS),
          'TIME_609t2':('zone_minion_buff',('deck',),1,1)}[cid]
  return effect,(effect,)*(count-1)

 def _fabled_effect(self,op,ctx):
  owner=ctx['owner']
  if op[0]=='medivh_clear':
   targets=[m for p in self.players for m in p.minions if m is not ctx.get('source')]
   for m in targets:self._silence(m)
   for m in targets:m.health=0
  elif op[0]=='talanji_find':
   p=self.players[owner]
   if any(self._card_data(c)['id']=='TIME_619t' for c in p.deck):
    self._draw(owner,lambda c:c['id']=='TIME_619t')
   elif 'TIME_619t' in p.death_history:
    self._summon(owner,'TIME_619t',entry_origin='resurrection',entry_site='talanji',entry_source=ctx.get('source'))
  elif op[0]=='choose_boon':
   options=[dict(card_id=cid) for cid in BOONS if cid not in self.players[owner].bwonsamdi_boons]
   if options:
    if self.pending_choice is not None:raise UnsupportedCard('Cannot overwrite Boon choice')
    self.pending_choice=dict(owner=owner,kind='fabled_boon',options=options)
    self.phase='choice'
  elif op[0]=='bwonsamdi_summon':
   boons=tuple(self.players[owner].bwonsamdi_boons);cost=4+2*len(boons)
   request=pool(card_type='MINION',minimum=cost,maximum=cost)
   candidates=self._generation_candidates(request,owner)
   if candidates and len(self.players[owner].board)<7:
    m=self._generation_place(self.rng.choice(candidates),'board',(),ctx)
    if m is not None:m.keywords.update(BOONS[cid] for cid in boons)
  elif op[0]=='fabled_resurrect':
   self._summon(owner,op[1],entry_origin='resurrection',entry_site='azure_oathstone',entry_source=ctx.get('physical_card'))
  elif op[0]=='fabled_recruit_fighter':
   cid,state=op[1:]
   if cid not in BLOOD_FIGHTERS:raise ValueError('Unknown Blood Fighter')
   m=self._recruit_from_zone(owner,'hand',(('id','in',BLOOD_FIGHTERS),),site='fabled_blood_fighter')
   if m is not None:
    self._buff(m,5,5)
    keyword={'TIME_850t':'TAUNT','TIME_850t1':'ELUSIVE'}.get(cid)
    if keyword:m.keywords.add(keyword)
    state['uid']=m.uid
  elif op[0]=='fabled_fighter_attack':
   if op[1]=='TIME_850' and op[2].get('uid'):
    m=self._force_live(op[2]['uid'])
    if m is not None:self._force_attack(m.uid,self._force_target(m.owner,'random_enemy_character'))
  else:return False
  return True

from . import rafaam
RULES.update(rafaam.RULES)
TOKEN_RULES.update(rafaam.TOKEN_RULES)
DEATH_EFFECTS.update(rafaam.DEATH_EFFECTS)

from . import garona
RULES.update(garona.RULES)
TOKEN_RULES.update(garona.TOKEN_RULES)

from . import broxigar
RULES.update(broxigar.RULES)
TOKEN_RULES.update(broxigar.TOKEN_RULES)
DEATH_EFFECTS.update(broxigar.DEATH_EFFECTS)

from . import gelbin
RULES.update(gelbin.RULES)
TOKEN_RULES.update(gelbin.TOKEN_RULES)

from . import muradin
RULES.update(muradin.RULES)
TOKEN_RULES.update(muradin.TOKEN_RULES)
DEATH_EFFECTS.update(muradin.DEATH_EFFECTS)
