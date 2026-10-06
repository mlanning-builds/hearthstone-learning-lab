import unittest
from unittest.mock import patch
from copy import deepcopy
from expanded import Game, Action, random_deck
from expanded.cards import DEATH_EFFECTS, TRIGGERS


class DeathSummonSequenceTests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('PALADIN',31),random_deck('MAGE',53)],seed=71)
        g.step(Action('mulligan'));g.step(Action('mulligan'))
        for p in g.players:
            p.hand=[];p.board=[];p.deck=['CORE_CS2_029']*20;p.mana=p.max_mana=10
        return g
    def choose(self,g):
        g.step(next(a for a in g.legal_actions() if a.kind=='choose'))
    def test_fixed_summons_preserve_position(self):
        g=self.game();left=g._summon(0,'CS2_033');dead=g._summon(0,'CORE_WON_351');right=g._summon(0,'CS2_033')
        with patch.dict(DEATH_EFFECTS,{'CORE_WON_351':[('death_summon','CORE_EX1_506',3)]}):
            dead.health=0;g._settle()
        self.assertEqual([m.card_id for m in g.players[0].board],['CS2_033']+['CORE_EX1_506']*3+['CS2_033'])
        self.assertEqual(g.players[0].board[0].uid,left.uid);self.assertEqual(g.players[0].board[-1].uid,right.uid)
    def test_mixed_group_preserves_order(self):
        g=self.game();dead=g._summon(0,'CORE_WON_351');right=g._summon(0,'CS2_033')
        with patch.dict(DEATH_EFFECTS,{'CORE_WON_351':[('death_summon_group',('CORE_EX1_506','CS2_033','CORE_EX1_509'))]}):
            dead.health=0;g._settle()
        self.assertEqual([m.card_id for m in g.players[0].board],['CORE_EX1_506','CS2_033','CORE_EX1_509','CS2_033'])
        self.assertEqual(g.players[0].board[-1].uid,right.uid)
    def test_choice_and_retry_preserve_offset(self):
        g=self.game();listener=g._summon(0,'CORE_EX1_509');dead=g._summon(0,'CORE_WON_351');right=g._summon(0,'CS2_033');g._settle()
        with patch.dict(DEATH_EFFECTS,{'CORE_WON_351':[('death_summon','CORE_EX1_506',2),('armor',4)]}), patch.dict(TRIGGERS,{'CORE_EX1_509':(('summon','friendly','MURLOC'),[('choose_fixed_summon',('CS2_033',))])}):
            dead.health=0;g._settle()
            self.assertEqual(len(g.players[0].board),3);self.assertEqual(g.players[0].armor,0)
            before=deepcopy(g.__dict__)
            with patch.object(Game,'assert_invariants',side_effect=RuntimeError('injected')):
                with self.assertRaises(RuntimeError):self.choose(g)
            self.assertEqual(g.pending_choice,before['pending_choice'])
            self.assertEqual(g.rng.getstate(),before['rng'].getstate())
            self.choose(g)
            self.assertEqual([m.card_id for m in g.players[0].board[:4]],['CORE_EX1_509','CORE_EX1_506','CORE_EX1_506','CS2_033'])
            self.assertEqual(g.players[0].armor,0)
            self.choose(g)
        self.assertEqual(g.players[0].armor,4);self.assertEqual(len(g.players[0].board),6)
        self.assertIsNone(g._death_frame)
    def test_mixed_group_waits_for_choice(self):
        g=self.game();g._summon(0,'CORE_EX1_509');dead=g._summon(0,'CORE_WON_351');g._settle()
        with patch.dict(DEATH_EFFECTS,{'CORE_WON_351':[('death_summon_group',('CORE_EX1_506','CS2_033'))]}), patch.dict(TRIGGERS,{'CORE_EX1_509':(('summon','friendly','MURLOC'),[('choose_fixed_summon',('CS2_033',))])}):
            dead.health=0;g._settle();self.assertEqual(len(g.players[0].board),2)
            self.choose(g)
        self.assertEqual([m.card_id for m in g.players[0].board],['CORE_EX1_509','CORE_EX1_506','CS2_033','CS2_033'])
        self.assertIsNone(g._death_frame)
    def test_lethal_reaction_cancels_remaining_death_summons(self):
        g=self.game();g._summon(0,'CORE_EX1_509');dead=g._summon(0,'CORE_WON_351');g._settle();g.players[1].health=3
        with patch.dict(DEATH_EFFECTS,{'CORE_WON_351':[('death_summon','CORE_EX1_506',3)]}), patch.dict(TRIGGERS,{'CORE_EX1_509':(('summon','friendly','MURLOC'),[('damage_random_enemy',3)])}):
            dead.health=0;g._settle()
        self.assertTrue(g.terminal);self.assertEqual(len(g.players[0].board),2);self.assertIsNone(g._death_frame)
    def test_full_board_group_finishes(self):
        g=self.game();dead=g._summon(0,'CORE_WON_351')
        for _ in range(6):g._summon(0,'CS2_033')
        with patch.dict(DEATH_EFFECTS,{'CORE_WON_351':[('death_summon_group',('CORE_EX1_506','CS2_033')),('armor',2)]}):
            dead.health=0;g._settle()
        self.assertEqual(len(g.players[0].board),7);self.assertEqual(g.players[0].board[0].card_id,'CORE_EX1_506')
        self.assertEqual(g.players[0].armor,2);self.assertIsNone(g._death_frame)
    def test_empty_group_continues(self):
        g=self.game();dead=g._summon(0,'CORE_WON_351')
        with patch.dict(DEATH_EFFECTS,{'CORE_WON_351':[('death_summon_group',()),('armor',2)]}):
            dead.health=0;g._settle()
        self.assertEqual(g.players[0].board,[]);self.assertEqual(g.players[0].armor,2)
