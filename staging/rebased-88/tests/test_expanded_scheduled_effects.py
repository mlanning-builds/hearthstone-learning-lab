import unittest
from expanded import Game, Action, random_deck
from expanded.game import Card

class ScheduledEffectTests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('PALADIN',31),random_deck('MAGE',53)],seed=71)
        g.step(Action('mulligan'));g.step(Action('mulligan'))
        for p in g.players:
            p.hand=[];p.board=[];p.deck=['CORE_CS2_029']*20;p.mana=p.max_mana=10
        return g
    def play(self,g,cid):
        c=Card(g._new_id(),cid);g.players[0].hand.append(c)
        g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid))
    def end(self,g):g.step(Action('end'))
    def test_sigil_next_owner_turn_once(self):
        g=self.game();self.play(g,'CATA_528');self.assertEqual(g.players[0].board,[])
        self.end(g);self.assertEqual(g.players[0].board,[]);self.end(g)
        self.assertEqual([m.card_id for m in g.players[0].board],['CATA_528t'])
        self.assertFalse(g.players[0].scheduled_effects)
    def test_hatching_waits_for_next_end(self):
        g=self.game();m=g._summon(0,'CS2_033');self.play(g,'DINO_405')
        self.end(g);self.assertEqual(m.attack,3);self.end(g);self.assertEqual(m.attack,3)
        self.end(g);self.assertEqual(m.attack,5);self.assertFalse(g.players[0].scheduled_effects)
    def test_aura_three_owner_ends(self):
        g=self.game();self.play(g,'TIME_700')
        for count in range(1,4):
            self.end(g);self.assertEqual(len(g.players[0].board),count)
            self.end(g)
        self.assertFalse(g.players[0].scheduled_effects)
        self.end(g);self.assertEqual(len(g.players[0].board),3)
    def test_full_board_still_expires(self):
        g=self.game()
        for _ in range(7):g._summon(0,'CS2_033')
        self.play(g,'CATA_528');self.end(g);self.end(g)
        self.assertEqual(len(g.players[0].board),7);self.assertFalse(g.players[0].scheduled_effects)
    def test_due_choice_resumes_remaining_operations(self):
        g=self.game();g._schedule_turn_effect(0,'end',0,1,(('choose_fixed_summon',('CS2_033',)),('armor',3)))
        self.end(g);self.assertIsNotNone(g.pending_choice);self.assertEqual(g.players[0].armor,0)
        g.step(next(a for a in g.legal_actions() if a.kind=='choose'))
        self.assertEqual(g.players[0].armor,3);self.assertEqual(g.current,1)
        self.assertFalse(g.players[0].scheduled_effects)

    def test_acceleration_temporary_mana_three_starts(self):
        g=self.game();self.play(g,'END_011');g.players[0].max_mana=2
        for expected in (3,4,5):
            self.end(g);self.end(g)
            self.assertEqual(g.players[0].max_mana,expected)
            self.assertEqual(g.players[0].mana,expected+1)
        self.assertFalse(g.players[0].scheduled_effects)
        self.end(g);self.end(g)
        self.assertEqual(g.players[0].mana,g.players[0].max_mana)
    def test_reinforcement_recruits_without_battlecry(self):
        g=self.game();g.players[0].deck=['CORE_EX1_506']+['CORE_CS2_029']*10
        self.play(g,'JAIL_327');self.end(g)
        self.assertEqual([m.card_id for m in g.players[0].board],['CORE_EX1_506'])
        self.assertNotIn('CORE_EX1_506',g.players[0].deck)
        self.assertEqual(g.players[0].scheduled_effects[0]['remaining'],2)
    def test_reinforcement_full_board_keeps_deck_card(self):
        g=self.game();g.players[0].deck=['CORE_EX1_506']+['CORE_CS2_029']*10
        for _ in range(7):g._summon(0,'CS2_033')
        self.play(g,'JAIL_327');self.end(g)
        self.assertIn('CORE_EX1_506',g.players[0].deck)
        self.assertEqual(g.players[0].scheduled_effects[0]['remaining'],2)
    def test_scheduled_tokens_can_be_played_from_hand(self):
        for cid in ('CATA_528t','TIME_700t'):
            g=self.game();self.play(g,cid)
            self.assertEqual(g.players[0].board[0].card_id,cid)
            self.assertIn('TAUNT',g.players[0].board[0].keywords)

    def test_failed_end_restores_due_effect_and_can_retry(self):
        from copy import deepcopy
        from unittest.mock import patch
        g=self.game();self.play(g,'TIME_700');before=deepcopy(g.__dict__)
        with patch.object(Game,'assert_invariants',side_effect=RuntimeError('injected')):
            with self.assertRaises(RuntimeError):self.end(g)
        self.assertEqual(g.players[0].scheduled_effects,before['players'][0].scheduled_effects)
        self.assertEqual(g.rng.getstate(),before['rng'].getstate())
        self.assertEqual(g.current,0);self.assertEqual(g.players[0].board,[])
        self.end(g);self.assertEqual(len(g.players[0].board),1)
        self.assertEqual(g.players[0].scheduled_effects[0]['remaining'],2)
    def test_repeated_choice_keeps_future_occurrence(self):
        g=self.game();g._schedule_turn_effect(0,'end',0,2,(('choose_fixed_summon',('CS2_033',)),('armor',3)))
        for occurrence in range(2):
            self.end(g);self.assertIsNotNone(g.pending_choice)
            g.step(next(a for a in g.legal_actions() if a.kind=='choose'))
            self.assertEqual(g.players[0].armor,3*(occurrence+1))
            self.assertEqual(len(g.players[0].board),occurrence+1)
            self.end(g)
        self.assertFalse(g.players[0].scheduled_effects)
    def test_schedule_observation_is_detached_and_omits_internal_id(self):
        g=self.game();self.play(g,'TIME_700');view=g.observe(0)
        effects=view['players'][0]['scheduled_effects']
        self.assertNotIn('uid',effects[0]);self.assertEqual(effects[0]['remaining'],3)
        effects[0]['remaining']=0
        self.assertEqual(g.players[0].scheduled_effects[0]['remaining'],3)

    def test_lakkari_empty_hand_still_fills(self):
        g=self.game();self.play(g,'TLC_466');self.end(g)
        self.assertEqual([m.card_id for m in g.players[0].board],['UNG_829t3']*7)
        self.assertEqual(g.players[0].scheduled_effects[0]['remaining'],2)
    def test_lakkari_full_board_still_discards(self):
        g=self.game()
        for _ in range(7):g._summon(0,'CS2_033')
        self.play(g,'TLC_466');g.players[0].hand.append(Card(g._new_id(),'CORE_CS2_029'))
        self.end(g);self.assertFalse(g.players[0].hand)
        self.assertEqual([m.card_id for m in g.players[0].board],['CS2_033']*7)
    def test_lakkari_refills_each_remaining_turn(self):
        g=self.game();self.play(g,'TLC_466')
        for occurrence in range(3):
            self.end(g);self.assertEqual(len(g.players[0].board),7)
            for m in list(g.players[0].minions):m.health=0
            g._settle();self.end(g)
        self.assertFalse(g.players[0].scheduled_effects)
        self.end(g);self.assertFalse(g.players[0].board)

    def test_ravenous_flock_three_hatchlings_next_turn(self):
        g=self.game();self.play(g,'TLC_232');self.end(g)
        self.assertEqual(g.players[0].board,[]);self.end(g)
        self.assertEqual([m.card_id for m in g.players[0].board],['TLC_237t']*3)
        self.assertTrue(all((m.attack,m.health)==(2,1) for m in g.players[0].minions))
        self.assertFalse(g.players[0].scheduled_effects)
    def test_ravenous_flock_uses_available_space(self):
        g=self.game()
        for _ in range(6):g._summon(0,'CS2_033')
        self.play(g,'TLC_232');self.end(g);self.end(g)
        self.assertEqual(sum(m.card_id=='TLC_237t' for m in g.players[0].minions),1)
        self.assertFalse(g.players[0].scheduled_effects)
