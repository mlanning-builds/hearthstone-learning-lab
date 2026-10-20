"""Actual registry plays use full frozen membership, never fixture pools."""
import unittest
import test_expanded_generation as fixtures
from expanded import Action
from expanded.cards import RULES
from expanded.game import Card
from expanded.generation_cards import requests_for
from engine.cards import UnsupportedCard

class GenerationProductionBatchTests(unittest.TestCase):
    def setUp(self):self.g=fixtures.GenerationTests().game();self.p=self.g.players[0]
    def play(self,cid,target=0):
        card=self.g._enter_hand(0,Card(self.g._new_id(),cid))
        action=next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==card.uid and a.target==target)
        self.g.step(action)
        return card
    def test_sky_raider_paid_play_generates_from_complete_pirate_universe(self):
        self.assertIn('CORE_DRG_024',RULES)
        self.play('CORE_DRG_024')
        generated=self.p.hand[-1]
        self.assertIn('PIRATE',self.g.cards[generated.card_id].get('races',()))
        self.assertEqual(self.p.played_history[-1]['card_id'],'CORE_DRG_024')
        self.assertEqual(len(self.p.minions),1)
    def test_frost_spell_generation_after_enemy_freeze(self):
        enemy=self.g._summon(1,'EDR_851t')
        self.play('JAIL_125',enemy.uid)
        self.assertGreaterEqual(enemy.frozen_until,0)
        self.assertEqual(self.g.cards[self.p.hand[-1].card_id]['spellSchool'],'FROST')
    def test_hook_heave_paid_choice_continues_to_two_exact_bodies(self):
        self.play('CAP_105')
        self.assertEqual(self.g.pending_choice['kind'],'generation_discover')
        self.assertFalse(self.p.board)
        self.g.step(Action('choose',choices=(0,)))
        self.assertEqual([m.card_id for m in self.p.minions],['CAP_107t','CAP_107t'])
        self.assertEqual(self.p.discoveries_total,1)
        self.assertEqual(len(self.p.hand),1)
    def test_closed_pirate_pools_across_all_classes(self):
        from standard.catalog import CLASSES
        for hero in CLASSES:
            self.p.hero_class=hero
            for cid in ('CORE_DRG_024','CAP_105'):
                for req in requests_for(cid):
                    self.assertTrue(self.g._generation_candidates(req,0))
    def test_unresolved_broad_pool_rolls_back_paid_play(self):
        request=next(iter(requests_for('CORE_EX1_189')))
        del self.g.cards[self.g._generation_candidates(request,0)[0]]
        c=self.g._enter_hand(0,Card(self.g._new_id(),'CORE_EX1_189'))
        before=self.g.observe(0);rng=self.g.rng.getstate()
        action=next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid)
        with self.assertRaisesRegex(UnsupportedCard,'eligible effects not implemented'):
            self.g.step(action)
        self.assertEqual(self.g.observe(0),before)
        self.assertEqual(self.g.rng.getstate(),rng)

    def test_illidari_studies_paid_discover_arms_outcast_discount(self):
        self.play('CORE_YOP_001')
        self.g.step(Action('choose',choices=(0,)))
        chosen=self.p.hand[-1]
        self.assertIn('OUTCAST',self.g.cards[chosen.card_id].get('mechanics',()))
        self.assertEqual(self.p.discoveries_total,1)
        self.assertTrue(self.p.cost_effects)

    def test_symbiosis_uses_complete_other_class_choose_one_pool(self):
        self.play('EDR_273')
        self.g.step(Action('choose',choices=(0,)))
        chosen=self.g.cards[self.p.hand[-1].card_id]
        self.assertIn('CHOOSE_ONE',chosen.get('mechanics',()))
        self.assertNotEqual(chosen['cardClass'],self.p.hero_class)

    def test_noxious_bribe_combines_owner_and_creates_plain_enemy_copy(self):
        self.p.hero_class='DRUID'
        self.play('JAIL_861')
        self.g.step(Action('choose',choices=(0,)))
        mine=self.p.hand[-1];theirs=self.g.players[1].hand[-1]
        self.assertEqual(mine.card_id,theirs.card_id)
        self.assertNotEqual(mine.uid,theirs.uid)
        self.assertTrue(mine.rule_state['choose_both'])
        self.assertFalse(getattr(theirs,'rule_state',{}).get('choose_both'))
