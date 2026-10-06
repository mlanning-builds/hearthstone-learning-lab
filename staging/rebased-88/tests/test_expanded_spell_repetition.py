"""Resumable effect repetition; consumer attribution remains separately reviewed."""
import unittest
from unittest.mock import patch
from expanded import Game,Action,random_deck
from engine.game import Card
from engine.cards import UnsupportedCard
from expanded.cards import RULES

class SpellRepetitionTests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('MAGE',31),random_deck('ROGUE',53)],seed=71)
        g.step(Action('mulligan'));g.step(Action('mulligan'))
        for p in g.players:
            p.hand=[];p.board=[];p.deck=[];p.health=30;p.mana=p.max_mana=10;p.cards_played=0
        return g
    def context(self,g,target=0):
        return dict(owner=0,source=None,target=target,card_id='CORE_CS2_029',spell=True,bonus=0,lifesteal=False,physical_card=Card(g._new_id(),'CORE_CS2_029'))
    def repeat(self,g,ops,ctx,count=2):
        g._start_play_effects([('repeat_spell_effects',tuple(ops),ctx,count)],ctx)
    def test_same_target_is_preserved(self):
        g=self.game();a=g._summon(1,'AT_037t');b=g._summon(1,'AT_037t');a.health=a.max_health=10
        self.repeat(g,[('damage',2)],self.context(g,a.uid))
        self.assertEqual(a.health,6);self.assertEqual(b.health,b.max_health)
        self.assertEqual(g._spell_repeat_depth,0)
    def test_lethal_damage_then_healing_precedes_death_settlement(self):
        g=self.game();m=g._summon(0,'AT_037t');m.health=2;m.max_health=10
        self.repeat(g,[('damage',3),('heal',4)],self.context(g,m.uid))
        self.assertIn(m,g.players[0].minions);self.assertEqual(m.health,4)
        self.assertFalse(g.players[0].death_records)
    def test_hero_can_recover_before_winner_check(self):
        g=self.game();g.players[0].health=2
        self.repeat(g,[('damage',3),('heal',4)],self.context(g,-1))
        self.assertFalse(g.terminal);self.assertEqual(g.players[0].health,4)
    def test_unhealed_hero_finishes_after_boundary(self):
        g=self.game();g.players[1].health=2
        self.repeat(g,[('damage',3)],self.context(g,-2))
        self.assertTrue(g.terminal);self.assertEqual(g.winner,0);self.assertEqual(g._spell_repeat_depth,0)
    def test_manual_choices_suspend_each_copy(self):
        g=self.game();g.players[0].deck=['CORE_CS2_029','CORE_CS2_024']
        self.repeat(g,[('discover_deck',)],self.context(g))
        self.assertEqual(g.phase,'choice');self.assertEqual(g._spell_repeat_depth,1)
        g.step(Action('choose',choices=(0,)))
        self.assertIsNotNone(g.pending_choice);self.assertEqual(len(g.players[0].hand),1)
        g.step(Action('choose',choices=(0,)))
        self.assertIsNone(g.pending_choice);self.assertEqual(len(g.players[0].hand),2)
        self.assertEqual(g._spell_repeat_depth,0);g.assert_invariants()
    def test_zero_health_target_survives_choice_and_recovers(self):
        g=self.game();m=g._summon(0,'AT_037t');m.health=2;m.max_health=10
        g.players[0].deck=['CORE_CS2_029','CORE_CS2_024']
        self.repeat(g,[('damage',3),('discover_deck',),('heal',4)],self.context(g,m.uid))
        self.assertEqual(m.health,-1);g.assert_invariants()
        g.step(Action('choose',choices=(0,)))
        self.assertEqual(m.health,0);self.assertIsNotNone(g.pending_choice)
        g.step(Action('choose',choices=(0,)))
        self.assertEqual(m.health,4);self.assertIn(m,g.players[0].minions)
    def test_nested_repetition_balances_boundaries(self):
        g=self.game();ctx=self.context(g,-2)
        self.repeat(g,[('repeat_spell_effects',(('damage',1),),ctx,2)],ctx)
        self.assertEqual(g.players[1].health,26);self.assertEqual(g._spell_repeat_depth,0)
    def test_effect_repetition_does_not_pay_or_publish_play(self):
        g=self.game();ctx=self.context(g,-2)
        self.repeat(g,[('damage',1)],ctx)
        p=g.players[0];self.assertEqual(p.mana,10);self.assertEqual(p.cards_played,0);self.assertFalse(p.played_history)
    def test_target_removed_by_first_copy_is_not_replaced(self):
        g=self.game();m=g._summon(1,'AT_037t');other=g._summon(1,'AT_037t')
        self.repeat(g,[('dream_bounce',)],self.context(g,m.uid))
        self.assertNotIn(m,g.players[1].minions);self.assertIn(other,g.players[1].minions)
        self.assertEqual(len(g.players[1].hand),1);self.assertEqual(g._spell_repeat_depth,0)
    def test_failed_play_rolls_back_repetition_boundary_and_damage(self):
        g=self.game();c=g._add(0,'CORE_CS2_029');ctx=self.context(g,-2)
        action=next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid and a.target==-2)
        before=g.observe(0);state=g.rng.getstate()
        with patch.dict(RULES,{'CORE_CS2_029':('character',[('repeat_spell_effects',(('damage',1),('nonexistent_opcode',)),ctx,2)])}):
            with self.assertRaises(UnsupportedCard):g.step(action)
        self.assertEqual(g.observe(0),before);self.assertEqual(g.rng.getstate(),state);self.assertEqual(g._spell_repeat_depth,0)
    def test_lifesteal_is_not_aggregated_across_repetitions(self):
        g=self.game();g.players[0].health=10;ctx=self.context(g,-2);ctx['lifesteal']=True
        self.repeat(g,[('damage',2)],ctx)
        heals=[e for e in g.events if e.get('event')=='heal' and e.get('target')==-1]
        self.assertEqual(g.players[0].health,14);self.assertEqual(len(heals),2)
    def test_damage_listeners_run_between_copies(self):
        g=self.game();g.players[0].deck=['CORE_CS2_029','CORE_CS2_024']
        m=g._summon(0,'CORE_EX1_007');m.health=m.max_health=10
        self.repeat(g,[('damage',1)],self.context(g,m.uid))
        self.assertEqual(len(g.players[0].hand),2);self.assertEqual(m.health,8)
    def test_automatic_choices_do_not_leave_boundary_open(self):
        g=self.game();g.players[0].deck=['CORE_CS2_029','CORE_CS2_024'];ctx=self.context(g);ctx['automatic_choices']=True
        self.repeat(g,[('discover_deck',)],ctx)
        self.assertIsNone(g.pending_choice);self.assertEqual(len(g.players[0].hand),2);self.assertEqual(g._spell_repeat_depth,0)
    def test_deathrattle_runs_once_after_all_damage(self):
        g=self.game();g.players[0].deck=['CORE_CS2_029'];m=g._summon(0,'CORE_EX1_096')
        self.repeat(g,[('damage',1)],self.context(g,m.uid))
        self.assertEqual(len(g.players[0].hand),1);self.assertEqual(len(g.players[0].death_records),1)
        self.assertEqual(g._spell_repeat_depth,0)
