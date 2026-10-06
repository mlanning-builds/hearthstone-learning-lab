import unittest
from copy import deepcopy
from expanded import Game,Action,random_deck
from expanded.game import Card

class SpiritspeakerTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('HUNTER',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p=self.g.players[0];self.p.hand=[];self.p.mana=self.p.max_mana=10
    def play(self):
        c=Card(self.g._new_id(),'MEND_301');self.p.hand.append(c)
        self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid))
    def test_each_companion_is_selectable(self):
        self.play();base=deepcopy(self.g)
        for i,cid in enumerate(('NEW1_034','NEW1_033','NEW1_032')):
            with self.subTest(card=cid):
                g=deepcopy(base);deck=deepcopy(g.players[0].deck);rng=g.rng.getstate()
                g.step(Action('choose',choices=(i,)))
                self.assertEqual(g.players[0].minions[-1].card_id,cid)
                self.assertEqual(g.players[0].deck,deck);self.assertEqual(g.rng.getstate(),rng)
                self.assertIsNone(g.pending_choice);self.assertIsNone(g.pending_frame)
    def test_only_choice_actions_while_suspended(self):
        self.play();self.assertEqual([a.kind for a in self.g.legal_actions()],['choose']*3)
    def test_illegal_choice_rolls_back(self):
        self.play();before=self.g.observe(0)
        with self.assertRaises(ValueError):self.g.step(Action('choose',choices=(3,)))
        self.assertEqual(self.g.observe(0),before)
    def test_choice_options_visible_only_to_owner(self):
        self.play();self.assertEqual(len(self.g.observe(0)['pending_choice']['options']),3)
        self.assertNotIn('options',self.g.observe(1)['pending_choice'])
    def test_huffer_can_attack_after_choice(self):
        self.play();self.g.step(Action('choose',choices=(0,)))
        m=self.p.minions[-1];self.assertTrue(any(a.kind=='attack' and a.source==m.uid for a in self.g.legal_actions()))
    def test_summoning_does_not_open_choice(self):
        self.g._summon(0,'MEND_301');self.assertIsNone(self.g.pending_choice)
