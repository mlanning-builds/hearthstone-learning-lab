"""Untouchable board objects with explicit activations.

Objects occupy board slots and interrupt adjacency, but are neither minions nor
locations. The Rift consumes a hand card without play/discard/destroy events.
"""
from dataclasses import dataclass
from engine.game import Action
from engine.cards import UnsupportedCard
from .pools import GenerationPool

RIFT='TLC_446t1'
FEL_BEASTS=('TLC_446t2','TLC_446t3','TLC_446t4')
FEL_POOL=GenerationPool('Underfel Rift Fel Beasts',FEL_BEASTS,
    'Pinned TLC_446 reward family: Felscreamer, Felraptor, Felhorn')
NETHER_PORTAL='UNG_829t2'
NETHER_IMP='UNG_829t3'
PERMANENT_IDS={RIFT,NETHER_PORTAL}
TOKEN_IDS={RIFT,'TLC_446t',*FEL_BEASTS}
PLAYABLE_TOKENS={'TLC_446t',*FEL_BEASTS}
TOKEN_RULES={'TLC_446t':('none',[('open_permanent',RIFT)])}

@dataclass
class Permanent:
    uid: int
    card_id: str
    owner: int
    used_turn: int = -1

class Permanents:
    def _permanent_entity(self,uid):
        return next((obj for p in self.players for obj in p.permanents if obj.uid==uid),None)

    def _place_permanent(self,owner,cid,position=-1):
        if cid not in PERMANENT_IDS:raise UnsupportedCard('Unknown permanent: '+cid)
        p=self.players[owner]
        if len(p.board)>=7:return None
        obj=Permanent(self._new_id(),cid,owner)
        if position<0:position=len(p.board)
        p.board.insert(position,obj)
        self._log('permanent_opened',player=owner,card=cid,entity=obj.uid,position=position)
        self._trace_phase('permanent_opened',owner=owner,card_id=cid,subject=obj.uid)
        self._refresh_auras()
        return obj

    def _permanent_actions(self):
        p=self.players[self.current]
        return [Action('activate',obj.uid,c.uid) for obj in p.permanents
                if obj.card_id==RIFT and obj.used_turn!=p.turns_taken for c in p.hand]

    def _activate_permanent(self,action):
        owner=self.current;p=self.players[owner]
        obj=next(obj for obj in p.permanents if obj.uid==action.source)
        if obj.card_id!=RIFT:raise UnsupportedCard('Permanent has no activation')
        if obj.used_turn==p.turns_taken:raise ValueError('Permanent already used this turn')
        card=next(c for c in p.hand if c.uid==action.target)
        # Validate the entire fixed pool before committing the card or RNG.
        FEL_POOL.resolve(self.cards,self.cards)
        p.hand.remove(card);obj.used_turn=p.turns_taken
        # No hidden card identity or hand entity ID is placed in public logs.
        self._log('permanent_activated',player=owner,entity=obj.uid)
        self._refresh_auras()
        self._start_play_effects((('rift_summon',),('rift_summon',)),
            dict(owner=owner,source=None,target=0,bonus=0,lifesteal=False))

    def _permanent_turn_entries(self,phase):
        if phase!='end':return []
        return [dict(source=None,order=obj.uid,operations=(('nether_imp',obj.uid,0),('nether_imp',obj.uid,1)))
                for obj in self.players[self.current].permanents if obj.card_id==NETHER_PORTAL
                for _ in range(self._end_trigger_count(self.current))]

    def _permanent_effect(self,op,ctx):
        if op[0]=='open_permanent':self._place_permanent(ctx['owner'],op[1])
        elif op[0]=='nether_portal':
            if NETHER_PORTAL not in self.cards or NETHER_IMP not in self.cards:raise UnsupportedCard('Missing Nether Portal dependency')
            self._place_permanent(ctx['owner'],NETHER_PORTAL)
        elif op[0]=='nether_imp':
            obj=self._permanent_entity(op[1]);owner=ctx['owner']
            if obj is not None and obj.owner==owner and obj.card_id==NETHER_PORTAL:
                board=self.players[owner].board
                self._summon(owner,NETHER_IMP,position=board.index(obj)+op[2],entry_origin='permanent',entry_site='nether_portal')
        elif op[0]=='rift_summon':
            pool=FEL_POOL.resolve(self.cards,self.cards)
            if len(self.players[ctx['owner']].board)<7:
                self._summon(ctx['owner'],self.rng.choice(pool),entry_origin='permanent',entry_site='underfel_rift')
        else:return False
        return True
