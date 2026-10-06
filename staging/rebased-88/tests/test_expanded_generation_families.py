"""Live closed-family generation and physical Aura durations."""
import unittest
import test_expanded_generation as fixtures
from expanded.generation_families import FAMILIES
from expanded.generation_extensions import RULES as STAGED,CHOICES
from expanded.cards import RULES,COLLECTIBLE_IDS
from expanded.generation_cards import pool
from expanded.selectors import HERO_CLASSES
from engine.game import Card
from engine.cards import UnsupportedCard

class GenerationFamilyTests(unittest.TestCase):
    def setUp(self):self.h=fixtures.GenerationTests();self.g=self.h.game()
    def play(self,cid):
        card=Card(self.g._new_id(),cid);self.g._enter_hand(0,card)
        action=next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==card.uid)
        self.g.step(action)
    def test_live_family_outcomes_are_all_registered(self):
        self.assertTrue({'CATA_621','DINO_427'}<=COLLECTIBLE_IDS)
        for ids in FAMILIES.values():self.assertTrue(set(ids)<=COLLECTIBLE_IDS)
    def test_mask_pool_is_complete_for_each_class(self):
        request=RULES['DINO_427'][1][0][1]
        for hero in HERO_CLASSES:
            self.g.players[0].hero_class=hero
            actual=self.g._generation_candidates(request,0)
            expected={cid for cid in FAMILIES['mask'] if self.g.cards[cid]['cardClass']!=hero}
            self.assertEqual(set(actual),expected)
    def test_aura_pool_includes_dual_class_acceleration(self):
        self.assertEqual(set(self.g._generation_candidates(RULES['CATA_621'][1][0][1],0)),set(FAMILIES['paladin_aura']))
    def test_real_play_merchant_no_combo(self):
        self.g.players[0].cards_played=0;self.play('DINO_427')
        card=self.g.players[0].hand[0];self.assertIn(card.card_id,FAMILIES['mask']);self.assertEqual(card.cost_delta,0)
    def test_real_play_merchant_combo(self):
        self.g.players[0].cards_played=1;self.play('DINO_427')
        self.assertEqual(self.g.players[0].hand[0].cost_delta,-2)
    def test_real_play_triumph_has_attached_duration(self):
        self.play('CATA_621');card=self.g.players[0].hand[0]
        self.assertIn(card.card_id,FAMILIES['paladin_aura']);self.assertEqual(card.rule_state['aura_duration_delta'],1)
    def test_duration_affects_each_aura_without_changing_printed_rules(self):
        for cid in FAMILIES['paladin_aura']:
            with self.subTest(cid=cid):
                g=self.h.game();card=Card(g._new_id(),cid);g._b60_state(card)['aura_duration_delta']=1
                self.h.run_ops(g,RULES[cid][1],card_id=cid,physical_card=card)
                if cid=='CATA_480':self.assertEqual(g.players[0].end_repeat_expiries,[g.players[0].turns_taken+3])
                elif cid=='TTN_851':
                    effect=g.players[1].timed_cost_increases[-1];self.assertEqual(effect['end']-effect['start'],4)
                else:self.assertEqual(g.players[0].scheduled_effects[-1]['remaining'],4)
    def test_copy_preserves_duration(self):
        self.play('CATA_621');original=self.g.players[0].hand[0];copy=self.g._copy_card(original)
        self.assertEqual(copy.rule_state,original.rule_state);self.assertNotEqual(copy.uid,original.uid)
    def test_family_does_not_approve_arbitrary_modified_request(self):
        with self.assertRaises(UnsupportedCard):self.g._generation_candidates(pool(family='mask'),0)
    def test_small_attack_choice_uses_current_attack(self):
        # Staged choice registration stays gated; validate its shared target mode.
        a=self.g._summon(0,'EDR_851t');b=self.g._summon(1,'EX1_tk34')
        self.assertEqual(self.g._targets_for('CORE_CS2_029',0,CHOICES['EDR_463'][0][1]),[a.uid])
        self.g._buff(a,3,0)
        self.assertEqual(self.g._targets_for('CORE_CS2_029',0,CHOICES['EDR_463'][0][1]),[])
