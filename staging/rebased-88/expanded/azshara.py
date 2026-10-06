"""Staged Azshara family: physical upgrades, removal, copying and spell creation."""
from copy import deepcopy
from engine.cards import UnsupportedCard
from .generation_cards import pool

WELL=('TIME_211t1','TIME_211t1t')
ZIN=('TIME_211t2','TIME_211t2t')
UPGRADES={WELL[0]:WELL[1],ZIN[0]:ZIN[1]}
SPELLS=pool(card_type='SPELL')
RULES={'TIME_211':('none',[])}
CHOICES={'TIME_211':[
 ('Empower Zin-Azshari','none',[('azshara_empower',ZIN,WELL)]),
 ('Empower the Well','none',[('azshara_empower',WELL,ZIN)]),
]}
LOCATION_RULES={cid:'none' for cid in WELL}
LOCATION_RULES.update({cid:'friendly_minion' for cid in ZIN})
LOCATION_EFFECTS={cid:[('azshara_well',cid==WELL[1])] for cid in WELL}
LOCATION_EFFECTS.update({cid:[('azshara_copy',cid==ZIN[1])] for cid in ZIN})

def requests_for(cid):return {SPELLS} if cid=='TIME_211' or cid in WELL else set()

class Azshara:
 def _azshara_split(self,op,ctx):
  if op[0]!='azshara_well':return None
  count=max(0,10-len(self.players[ctx['owner']].hand))
  mods=(('temporary',True),)+( (('repeat_spell',True),) if op[1] else ())
  return self._generation_split(('generate_random',SPELLS,count,'hand',mods),ctx)

 def _azshara_effect(self,op,ctx):
  owner=ctx['owner'];p=self.players[owner]
  if op[0]=='azshara_empower':
   chosen,destroyed=op[1:]
   if (chosen,destroyed) not in ((WELL,ZIN),(ZIN,WELL)):raise UnsupportedCard('Invalid Azshara location family')
   for cid in (*WELL,*ZIN):
    if self.cards.get(cid,{}).get('type')!='LOCATION':raise UnsupportedCard('Missing Azshara location: '+cid)
   # Change actual entities in-place: no draws, discards, replays, cooldown
   # reset, or durability refresh. Destruction recognizes upgraded copies too.
   for zone_name in ('hand','deck'):
    zone=getattr(p,zone_name)
    for card in tuple(zone):
     cid=self._card_data(card)['id']
     if cid in destroyed:
      zone.remove(card);self._log('azshara_removed',player=owner,zone=zone_name,card=cid)
     elif cid==chosen[0]:
      if isinstance(card,str):zone[zone.index(card)]=chosen[1]
      else:card.card_id=chosen[1]
   for location in tuple(p.locations):
    if location.card_id in destroyed:self._remove_location(location)
    elif location.card_id==chosen[0]:location.card_id=chosen[1]
   self._refresh_auras()
  elif op[0]=='azshara_copy':
   target=next((m for m in p.minions if m.uid==ctx['target'] and m.health>0),None)
   if target is not None and len(p.board)<7:
    snapshot=deepcopy(target)
    if op[1]:
     # Prepare the doubled copy before its arrival notifications. External
     # aura contributions are stripped/reapplied by the shared copy path.
     snapshot.attack+=max(0,snapshot.attack-snapshot.aura_attack)
     health=max(0,snapshot.health-snapshot.aura_health)
     snapshot.max_health+=health;snapshot.health+=health
    self._summon(owner,target.card_id,copy_from=snapshot,entry_origin='copy',entry_site='zin_azshari',entry_source=target)
  else:return False
  return True
