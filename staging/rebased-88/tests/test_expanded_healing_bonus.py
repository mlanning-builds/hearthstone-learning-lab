import unittest
from expanded import Game, Action, random_deck
from expanded.game import Card


class PersistentHealingTests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('PRIEST',31),random_deck('MAGE',53)],seed=71)
        g.step(Action('mulligan'));g.step(Action('mulligan'))
        for p in g.players:
            p.hand=[];p.board=[];p.deck=['CORE_CS2_029']*20;p.health=10;p.mana=p.max_mana=10
        return g
    def play(self,g):
        c=Card(g._new_id(),'CATA_216');g.players[0].hand.append(c)
        g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid))
    def test_actual_battlecry_stacks_and_survives_silence(self):
        g=self.game();self.play(g);self.play(g)
        for m in list(g.players[0].minions):g._silence(m)
        self.assertEqual(g.players[0].permanent_healing_bonus,4)
        self.assertEqual(g._heal(g.hero_id(0),2,healer=0),6)
    def test_source_owner_not_target_controls_bonus(self):
        g=self.game();self.play(g)
        self.assertEqual(g._heal(g.hero_id(1),2,healer=0),4)
        self.assertEqual(g._heal(g.hero_id(0),2,healer=1),2)
    def test_zero_and_blocked_healing_do_not_gain_bonus(self):
        g=self.game();self.play(g)
        self.assertEqual(g._heal(g.hero_id(0),0,healer=0),0)
        g.players[0].healing_block_expiry_players=[1]
        self.assertEqual(g._heal(g.hero_id(0),3,healer=0),0)
    def test_caps_and_actual_healing_counter(self):
        g=self.game();self.play(g);g.players[0].health=29
        self.assertEqual(g._heal(g.hero_id(0),5,healer=0),1)
        self.assertEqual(g.players[0].healing_done_turn,1)
    def test_lifesteal_area_adds_bonus_once(self):
        g=self.game();self.play(g);a=g._summon(1,'CS2_033');b=g._summon(1,'CS2_033')
        ctx=dict(owner=0,source=None,bonus=0,lifesteal=True,spell=True)
        with g._damage_batch():
            g._deal_effect(a.uid,1,ctx);g._deal_effect(b.uid,1,ctx)
        self.assertEqual(g.players[0].health,14)
    def test_separate_lifesteal_hits_each_gain_bonus(self):
        g=self.game();self.play(g);a=g._summon(1,'CS2_033')
        ctx=dict(owner=0,source=None,bonus=0,lifesteal=True,spell=True)
        g._deal_effect(a.uid,1,ctx);g._deal_effect(a.uid,1,ctx)
        self.assertEqual(g.players[0].health,16)
