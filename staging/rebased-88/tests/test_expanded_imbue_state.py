"""Imbue progression, identity, ownership and visible state; not power fidelity."""
import unittest
from expanded import Game,Action,random_deck
from expanded.imbue import IMBUE_POWERS
from expanded.features import SCHEMA,encode_decision
from engine.cards import UnsupportedCard

class ImbueStateTests(unittest.TestCase):
    def game(self,hero='MAGE'):
        g=Game([random_deck(hero,31),random_deck('WARRIOR',53)],seed=71)
        g.step(Action('mulligan'));g.step(Action('mulligan'));g.current=0
        for p in g.players:p.hand=[];p.board=[];p.deck=['AT_037t']*10;p.mana=p.max_mana=10
        return g
    def test_all_eight_class_power_identities_use_frozen_metadata(self):
        for hero,cid in IMBUE_POWERS.items():
            with self.subTest(hero=hero):
                g=self.game(hero);g._imbue(0)
                self.assertEqual(g.players[0].primary_power['card_id'],cid)
                self.assertEqual(g.cards[cid]['type'],'HERO_POWER');self.assertEqual(g.cards[cid]['cardClass'],hero)
                self.assertEqual(g.players[0].primary_power['imbue_level'],1)
    def test_nonimbued_classes_still_record_payoff_progress(self):
        for hero in ('DEMONHUNTER','WARLOCK','WARRIOR'):
            g=self.game(hero);g._imbue(0,2)
            self.assertEqual(g.players[0].imbue_count,2);self.assertIsNone(g.players[0].primary_power)
    def test_upgrade_keeps_power_identity_and_does_not_refresh(self):
        g=self.game();g._imbue(0);p=g.players[0];uid=p.primary_power['uid'];p.power_used=True
        g._imbue(0,2);self.assertEqual(p.primary_power['uid'],uid)
        self.assertEqual(p.primary_power['imbue_level'],3);self.assertTrue(p.power_used)
    def test_progress_survives_replacement_and_is_restored(self):
        g=self.game();g._imbue(0,3);g._replace_primary_power(0,dict(card_id='EX1_tk33'))
        g._imbue(0);self.assertEqual(g.players[0].primary_power['card_id'],'EDR_851p')
        self.assertEqual(g.players[0].primary_power['imbue_level'],4)
    def test_imbue_targets_owner_without_switching_current_player(self):
        g=self.game();g.players[1].hero_class='HUNTER';g._effect(('imbue',2),dict(owner=1))
        self.assertEqual(g.players[1].imbue_count,2);self.assertEqual(g.players[0].imbue_count,0)
        self.assertEqual(g.current,0)
    def test_secondary_power_is_untouched(self):
        g=self.game();p=g.players[0];p.secondary_power=dict(card_id='JAIL_446hp',used=True)
        g._imbue(0);self.assertEqual(p.secondary_power,dict(card_id='JAIL_446hp',used=True))
    def test_invalid_count_leaves_state_unchanged(self):
        g=self.game()
        for count in (0,-1,True,1.5):
            with self.assertRaises(ValueError):g._imbue(0,count)
        self.assertEqual(g.players[0].imbue_count,0);self.assertIsNone(g.players[0].primary_power)
    def test_state_is_public_detached_and_encoded(self):
        g=self.game();g._imbue(0,3)
        for viewer in (0,1):
            view=g.observe(viewer);self.assertEqual(view['players'][0]['imbue_count'],3)
            view['players'][0]['primary_power']['imbue_level']=99
        self.assertEqual(g.players[0].primary_power['imbue_level'],3)
        view=g.observe(0);rows=encode_decision(dict(actor=0,observation=view,actions=view['legal_actions']))
        self.assertIn('imbue_count',str(rows));self.assertEqual(SCHEMA,'visible-action-features-v58')
    def test_missing_power_pool_raises_and_rolls_back_payment(self):
        g=self.game('PRIEST');g._imbue(0);before=g.observe(0)
        with self.assertRaisesRegex(UnsupportedCard,'no reviewed membership'):g.step(Action('power'))
        self.assertEqual(g.observe(0),before)
    def test_deathknight_passive_does_not_offer_an_activation(self):
        g=self.game('DEATHKNIGHT');g._imbue(0)
        self.assertFalse(any(a.kind=='power' for a in g.legal_actions()))
