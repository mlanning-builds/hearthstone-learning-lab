"""Post-draw continuation and provenance/discard casting integration."""
import unittest
from unittest.mock import patch
from expanded import Game,Action,random_deck
from engine.game import Card

class CastDrawFollowupsTests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('MAGE',31),random_deck('ROGUE',53)],seed=71)
        g.step(Action('mulligan'));g.step(Action('mulligan'))
        for p in g.players:
            p.hand=[];p.board=[];p.deck=[];p.health=30;p.mana=p.max_mana=10;p.armor=0
        return g
    def card(self,g,cid,original=False):
        c=Card(g._new_id(),cid)
        if original:
            c._starting_owner=0;d=g.cards[cid];c._starting_identity=d.get('countAsCopyOfDbfId',d.get('dbfId',cid))
        return c
    def cast(self,g,cid):
        g._start_play_effects([('cast_fixed_spell',cid,'random')],dict(owner=0,source=None,target=0,bonus=0,lifesteal=False))
    def interrupt_draw(self,g):
        dispatch=g._dispatch_effect
        def effect(op,ctx):
            dispatch(op,ctx)
            if op[0]=='capture_effect_draw':g._effect(('choose_fixed_summon',('AT_037t',)),dict(owner=0,source=None))
        return patch.object(g,'_dispatch_effect',side_effect=effect)
    def test_barnabus_waits_before_buff_and_armor(self):
        g=self.game();c=self.card(g,'CS3_020');g.players[0].deck=[c]
        with self.interrupt_draw(g):
            self.cast(g,'TLC_231');self.assertIn(c,g.players[0].hand)
            self.assertEqual(c.health_bonus,0);self.assertEqual(g.players[0].armor,0)
            g.step(g.legal_actions()[0])
        self.assertEqual(c.health_bonus,5);self.assertEqual(g.players[0].armor,5)
    def test_barnabus_small_minion_has_no_bonus(self):
        g=self.game();c=self.card(g,'AT_037t');g.players[0].deck=[c];self.cast(g,'TLC_231')
        self.assertEqual(c.health_bonus,0);self.assertEqual(g.players[0].armor,0)
    def test_barnabus_burn_does_not_gain_armor(self):
        g=self.game();g.players[0].deck=['CS3_020'];g.players[0].hand=[self.card(g,'CORE_CS2_029') for _ in range(10)]
        self.cast(g,'TLC_231');self.assertEqual(g.players[0].armor,0);self.assertFalse(g.players[0].deck)
    def test_reflection_waits_and_creates_fresh_stats(self):
        g=self.game();c=self.card(g,'CS3_020');c.attack_bonus=4;g.players[0].deck=[c]
        with self.interrupt_draw(g):
            self.cast(g,'FIR_941');self.assertFalse(g.players[0].minions)
            g.step(g.legal_actions()[0])
        m=next(m for m in g.players[0].minions if m.card_id==c.card_id)
        self.assertEqual((m.attack,m.max_health),(8,8));self.assertIn('DIVINE_SHIELD',m.keywords)
        self.assertIn(c,g.players[0].hand);self.assertEqual(c.attack_bonus,4)
    def test_reflection_keeps_burned_identity_for_summon(self):
        g=self.game();g.players[0].deck=['CS3_020'];g.players[0].hand=[self.card(g,'CORE_CS2_029') for _ in range(10)]
        self.cast(g,'FIR_941');self.assertEqual(len(g.players[0].minions),1);self.assertEqual(len(g.players[0].hand),10)
    def test_origin_draws_select_original_and_generated_spells(self):
        g=self.game();a=self.card(g,'CORE_CS2_029',True);b=self.card(g,'CORE_CS2_029');m=self.card(g,'CS3_020')
        g.players[0].deck=[a,m,b];self.cast(g,'EDR_251')
        self.assertEqual(g.players[0].hand,[a,b]);self.assertEqual(g.players[0].deck,[m])
    def test_origin_discount_preserves_original_cost(self):
        g=self.game();a=self.card(g,'CORE_CS2_029',True);b=self.card(g,'CORE_CS2_029');g.players[0].hand=[a,b]
        before=(g._cost(a,0),g._cost(b,0));self.cast(g,'TLC_364')
        self.assertEqual((g._cost(a,0),g._cost(b,0)),(before[0],before[1]-1))
    def test_discard_condition_repeats_damage_only_with_eligible_card(self):
        for eligible in (False,True):
            with self.subTest(eligible=eligible):
                g=self.game();g.players[0].hand=[self.card(g,'CORE_CS2_029' if eligible else 'CS3_020')]
                self.cast(g,'FIR_910')
                self.assertEqual(sum(p.health for p in g.players),60-(6 if eligible else 3))
                self.assertEqual(len(g.players[0].hand),0 if eligible else 1)
    def test_unknown_discard_child_not_admitted(self):
        g=self.game();self.assertFalse(g._supports_internal_operations([('if_discarded',('unknown_effect',))]))
