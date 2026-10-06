import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class HoarderTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('WARLOCK',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
        for p in self.g.players:p.hand=[];p.deck=[];p.mana=p.max_mana=10
    def give(self,cid):
        c=Card(self.g._new_id(),cid);self.p.hand.append(c);return c
    def play(self):
        c=self.give('CATA_897');self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid))
        return self.p.minions[-1]
    def prepare(self):
        c=self.give('CORE_CS2_029');m=self.play();self.g.step(Action('choose',choices=(0,)));return m,c
    def kill(self,m):m.health=0;self.g._settle()
    def test_returns_selected_card_discounted_without_old_enchantments(self):
        c=self.give('CORE_EX1_506');c.attack_bonus=5;c.cost_delta=-2
        m=self.play();self.g.step(Action('choose',choices=(0,)));self.kill(m)
        returned=self.p.hand[0];self.assertEqual(returned.card_id,c.card_id)
        self.assertNotEqual(returned.uid,c.uid);self.assertEqual(returned.attack_bonus,0)
        self.assertEqual(returned.cost_delta,-1);self.assertEqual(self.g._cost(returned,0),1)
    def test_empty_hand_does_not_invent_a_return(self):
        m=self.play();self.assertIsNone(self.g.pending_choice);self.kill(m);self.assertFalse(self.p.hand)
    def test_silence_clears_memory_and_deathrattle(self):
        m,c=self.prepare();self.g._silence(m);self.assertEqual(m.remembered_discards,[])
        self.kill(m);self.assertFalse(self.p.hand)
    def test_copy_keeps_independent_memory(self):
        m,c=self.prepare();copy=self.g._summon(0,'CATA_897',copy_from=m)
        self.g._silence(m);self.kill(copy)
        self.assertEqual([c.card_id for c in self.p.hand],['CORE_CS2_029'])
    def test_full_hand_burns_return(self):
        m,c=self.prepare()
        for _ in range(10):self.give('CORE_EX1_506')
        self.kill(m);self.assertEqual(len(self.p.hand),10)
        self.assertFalse(any(c.card_id=='CORE_CS2_029' for c in self.p.hand))
    def test_summoned_hoarder_has_no_remembered_card(self):
        m=self.g._summon(0,'CATA_897');self.kill(m);self.assertFalse(self.p.hand)
    def test_memory_is_public_only_after_actual_discard(self):
        c=self.give('CORE_CS2_029');m=self.play()
        self.assertEqual(self.g.observe(1)['players'][0]['board'][0]['remembered_discards'],[])
        self.g.step(Action('choose',choices=(0,)))
        self.assertEqual(self.g.observe(1)['players'][0]['board'][0]['remembered_discards'],[c.card_id])

    def test_discount_does_not_make_negative_cost(self):
        self.give('TOKEN_COIN');m=self.play();self.g.step(Action('choose',choices=(0,)))
        self.kill(m);self.assertEqual(self.g._cost(self.p.hand[0],0),0)
