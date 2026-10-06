"""Kindred membership and printed-identity partner integration."""
import unittest
from copy import deepcopy
from unittest.mock import patch
from expanded import Game, Action, random_deck
from expanded.game import Card
from expanded.kindred import KINDRED_IDS, activates_kindred
from expanded.selectors import effective_tribes, common_tribes, TRIBES

class KindredIdentityTests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('PALADIN',31),random_deck('MAGE',53)],seed=71)
        g.step(Action('mulligan'));g.step(Action('mulligan'))
        for p in g.players:
            p.hand=[];p.board=[];p.deck=['CORE_CS2_029']*25;p.health=30;p.mana=p.max_mana=10;p.armor=0
        return g
    def put(self,g,cid,owner=0):
        c=Card(g._new_id(),cid);g.players[owner].hand.append(c);return c
    def play_card(self,g,c,target=None,choice=None):
        g.players[g.current].mana=10
        actions=[a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid and (target is None or a.target==target) and (choice is None or a.choices==(choice,))]
        self.assertTrue(actions,(c.card_id,target,choice));first=actions[0];g.step(max((a for a in actions if a.target==first.target and a.choices==first.choices),key=lambda a:a.position));return c
    def play(self,g,cid,target=None,choice=None):return self.play_card(g,self.put(g,cid,g.current),target,choice)
    def choose(self,g,i=0):g.step(Action('choose',choices=(i,)))
    def cycle(self,g):g.step(Action('end'));g.step(Action('end'))
    def kill(self,g,m):m.health=0;g._settle(allow_event_choices=True)
    def attack(self,g,m,target):
        m.summoned_turn=g.turn-1
        g.step(next(a for a in g.legal_actions() if a.kind=='attack' and a.source==m.uid and a.target==target))
    def test_missing_metadata_does_not_hide_kindred(self):
        g=self.game();self.assertNotIn('KINDRED',g.cards['TLC_428'].get('mechanics',[]));self.assertIn('TLC_428',KINDRED_IDS)
    def test_referencing_cards_are_not_kindred(self):
        self.assertNotIn('TLC_102',KINDRED_IDS);self.assertNotIn('TLC_251',KINDRED_IDS)
    def test_dual_type_either_partner(self):
        g=self.game();kindred=g.cards['TLC_432']
        self.assertTrue(activates_kindred(kindred,g.cards['EDR_851t']))
        self.assertTrue(activates_kindred(kindred,g.cards['TLC_903']))
        self.assertFalse(activates_kindred(kindred,g.cards['CS2_033']))
    def test_all_type_kindred_matches_known_minion_only(self):
        g=self.game();kindred=g.cards['DINO_435']
        self.assertTrue(activates_kindred(kindred,g.cards['EDR_851t']))
        self.assertFalse(activates_kindred(kindred,g.cards['CORE_CS2_029']))
        self.assertFalse(activates_kindred(kindred,g.cards['CORE_SCH_717']))
    def test_all_type_partner(self):
        g=self.game();self.assertTrue(activates_kindred(g.cards['TLC_428'],g.cards['DINO_435']))
    def test_spell_same_school_only(self):
        g=self.game();kindred=g.cards['TLC_236']
        self.assertTrue(activates_kindred(kindred,g.cards['CORE_EX1_169']))
        self.assertFalse(activates_kindred(kindred,g.cards['CORE_CS2_029']))
        self.assertFalse(activates_kindred(kindred,g.cards['TLC_903']))
    def test_unknown_tribe_not_constructed_identity(self):
        self.assertEqual(effective_tribes(dict(type='MINION',races=['INVALID'])),frozenset())
        self.assertEqual(effective_tribes(dict(type='SPELL',races=['ALL'])),frozenset())
    def test_common_type_is_intersection_not_pairwise_overlap(self):
        cards=[dict(type='MINION',races=x) for x in [('BEAST','UNDEAD'),('BEAST','DEMON'),('DEMON','UNDEAD')]]
        self.assertFalse(common_tribes(cards))
        self.assertEqual(common_tribes(cards[:2]),frozenset(['BEAST']))
    def test_common_all_and_untyped(self):
        all_type=dict(type='MINION',races=['ALL']);beast=dict(type='MINION',race='BEAST')
        self.assertEqual(common_tribes([all_type,beast]),frozenset(['BEAST']))
        self.assertFalse(common_tribes([all_type,dict(type='MINION')]))
        self.assertEqual(effective_tribes(all_type),TRIBES)
    def test_torga_draws_kindred_and_matching_minion(self):
        g=self.game();g.players[0].deck=['TLC_428','CAP_107t','CORE_CS2_029','TLC_429']
        with patch.object(g.rng,'choice',side_effect=lambda xs:xs[0]):self.play(g,'TLC_102')
        self.assertEqual([c.card_id for c in g.players[0].hand],['TLC_428','TLC_429'])
        self.assertEqual(g.players[0].deck,['CAP_107t','CORE_CS2_029'])
    def test_torga_draws_same_school_spell_partner(self):
        g=self.game();g.players[0].deck=['TLC_236','CORE_EX1_169','CORE_CS2_029'];self.play(g,'TLC_102')
        self.assertEqual([c.card_id for c in g.players[0].hand],['TLC_236','CORE_EX1_169'])
    def test_torga_no_kindred_no_draw_or_fatigue(self):
        for deck in ([],['CORE_CS2_029'],['TLC_102']):
            g=self.game();g.players[0].deck=deck.copy();self.play(g,'TLC_102')
            self.assertFalse(g.players[0].hand);self.assertEqual(g.players[0].deck,deck);self.assertEqual(g.players[0].health,30)
    def test_torga_no_partner_only_one_draw(self):
        g=self.game();g.players[0].deck=['TLC_428','CORE_CS2_029'];self.play(g,'TLC_102')
        self.assertEqual([c.card_id for c in g.players[0].hand],['TLC_428']);self.assertEqual(g.players[0].health,30)
    def test_torga_retains_physical_modifiers(self):
        g=self.game();a=Card(g._new_id(),'TLC_236');b=Card(g._new_id(),'CORE_EX1_169');b.cost_delta=-1;g.players[0].deck=[a,b]
        self.play(g,'TLC_102');self.assertIs(g.players[0].hand[1],b);self.assertEqual(b.cost_delta,-1)
    def test_torga_burns_still_remove_matching_second(self):
        g=self.game();g.players[0].deck=['TLC_236','CORE_EX1_169','CORE_CS2_029']
        for _ in range(9):self.put(g,'EDR_851t')
        self.play(g,'TLC_102');self.assertEqual(len(g.players[0].hand),10);self.assertEqual(g.players[0].deck,['CORE_CS2_029'])
    def test_torga_between_draws_observes_listener(self):
        g=self.game();g._summon(0,'CORE_TTN_843');g.players[0].deck=['TLC_236','CORE_EX1_169'];seen=[];original=g._receive_draw
        def receive(owner,value,**kwargs):
            seen.append(len(g.players[0].minions));return original(owner,value,**kwargs)
        with patch.object(g,'_receive_draw',side_effect=receive):self.play(g,'TLC_102')
        self.assertEqual(seen,[2,3]);self.assertEqual(len(g.players[0].minions),4)
    def test_torga_choice_suspends_preserving_first_identity(self):
        from expanded.cards import TRIGGERS
        g=self.game();g._summon(0,'CORE_TTN_843');g.players[0].deck=['TLC_236','CORE_EX1_169','CORE_CS2_029']
        with patch.dict(TRIGGERS,{'CORE_TTN_843':('friendly_card_drawn',[('discover_deck',)])}):
            self.play(g,'TLC_102');copy=deepcopy(g)
            index=next(i for i,o in enumerate(g.pending_choice['options']) if o['card_id']=='CORE_CS2_029')
            self.choose(g,index);self.choose(copy,index)
            self.assertEqual(g.observe(0),copy.observe(0));self.assertEqual([c.card_id for c in g.players[0].hand],['TLC_236','CORE_CS2_029','CORE_EX1_169'])
    def test_live_kindred_uses_race_fallback_and_valid_types(self):
        g=self.game();g.cards['TLC_428']=dict(g.cards['TLC_428'],races=[],race='MURLOC');g.players[0].previous_tribes={'MURLOC'}
        self.assertTrue(g._kindred('TLC_428',0));g.players[0].previous_tribes={'INVALID'};self.assertFalse(g._kindred('TLC_428',0))
