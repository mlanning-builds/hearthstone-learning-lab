"""Rewind restores game outcomes, not player RNG/decision history."""
import copy,json,unittest
import test_expanded_generation as fixtures
from expanded import Action
from expanded.cards import COLLECTIBLE_IDS
from expanded.rewind import RULES
from engine.game import Card

class RewindTests(unittest.TestCase):
    def setUp(self):self.h=fixtures.GenerationTests();self.g=self.h.game()
    def add(self,cid,owner=0):
        c=Card(self.g._new_id(),cid);self.g._enter_hand(owner,c);return c
    def play(self,cid):
        c=self.add(cid);a=next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid)
        self.g.step(a);return c
    def choose(self,rewind):self.g.step(Action('choose',choices=(int(rewind),)))
    def test_registered_six_closed_outcome_cards(self):self.assertTrue(set(RULES)<=COLLECTIBLE_IDS)
    def test_keep_retains_damage_and_exits_choice(self):
        self.play('TIME_001');self.assertEqual(self.g.players[1].health,24)
        self.assertEqual(self.g.pending_choice['kind'],'rewind');self.choose(False)
        self.assertEqual(self.g.players[1].health,24);self.assertIsNone(self.g.pending_choice)
    def test_rewind_does_not_double_damage_or_payment(self):
        self.play('TIME_001');mana=self.g.players[0].mana;self.choose(True)
        self.assertEqual(self.g.players[1].health,24);self.assertEqual(self.g.players[0].mana,mana)
        self.assertEqual(self.g.players[0].cards_played,1)
        self.assertEqual([e['card_id'] for e in self.g.players[0].played_history],['TIME_001'])
    def test_rewind_advances_randomness_instead_of_restoring_same_roll(self):
        self.g._summon(1,'EX1_tk34');self.g._summon(1,'EX1_tk34')
        self.play('TIME_001');before=self.g.rng.getstate();self.choose(True)
        self.assertNotEqual(self.g.rng.getstate(),before)
    def test_all_cards_are_blocked_until_rewind_choice(self):
        self.add('TOKEN_COIN');self.play('TIME_001')
        self.assertEqual([a.kind for a in self.g.legal_actions()],['choose','choose'])
    def test_snapshot_not_exposed_to_either_player(self):
        self.play('TIME_001')
        for owner in (0,1):
            serialized=json.dumps(self.g.observe(owner))
            self.assertNotIn('snapshot',serialized);self.assertNotIn('_rewind_state',serialized)
        self.assertEqual(self.g.observe(1)['pending_choice'],{'owner':0,'waiting':True})
    def test_choice_is_not_discover(self):
        self.play('TIME_001');self.choose(False)
        self.assertEqual(self.g.players[0].discoveries_total,0)
    def test_hero_lethal_has_no_rewind(self):
        self.g.players[1].health=2;self.play('TIME_001')
        self.assertTrue(self.g.terminal);self.assertIsNone(self.g.pending_choice)
    def test_minion_rewind_does_not_duplicate_source(self):
        self.play('TIME_004');self.choose(True)
        self.assertEqual([m.card_id for m in self.g.players[0].minions],['TIME_004'])
        self.assertEqual(self.g.players[1].health,23)
    def test_source_remembers_used_rewind_through_bounce(self):
        self.play('TIME_004');self.choose(True);m=self.g.players[0].minions[0]
        self.g._bounce(m);c=self.g.players[0].hand[0];self.g.players[0].mana=10
        a=next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid);self.g.step(a)
        self.assertIsNone(self.g.pending_choice);self.assertEqual(self.g.players[1].health,16)
    def test_keep_does_not_consume_unspent_rewind(self):
        self.play('TIME_004');self.choose(False);self.g._bounce(self.g.players[0].minions[0]);self.g.players[0].mana=10
        c=self.g.players[0].hand[0];self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid))
        self.assertEqual(self.g.pending_choice['kind'],'rewind')
    def test_recruit_does_not_offer_rewind_or_run_battlecry(self):
        self.g._summon(0,'TIME_004');self.g._settle();self.assertIsNone(self.g.pending_choice)
        self.assertEqual(self.g.players[1].health,30)
    def test_draw_buff_rewind_replaces_draw_and_buff(self):
        self.g.players[0].deck=['CORE_CS2_188','CORE_CS2_189'];self.play('TIME_003');self.choose(True)
        self.assertEqual(len(self.g.players[0].deck),1);self.assertEqual(len(self.g.players[0].hand),1)
        self.assertEqual((self.g.players[0].hand[0].attack_bonus,self.g.players[0].hand[0].health_bonus),(2,2))
    def test_discard_rewind_restores_both_hands_before_rediscard(self):
        for owner in (0,1):
            self.add('TOKEN_COIN',owner);self.add('CORE_CS2_029',owner)
        self.play('TIME_008');self.choose(True)
        for p in self.g.players:
            self.assertEqual(len(p.hand),1);self.assertEqual(len(p.discard_history),1)
    def test_silence_destroy_suppresses_deathrattle_on_both_attempts(self):
        self.g._summon(1,'CORE_EX1_012');self.play('TIME_433');self.choose(True)
        self.assertEqual(len(self.g.players[1].hand),0);self.assertEqual(len(self.g.players[1].death_history),1)
    def test_aeon_rend_hits_two_distinct_enemies(self):
        self.g._summon(1,'EX1_tk34');self.play('TIME_441');self.choose(True)
        self.assertEqual(self.g.players[1].health,26);self.assertEqual(self.g.players[1].minions[0].health,2)
    def test_spell_damage_added_to_each_knife(self):
        self.g._summon(0,'CORE_EX1_012');self.play('TIME_001');self.choose(True)
        self.assertEqual(self.g.players[1].health,21)
    def test_invalid_choice_does_not_change_state(self):
        self.play('TIME_001');before=self.g.rng.getstate()
        with self.assertRaises(ValueError):self.g.step(Action('choose',choices=(2,)))
        self.assertEqual(self.g.rng.getstate(),before);self.assertEqual(self.g.pending_choice['kind'],'rewind')
    def test_decision_history_keeps_rewind_action(self):
        self.play('TIME_001');self.choose(True)
        self.assertEqual(self.g.history[-1]['action']['kind'],'choose')
    def test_minion_after_play_secret_waits_until_choice(self):
        # Explosive Runes reacts only after the timeline is accepted.
        self.g._effect(('secret','CORE_LOOT_101'),dict(owner=1,source=None,target=0,bonus=0,lifesteal=False))
        self.play('TIME_004');self.assertEqual(len(self.g.players[1].secrets),1)
        self.choose(True);self.assertFalse(self.g.players[1].secrets)
    def test_counterspell_has_no_rewind_offer(self):
        self.g._effect(('secret','CORE_EX1_287'),dict(owner=1,source=None,target=0,bonus=0,lifesteal=False))
        self.play('TIME_001');self.assertIsNone(self.g.pending_choice);self.assertEqual(self.g.players[1].health,30)

    def test_shades_have_two_distinct_bonus_effects(self):
        from expanded.bonus_effects import BONUS_EFFECTS
        self.play('TIME_610')
        self.assertEqual(len(self.g.players[0].minions),4)
        for m in self.g.players[0].minions:
            self.assertEqual((m.attack,m.health),(3,2))
            self.assertEqual(len(m.keywords & BONUS_EFFECTS),2)
        self.choose(True)
        self.assertEqual(len(self.g.players[0].minions),4)
        self.assertEqual(self.g.players[0].cards_played,1)
    def test_shades_respect_board_capacity_on_both_timelines(self):
        for _ in range(6):self.g._summon(0,'CORE_CS2_188')
        self.play('TIME_610');self.choose(True)
        self.assertEqual(len(self.g.players[0].minions),7)
        self.assertEqual(sum(m.card_id=='TIME_610t2' for m in self.g.players[0].minions),1)
    def test_shade_keywords_reroll_without_preserving_first_timeline(self):
        self.play('TIME_610');before=self.g.rng.getstate();self.choose(True)
        self.assertNotEqual(before,self.g.rng.getstate())
        self.assertEqual(len({m.uid for m in self.g.players[0].minions}),4)
