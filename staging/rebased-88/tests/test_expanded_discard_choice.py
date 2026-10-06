import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class DiscardChoiceTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('WARLOCK',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
        for p in self.g.players:p.hand=[];p.deck=['CORE_CS2_029']*30;p.mana=p.max_mana=10
    def add(self,cid):
        c=Card(self.g._new_id(),cid);self.p.hand.append(c);return c
    def play(self):
        c=self.add('CATA_490');self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid));return c
    def test_select_exact_duplicate_and_keep_other(self):
        a=self.add('CORE_CS2_029');b=self.add('CORE_CS2_029');b.cost_delta=-1
        self.play();self.g.step(Action('choose',choices=(1,)))
        self.assertEqual([c.uid for c in self.p.hand],[a.uid])
        self.assertEqual(self.p.discard_history,['CORE_CS2_029'])
        self.assertEqual(self.g.phase,'play');self.assertIn('TAUNT',self.p.minions[0].keywords)
    def test_empty_hand_skips_choice(self):
        self.play();self.assertEqual(self.g.phase,'play');self.assertIsNone(self.g.pending_choice)
        self.assertEqual(self.p.discard_history,[])
    def test_opponent_cannot_see_private_choice_options(self):
        self.add('CORE_CS2_029');self.play()
        view=self.g.observe(1);self.assertNotIn('options',view['pending_choice'])
        self.assertEqual(view['legal_actions'],[])
    def test_invalid_choice_rolls_back(self):
        a=self.add('CORE_CS2_029');self.play()
        with self.assertRaises(ValueError):self.g.step(Action('choose',choices=(99,)))
        self.assertEqual(self.g.players[0].hand[0].uid,a.uid)
        self.assertEqual(self.g.players[0].discard_history,[])
    def test_random_discard_uses_same_public_history(self):
        self.add('CORE_CS2_029')
        self.g._effect(('discard',1),dict(owner=0,source=None,target=0,bonus=0,lifesteal=False))
        self.assertEqual(self.g.observe(1)['players'][0]['discard_history'],['CORE_CS2_029'])
        self.assertFalse(self.p.hand);self.assertFalse(self.p.death_history)
    def test_summon_does_not_trigger_battlecry(self):
        self.add('CORE_CS2_029');self.g._summon(0,'CATA_490')
        self.assertEqual(len(self.p.hand),1);self.assertIsNone(self.g.pending_choice)
