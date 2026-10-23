"""Scripted Herald routing and starting-deck eligibility; no neural games."""
import unittest
from unittest.mock import patch
from expanded import Action
from expanded.herald import SOLDIERS, HERALD_COLOSSALS
from expanded.generation_cards import pool
from expanded.pools import GenerationPool
import test_expanded_generation as fixtures


class HeraldRoutingResumeTests(unittest.TestCase):
    def game(self):
        g=fixtures.GenerationTests().game()
        g.players[0].hero_class='DRUID'
        g.players[1].hero_class='WARRIOR'
        return g

    def test_paid_ultraxion_uses_opponent_army_and_discounts_deathwing(self):
        g=self.game(); c=g._add(0,'CATA_497')
        g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid))
        self.assertIn(SOLDIERS['WARRIOR'],[m.card_id for m in g.players[0].minions])
        self.assertEqual(g.players[0].herald_count,1)
        self.assertEqual(g.players[0].deathwing_discount,1)
        g.assert_invariants()

    def test_all_six_opponent_armies_route_without_random_choice(self):
        for army,cid in SOLDIERS.items():
            with self.subTest(army=army):
                g=self.game();g.players[1].hero_class=army
                with patch.object(g,'_summon',return_value=None) as summon, patch.object(g,'_herald_entry_preflight'):
                    before=g.rng.getstate();g._herald(0,source_card_id='CATA_497')
                    self.assertEqual(summon.call_args.args[1],cid)
                    self.assertEqual(g.rng.getstate(),before)
                    self.assertEqual(g.players[0].herald_count,1)

    def test_owner_class_then_single_source_class_precede_opponent(self):
        g=self.game();g.players[0].hero_class='WARRIOR'
        with patch.object(g,'_summon',return_value=None) as summon, patch.object(g,'_herald_entry_preflight'):
            g._herald(0,source_card_id='CATA_525')
            self.assertEqual(summon.call_args.args[1],SOLDIERS['WARRIOR'])
            g.players[0].hero_class='DRUID';g._herald(0,source_card_id='CATA_525')
            self.assertEqual(summon.call_args.args[1],SOLDIERS['DEMONHUNTER'])

    def candidates(self,g):
        r=pool(card_type='MINION',tribe='DRAGON')
        g._generation_pools={(r,'DRUID'):GenerationPool('fixture',('CATA_497','CORE_EX1_043'),'Controlled membership')}
        return g._generation_candidates(r,0)

    def test_merithra_random_dragon_pool_excludes_ultraxion_without_starting_herald(self):
        g=self.game();self.assertNotIn('CATA_497',self.candidates(g))
        g._add(0,'CATA_497')
        self.assertNotIn('CATA_497',self.candidates(g))

    def test_starting_herald_or_related_colossal_unlocks_pool(self):
        for source in ('CATA_497','CATA_561','CATA_190h',*sorted(HERALD_COLOSSALS)):
            with self.subTest(source=source):
                g=self.game();g.players[0].starting_deck.append(source)
                self.assertIn('CATA_497',self.candidates(g))

    def test_generation_gate_is_per_owner_not_opponent(self):
        g=self.game();g.players[1].starting_deck.append('CATA_497')
        self.assertNotIn('CATA_497',self.candidates(g))
