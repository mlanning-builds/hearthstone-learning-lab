"""Damage snapshots and follow-ups across internal spell continuations."""
import unittest
from unittest.mock import patch
from expanded import Game,Action,random_deck
from engine.game import Card

class CastDamageAmountsTests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('MAGE',31),random_deck('ROGUE',53)],seed=71)
        g.step(Action('mulligan'));g.step(Action('mulligan'))
        for p in g.players:
            p.hand=[];p.board=[];p.deck=['CORE_CS2_029']*20;p.health=30;p.mana=p.max_mana=10
        return g
    def cast(self,g,cid,policy='random',card=None):
        op=('cast_physical_spell',card,policy) if card else ('cast_fixed_spell',cid,policy)
        g._start_play_effects([op],dict(owner=0,source=None,target=0,bonus=0,lifesteal=False))
    def interrupt(self,g,opcode='damage_amount_hit'):
        dispatch=g._dispatch_effect;seen=[]
        def effect(op,ctx):
            dispatch(op,ctx)
            if op[0]==opcode:
                seen.append(op)
                if len(seen)==1:g._effect(('choose_fixed_summon',('AT_037t',)),dict(owner=0,source=None))
        return patch.object(g,'_dispatch_effect',side_effect=effect),seen
    def test_victim_owner_draw_waits_and_survives_victim_death(self):
        g=self.game();g._summon(1,'AT_037t');hook,_=self.interrupt(g)
        with hook:
            self.cast(g,'FIR_954');self.assertFalse(g.players[1].hand)
            g.step(g.legal_actions()[0])
        self.assertEqual(len(g.players[1].hand),1);self.assertFalse(g.players[0].hand)
    def test_damage_summon_count_waits_and_uses_actual_damage(self):
        g=self.game();m=g._summon(1,'CS3_020');hook,_=self.interrupt(g)
        with hook:
            self.cast(g,'TLC_221','enemies');self.assertFalse(g.players[0].minions)
            g.step(g.legal_actions()[0])
        self.assertEqual(sum(c.card_id=='TLC_249' for c in g.players[0].minions),3)
    def test_shielded_damage_does_not_summon(self):
        g=self.game();m=g._summon(1,'CS3_020');m.keywords.add('DIVINE_SHIELD')
        with patch.object(g.rng,'choice',side_effect=lambda options: m.uid if m.uid in options else options[0]):
            self.cast(g,'TLC_221','enemies')
        self.assertFalse(g.players[0].minions);self.assertNotIn('DIVINE_SHIELD',m.keywords)
    def test_torch_waits_before_generating_excess_copy(self):
        g=self.game();m=g._summon(1,'CS3_020');m.health=2;hook,_=self.interrupt(g)
        with hook:
            self.cast(g,'CATA_585');self.assertFalse(g.players[0].hand)
            g.step(g.legal_actions()[0])
        c=g.players[0].hand[0];self.assertEqual(c.card_id,'CATA_585');self.assertEqual(c.rule_state['damage'],6)
    def test_torch_uses_physical_payload_and_ignores_bonus(self):
        g=self.game();m=g._summon(1,'CS3_020');m.health=5
        c=Card(g._new_id(),'CATA_585');c.rule_state={'damage':3};c.spell_damage_bonus=5
        self.cast(g,c.card_id,card=c);self.assertEqual(m.health,2);self.assertFalse(g.players[0].hand)
    def test_overkill_discount_waits_and_uses_excess(self):
        g=self.game();m=g._summon(1,'AT_037t');c=g._add(0,'CORE_CS2_029');hook,_=self.interrupt(g)
        with hook:
            self.cast(g,'CATA_978');self.assertEqual(getattr(c,'cost_delta',0),0)
            g.step(g.legal_actions()[0])
        self.assertEqual(c.cost_delta,-7)
    def test_bone_flurry_pauses_between_individual_missiles(self):
        g=self.game();hook,seen=self.interrupt(g,'missile_hit')
        with hook:
            self.cast(g,'JAIL_445');self.assertEqual(len(seen),1)
            self.assertEqual(g.players[1].health,29);g.step(g.legal_actions()[0])
        self.assertEqual(len(seen),3);self.assertEqual(g.players[1].health,27)
    def test_bone_flurry_uses_current_death_history(self):
        g=self.game();g.players[0].minions_died_turn=1;self.cast(g,'JAIL_445');self.assertEqual(g.players[1].health,24)
    def test_held_armor_and_stealth_flags_survive_physical_cast(self):
        for cid,flag in [('TIME_702','minion'),('CAP_006','stealth_attack')]:
            with self.subTest(cid=cid):
                g=self.game();c=Card(g._new_id(),cid);c.rule_state={flag:True}
                self.cast(g,cid,'enemies',c);self.assertEqual(g.players[1].health,27)
                self.assertEqual(g.players[0].armor,5 if cid=='TIME_702' else 0)
    def test_distinct_damage_does_not_repeat_single_enemy(self):
        g=self.game();self.cast(g,'FIR_909');self.assertEqual(g.players[1].health,28)
    def test_other_damage_excludes_primary_target(self):
        g=self.game();self.cast(g,'TIME_855');self.assertEqual(g.players[1].health,27)
    def test_nab_shuffles_confirmed_dead_target(self):
        g=self.game();m=g._summon(1,'AT_037t');self.cast(g,'JAIL_225')
        copies=[c for c in g.players[0].deck if getattr(c,'card_id',None)=='AT_037t']
        self.assertEqual(len(copies),1);self.assertNotIn(m,g.players[1].board)
