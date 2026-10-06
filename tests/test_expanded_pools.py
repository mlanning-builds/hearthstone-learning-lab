"""User-run pool contracts; synthetic records are not real card definitions."""
import random
import unittest
from expanded.pools import GenerationPool,deck_choice_options,require_fixed_cards
from expanded.selectors import CardSelector
from expanded.game import Card
from engine.cards import UnsupportedCard


class PoolContractTests(unittest.TestCase):
    def setUp(self):
        self.data={
            'a':dict(id='a',type='MINION',races=['ALL'],cardClass='NEUTRAL',cost=2),
            'b':dict(id='b',type='MINION',races=['BEAST'],cardClass='MAGE',cost=3),
            'c':dict(id='c',type='SPELL',spellSchool='FIRE',cardClass='ROGUE',cost=1)}
        self.pool=GenerationPool('fixture',('a','b','c'),'Synthetic contract fixture')
        self.rng=random.Random(5)

    def test_missing_eligible_effect_blocks_entire_sample_before_rng(self):
        before=self.rng.getstate()
        with self.assertRaisesRegex(UnsupportedCard,'b'):
            self.pool.sample(self.data,{'a','c'},self.rng,count=1)
        self.assertEqual(self.rng.getstate(),before)

    def test_unknown_metadata_is_not_silently_dropped(self):
        before=self.rng.getstate()
        with self.assertRaisesRegex(UnsupportedCard,'missing card data'):
            self.pool.sample({'a':self.data['a']},{'a'},self.rng)
        self.assertEqual(self.rng.getstate(),before)

    def test_explicit_condition_filters_before_implementation_gate(self):
        result=self.pool.resolve(self.data,{'c'},CardSelector(school='FIRE'))
        self.assertEqual(result,('c',))

    def test_explicit_exclusion_removes_ineligible_identity(self):
        self.assertEqual(self.pool.resolve(self.data,{'a','c'},exclude={'b'}),('a','c'))

    def test_all_type_is_included_by_tribal_pool_selector(self):
        self.assertEqual(self.pool.resolve(self.data,{'a','b'},CardSelector(tribe='BEAST')),('a','b'))

    def test_discover_sample_is_unique_capped_and_reproducible(self):
        a=self.pool.sample(self.data,self.data,self.rng,count=10)
        b=self.pool.sample(self.data,self.data,random.Random(5),count=10)
        self.assertEqual(a,b);self.assertEqual(set(a),set(self.data))
        self.assertEqual(len(a),3)

    def test_empty_explicit_pool_returns_no_options(self):
        p=GenerationPool('empty',(),'Synthetic empty fixture')
        self.assertEqual(p.sample({},set(),self.rng,count=3),[])

    def test_duplicate_pool_ids_and_invalid_counts_are_rejected(self):
        with self.assertRaises(ValueError):GenerationPool('bad',('a','a'),'fixture')
        for count in (-1,True,1.5):
            with self.assertRaises(ValueError):self.pool.sample(self.data,self.data,self.rng,count=count)

    def test_deck_choices_preserve_physical_index_without_mutating_instances(self):
        a=Card(1,'a');a.attack_bonus=4
        deck=[a,'a','b']
        options=deck_choice_options(deck,self.data,3,self.rng)
        self.assertEqual({o['card_id'] for o in options},{'a','b'})
        self.assertEqual(next(o['index'] for o in options if o['card_id']=='a'),0)
        self.assertIs(deck[0],a);self.assertEqual(a.attack_bonus,4)
        self.assertEqual(len(deck),3)

    def test_fixed_dependency_check_fails_before_sampling_or_mutation(self):
        with self.assertRaisesRegex(UnsupportedCard,'missing'):
            require_fixed_cards(('a','missing'),self.data)
        self.assertIsNone(require_fixed_cards(('a','b'),self.data))
