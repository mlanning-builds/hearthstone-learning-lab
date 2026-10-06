"""Stored spells, owner-turn lifetime and scheduled observation isolation."""
import json
import unittest
from unittest.mock import patch
from expanded import Game,Action,random_deck
from engine.cards import UnsupportedCard
from expanded.features import encode_decision

class StoredSpellAuraTests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('PALADIN',31),random_deck('MAGE',53)],seed=71)
        g.step(Action('mulligan'));g.step(Action('mulligan'));g.current=0
        for p in g.players:
            p.hand=[];p.board=[];p.deck=['AT_037t']*20;p.health=p.max_health=100;p.mana=p.max_mana=10;p.armor=0
        return g
    def ursol(self,g):
        g.players[0].mana=10;c=g._add(0,'EDR_259')
        g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid))
        return next(m for m in g.players[0].minions if m.card_id=='EDR_259')
    def next_owner(self,g):
        g.step(Action('end'));g.step(Action('end'))
    def test_removes_highest_spell_without_immediate_cast_or_discard(self):
        g=self.game();c=g._add(0,'CORE_EX1_606');small=g._add(0,'TOKEN_COIN');self.ursol(g)
        self.assertNotIn(c,g.players[0].hand);self.assertIn(small,g.players[0].hand)
        self.assertEqual(g.players[0].armor,0);self.assertFalse(g.players[0].discard_history)
        self.assertIs(g.players[0].scheduled_effects[0]['stored_card'],c)
    def test_exactly_three_owner_end_casts_and_expiry(self):
        g=self.game();g._add(0,'CORE_EX1_606');self.ursol(g)
        for expected in (5,10,15):
            self.next_owner(g);self.assertEqual(g.players[0].armor,expected)
        self.assertFalse(g.players[0].scheduled_effects);self.next_owner(g)
        self.assertEqual(g.players[0].armor,15)
    def test_opponent_end_does_not_spend_owner_aura(self):
        g=self.game();g._add(0,'CORE_EX1_606');self.ursol(g);g.step(Action('end'))
        self.assertEqual(g.players[0].scheduled_effects[0]['remaining'],2)
        g.step(Action('end'));self.assertEqual(g.players[0].scheduled_effects[0]['remaining'],2)
    def test_highest_uses_current_hand_cost(self):
        g=self.game();a=g._add(0,'CORE_CS2_029');a.set_cost=0;b=g._add(0,'CORE_EX1_606');self.ursol(g)
        self.assertIn(a,g.players[0].hand);self.assertIs(g.players[0].scheduled_effects[0]['stored_card'],b)
    def test_tied_cost_pool_keeps_each_physical_copy(self):
        g=self.game();a=g._add(0,'CORE_EX1_606');b=g._add(0,'CORE_EX1_606')
        with patch.object(g.rng,'choice',return_value=b) as choose:self.ursol(g)
        self.assertEqual([c.uid for c in choose.call_args[0][0]],[a.uid,b.uid])
        self.assertIn(a,g.players[0].hand);self.assertNotIn(b,g.players[0].hand)
    def test_no_spell_does_not_create_empty_aura(self):
        g=self.game();g._add(0,'AT_037t');self.ursol(g);self.assertFalse(g.players[0].scheduled_effects)
    def test_aura_survives_source_silence_and_death(self):
        g=self.game();g._add(0,'CORE_EX1_606');m=self.ursol(g);g._silence(m);m.health=0;g._settle()
        self.next_owner(g);self.assertEqual(g.players[0].armor,5)
    def test_stored_spell_remains_fixed_after_new_spell_enters_hand(self):
        g=self.game();g._add(0,'CORE_EX1_606');self.ursol(g);c=g._add(0,'CORE_CS2_029');c.set_cost=9
        self.next_owner(g);self.assertEqual(g.players[0].armor,5);self.assertIn(c,g.players[0].hand)
    def test_each_tick_has_independent_spell_copy_and_current_spell_damage(self):
        g=self.game();c=g._add(0,'CORE_CS2_029');c.spell_damage_bonus=2;self.ursol(g)
        # Remove caster so the only random targets are the two heroes.
        g.players[0].board.clear();before=sum(p.health for p in g.players)
        self.next_owner(g);self.assertEqual(sum(p.health for p in g.players),before-8)
        with patch.object(g,'_spell_damage',return_value=1):self.next_owner(g)
        self.assertEqual(sum(p.health for p in g.players),before-17)
        self.assertEqual(c.spell_damage_bonus,2)
    def test_automatic_discover_completes_end_turn(self):
        g=self.game();g._add(0,'CORE_DS1_184');self.ursol(g);g.step(Action('end'))
        self.assertIsNone(g.pending_choice);self.assertEqual(g.current,1)
        self.assertEqual(len(g.players[0].hand),1)
    def test_minion_end_doubling_does_not_double_scheduled_spell(self):
        g=self.game();g._add(0,'CORE_EX1_606');self.ursol(g);g.players[0].end_repeat_expiries=[10]
        self.next_owner(g);self.assertEqual(g.players[0].armor,5)
    def test_aura_counts_as_active_and_public_view_has_no_card_object(self):
        g=self.game();c=g._add(0,'CORE_EX1_606');c._starting_owner=0;self.ursol(g)
        self.assertTrue(g._batch30_state('aura_active',0))
        for viewer in (0,1):
            v=g.observe(viewer);e=v['players'][0]['scheduled_effects'][0]
            self.assertEqual(e['stored_spell']['card_id'],'CORE_EX1_606')
            self.assertNotIn('_starting_owner',json.dumps(e));e['stored_spell']['card_id']='wrong'
        self.assertEqual(c.card_id,'CORE_EX1_606')
        view=g.observe(0);rows=encode_decision(dict(actor=0,observation=view,actions=view['legal_actions']))
        self.assertIn('stored_spell',str(rows))
    def test_unsupported_highest_is_not_replaced_by_supported_lower(self):
        g=self.game();c=g._add(0,'CORE_RLK_567');c.set_cost=9;g._add(0,'CORE_EX1_606');u=g._add(0,'EDR_259')
        action=next(a for a in g.legal_actions() if a.kind=='play' and a.source==u.uid);before=g.observe(0)
        with self.assertRaises(UnsupportedCard):g.step(action)
        self.assertEqual(g.observe(0),before)
    def test_two_auras_store_separate_spells(self):
        g=self.game();g._add(0,'CORE_EX1_606');self.ursol(g);g._add(0,'CORE_EX1_606');self.ursol(g)
        self.next_owner(g);self.assertEqual(g.players[0].armor,10)
        self.assertEqual(len(g.players[0].scheduled_effects),2)
    def test_generated_aura_token_is_cast_and_dependency_is_declared(self):
        from expanded.dependencies import literal_dependencies
        from expanded.cards import RULES
        g=self.game();g._add(0,'CORE_EX1_606');self.ursol(g)
        self.assertEqual(g.players[0].scheduled_effects[0]['source_card_id'],'EDR_259e1')
        self.assertTrue(any(e['event']=='internal_spell_cast' and e['card']=='EDR_259e1' for e in g.events))
        self.assertIn('EDR_259e1',literal_dependencies(RULES['EDR_259'][1]))
    def test_unbound_aura_token_does_not_guess_a_payload(self):
        g=self.game()
        with self.assertRaisesRegex(UnsupportedCard,'requires its spell payload'):
            g._start_play_effects([('cast_fixed_spell','EDR_259e1','random')],dict(owner=0,source=None,target=0,bonus=0,lifesteal=False))
        self.assertFalse(g.players[0].scheduled_effects)
    def test_niri_repeats_bound_aura_without_consuming_another_hand_spell(self):
        g=self.game();g._summon(0,'TLC_836');g._add(0,'CORE_EX1_606');small=g._add(0,'TOKEN_COIN')
        self.ursol(g);self.assertEqual(len(g.players[0].scheduled_effects),2)
        self.assertIn(small,g.players[0].hand)
        self.next_owner(g);self.assertEqual(g.players[0].armor,10)
