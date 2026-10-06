import json
import unittest
from copy import deepcopy
from unittest.mock import patch
from expanded import Game, Action, random_deck
from expanded.game import Card


class EntryTraceTests(unittest.TestCase):
    def game(self, trace=True):
        g=Game([random_deck('PALADIN',31),random_deck('MAGE',53)],seed=71)
        g.step(Action('mulligan'));g.step(Action('mulligan'))
        for p in g.players:
            p.hand=[];p.board=[];p.deck=['CORE_CS2_029']*20;p.mana=p.max_mana=10
        if trace:g.configure_entry_trace()
        return g

    def play(self,g,cid):
        c=Card(g._new_id(),cid);g.players[0].hand.append(c)
        action=next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid)
        g.step(action)

    def rows(self,g,phase):
        return [r for r in g.entry_trace()['records'] if r['phase']==phase]

    def test_disabled_by_default(self):
        g=self.game(False);g._summon(0,'CORE_WON_351')
        self.assertEqual(g.entry_trace()['records'],[])
        self.assertEqual(g.entry_trace()['recorded'],0)

    def test_bounded_storage_and_snapshot_isolation(self):
        g=self.game();g.configure_entry_trace(2)
        for _ in range(3):g._summon(0,'CORE_WON_351')
        trace=g.entry_trace();self.assertEqual(len(trace['records']),2)
        self.assertEqual(trace['recorded'],6);self.assertEqual(trace['dropped'],4)
        trace['records'][0]['phase']='corrupted'
        self.assertNotEqual(g.entry_trace()['records'][0]['phase'],'corrupted')
        json.dumps(g.entry_trace())

    def test_invalid_configuration_does_not_clear_trace(self):
        g=self.game();g._summon(0,'CORE_WON_351');before=g.entry_trace()
        for bad in (True,-1,100001,1.5,'2'):
            with self.assertRaises(ValueError):g.configure_entry_trace(bad)
            self.assertEqual(g.entry_trace(),before)

    def test_play_has_origin_and_after_play_boundary(self):
        g=self.game();self.play(g,'CORE_WON_351')
        attempts=self.rows(g,'entry_attempt');self.assertEqual(len(attempts),1)
        self.assertEqual(attempts[0]['origin'],'play');self.assertEqual(attempts[0]['zone'],'hand')
        self.assertEqual(attempts[0]['source_card_id'],'CORE_WON_351')
        self.assertLess(self.rows(g,'entry_result')[0]['sequence'],self.rows(g,'after_play')[0]['sequence'])

    def test_recruitment_records_post_grant_state_without_battlecry(self):
        g=self.game();g.players[0].deck=['CORE_EX1_319'];self.play(g,'JAIL_516')
        attempts=self.rows(g,'entry_attempt')
        self.assertEqual([r['origin'] for r in attempts],['play','recruit'])
        recruited=self.rows(g,'recruit_initialized')[0]['entity']
        self.assertIn('RUSH',recruited['stored_keywords']);self.assertEqual(g.players[0].health,30)
        self.assertEqual([r['card_id'] for r in self.rows(g,'after_play')],['JAIL_516'])

    def test_reborn_has_separate_initialized_state(self):
        g=self.game();m=g._summon(0,'CORE_WON_351');m.keywords.add('REBORN');m.health=0
        g.configure_entry_trace();g._settle()
        self.assertEqual(self.rows(g,'entry_attempt')[0]['origin'],'reborn')
        r=self.rows(g,'reborn_initialized')[0]['entity']
        self.assertEqual(r['health'],1);self.assertNotIn('REBORN',r['stored_keywords'])

    def test_transform_is_not_a_summon(self):
        g=self.game();m=g._summon(0,'CORE_WON_351');g.configure_entry_trace()
        g._transform(m,'CS3_025')
        self.assertEqual(self.rows(g,'entry_attempt'),[])
        self.assertEqual(len(self.rows(g,'replacement_result')),1)

    def test_full_board_records_failure_without_new_entity(self):
        g=self.game()
        for _ in range(7):g._summon(0,'CORE_WON_351')
        g.configure_entry_trace();uid=g.uid
        self.assertIsNone(g._summon(0,'CORE_WON_351'))
        self.assertEqual(g.uid,uid);self.assertFalse(self.rows(g,'entry_result')[0]['success'])
        self.assertIsNone(self.rows(g,'entry_result')[0]['entity'])

    def test_hero_power_origin(self):
        g=self.game();action=next(a for a in g.legal_actions() if a.kind=='power');g.step(action)
        self.assertEqual(self.rows(g,'entry_attempt')[0]['origin'],'hero_power')

    def test_choice_origin_and_no_duplicate_summon(self):
        g=self.game();g.pending_choice=dict(owner=0,kind='fixed_summon',options=[dict(card_id='CORE_WON_351')]);g.phase='choice'
        action=next(a for a in g.legal_actions() if a.kind=='choose');g.step(action)
        self.assertEqual(len(self.rows(g,'entry_result')),1)
        self.assertEqual(self.rows(g,'entry_attempt')[0]['origin'],'choice')
        self.assertEqual(len(self.rows(g,'choice_selected')),1)

    def test_failed_action_rolls_back_trace_and_rng(self):
        g=self.game();c=Card(g._new_id(),'CORE_WON_351');g.players[0].hand.append(c)
        action=next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid)
        before=g.entry_trace();rng=g.rng.getstate();uid=g.uid
        with patch.object(Game,'assert_invariants',side_effect=RuntimeError('injected failure')):
            with self.assertRaises(RuntimeError):g.step(action)
        self.assertEqual(g.entry_trace(),before);self.assertEqual(g.rng.getstate(),rng)
        self.assertEqual(g.uid,uid);self.assertEqual(g.players[0].board,[])

    def test_trace_does_not_change_game_rng_or_observations(self):
        a=self.game(False);b=self.game(True)
        for g in (a,b):
            g.players[0].deck=['CORE_EX1_319','CORE_WON_351'];self.play(g,'JAIL_516')
        self.assertEqual(a.rng.getstate(),b.rng.getstate());self.assertEqual(a.uid,b.uid)
        self.assertEqual(a.events,b.events);self.assertEqual(a.history,b.history)
        for viewer in (0,1):self.assertEqual(a.observe(viewer),b.observe(viewer))
        self.assertEqual(a.legal_actions(),b.legal_actions())

    def test_damage_batches_are_distinct_and_preserve_current_checkpoints(self):
        g=self.game();m=g._summon(1,'CORE_WON_351');m.keywords.add('REBORN');g.configure_entry_trace()
        self.play(g,'JAIL_307')
        starts=self.rows(g,'damage_batch_begin');ends=self.rows(g,'damage_batch_end')
        self.assertEqual(len(starts),2);self.assertEqual(len(ends),2)
        reborn=self.rows(g,'reborn_initialized')[0]
        self.assertLess(ends[0]['sequence'],reborn['sequence']);self.assertLess(reborn['sequence'],starts[1]['sequence'])
