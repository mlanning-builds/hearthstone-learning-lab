import unittest
from copy import deepcopy
from unittest.mock import patch
from expanded import Game,Action,random_deck
from expanded.game import Card
from expanded.cards import TRIGGERS


class PostplayPhaseTests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('PALADIN',31),random_deck('MAGE',53)],seed=71)
        g.step(Action('mulligan'));g.step(Action('mulligan'))
        for p in g.players:
            p.hand=[];p.board=[];p.deck=['CORE_CS2_029']*20;p.mana=p.max_mana=10;p.corpses=0
        return g
    def listener(self,g):
        m=g._summon(0,'CORE_EX1_509');g._settle();return m
    def play(self,g,cid='CORE_EX1_509'):
        c=Card(g._new_id(),cid);g.players[0].hand.append(c)
        g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid))
    def stages(self,g):
        return [r['stage'] for r in g.entry_trace()['records'] if r['phase']=='minion_postplay_stage']
    def test_stage_order_and_cleanup(self):
        g=self.game();self.listener(g);g.configure_entry_trace();self.play(g)
        self.assertEqual(self.stages(g),['summon','played','after_card_secrets'])
        self.assertIsNone(g._minion_after_play_frame)
    def test_secret_observes_completed_summon_reaction(self):
        g=self.game();m=self.listener(g);observed=[];original=Game._secret_event
        def secret(game,event,actor,**data):
            if event=='after_card':observed.append(m.attack)
            return original(game,event,actor,**data)
        with patch.object(Game,'_secret_event',secret):self.play(g)
        self.assertEqual(observed,[2])
    def test_choice_blocks_later_stages_and_resumes_once(self):
        g=self.game();self.listener(g);g.configure_entry_trace()
        with patch.dict(TRIGGERS,{'CORE_EX1_509':(('summon','friendly','MURLOC'),[('choose_fixed_summon',('CORE_WON_351',))])}):
            self.play(g)
            self.assertEqual(self.stages(g),['summon']);self.assertIsNotNone(g.pending_choice)
            g.step(next(a for a in g.legal_actions() if a.kind=='choose'))
        self.assertEqual(self.stages(g),['summon','played','after_card_secrets'])
        self.assertIsNone(g._minion_after_play_frame);self.assertEqual(len(g.players[0].minions),3)
    def test_multiple_listener_choices_complete_before_secret_stage(self):
        g=self.game();self.listener(g);self.listener(g);g.configure_entry_trace()
        with patch.dict(TRIGGERS,{'CORE_EX1_509':(('summon','friendly','MURLOC'),[('choose_fixed_summon',('CORE_WON_351',))])}):
            self.play(g)
            for _ in range(2):
                self.assertEqual(self.stages(g),['summon'])
                g.step(next(a for a in g.legal_actions() if a.kind=='choose'))
        self.assertEqual(self.stages(g),['summon','played','after_card_secrets'])
        self.assertIsNone(g.pending_choice)
    def test_lethal_summon_reaction_prevents_later_secret(self):
        g=self.game();self.listener(g);g.players[1].health=3;g.players[0].cards_played=2
        secret=Card(g._new_id(),'CORE_GIL_577');g.players[1].secrets.append(secret)
        with patch.dict(TRIGGERS,{'CORE_EX1_509':(('summon','friendly','MURLOC'),[('damage_random_enemy',3)])}):self.play(g)
        self.assertTrue(g.terminal);self.assertIn(secret,g.players[1].secrets)
        self.assertEqual(g.players[1].board,[]);self.assertIsNone(g._minion_after_play_frame)
    def test_rat_trap_fires_once_after_completed_reactions(self):
        g=self.game();m=self.listener(g);g.players[0].cards_played=2
        g.players[1].secrets.append(Card(g._new_id(),'CORE_GIL_577'));self.play(g)
        self.assertEqual(m.attack,2);self.assertEqual([x.card_id for x in g.players[1].minions],['GIL_577t'])
        self.assertEqual(g.players[1].secrets,[])
    def test_rat_trap_waits_for_choice(self):
        g=self.game();self.listener(g);g.players[0].cards_played=2
        g.players[1].secrets.append(Card(g._new_id(),'CORE_GIL_577'))
        with patch.dict(TRIGGERS,{'CORE_EX1_509':(('summon','friendly','MURLOC'),[('choose_fixed_summon',('CORE_WON_351',))])}):
            self.play(g);self.assertEqual(len(g.players[1].secrets),1)
            self.assertEqual(g.players[1].board,[])
            g.step(next(a for a in g.legal_actions() if a.kind=='choose'))
        self.assertEqual([x.card_id for x in g.players[1].minions],['GIL_577t'])
    def test_failed_choice_restores_frame_and_can_retry(self):
        g=self.game();self.listener(g)
        with patch.dict(TRIGGERS,{'CORE_EX1_509':(('summon','friendly','MURLOC'),[('choose_fixed_summon',('CORE_WON_351',))])}):
            self.play(g);action=next(a for a in g.legal_actions() if a.kind=='choose')
            before=deepcopy(g.__dict__)
            with patch.object(Game,'assert_invariants',side_effect=RuntimeError('injected')):
                with self.assertRaises(RuntimeError):g.step(action)
            self.assertEqual(g._minion_after_play_frame['stage'],before['_minion_after_play_frame']['stage'])
            self.assertEqual(g.pending_choice,before['pending_choice'])
            self.assertEqual(g.rng.getstate(),before['rng'].getstate())
            g.step(action);self.assertIsNone(g._minion_after_play_frame)
    def test_plain_play_does_not_duplicate_history(self):
        g=self.game();self.play(g,'CORE_WON_351')
        self.assertEqual(g.players[0].cards_played,1);self.assertEqual(len(g.players[0].played_history),1)
        self.assertEqual(len(g.players[0].minions),1)
    def test_spell_counter_path_does_not_start_minion_stages(self):
        g=self.game();g.configure_entry_trace();g.players[1].secrets.append(Card(g._new_id(),'CORE_EX1_287'))
        c=Card(g._new_id(),'CORE_CS2_029');g.players[0].hand.append(c)
        g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid))
        self.assertEqual(self.stages(g),[]);self.assertIsNone(g._minion_after_play_frame)
    def test_phase_frame_is_private(self):
        g=self.game();self.listener(g)
        with patch.dict(TRIGGERS,{'CORE_EX1_509':(('summon','friendly','MURLOC'),[('choose_fixed_summon',('CORE_WON_351',))])}):
            self.play(g)
            for viewer in (0,1):self.assertNotIn('_minion_after_play_frame',str(g.observe(viewer)))
