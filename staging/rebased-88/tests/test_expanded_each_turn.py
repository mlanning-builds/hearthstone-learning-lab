import unittest
from expanded import Game,Action,random_deck

class EachTurnTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('WARRIOR',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
        for p in self.g.players:p.hand=[];p.deck=['CORE_CS2_029']*30;p.mana=p.max_mana=10
    def coins(self,p):return sum(c.card_id=='TOKEN_COIN' for c in p.hand)
    def test_skipper_gives_coin_to_ending_player_on_both_turns(self):
        self.g._summon(0,'TIME_054');self.g.step(Action('end'))
        self.assertEqual((self.coins(self.p),self.coins(self.q)),(1,0))
        self.g.step(Action('end'))
        self.assertEqual((self.coins(self.p),self.coins(self.q)),(1,1))
    def test_two_opposing_skippers_both_reward_current_player(self):
        self.g._summon(0,'TIME_054');self.g._summon(1,'TIME_054')
        self.g.step(Action('end'));self.assertEqual((self.coins(self.p),self.coins(self.q)),(2,0))
    def test_opposing_golem_gains_reborn_at_your_turn_end(self):
        m=self.g._summon(1,'JAIL_883');m.keywords.discard('REBORN')
        self.g.step(Action('end'));self.assertIn('REBORN',m.keywords)
    def test_silence_blocks_both_new_listeners(self):
        self.g._silence(self.g._summon(0,'TIME_054'))
        m=self.g._summon(1,'JAIL_883');self.g._silence(m)
        self.g.step(Action('end'));self.assertEqual(self.coins(self.p),0)
        self.assertNotIn('REBORN',m.keywords)
    def test_ordinary_opponent_end_effect_does_not_run(self):
        self.g._summon(1,'CATA_475');self.g.step(Action('end'))
        self.assertEqual(self.p.health,30)
    def test_listener_killed_by_earlier_end_effect_does_not_run(self):
        self.g._summon(0,'CATA_475');m=self.g._summon(1,'TIME_054');m.health=1
        self.g.step(Action('end'));self.assertEqual(self.coins(self.p),0)
