"""Failure-closed filters, instance stats, and physical deck sampling."""
import random
import unittest
from types import SimpleNamespace
from expanded.batch_effects import BatchEffects
from engine.game import Card

class FilterHarness(BatchEffects):
    def __init__(self):
        self.cards={'m':dict(id='m',type='MINION',cost=3,attack=2,health=4,races=['ALL']),
                    's':dict(id='s',type='SPELL',cost=0)}
        self.players=[SimpleNamespace(deck=[])]
        self.rng=random.Random(19)
    def _draw_index(self,owner,index):
        return self.players[owner].deck.pop(index)

class BatchFilterTests(unittest.TestCase):
    def setUp(self):self.g=FilterHarness()
    def test_bad_later_clause_is_not_hidden_by_first_nonmatch(self):
        with self.assertRaises(ValueError):
            self.g._matches_filter('s',(('type','eq','MINION'),('cost','gte',3)))
    def test_empty_deck_still_rejects_unknown_fields_without_rng_use(self):
        before=self.g.rng.getstate()
        with self.assertRaises(ValueError):self.g._draw_filtered(0,(('mana','eq',3),))
        self.assertEqual(self.g.rng.getstate(),before)
    def test_identity_operators_and_domains_are_checked(self):
        for clause in [('tribe','le','BEAST'),('type','eq','MERCENARY'),('tribe','eq','HUMAN'),('cost','eq',True)]:
            with self.subTest(clause=clause),self.assertRaises(ValueError):
                self.g._matches_filter('m',(clause,))
    def test_missing_stat_is_not_zero(self):
        self.assertFalse(self.g._matches_filter('s',(('attack','eq',0),)))
    def test_enchanted_instance_stats_and_all_tribes(self):
        c=Card(1,'m');c.attack_bonus=3;c.cost_delta=-2
        self.assertTrue(self.g._matches_filter(c,(('tribe','eq','BEAST'),('attack','ge',5),('cost','eq',1))))
        self.assertFalse(self.g._matches_filter('m',(('attack','ge',5),)))
    def test_duplicate_instances_preserved_and_nonmatch_untouched(self):
        a,b=Card(1,'m'),Card(2,'m');self.g.players[0].deck=['s',a,b]
        first=self.g._draw_filtered(0,(('tribe','eq','DRAGON'),))
        second=self.g._draw_filtered(0,(('tribe','eq','DRAGON'),))
        self.assertEqual({first.uid,second.uid},{1,2})
        self.assertEqual(self.g.players[0].deck,['s'])
        state=self.g.rng.getstate()
        self.assertIsNone(self.g._draw_filtered(0,(('type','eq','MINION'),)))
        self.assertEqual(self.g.rng.getstate(),state)
