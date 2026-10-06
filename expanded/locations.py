"""Explicit location rules; unknown locations remain rejected by the registry."""
from dataclasses import dataclass
from engine.game import Action
from engine.cards import UnsupportedCard

LOCATION_RULES = {
    'CORE_REV_990': 'minion',
    'CATA_477': 'hand_minion',
    'CATA_584': 'none',
    'JAIL_877': 'none',
}


@dataclass
class Location:
    uid: int
    card_id: str
    owner: int
    durability: int
    ready_turn: int = 0


class Locations:
    def _place_location(self, owner, cid, position=-1):
        if cid not in LOCATION_RULES:
            raise UnsupportedCard('Location not implemented: '+cid)
        p=self.players[owner]
        if len(p.board)>=7: return None
        location=Location(self._new_id(),cid,owner,self.cards[cid]['health'])
        if position<0:position=len(p.board)
        p.board.insert(position,location)
        self._log('location_played',player=owner,card=cid,entity=location.uid,position=position)
        self._refresh_auras()
        return location

    def _location_actions(self):
        p=self.players[self.current]
        actions=[]
        for location in p.locations:
            if self.turn<location.ready_turn:continue
            mode=LOCATION_RULES[location.card_id]
            if mode=='hand_minion':
                targets=[c.uid for c in p.hand if self.cards[c.card_id]['type']=='MINION']
            elif mode=='none':
                targets=[0]
            else:
                targets=self._targets_for(location.card_id,self.current,mode)
            for target in targets:actions.append(Action('activate',location.uid,target))
        return actions

    def _activate_location(self, action):
        owner=self.current;p=self.players[owner]
        location=next(x for x in p.locations if x.uid==action.source)
        cid=location.card_id
        position=p.board.index(location)
        self._log('location_activated',player=owner,card=cid,entity=location.uid,
                  target=action.target if cid!='CATA_477' else 'PRIVATE_HAND_CARD')
        location.durability-=1
        # Skip the owner's next turn: each engine turn is one player's turn.
        location.ready_turn=self.turn+4
        # Patch 32.0: final-charge summons have the freed location slot available.
        if location.durability==0:
            p.board.remove(location)
            self._log('location_removed',player=owner,card=cid,entity=location.uid)
            self._refresh_auras()
        if cid=='CORE_REV_990':
            target=self._find(action.target)
            self._damage(target.uid,1)
            self._buff(target,2,0)
        elif cid=='CATA_477':
            card=next(c for c in p.hand if c.uid==action.target)
            card.attack_bonus+=2;card.health_bonus+=2
        elif cid=='CATA_584':
            shots=6 if p.fire_spell_played else 3
            self._effect(('missiles','enemies',shots),dict(owner=owner,source=None,
                         target=0,bonus=0,lifesteal=False))
        elif cid=='JAIL_877':
            self._summon(owner,'JAIL_877t',position if location.durability==0 else position+1)
        else:
            raise UnsupportedCard('Location effect not implemented: '+cid)
        self._settle()
