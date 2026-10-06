"""Every registered noncollectible minion must remain playable after a bounce."""
import unittest
from expanded import Game,Action,random_deck
from expanded.cards import registry,COLLECTIBLE_IDS
from expanded.permanents import PERMANENT_IDS

class ReturnedTokenTests(unittest.TestCase):
    def test_registered_minions_can_return_to_hand_and_be_replayed(self):
        # Raw MINION records also encode untouchable board objects, which cannot
        # enter a hand or be played as minions; their lifecycle is tested separately.
        ids=sorted(cid for cid,c in registry().items() if c['type']=='MINION'
                   and cid not in COLLECTIBLE_IDS and cid not in PERMANENT_IDS)
        self.assertGreater(len(ids),20)
        for cid in ids:
            with self.subTest(card=cid):
                g=Game([random_deck('WARRIOR',31),random_deck('WARRIOR',53)],seed=71)
                g.step(Action('mulligan'));g.step(Action('mulligan'))
                p=g.players[0];p.hand=[];p.mana=p.max_mana=10
                m=g._summon(0,cid);self.assertIsNotNone(m)
                if m.dormant:
                    g._bounce(m)
                    self.assertEqual(p.hand,[])
                    self.assertIn(m,p.board)
                    g._awaken(m)
                g._bounce(m);card=p.hand[0]
                # Exercise play dispatch independent of unusually expensive tokens.
                card.cost_delta=-g.cards[cid]['cost']
                action=next(a for a in g.legal_actions() if a.kind=='play' and a.source==card.uid)
                g.step(action);g.assert_invariants()
                self.assertTrue(any(m.card_id==cid for m in p.all_minions))
                if m.card_id in ('EDR_416t','EDR_840t','EDR_840t1','EDR_840t2'):
                    self.assertTrue(next(x for x in p.all_minions if x.card_id==cid).dormant)
                self.assertFalse(any(c.uid==card.uid for c in p.hand))
