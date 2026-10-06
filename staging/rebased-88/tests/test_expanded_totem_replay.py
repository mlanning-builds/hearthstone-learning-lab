import unittest
from expanded import Game,Action,random_deck
from expanded.game import TOTEMS

class TotemReplayTests(unittest.TestCase):
    def test_all_basic_totems_can_be_bounced_and_replayed(self):
        for cid in TOTEMS:
            with self.subTest(card=cid):
                g=Game([random_deck('SHAMAN',31),random_deck('WARRIOR',53)],seed=71)
                g.step(Action('mulligan'));g.step(Action('mulligan'))
                p=g.players[0];p.hand=[];p.mana=p.max_mana=10
                m=g._summon(0,cid);g._bounce(m)
                card=p.hand[0];cost=g._cost(card,0)
                g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==card.uid))
                self.assertEqual(p.mana,10-cost)
                self.assertEqual([m.card_id for m in p.minions],[cid])
                self.assertEqual(p.hand,[])
