import unittest
from copy import deepcopy
from unittest.mock import patch
from expanded import Game,Action,random_deck
from expanded.game import Card
from expanded.cards import TRIGGERS,RULES


class SummonListenerTests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('PALADIN',31),random_deck('MAGE',53)],seed=71)
        g.step(Action('mulligan'));g.step(Action('mulligan'))
        for p in g.players:
            p.hand=[];p.board=[];p.deck=['CORE_CS2_029']*20;p.mana=p.max_mana=10;p.corpses=0
        return g
    def summon(self,g,owner,cid):
        m=g._summon(owner,cid);g._settle();return m
    def play(self,g,cid):
        c=Card(g._new_id(),cid);g.players[g.current].hand.append(c)
        a=next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid)
        g.step(a);return c
    def test_tidecaller_does_not_trigger_for_itself(self):
        g=self.game();m=self.summon(g,0,'CORE_EX1_509');self.assertEqual(m.attack,1)
    def test_tidecaller_owner_and_tribe_filter(self):
        g=self.game();m=self.summon(g,0,'CORE_EX1_509')
        self.summon(g,1,'CORE_EX1_506');self.summon(g,0,'CORE_WON_351');self.assertEqual(m.attack,1)
        self.summon(g,0,'CORE_EX1_506');self.assertEqual(m.attack,2)
    def test_played_murloc_and_battlecry_token_each_notify(self):
        g=self.game();m=self.summon(g,0,'CORE_EX1_509');self.play(g,'CORE_EX1_506')
        self.assertEqual(m.attack,3)
    def test_full_board_is_not_a_summon(self):
        g=self.game();m=self.summon(g,0,'CORE_EX1_509')
        for _ in range(6):self.summon(g,0,'CORE_WON_351')
        self.assertIsNone(g._summon(0,'CORE_EX1_506'));g._settle();self.assertEqual(m.attack,1)
    def test_transform_does_not_emit_summon(self):
        g=self.game();m=self.summon(g,0,'CORE_EX1_509');target=self.summon(g,0,'CORE_WON_351')
        g._transform(target,'CORE_EX1_506');g._settle();self.assertEqual(m.attack,1)
    def test_silenced_listener_does_not_react(self):
        g=self.game();m=self.summon(g,0,'CORE_EX1_509');g._silence(m)
        self.summon(g,0,'CORE_EX1_506');self.assertEqual(m.attack,1)
    def test_listener_removed_before_checkpoint_is_skipped(self):
        g=self.game();m=self.summon(g,0,'CORE_EX1_509');g._summon(0,'CORE_EX1_506')
        g.players[0].board.remove(m);g._settle();self.assertEqual(m.attack,1)
    def test_new_listener_does_not_receive_prior_summons(self):
        g=self.game();a=self.summon(g,0,'CORE_EX1_509');g._summon(0,'CORE_EX1_506')
        b=g._summon(0,'CORE_EX1_509');g._settle()
        self.assertEqual((a.attack,b.attack),(3,1))
    def test_pageturner_uses_elemental_summons_and_not_own_entry(self):
        g=self.game();self.summon(g,0,'TLC_220');self.assertEqual(g.players[1].health,30)
        self.summon(g,0,'CS2_033');self.assertEqual(g.players[1].health,27)
        self.summon(g,1,'CS2_033');self.assertEqual(g.players[0].health,30)
    def test_pageturner_damage_does_not_use_spell_damage(self):
        g=self.game();self.summon(g,0,'TLC_220');g.players[0].spell_damage_turn=9
        self.summon(g,0,'CS2_033');self.assertEqual(g.players[1].health,27)
    def test_corpse_flower_pays_for_enemy_summon(self):
        g=self.game();self.summon(g,1,'EDR_815');g.players[1].corpses=2
        m=self.summon(g,0,'CS3_025');self.assertEqual(m.health,3);self.assertEqual(g.players[1].corpses,0)
    def test_corpse_flower_insufficient_corpses(self):
        g=self.game();self.summon(g,1,'EDR_815');g.players[1].corpses=1
        m=self.summon(g,0,'CS3_025');self.assertEqual(m.health,6);self.assertEqual(g.players[1].corpses,1)
    def test_corpse_flower_ignores_friendly_summon(self):
        g=self.game();self.summon(g,0,'EDR_815');g.players[0].corpses=4
        m=self.summon(g,0,'CS3_025');self.assertEqual(m.health,6);self.assertEqual(g.players[0].corpses,4)
    def test_corpse_flower_pays_even_when_shield_prevents_damage(self):
        g=self.game();self.summon(g,1,'EDR_815');g.players[1].corpses=2
        m=g._summon(0,'CS3_025');m.keywords.add('DIVINE_SHIELD');g._settle()
        self.assertEqual(m.health,6);self.assertNotIn('DIVINE_SHIELD',m.keywords);self.assertEqual(g.players[1].corpses,0)
    def test_dead_subject_does_not_consume_corpses(self):
        g=self.game();self.summon(g,1,'EDR_815');g.players[1].corpses=2
        m=g._summon(0,'CS3_025');m.health=0;g._settle();self.assertEqual(g.players[1].corpses,2)
    def test_reborn_notification_sees_initialized_one_health(self):
        g=self.game();m=self.summon(g,0,'CORE_WON_351');m.keywords.add('REBORN')
        self.summon(g,1,'EDR_815');g.players[1].corpses=2;m.health=0;g._settle()
        self.assertEqual(g.players[0].minions,[]);self.assertEqual(g.players[1].corpses,0)
        self.assertEqual(g._pending_summon_events,{})
    def test_play_battlecry_finishes_before_enemy_summon_damage(self):
        g=self.game();self.summon(g,1,'EDR_815');g.players[1].corpses=2
        self.play(g,'CORE_EX1_319')
        self.assertEqual(g.players[0].health,27);self.assertEqual(g.players[0].minions,[])
    def test_copy_is_an_independent_summon(self):
        g=self.game();m=self.summon(g,0,'CORE_EX1_509');original=self.summon(g,0,'CORE_EX1_506')
        g._summon(0,original.card_id,copy_from=original,entry_origin='copy');g._settle();self.assertEqual(m.attack,3)
    def test_recruitment_uses_shared_summon_notification(self):
        g=self.game();m=self.summon(g,0,'CORE_EX1_509');g.players[0].deck=['CORE_EX1_506']
        self.play(g,'JAIL_516');self.assertEqual(m.attack,2)
        self.assertEqual(len(g.players[0].minions),3)
    def test_failed_action_rolls_back_queued_and_pending_notifications(self):
        g=self.game();self.summon(g,1,'EDR_815');g.players[1].corpses=2
        c=Card(g._new_id(),'CORE_WON_351');g.players[0].hand.append(c)
        a=next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid)
        before=deepcopy(g.__dict__)
        with patch.object(Game,'assert_invariants',side_effect=RuntimeError('injected')):
            with self.assertRaises(RuntimeError):g.step(a)
        self.assertEqual(g.players[1].corpses,2);self.assertEqual(g._pending_summon_events,{})
        self.assertEqual(list(g._rule_events),list(before['_rule_events']))
        self.assertEqual(g.rng.getstate(),before['rng'].getstate());self.assertEqual(g.players[0].board,[])
    def test_choice_defers_play_notification_until_resume(self):
        g=self.game();self.summon(g,1,'EDR_815');g.players[1].corpses=2
        # Synthetic effect sequence isolates continuation behavior, not a card rule.
        with patch.dict(RULES,{'CORE_WON_351':('none',[('choose_fixed_summon',('CS2_033',))])}):
            self.play(g,'CORE_WON_351');self.assertIsNotNone(g.pending_choice)
            self.assertEqual(len(g._pending_summon_events),1);self.assertEqual(g.players[1].corpses,2)
            g.step(next(a for a in g.legal_actions() if a.kind=='choose'))
            self.assertEqual(g._pending_summon_events,{})
    def test_all_tribe_marker_matches_without_text_parsing(self):
        g=self.game();m=self.summon(g,0,'CORE_EX1_509')
        raw=dict(g.cards['CORE_WON_351']);raw['races']=['ALL']
        with patch.dict(g.cards,{'CORE_WON_351':raw}):self.summon(g,0,'CORE_WON_351')
        self.assertEqual(m.attack,2)
