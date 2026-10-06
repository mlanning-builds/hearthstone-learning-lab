import unittest
from unittest.mock import patch
from expanded import Game, Action, random_deck
from expanded.cards import TRIGGERS


class FixedSummonSequenceTests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('PALADIN',31),random_deck('MAGE',53)],seed=71)
        g.step(Action('mulligan'));g.step(Action('mulligan'))
        for p in g.players:
            p.hand=[];p.board=[];p.deck=['CORE_CS2_029']*20;p.mana=p.max_mana=10
        return g
    def context(self):
        return dict(owner=0,source=None,target=0,bonus=0,lifesteal=False)
    def test_reaction_finishes_before_next_entry(self):
        g=self.game();m=g._summon(0,'CORE_EX1_509');g._settle()
        observed=[];original=Game._summon
        def summon(game,*args,**kwargs):
            observed.append(m.attack);return original(game,*args,**kwargs)
        with patch.object(Game,'_summon',summon):
            g._start_play_effects([('summon','CORE_EX1_509',3)],self.context())
        self.assertEqual(observed,[1,2,3])
        self.assertIsNone(g.pending_frame)
    def test_choice_preserves_remaining_summon_and_following_effect(self):
        g=self.game();g._summon(0,'CORE_EX1_509');g._settle()
        rule=(('summon','friendly','MURLOC'),[('choose_fixed_summon',('CORE_WON_351',))])
        # Use a different Murloc as subject, so it does not become another listener.
        with patch.dict(TRIGGERS,{'CORE_EX1_509':rule}):
            g._start_play_effects([('summon','CORE_EX1_506',2),('armor',4)],self.context())
            self.assertEqual(len(g.players[0].board),2)
            self.assertEqual(g.players[0].armor,0)
            g.step(next(a for a in g.legal_actions() if a.kind=='choose'))
            self.assertEqual(len(g.players[0].board),4)
            self.assertEqual(g.players[0].armor,0)
            g.step(next(a for a in g.legal_actions() if a.kind=='choose'))
        self.assertEqual(len(g.players[0].board),5)
        self.assertEqual(g.players[0].armor,4);self.assertIsNone(g.pending_frame)
    def test_lethal_stops_remainder(self):
        g=self.game();g._summon(0,'CORE_EX1_509');g._settle();g.players[1].health=3
        with patch.dict(TRIGGERS,{'CORE_EX1_509':(('summon','friendly','MURLOC'),[('damage_random_enemy',3)])}):
            g._start_play_effects([('summon','CORE_EX1_506',3)],self.context())
        self.assertTrue(g.terminal);self.assertEqual(len(g.players[0].board),2)
        self.assertIsNone(g.pending_frame)
    def test_full_board_finishes_without_extra_entities(self):
        g=self.game()
        g._start_play_effects([('summon','CORE_WON_351',10),('armor',2)],self.context())
        self.assertEqual(len(g.players[0].board),7);self.assertEqual(g.players[0].armor,2)
    def test_inactive_combo_does_not_expand_or_summon(self):
        g=self.game();g._start_play_effects([('combo_summon','CORE_WON_351',3)],self.context())
        self.assertEqual(g.players[0].board,[])
    def test_active_combo_summons_count(self):
        g=self.game();ctx=self.context();ctx['combo']=True
        g._start_play_effects([('combo_summon','CORE_WON_351',3)],ctx)
        self.assertEqual(len(g.players[0].board),3)
    def test_zero_count_continues(self):
        g=self.game();g._start_play_effects([('summon','CORE_WON_351',0),('armor',2)],self.context())
        self.assertEqual(g.players[0].board,[]);self.assertEqual(g.players[0].armor,2)
    def test_compound_operations_keep_boundary(self):
        g=self.game()
        for op in [('raise_corpses','CORE_WON_351',3),('tomb_guardians',)]:
            self.assertEqual(g._split_fixed_summon(op,self.context()),(op,()))

    def test_event_sequence_waits_for_child_choice(self):
        g=self.game();m=g._summon(0,'CORE_WON_351');g._summon(0,'CORE_EX1_509');g._settle()
        rules={'CORE_WON_351':('spell_cast',[('summon','CORE_EX1_506',2)]),
               'CORE_EX1_509':(('summon','friendly','MURLOC'),[('choose_fixed_summon',('CS2_033',))])}
        with patch.dict(TRIGGERS,rules):
            g._queue_event('spell_cast',owner=0,card_id='CORE_CS2_029',source=0)
            g._settle(allow_event_choices=True)
            self.assertEqual(len(g.players[0].board),3)
            g.step(next(a for a in g.legal_actions() if a.kind=='choose'))
            self.assertEqual(len(g.players[0].board),5)
            g.step(next(a for a in g.legal_actions() if a.kind=='choose'))
        self.assertEqual(len(g.players[0].board),6);self.assertFalse(g._event_frames)
    def test_death_sequence_waits_for_choice(self):
        from expanded.cards import DEATH_EFFECTS
        g=self.game();m=g._summon(0,'CORE_WON_351');g._summon(0,'CORE_EX1_509');g._settle()
        with patch.dict(DEATH_EFFECTS,{'CORE_WON_351':[('summon','CORE_EX1_506',2)]}), patch.dict(TRIGGERS,{'CORE_EX1_509':(('summon','friendly','MURLOC'),[('choose_fixed_summon',('CS2_033',))])}):
            m.health=0;g._settle(allow_event_choices=True)
            self.assertEqual(len(g.players[0].board),2)
            g.step(next(a for a in g.legal_actions() if a.kind=='choose'))
            self.assertEqual(len(g.players[0].board),4)
            g.step(next(a for a in g.legal_actions() if a.kind=='choose'))
        self.assertEqual(len(g.players[0].board),5);self.assertIsNone(g._death_frame)
    def test_turn_sequence_waits_for_choice(self):
        from expanded.cards import END_EFFECTS
        g=self.game();g._summon(0,'CORE_WON_351');g._summon(0,'CORE_EX1_509');g._settle()
        with patch.dict(END_EFFECTS,{'CORE_WON_351':[('summon','CORE_EX1_506',2)]}), patch.dict(TRIGGERS,{'CORE_EX1_509':(('summon','friendly','MURLOC'),[('choose_fixed_summon',('CS2_033',))])}):
            g._end_turn();self.assertEqual(len(g.players[0].board),3)
            g.step(next(a for a in g.legal_actions() if a.kind=='choose'))
            self.assertEqual(len(g.players[0].board),5)
            g.step(next(a for a in g.legal_actions() if a.kind=='choose'))
        self.assertEqual(len(g.players[0].board),6);self.assertIsNone(g._turn_frame)
        self.assertEqual(g.current,1)
