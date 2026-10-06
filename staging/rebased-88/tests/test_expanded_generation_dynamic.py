"""Resource-dependent pools, physical death tracking and generated Deathrattles."""
import unittest
import test_expanded_generation as fixtures
from expanded.generation_cards import pool
from expanded.generation_extensions import RULES,DEATH_EFFECTS
from engine.cards import UnsupportedCard
from expanded import Action

class DynamicGenerationTests(unittest.TestCase):
    def setUp(self):self.h=fixtures.GenerationTests();self.g=self.h.game()
    def install(self,cost,cid):self.h.install(self.g,pool(card_type='MINION',minimum=cost,maximum=cost),[cid])
    def run_card(self,cid,**ctx):self.h.run_ops(self.g,RULES[cid][1],**ctx)
    def test_remaining_mana_spent_once(self):
        self.g.players[0].mana=6;self.install(6,'EX1_tk34');self.run_card('CATA_EVENT_400')
        self.assertEqual(self.g.players[0].mana,0);self.assertEqual(self.g.players[0].minions[0].card_id,'EX1_tk34')
    def test_missing_resource_pool_does_not_spend(self):
        before=self.g.rng.getstate()
        with self.assertRaises(UnsupportedCard):self.run_card('CATA_EVENT_400')
        self.assertEqual(self.g.players[0].mana,10);self.assertEqual(self.g.rng.getstate(),before)
    def test_corpses_use_actual_available_amount(self):
        self.g.players[0].corpses=6;self.install(6,'EX1_tk34');self.run_card('CORE_WW_374')
        self.assertEqual(self.g.players[0].corpses,0);self.assertEqual(len(self.g.players[0].minions),1)
    def test_missing_corpse_pool_preserves_resource(self):
        self.g.players[0].corpses=8
        with self.assertRaises(UnsupportedCard):self.run_card('CORE_WW_374')
        self.assertEqual(self.g.players[0].corpses,8)
    def test_hand_size_pool(self):
        from expanded.game import Card
        self.g.players[0].hand=[Card(self.g._new_id(),'TOKEN_COIN') for _ in range(6)]
        self.install(6,'EX1_tk34');self.run_card('CORE_BOT_256')
        self.assertEqual(len(self.g.players[0].hand),6);self.assertEqual(len(self.g.players[0].minions),1)
    def test_full_board_still_spends_mana(self):
        self.g.players[0].mana=6;self.install(6,'EX1_tk34')
        for _ in range(7):self.g._summon(0,'EDR_851t')
        self.run_card('CATA_EVENT_400');self.assertEqual(self.g.players[0].mana,0);self.assertEqual(len(self.g.players[0].minions),7)
    def test_surviving_damage_draws(self):
        m=self.g._summon(1,'EX1_tk34');self.run_card('END_020',target=m.uid)
        self.assertEqual(m.health,5);self.assertEqual(len(self.g.players[0].hand),1)
    def test_killed_target_summons(self):
        self.install(1,'CORE_CS2_188');m=self.g._summon(1,'EDR_851t');self.run_card('END_020',target=m.uid)
        self.assertFalse(self.g.players[1].minions);self.assertEqual(self.g.players[0].minions[0].card_id,'CORE_CS2_188')
    def test_absent_target_does_not_generate(self):
        self.run_card('END_020',target=999999);self.assertFalse(self.g.players[0].minions);self.assertFalse(self.g.players[0].hand)
    def test_ysondre_counts_recorded_deaths(self):
        request=DEATH_EFFECTS['EDR_465'][0][2]
        from expanded.generation import request_matches
        cid=next(cid for cid,d in self.g.cards.items() if request_matches(request,d,'MAGE'))
        self.h.install(self.g,request,[cid]);self.g.players[0].death_history=['EDR_465','EDR_851t','EDR_465']
        self.h.run_ops(self.g,DEATH_EFFECTS['EDR_465']);self.assertEqual(len(self.g.players[0].minions),2)
    def test_attached_random_deathrattle_excludes_source(self):
        source=self.g._summon(0,'EDR_851t');other=self.g._summon(0,'EX1_tk34')
        self.run_card('CORE_CATA_006',source=source)
        self.assertFalse(source.attached_death_effects)
        self.assertEqual(other.attached_death_effects,[('generation_dynamic_summon','death_source_cost')])
    def test_discover_summon_triggers_deathrattle_without_killing(self):
        from expanded.generation import request_matches
        request=RULES['DINO_415'][1][0][1]
        cid='CORE_SW_068'
        self.assertTrue(request_matches(request,self.g.cards[cid],'MAGE'))
        self.h.install(self.g,request,[cid]);self.run_card('DINO_415')
        self.g.step(Action('choose',choices=(0,)))
        self.assertTrue(any(m.card_id==cid for m in self.g.players[0].minions))
        self.assertNotIn(cid,self.g.players[0].death_history)
        self.assertEqual(self.g.players[0].armor,8)

    def test_outcast_and_corpse_additional_summons(self):
        from expanded.generation import request_matches
        request=pool(card_type='MINION',minimum=4,maximum=4)
        cid=next(cid for cid,d in self.g.cards.items() if request_matches(request,d,'MAGE'))
        self.h.install(self.g,request,[cid]);self.g.players[0].corpses=4
        self.run_card('END_005',outcast=True)
        self.assertEqual(len(self.g.players[0].minions),3);self.assertEqual(self.g.players[0].corpses,0)
    def test_insufficient_corpses_still_allows_outcast(self):
        from expanded.generation import request_matches
        request=pool(card_type='MINION',minimum=4,maximum=4)
        cid=next(cid for cid,d in self.g.cards.items() if request_matches(request,d,'MAGE'))
        self.h.install(self.g,request,[cid]);self.g.players[0].corpses=3
        self.run_card('END_005',outcast=True)
        self.assertEqual(len(self.g.players[0].minions),2);self.assertEqual(self.g.players[0].corpses,3)
    def test_attached_cost_resolves_when_minion_dies(self):
        source=self.g._summon(0,'EDR_851t');other=self.g._summon(0,'EX1_tk34')
        self.install(6,'EX1_tk34');self.run_card('CORE_CATA_006',source=source)
        old=other.uid;other.health=0;self.g._settle(allow_event_choices=True)
        replacement=next(m for m in self.g.players[0].minions if m.card_id=='EX1_tk34')
        self.assertNotEqual(replacement.uid,old);self.assertFalse(replacement.attached_death_effects)
    def test_bounced_target_is_not_counted_as_dead(self):
        m=self.g._summon(1,'EDR_851t');self.g._bounce(m)
        self.h.run_ops(self.g,[('generation_after_damage',m.uid,pool(card_type='MINION',minimum=1,maximum=1))])
        self.assertFalse(self.g.players[0].minions);self.assertFalse(self.g.players[0].hand)

    def test_silenced_summon_does_not_use_stale_deathrattle_snapshot(self):
        m=self.g._generation_place('CORE_SW_068','board',(('trigger_deathrattle',True),),dict(owner=0,source=None))
        self.g._silence(m);self.g._settle(allow_event_choices=True)
        self.assertEqual(self.g.players[0].armor,0)
