"""Pre-mulligan construction effects; original-deck predicates stay immutable.

Beatrix selections are explicit Deck input, never silently sampled. Azalina
samples physical positions from simultaneous snapshots, not identities.
"""
from engine.game import Card
RULES={'JAIL_397':('none',[]),'JAIL_430':('none',[('draw_until',10)])}

class DeckSetup:
    def _opening_effect_ids(self,owner):
        p=self.players[owner]
        return tuple(p.starting_deck)+tuple(getattr(p,'copied_opening_ids',()))

    def _prepare_constructed_decks(self,decks):
        for owner,(p,deck) in enumerate(zip(self.players,decks)):
            if 'JAIL_397' in p.starting_deck:
                if not deck.beatrix_minion:
                    raise ValueError('Missing Commander Beatrix selection')
                for _ in range(10):
                    c=Card(self._new_id(),deck.beatrix_minion)
                    # Added before play; not an ordinary generated hand card.
                    c._starting_owner=owner
                    d=self.cards[c.card_id]
                    c._starting_identity=d.get('countAsCopyOfDbfId',d.get('dbfId',c.card_id))
                    p.deck.append(c)
                self.rng.shuffle(p.deck)
        snapshots=[tuple(p.deck) for p in self.players]
        for owner,p in enumerate(self.players):
            p.copied_opening_ids=[]
            if 'JAIL_430' not in p.starting_deck:continue
            p.health=p.max_health=40
            selected=self.rng.sample(snapshots[1-owner],min(20,len(snapshots[1-owner])))
            for original in selected:
                cid=self._card_data(original)['id']
                c=Card(self._new_id(),cid)
                c._copied_opening_effect=True
                c._copied_from_owner=1-owner
                p.deck.append(c);p.copied_opening_ids.append(cid)
            self.rng.shuffle(p.deck)
