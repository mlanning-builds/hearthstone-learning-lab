"""Pre-mulligan construction effects; original-deck predicates stay immutable.

Beatrix selections are explicit Deck input, never silently sampled. Azalina
samples physical positions from simultaneous snapshots, not identities.
"""
from .identities import canonical_identity,identity_resolver
from engine.game import Card
RULES={'JAIL_397':('none',[]),'JAIL_430':('none',[('draw_until',10)])}

class DeckSetup:
    def _opening_effect_ids(self,owner):
        p=self.players[owner]
        return tuple(p.starting_deck)+tuple(getattr(p,'copied_opening_ids',()))

    def _starting_replay_card(self,owner,cid):
        prototype=getattr(self.players[owner],'_starting_custom_cards',{}).get(cid)
        return self._fresh_replay_card(prototype) if prototype is not None else Card(self._new_id(),cid)

    def _starting_card_data(self,owner,cid):
        return getattr(self.players[owner],'_starting_custom_definitions',{}).get(cid,self.cards[cid])

    def _prepare_constructed_decks(self,decks):
        from .historical_transfer_student import setup as setup_student
        setup_student(self)
        from .historical_zilliax import setup as setup_zilliax
        setup_zilliax(self,decks)
        from .historical_etc import setup as setup_etc
        setup_etc(self,decks)
        for owner,(p,deck) in enumerate(zip(self.players,decks)):
            if 'JAIL_397' in p.starting_deck:
                if not deck.beatrix_minion:
                    raise ValueError('Missing Commander Beatrix selection')
                for _ in range(10):
                    c=Card(self._new_id(),deck.beatrix_minion)
                    # Added before play; not an ordinary generated hand card.
                    c._starting_owner=owner
                    d=self.cards[c.card_id]
                    c._starting_identity=canonical_identity(d,self.cards)
                    p.deck.append(c)
                self.rng.shuffle(p.deck)
        for p in self.players:
            if 'REV_018' in p.starting_deck:p.health=p.max_health=40
        snapshots=[tuple(p.deck) for p in self.players]
        for owner,p in enumerate(self.players):
            p.copied_opening_ids=[]
            if 'JAIL_430' not in p.starting_deck:continue
            p.health=p.max_health=40
            selected=self.rng.sample(snapshots[1-owner],min(20,len(snapshots[1-owner])))
            for original in selected:
                cid=self._card_data(original)['id']
                c=self._fresh_replay_card(original)
                self._carry_origin(original,c,copied=True,source_owner=1-owner)
                c._copied_opening_effect=True
                c._copied_from_owner=1-owner
                p.deck.append(c);p.copied_opening_ids.append(cid)
            self.rng.shuffle(p.deck)

        from .historical_galakrond_batches import primary
        for owner in (0,1):primary(self,owner,initial=True)
