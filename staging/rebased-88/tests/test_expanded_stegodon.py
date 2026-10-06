import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class StegodonTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('WARRIOR',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p=self.g.players[0];self.p.hand=[];self.p.mana=self.p.max_mana=10
        c=Card(self.g._new_id(),'TLC_242');self.p.hand.append(c)
        self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid))
        self.m=self.p.minions[0]
    def choose(self,i):self.g.step(Action('choose',choices=(i,)))
    def test_taunt_only(self):
        self.choose(0);self.assertIn('TAUNT',self.m.keywords);self.assertNotIn('POISONOUS',self.m.keywords)
        self.assertEqual((self.m.attack,self.m.health),(1,5))
    def test_poisonous_only(self):
        self.choose(1);self.assertIn('POISONOUS',self.m.keywords);self.assertNotIn('TAUNT',self.m.keywords)
    def test_stats_only(self):
        self.choose(2);self.assertEqual((self.m.attack,self.m.health),(2,6))
        self.assertFalse({'TAUNT','POISONOUS'}&self.m.keywords)
    def test_owner_receives_distinguishable_labels(self):
        options=self.g.observe(0)['pending_choice']['options']
        self.assertEqual([o['label'] for o in options],['Taunt','Poisonous','+1/+1'])
        self.assertTrue(all('operation' not in o for o in options))
        self.assertNotIn('options',self.g.observe(1)['pending_choice'])
    def test_choice_does_not_spend_mana_twice(self):
        self.assertEqual(self.p.mana,7);self.choose(2);self.assertEqual(self.p.mana,7)
        self.assertIsNone(self.g.pending_frame);self.assertIsNone(self.g.pending_play)
    def test_silence_removes_choice_buff(self):
        self.choose(2);self.g._silence(self.m);self.g._settle()
        self.assertEqual((self.m.attack,self.m.health),(1,5))
