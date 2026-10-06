"""Execute extension bodies against explicit synthetic pools, not live eligibility."""
import unittest
import test_expanded_generation as fixtures
from expanded import Action
from expanded.cards import COLLECTIBLE_IDS
from expanded.generation_extensions import RULES,DEATH_EFFECTS,requests_for
from engine.cards import UnsupportedCard

class GenerationExtensionTests(unittest.TestCase):
    def setUp(self):self.helper=fixtures.GenerationTests();self.g=self.helper.game()
    def install(self,cid,ids):
        for request in requests_for(cid):self.helper.install(self.g,request,ids)
    def run_body(self,cid,death=False,**ctx):
        self.helper.run_ops(self.g,DEATH_EFFECTS[cid] if death else RULES[cid][1],**ctx)
    def test_only_closed_families_registered(self):
        self.assertEqual(set(RULES)&COLLECTIBLE_IDS,{'CATA_621','DINO_427'})
    def test_temporary_generated_minions_expire(self):
        cid='TLC_469';self.install(cid,['CORE_EX1_012']);self.run_body(cid,death=True)
        p=self.g.players[0];self.assertEqual(len(p.hand),2)
        self.assertTrue(all(self.g._is_temporary(c) for c in p.hand))
        self.g.step(Action('end'));self.assertFalse(p.hand)
    def test_temporary_discover_marks_selected_physical_card(self):
        cid='TLC_449';self.install(cid,['CORE_CS2_188']);self.run_body(cid)
        self.g.step(Action('choose',choices=(0,)))
        self.assertEqual(len(self.g.players[0].hand),1)
        self.assertTrue(self.g._is_temporary(self.g.players[0].hand[0]))
    def test_legendary_copies_have_one_cost_and_stats(self):
        cid='JAIL_448';self.install(cid,['CORE_EX1_012']);self.run_body(cid,death=True)
        hand=self.g.players[0].hand;self.assertEqual(len(hand),3)
        self.assertEqual(len({c.uid for c in hand}),3)
        for c in hand:
            d=self.g.cards[c.card_id]
            self.assertEqual((d['attack']+c.attack_bonus,d['health']+c.health_bonus,self.g._cost(c,0)),(1,1,1))
    def test_heal_then_summon_body(self):
        cid='JAIL_912';self.install(cid,['EX1_tk34']);self.g.players[0].health=10
        self.run_body(cid,death=True)
        self.assertEqual(self.g.players[0].health,16)
        self.assertEqual(self.g.players[0].minions[0].card_id,'EX1_tk34')
    def test_inactive_combo_does_not_require_pool(self):
        m=self.g._summon(1,'EDR_851t');self.run_body('TIME_712',target=m.uid,combo=False)
        self.assertFalse(self.g.players[1].minions);self.assertFalse(self.g.players[0].minions)
    def test_active_combo_without_pool_rejects(self):
        m=self.g._summon(1,'EDR_851t')
        with self.assertRaisesRegex(UnsupportedCard,'no reviewed membership'):
            self.run_body('TIME_712',target=m.uid,combo=True)

    def test_guard_dog_summons_deathrattle_minion(self):
        from expanded.generation import request_matches
        request=next(iter(requests_for('JAIL_878')))
        token=next(cid for cid,data in self.g.cards.items() if request_matches(request,data,'MAGE'))
        self.install('JAIL_878',[token]);self.run_body('JAIL_878',death=True)
        self.assertEqual(self.g.players[0].minions[0].card_id,token)
        self.assertFalse(self.g.players[0].hand)
    def test_active_combo_summons_after_destroy(self):
        from expanded.generation import request_matches
        request=next(iter(requests_for('TIME_712')))
        cid=next(cid for cid,data in self.g.cards.items() if request_matches(request,data,'MAGE'))
        self.install('TIME_712',[cid]);m=self.g._summon(1,'EDR_851t')
        self.run_body('TIME_712',target=m.uid,combo=True)
        self.assertFalse(self.g.players[1].minions)
        self.assertEqual(self.g.players[0].minions[0].card_id,cid)
