"""Prepared user-run Constructed selector and interaction checks."""
import unittest
from expanded import Game, Action, random_deck
from expanded.game import Card
from expanded.selectors import (CardSelector,TRIBES,has_tribe,has_any_tribe,
                                shares_tribe,has_school,has_class)


class SelectorTests(unittest.TestCase):
    def test_all_matches_every_constructed_tribe_but_not_keywords(self):
        card={'type':'MINION','races':['ALL']}
        for tribe in TRIBES:
            with self.subTest(tribe=tribe): self.assertTrue(has_tribe(card,tribe))
        with self.assertRaises(ValueError): has_tribe(card,'TAUNT')
        with self.assertRaises(ValueError): has_tribe(card,'HUMAN')

    def test_dual_types_match_both_and_not_a_third(self):
        card={'type':'MINION','races':['BEAST','UNDEAD']}
        self.assertTrue(has_tribe(card,'BEAST'));self.assertTrue(has_tribe(card,'UNDEAD'))
        self.assertFalse(has_tribe(card,'DRAGON'))

    def test_untyped_and_nonminions_do_not_match_tribes(self):
        for card in ({'type':'MINION'},{'type':'SPELL','races':['ALL']}):
            self.assertFalse(has_any_tribe(card))
            self.assertFalse(has_tribe(card,'BEAST'))
            self.assertFalse(shares_tribe(card,{'type':'MINION','races':['ALL']}))

    def test_shared_type_is_symmetric_and_supports_all(self):
        beast={'type':'MINION','races':['BEAST','UNDEAD']}
        all_card={'type':'MINION','races':['ALL']}
        self.assertTrue(shares_tribe(beast,all_card));self.assertTrue(shares_tribe(all_card,beast))
        self.assertFalse(shares_tribe(beast,{'type':'MINION','races':['DRAGON']}))

    def test_schools_require_spells_and_constructed_school(self):
        self.assertTrue(has_school({'type':'SPELL','spellSchool':'FROST'},'FROST'))
        self.assertFalse(has_school({'type':'MINION','spellSchool':'FROST'},'FROST'))
        self.assertFalse(has_school({'type':'SPELL'},'FROST'))
        with self.assertRaises(ValueError): has_school({'type':'SPELL'},'ATTACK')

    def test_class_matching_distinguishes_neutral_from_class_cards(self):
        dual={'classes':['MAGE','ROGUE'],'cardClass':'MAGE'}
        self.assertTrue(has_class(dual,'ROGUE'));self.assertFalse(has_class(dual,'WARRIOR'))
        neutral={'cardClass':'NEUTRAL'}
        self.assertFalse(has_class(neutral,'MAGE'))
        self.assertTrue(has_class(neutral,'MAGE',include_neutral=True))

    def test_composed_selection_preserves_multiplicity_and_order(self):
        a={'type':'MINION','races':['ALL'],'cardClass':'NEUTRAL','cost':3}
        b={'type':'MINION','races':['BEAST'],'cardClass':'MAGE','cost':5}
        c={'type':'MINION','races':['BEAST'],'cardClass':'ROGUE','cost':3}
        selector=CardSelector(tribe='BEAST',hero_class='MAGE',include_neutral=True,min_cost=2,max_cost=4)
        self.assertEqual(selector.select([a,b,a,c]),[a,a])

    def test_invalid_selector_configuration_fails_early(self):
        for kwargs in ({'tribe':'INVALID'},{'school':'ATTACK'},{'card_type':'MERCENARY'},
                       {'min_cost':4,'max_cost':2},{'min_cost':True},{'include_neutral':True}):
            with self.subTest(kwargs=kwargs),self.assertRaises(ValueError): CardSelector(**kwargs)


class SelectorInteractionTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('MAGE',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
        self.cid='Core_CS2_200'
        # Synthetic identity only: no new real card is being certified here.
        self.g.cards[self.cid]=dict(self.g.cards[self.cid],races=['ALL'])
        self.m=self.g._summon(0,self.cid)

    def test_silence_preserves_type_targeting_and_external_tribal_aura(self):
        base=self.g.cards[self.cid]['attack']
        self.g._summon(0,'CORE_EX1_507')
        self.assertEqual(self.m.attack,base+2)
        self.g._silence(self.m)
        self.assertEqual(self.m.attack,base+2)
        for mode in ('friendly_beast','friendly_undead'):
            self.assertIn(self.m.uid,self.g._targets_for('CORE_CS2_029',0,mode))

    def test_transform_replaces_type_membership_and_aura_eligibility(self):
        self.g._summon(0,'CORE_EX1_507')
        self.g.cards['hexfrog']=dict(self.g.cards['hexfrog'],races=[],race=None)
        replacement=self.g._transform(self.m,'hexfrog')
        self.assertFalse(has_any_tribe(self.g.cards[replacement.card_id]))
        self.assertEqual(replacement.aura_attack,0)
        self.assertNotIn(replacement.uid,self.g._targets_for('CORE_CS2_029',0,'friendly_beast'))

    def test_filtered_tribal_draw_includes_all_and_preserves_instance(self):
        self.p.hand=[]
        card=Card(self.g._new_id(),self.cid);card.attack_bonus=3
        self.p.deck=['CORE_CS2_029',card]
        self.g._effect(('draw_tribe','BEAST'),dict(owner=0,source=None,target=0))
        self.assertIs(self.p.hand[0],card)
        self.assertEqual(self.p.hand[0].attack_bonus,3)
        self.assertEqual(self.p.deck,['CORE_CS2_029'])

    def test_all_type_discount_does_not_match_keyword_discount(self):
        card=Card(self.g._new_id(),self.cid)
        self.assertTrue(self.g._discount_matches({'selector':'DEMON'},card))
        self.assertFalse(self.g._discount_matches({'selector':'BATTLECRY'},card))
