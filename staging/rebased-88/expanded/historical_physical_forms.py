"""Physical form payloads for Remornia and Sanc'Azel; unvalidated."""
from copy import deepcopy
from engine.game import Card

def body_snapshot(game,minion):
 body=deepcopy(minion)
 raw=minion.attack+minion.attack_deficit-minion.aura_attack
 body.attack=max(0,raw);body.attack_deficit=min(0,raw)
 body.max_health-=body.aura_health;body.health-=body.aura_health
 body.aura_attack=body.aura_health=0
 return body

def equip_remornia(game,minion):
 if minion is None or minion.health<=0 or minion.silenced:return
 owner=minion.owner;player=game.players[owner]
 if minion not in player.minions:return
 body=body_snapshot(game,minion);player.board.remove(minion)
 card=Card(game._new_id(),'REV_316t');card._historical_form_minion=body
 game._carry_origin(minion,card)
 card.health_bonus=body.health-game.cards['REV_316t']['health']
 game._equip(owner,'REV_316t',attack_bonus=body.attack-game.cards['REV_316t']['attack'],physical_card=card)
 weapon=player.weapon
 if weapon is not None and player.equipped_card is card:
  weapon['historical_keywords']=tuple(sorted(body.keywords|{effect['keyword'] for effect in body.temporary_keywords}))
  weapon['attached_death_effects']=deepcopy(body.attached_death_effects)
  weapon['historical_form_max_health']=body.max_health
  if weapon['durability']<=0:game._break_weapon(owner)
 game._refresh_auras()

def return_remornia(game,owner,weapon_uid):
 player=game.players[owner];weapon=player.weapon;card=player.equipped_card
 if not weapon or weapon['card_id']!='REV_316t' or getattr(card,'uid',None)!=weapon_uid or len(player.board)>=7:return
 body=deepcopy(getattr(card,'_historical_form_minion',None))
 if body is None:
  from .game import Minion
  data=game.cards['REV_316'];maximum=max(weapon['durability'],data['health']+getattr(card,'health_bonus',0))
  body=Minion(game._new_id(),'REV_316',owner,weapon['attack'],weapon['durability'],maximum,set(data.get('mechanics',())))
  card._historical_form_minion=deepcopy(body)
  weapon['historical_form_max_health']=maximum
  # The initial physical durability offset is zero for a native weapon.
  body.health=game.cards['REV_316t']['health']+getattr(card,'health_bonus',0)
  card._historical_form_minion.health=body.health
 body.attack=max(0,weapon['attack']);body.attack_deficit=min(0,weapon['attack'])
 body.max_health=max(weapon['durability'],weapon.get('historical_form_max_health',body.max_health)+getattr(card,'health_bonus',0)-(getattr(card,'_historical_form_minion').health-game.cards['REV_316t']['health']))
 body.health=weapon['durability'];body.owner=owner
 body.attached_death_effects=deepcopy(weapon.get('attached_death_effects',body.attached_death_effects))
 body.keywords.update(set(weapon.get('historical_keywords',()))-{effect['keyword'] for effect in body.temporary_keywords})
 player.weapon=None;player.equipped_card=None
 result=game._summon(owner,'REV_316',copy_from=body,entry_origin='effect',entry_site='remornia_return',entry_source=card)
 game._refresh_auras()
 return result

def make_sanc_location(game,minion):
 if minion is None or minion.health<=0 or minion.silenced:return
 owner=minion.owner;player=game.players[owner]
 if minion not in player.minions:return
 from .locations import Location
 body=body_snapshot(game,minion);position=player.board.index(minion)
 location=Location(game._new_id(),'VAC_923t',owner,max(0,body.health),ready_turn=body.rule_state.get('historical_sanc_ready_turn',0))
 location._historical_form_minion=body
 location.rule_state['historical_form_attack']=body.attack
 location.attached_death_effects=deepcopy(body.attached_death_effects)
 player.board[position]=location
 game._refresh_auras()
 if location.durability<=0:game._remove_location(location)
 return location

def activate_sanc(game,location,target):
 owner=location.owner;player=game.players[owner]
 body=getattr(location,'_historical_form_minion',None)
 amount=location.rule_state.get('historical_form_attack',game.cards['VAC_923']['attack'])
 if target is not None and target.owner==owner and target.health>0:
  game._buff(target,amount,0);target.keywords.add('RUSH')
 if location not in player.board or location.durability<=0:return
 position=player.board.index(location);player.board.remove(location)
 if body is None:
  result=game._create_minion(owner,'VAC_923',position)
  if result is not None:result.health=location.durability;result.max_health=max(result.max_health,result.health)
 else:
  body=deepcopy(body);body.owner=owner;body.health=location.durability
  body.max_health=max(body.max_health,body.health)
  result=game._create_minion(owner,'VAC_923',position,copy_from=body)
 if result is not None:result.rule_state['historical_sanc_ready_turn']=location.ready_turn
 game._refresh_auras()
 return result


def expire_form_buffs(game,phase):
 for owner,player in enumerate(game.players):
  carriers=list(player.locations)+([player.equipped_card] if player.equipped_card is not None else [])
  for carrier in carriers:
   body=getattr(carrier,'_historical_form_minion',None)
   if body is None:continue
   amount=body.temporary_attack if phase=='end' else 0
   if phase=='end':body.temporary_attack=0
   if phase=='start':
    expiring=[effect for effect in body.imbue_attack_expiries if effect['owner']==game.current]
    amount+=sum(effect['amount'] for effect in expiring)
    body.imbue_attack_expiries[:]=[effect for effect in body.imbue_attack_expiries if effect['owner']!=game.current]
   if amount:
    value=body.attack+body.attack_deficit-amount;body.attack=max(0,value);body.attack_deficit=min(0,value)
    if hasattr(carrier,'durability'):carrier.rule_state['historical_form_attack']=body.attack
    elif player.weapon is not None and player.equipped_card is carrier:
     player.weapon['attack']=max(0,player.weapon['attack']-amount);carrier.attack_bonus-=amount
   expired={effect['keyword'] for effect in body.temporary_keywords if effect['phase']==phase and effect['turn']<=game.turn}
   body.temporary_keywords[:]=[effect for effect in body.temporary_keywords if not(effect['phase']==phase and effect['turn']<=game.turn)]
   retained=body.keywords|{effect['keyword'] for effect in body.temporary_keywords}
   if player.weapon is not None and player.equipped_card is carrier:
    player.weapon['historical_keywords']=tuple(sorted(set(player.weapon.get('historical_keywords',()))-(expired-retained)))


def weapon_death_source(weapon,card):
 body=deepcopy(getattr(card,'_historical_form_minion',None))
 if weapon['card_id']!='REV_316t' or body is None:return None
 body.attack=max(0,weapon['attack']);body.attack_deficit=min(0,weapon['attack'])
 body.health=weapon['durability'];body.keywords.update(weapon.get('historical_keywords',()))
 return body
