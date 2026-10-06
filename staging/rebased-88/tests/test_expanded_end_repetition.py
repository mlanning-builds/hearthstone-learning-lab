import unittest
from unittest.mock import patch
from expanded import Game,Action,random_deck
from expanded.game import Card
from expanded.cards import END_EFFECTS

class EndRepetitionTests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('PALADIN',31),random_deck('MAGE',53)],seed=71)
        g.step(Action('mulligan'));g.step(Action('mulligan'))
        for p in g.players:
            p.hand=[];p.board=[];p.deck=['CORE_CS2_029']*30;p.mana=p.max_mana=10;p.health=30;p.armor=0
        return g
    def play(self,g,cid):
        c=g._enter_hand(g.current,Card(g._new_id(),cid))
        g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid))
    def end(self,g):g.step(Action('end'))
    def coins(self,g,owner):return sum(c.card_id=='TOKEN_COIN' for c in g.players[owner].hand)
    def test_doubles_minion_effect(self):
        g=self.game();g._summon(0,'TIME_054');self.play(g,'CATA_480');self.end(g)
        self.assertEqual(self.coins(g,0),2)
    def test_every_turn_effect_rewards_ending_player_with_source_multiplier(self):
        g=self.game();g._summon(0,'TIME_054');self.play(g,'CATA_480');self.end(g);self.end(g)
        self.assertEqual(self.coins(g,0),2);self.assertEqual(self.coins(g,1),2)
    def test_opponent_minion_not_doubled(self):
        g=self.game();g._summon(1,'TIME_054');self.play(g,'CATA_480');self.end(g)
        self.assertEqual(self.coins(g,1),0);self.assertEqual(self.coins(g,0),1)
    def test_three_owner_ends_then_expires(self):
        g=self.game();m=g._summon(0,'EDR_940');self.play(g,'CATA_480')
        for n in range(1,4):
            self.end(g);self.assertEqual(g.players[0].armor,2*n);self.end(g)
        self.assertEqual(g._end_trigger_count(0),1);self.end(g);self.assertEqual(g.players[0].armor,7)
    def test_two_auras_do_not_quadruple(self):
        g=self.game();g._summon(0,'EDR_940');self.play(g,'CATA_480');self.play(g,'CATA_480');self.end(g)
        self.assertEqual(g.players[0].armor,2)
    def test_later_aura_outlasts_first(self):
        g=self.game();self.play(g,'CATA_480');self.end(g);self.end(g);self.play(g,'CATA_480')
        for _ in range(2):self.end(g);self.end(g)
        self.assertEqual(len(g.players[0].end_repeat_expiries),1);self.assertEqual(g._end_trigger_count(0),2)
    def test_no_minions_still_consumes_duration(self):
        g=self.game();self.play(g,'CATA_480')
        for _ in range(6):self.end(g)
        self.assertFalse(g.players[0].end_repeat_expiries)
    def test_does_not_double_spell_schedule(self):
        g=self.game();self.play(g,'CATA_480');self.play(g,'TIME_700');self.end(g)
        self.assertEqual(len(g.players[0].minions),1)
    def test_does_not_double_player_end_damage(self):
        g=self.game();self.play(g,'CATA_480');g.players[0].permanent_end_damage=[2];self.end(g)
        self.assertEqual(g.players[1].health,28)
    def test_silence_suppresses_effects(self):
        g=self.game();m=g._summon(0,'EDR_940');g._silence(m);self.play(g,'CATA_480');self.end(g)
        self.assertEqual(g.players[0].armor,0)
    def test_source_dying_after_first_does_not_repeat(self):
        g=self.game();m=g._summon(0,'EDR_940');self.play(g,'CATA_480')
        with patch.dict(END_EFFECTS,{'EDR_940':[('armor',1),('damage',99)]}):
            original=g._effect
            def effect(op,ctx):
                if op==('damage',99):ctx['source'].health=0
                else:original(op,ctx)
            with patch.object(g,'_effect',side_effect=effect):self.end(g)
        self.assertNotIn(m,g.players[0].board);self.assertEqual(g.players[0].armor,1)
    def test_expiring_source_repeats_before_expiration(self):
        g=self.game();m=g._summon(0,'EDR_940',expires=True);self.play(g,'CATA_480');self.end(g)
        self.assertEqual(g.players[0].armor,2);self.assertNotIn(m,g.players[0].board)
    def test_explicit_replay_is_doubled(self):
        g=self.game();g._summon(0,'EDR_940');self.play(g,'CATA_480')
        g._start_play_effects([('replay_random_end',)],dict(owner=0,source=None,target=0,bonus=0,lifesteal=False));g._settle()
        self.assertEqual(g.players[0].armor,2)
    def test_explicit_skipper_replay_rewards_current_player(self):
        g=self.game();g._summon(0,'TIME_054');self.play(g,'CATA_480');self.end(g)
        g._start_play_effects([('replay_random_end',)],dict(owner=0,source=None,target=0,bonus=0,lifesteal=False));g._settle()
        self.assertEqual(self.coins(g,0),2);self.assertEqual(self.coins(g,1),2)
    def test_replay_choice_resumes_repeated_source(self):
        g=self.game();m=g._summon(0,'EDR_940');self.play(g,'CATA_480')
        with patch.dict(END_EFFECTS,{'EDR_940':[('choose_fixed_summon',('CS2_033',)),('armor',1)]}):
            g._start_play_effects([('replay_random_end',)],dict(owner=0,source=None,target=0,bonus=0,lifesteal=False));g._settle()
            self.assertIsNotNone(g.pending_choice);self.assertEqual(g.players[0].armor,0)
            g.step(g.legal_actions()[0]);self.assertIsNotNone(g.pending_choice);self.assertEqual(g.players[0].armor,1)
            g.step(g.legal_actions()[0]);self.assertIsNone(g.pending_choice);self.assertEqual(g.players[0].armor,2)
    def test_counterspell_prevents_aura(self):
        g=self.game();g.players[1].secrets.append(Card(g._new_id(),'CORE_EX1_287'));self.play(g,'CATA_480');self.assertEqual(g._end_trigger_count(0),1)
    def test_aura_condition_recognizes_sandfury(self):
        g=self.game();self.play(g,'CATA_480');self.assertTrue(g._batch30_state('aura_active',0))
    def test_public_duration_does_not_consume_rng(self):
        g=self.game();self.play(g,'CATA_480');state=g.rng.getstate()
        self.assertEqual(g.observe(0)['players'][0]['end_repeat_turns'],[3])
        self.assertEqual(g.observe(1)['players'][0]['end_repeat_turns'],[3]);self.assertEqual(g.rng.getstate(),state)

if __name__=='__main__':unittest.main()
