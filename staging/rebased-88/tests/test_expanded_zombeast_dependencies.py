"""Paid historical bodies and compiled timed Dormant entry, without training."""
import unittest
import test_expanded_generation as fixtures
import test_expanded_forge_intrinsics as intrinsic_fixtures
from expanded import Action,cards
from expanded.game import Card
from expanded.selectors import has_tribe,TRIBES
from engine.cards import UnsupportedCard


class ZombeastDependencyTests(unittest.TestCase):
    def game(self):return fixtures.GenerationTests().game()

    def play(self,g,cid):
        c=Card(g._new_id(),cid);g.players[0].hand.append(c)
        g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid))
        return next(m for m in g.players[0].all_minions if m.card_id==cid)

    def test_amalgams_have_all_types_after_paid_play_and_silence(self):
        for cid in ('DMF_532','GIL_681','NX2_050'):
            with self.subTest(cid=cid):
                g=self.game();m=self.play(g,cid)
                for tribe in TRIBES:self.assertTrue(has_tribe(g._card_data(m),tribe))
                if cid=='DMF_532':self.assertIn('TAUNT',g._effective_keywords(m))
                g._silence(m)
                for tribe in TRIBES:self.assertTrue(has_tribe(g._card_data(m),tribe))
                self.assertNotIn(cid,cards.COLLECTIBLE_IDS)

    def test_pelican_sleeps_then_awakes_with_rush(self):
        g=self.game();enemy=g._summon(1,'EDR_851t');m=self.play(g,'TSC_647')
        self.assertEqual(m.dormant,1);self.assertNotIn(m,g.players[0].minions)
        g.step(Action('end'));g.step(Action('end'))
        self.assertEqual(m.dormant,0)
        attacks=[a for a in g.legal_actions() if a.kind=='attack' and a.source==m.uid]
        self.assertTrue(any(a.target==enemy.uid for a in attacks));self.assertFalse(any(a.target<0 for a in attacks))

    def test_explicit_component_recipes_have_complete_structural_contracts(self):
        from expanded.zombeast_keyword_parts import PARTS,KEYWORDS
        g=self.game();g.forge_contracts={('zombeast',2):tuple(PARTS.values())}
        self.assertEqual(len(KEYWORDS),29);self.assertEqual(len(g._forge_pool('zombeast',2,0)),34)
        self.assertIsNotNone(g.standard_pack_contract)


class CompiledDormancyTests(unittest.TestCase):
    def setUp(self):
        self.fixture=intrinsic_fixtures.ForgeIntrinsicTests();self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups);self.game=self.fixture.game

    def test_compiled_dormancy_precedes_entry_and_counts_owner_turns(self):
        g=self.game;c=self.fixture.craft((('dormant_turns',3),),keywords=('TAUNT',))
        g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid))
        m=g.players[0].all_minions[-1]
        self.assertEqual(m.dormant,3);self.assertNotIn(m,g.players[0].minions)
        for remaining in (2,1,0):
            g.step(Action('end'));g.step(Action('end'));self.assertEqual(m.dormant,remaining)
        self.assertIn('TAUNT',g._effective_keywords(m))

    def test_copy_keeps_remaining_dormancy_but_fresh_recipe_restarts_it(self):
        g=self.game;c=self.fixture.craft((('dormant_turns',3),))
        m=g._summon(0,c.card_id,entry_source=c);m.dormant=2
        copied=g._summon(0,m.card_id,copy_from=m)
        fresh=g._summon(0,m.card_id,entry_source=m)
        self.assertEqual((copied.dormant,fresh.dormant),(2,3))

    def test_invalid_initial_duration_rejects_before_rng(self):
        for value in (True,0,-1,'1'):
            with self.subTest(value=value):
                rng=self.game.rng.getstate()
                with self.assertRaises(UnsupportedCard):self.fixture.craft((('dormant_turns',value),))
                self.assertEqual(self.game.rng.getstate(),rng)
