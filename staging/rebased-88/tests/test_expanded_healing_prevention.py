import unittest
from unittest.mock import patch
from expanded import Game,Action,random_deck
from expanded.game import Card

class HealingPreventionTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('HUNTER',31),random_deck('PRIEST',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
        for p in self.g.players:p.hand=[];p.deck=['CORE_CS2_029']*10;p.mana=p.max_mana=10;p.health=15
    def play(self):
        c=Card(self.g._new_id(),'TLC_250');self.p.hand.append(c)
        self.g.step(Action('play',c.uid,position=len(self.p.board)))
        return self.p.board[-1]
    def test_only_enemy_hero_healing_is_prevented(self):
        m=self.play();m.health=2
        self.assertEqual(self.g._heal(-2,5,healer=0),0)
        self.assertEqual(self.g._heal(-1,5,healer=0),5)
        self.assertEqual(self.g._heal(m.uid,1,healer=0),1)
        self.assertEqual(self.p.healing_done_turn,6);self.assertEqual(self.q.health,15)
    def test_persists_after_silence_and_death(self):
        m=self.play();self.g._silence(m);m.health=0;self.g._settle()
        self.assertEqual(self.g._heal(-2,5),0)
    def test_priest_power_spends_mana_without_healing(self):
        self.play();self.g.step(Action('end'))
        before=self.q.mana;self.g._base_power(-2)
        self.assertEqual(self.q.mana,before-2);self.assertTrue(self.q.power_used)
        self.assertEqual(self.q.health,15);self.assertEqual(self.q.healing_done_turn,0)
    def test_expires_before_owner_start_effects(self):
        self.play();self.g.step(Action('end'));self.assertEqual(self.g._heal(-2,4),0)
        with patch.object(self.g,'_start_effects',side_effect=lambda:self.g._heal(-2,4)):
            self.g.step(Action('end'))
        self.assertEqual(self.q.health,19);self.assertEqual(self.q.healing_block_expiry_players,[])
    def test_lifesteal_still_deals_damage(self):
        self.play();self.g._deal_effect(-1,3,dict(owner=1,source=None,bonus=0,lifesteal=True))
        self.assertEqual(self.p.health,12);self.assertEqual(self.q.health,15)
    def test_repeated_battlecries_expire_together(self):
        self.play();self.play();self.assertEqual(self.q.healing_block_expiry_players,[0,0])
        self.g.step(Action('end'));self.g.step(Action('end'))
        self.assertEqual(self.g._heal(-2,3),3)
    def test_effect_visible_to_both_players_and_copy_independent(self):
        import copy
        self.play()
        for viewer in (0,1):self.assertEqual(self.g.observe(viewer)['players'][1]['healing_block_expiry_players'],[0])
        clone=copy.deepcopy(self.g);clone.players[1].healing_block_expiry_players.clear()
        self.assertEqual(self.q.healing_block_expiry_players,[0])
    def test_summoning_alone_does_not_block(self):
        self.g._summon(0,'TLC_250');self.assertEqual(self.g._heal(-2,3),3)
