"""Staged generation hooks, tested with explicit synthetic outcome contracts."""
import gzip
import json
import unittest
from pathlib import Path
import test_expanded_generation as fixtures
from expanded import Action
from engine.game import Card
from expanded.generation import request_matches
from expanded.generation_cards import pool
from expanded.generation_extensions import RULES, TOKEN_RULES, requests_for

class GenerationHeldHooksTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with gzip.open(Path(__file__).resolve().parents[1]/'data/standard/all_cards.json.gz','rt') as f:
            cls.metadata={d['id']:d for d in json.load(f)}
    def setUp(self):
        self.h=fixtures.GenerationTests();self.g=self.h.game()
        self.g.cards=dict(self.g.cards)
        for cid in ('CATA_140','CATA_499','DINO_430','EDR_461','EDR_461t','EDR_781'):
            self.g.cards[cid]=self.metadata[cid]
    def run_card(self,cid,**ctx):self.h.run_ops(self.g,RULES[cid][1],**ctx)
    def install(self,request):
        cid=next(cid for cid,d in self.g.cards.items() if request_matches(request,d,'MAGE'))
        self.h.install(self.g,request,[cid]);return cid
    def held(self,cid):
        card=Card(self.g._new_id(),cid);self.g._enter_hand(0,card);return card
    def test_fill_hand_discount_uses_physical_progress(self):
        card=self.held('CATA_140');self.g._held_spend(0,25)
        self.g.players[0].hand.remove(card)
        request=RULES['CATA_140'][1][0][1];self.install(request)
        self.run_card('CATA_140',physical_card=card)
        self.assertEqual(len(self.g.players[0].hand),10)
        self.assertTrue(all(self.g._cost(c,0)==1 for c in self.g.players[0].hand))
    def test_fill_hand_without_progress_keeps_printed_cost(self):
        card=self.held('CATA_140');self.g._held_spend(0,24)
        self.g.players[0].hand.remove(card);request=RULES['CATA_140'][1][0][1];self.install(request)
        self.run_card('CATA_140',physical_card=card)
        self.assertTrue(all(c.cost_delta==0 for c in self.g.players[0].hand))
    def test_held_mana_is_per_copy_and_capped(self):
        a=self.held('CATA_140');self.g._held_spend(0,24);b=self.held('CATA_140');self.g._held_spend(0,3)
        self.assertEqual(a.rule_state['held_mana_spent'],25);self.assertEqual(b.rule_state['held_mana_spent'],3)
    def test_full_hand_fill_does_not_use_rng(self):
        self.install(RULES['CATA_140'][1][0][1])
        for _ in range(10):self.held('TOKEN_COIN')
        before=self.g.rng.getstate();self.run_card('CATA_140')
        self.assertEqual(self.g.rng.getstate(),before)
    def test_multiple_type_filter_uses_distinct_types(self):
        request=pool(card_type='MINION',minimum_tribes=2)
        for types,expected in [(['BEAST','UNDEAD'],True),(['BEAST','BEAST'],False),(['ALL'],True),([],False)]:
            self.assertEqual(request_matches(request,dict(type='MINION',cost=1,races=types),'MAGE'),expected)
    def test_discard_has_intrinsic_summons(self):
        card=self.held('CATA_499');request=next(iter(requests_for('CATA_499')));self.install(request)
        self.g._discard_card(0,card);self.g._settle(allow_event_choices=True)
        self.assertEqual(len(self.g.players[0].minions),2);self.assertEqual(self.g.players[0].discard_history,['CATA_499'])
    def test_play_body_does_not_discard(self):
        self.install(next(iter(requests_for('CATA_499'))));self.run_card('CATA_499')
        self.assertEqual(len(self.g.players[0].minions),2);self.assertFalse(self.g.players[0].discard_history)
    def test_successful_return_generates_two_minions(self):
        self.install(next(iter(requests_for('EDR_781'))));m=self.g._summon(0,'EDR_781')
        self.g._bounce(m);self.g._settle(allow_event_choices=True)
        self.assertEqual(len(self.g.players[0].minions),2);self.assertEqual(self.g.players[0].hand[0].card_id,'EDR_781')
    def test_full_hand_return_does_not_generate(self):
        m=self.g._summon(0,'EDR_781')
        for _ in range(10):self.held('TOKEN_COIN')
        self.g._bounce(m);self.g._settle(allow_event_choices=True)
        self.assertFalse(self.g.players[0].minions)
    def test_silenced_return_has_no_trigger(self):
        m=self.g._summon(0,'EDR_781');self.g._silence(m);self.g._bounce(m);self.g._settle(allow_event_choices=True)
        self.assertFalse(self.g.players[0].minions)
    def test_moon_transform_after_three_owner_spells(self):
        card=self.held('EDR_461');uid=card.uid
        self.g._b60_event('spell_cast',dict(owner=1,card_id='TOKEN_COIN'))
        for _ in range(2):self.g._b60_event('spell_cast',dict(owner=0,card_id='TOKEN_COIN'))
        self.assertEqual(card.card_id,'EDR_461')
        self.g._b60_event('spell_cast',dict(owner=0,card_id='TOKEN_COIN'))
        self.assertEqual((card.card_id,card.uid),('EDR_461t',uid))
    def test_upgraded_moon_body_summons_six_cost(self):
        ops=TOKEN_RULES['EDR_461t'][1];cid=self.install(ops[0][1]);self.h.run_ops(self.g,ops)
        self.assertEqual([m.card_id for m in self.g.players[0].minions],[cid,cid])
    def test_absorb_choice_adds_stats_and_death_payload_without_hand_card(self):
        source=self.g._summon(0,'DINO_430');request=RULES['DINO_430'][1][0][1];cid=self.install(request)
        before=(source.attack,source.health);self.run_card('DINO_430',source=source)
        self.g.step(Action('choose',choices=(0,)))
        self.assertEqual((source.attack,source.health),(before[0]+self.g.cards[cid]['attack'],before[1]+self.g.cards[cid]['health']))
        self.assertFalse(self.g.players[0].hand)
        source.health=0;self.g._settle(allow_event_choices=True)
        self.assertEqual([m.card_id for m in self.g.players[0].minions],[cid])
    def test_absorb_missing_source_does_not_buff_replacement(self):
        source=self.g._summon(0,'DINO_430');self.install(RULES['DINO_430'][1][0][1])
        self.run_card('DINO_430',source=source);self.g.players[0].board.remove(source)
        replacement=self.g._summon(0,'EDR_851t');self.g.step(Action('choose',choices=(0,)))
        self.assertEqual((replacement.attack,replacement.health),(1,1));self.assertFalse(replacement.attached_death_effects)
    def test_absorbed_death_payload_is_removed_by_silence(self):
        source=self.g._summon(0,'DINO_430');self.install(RULES['DINO_430'][1][0][1]);self.run_card('DINO_430',source=source)
        self.g.step(Action('choose',choices=(0,)));self.g._silence(source);source.health=0;self.g._settle(allow_event_choices=True)
        self.assertFalse(self.g.players[0].minions)
