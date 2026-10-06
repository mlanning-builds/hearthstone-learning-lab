"""Automatic spell casting through shared forced-combat and copy frames."""
import unittest
from unittest.mock import patch
from expanded import Game,Action,random_deck

class CastForcedGroupsTests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('MAGE',31),random_deck('ROGUE',53)],seed=71)
        g.step(Action('mulligan'));g.step(Action('mulligan'))
        for p in g.players:
            p.hand=[];p.board=[];p.deck=['CORE_CS2_029']*20;p.health=30;p.mana=p.max_mana=10
        return g
    def cast(self,g,cid,policy='random'):
        g._start_play_effects([('cast_fixed_spell',cid,policy)],dict(owner=0,source=None,target=0,bonus=0,lifesteal=False))
    def test_hounds_attack_without_deck_minions(self):
        g=self.game();self.cast(g,'TIME_443');self.assertEqual(g.players[1].health,24)
        self.assertEqual(len(g.players[0].minions),2)
        self.assertTrue(all(m.attacks==0 for m in g.players[0].minions))
    def test_hounds_do_not_attack_with_deck_minion(self):
        g=self.game();g.players[0].deck.append('AT_037t');self.cast(g,'TIME_443')
        self.assertEqual(g.players[1].health,30);self.assertEqual(len(g.players[0].minions),2)
    def test_surgery_keeps_summons_when_target_dies(self):
        g=self.game();m=g._summon(1,'EDR_851t');self.cast(g,'JAIL_454')
        self.assertNotIn(m,g.players[1].board);self.assertEqual(len(g.players[0].minions),3)
    def test_trees_can_force_attacks_into_own_minion(self):
        g=self.game();m=g._summon(0,'CS3_020');self.cast(g,'TLC_230')
        self.assertNotIn(m,g.players[0].board)
    def test_behemoth_enemy_target_preserves_controller(self):
        g=self.game();a=g._summon(0,'EDR_851t');b=g._summon(1,'EDR_851t');self.cast(g,'DINO_428','enemies')
        self.assertNotIn(a,g.players[0].board);self.assertIn(b,g.players[1].board)
        self.assertEqual(b.attack,8);self.assertIn('LIFESTEAL',b.keywords)
    def test_copy_group_pauses_between_copies(self):
        g=self.game();m=g._summon(0,'CS3_020');m.keywords.add('TAUNT')
        dispatch=g._dispatch_effect;seen=[]
        def effect(op,ctx):
            dispatch(op,ctx)
            if op[0]=='summon_target_copy':
                seen.append(op)
                if len(seen)==1:g._effect(('choose_fixed_summon',('AT_037t',)),dict(owner=0,source=None))
        with patch.object(g,'_dispatch_effect',side_effect=effect):
            self.cast(g,'DINO_402');self.assertEqual(len(g.players[0].minions),2)
            self.assertIsNotNone(g.pending_choice);g.step(g.legal_actions()[0])
        self.assertEqual(len(g.players[0].minions),7);self.assertEqual(len(seen),6)
        copies=[c for c in g.players[0].minions if c.card_id==m.card_id]
        self.assertEqual(len(copies),6)
        self.assertTrue(all((c.attack,c.health)==(1,1) and 'TAUNT' in c.keywords for c in copies))
        self.assertIsNone(g.pending_frame)
    def test_copy_target_absent_fizzles(self):
        g=self.game();self.cast(g,'DINO_402');self.assertFalse(g.players[0].minions);self.assertIsNone(g.pending_frame)
