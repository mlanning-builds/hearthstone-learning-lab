"""Armor gains publish owner-correct events and resume forced attack chains."""
import unittest
from unittest.mock import patch
from expanded import Game, Action, random_deck
from expanded.game import Card

class ArmorAttackTests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('WARRIOR',31),random_deck('MAGE',53)],seed=71)
        g.step(Action('mulligan'));g.step(Action('mulligan'))
        for p in g.players:
            p.hand=[];p.board=[];p.deck=['CORE_CS2_029']*20;p.mana=p.max_mana=10;p.health=30;p.armor=0
        return g
    def play(self,g,cid):
        c=g._enter_hand(0,Card(g._new_id(),cid))
        g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid))
    def basher(self,g,owner=0):return g._summon(owner,'DINO_400')
    def test_play_has_no_battlecry(self):
        g=self.game();self.play(g,'DINO_400');m=g.players[0].minions[0]
        self.assertEqual(m.attack,g.cards[m.card_id]['attack'])
    def test_single_gain_buffs_once_regardless_amount(self):
        g=self.game();m=self.basher(g);a,h=m.attack,m.health
        g._gain_armor(0,20);g._settle()
        self.assertEqual((m.attack,m.health),(a+2,h+2));self.assertEqual(g.players[0].armor,20)
    def test_separate_gains_stack(self):
        g=self.game();m=self.basher(g);a=m.attack
        g._gain_armor(0,1);g._gain_armor(0,1);g._settle();self.assertEqual(m.attack,a+4)
    def test_zero_and_negative_are_not_gains(self):
        g=self.game();m=self.basher(g);a=m.attack
        g._gain_armor(0,0);g._gain_armor(0,-1);g._settle();self.assertEqual(m.attack,a);self.assertEqual(g.players[0].armor,0)
    def test_opponent_armor_does_not_trigger(self):
        g=self.game();m=self.basher(g);a=m.attack
        g._gain_armor(1,5);g._settle();self.assertEqual(m.attack,a)
    def test_armor_absorption_does_not_trigger(self):
        g=self.game();m=self.basher(g);a=m.attack;g.players[0].armor=5
        g._damage(g.hero_id(0),3);g._settle();self.assertEqual(m.attack,a)
    def test_silenced_basher_does_not_trigger(self):
        g=self.game();m=self.basher(g);g._silence(m);a=m.attack
        g._gain_armor(0,3);g._settle();self.assertEqual(m.attack,a)
    def test_new_listener_does_not_see_prior_gain(self):
        g=self.game();g._gain_armor(0,3);m=self.basher(g);a=m.attack
        g._settle();self.assertEqual(m.attack,a)
    def test_attack_uses_buff_and_does_not_spend_attack(self):
        g=self.game();m=self.basher(g);e=g._summon(1,'CS3_020');e.attack=0;e.health=e.max_health=50;a=m.attack
        g._gain_armor(0,1);g._settle();self.assertEqual(e.health,50-a-2);self.assertEqual(m.attacks,0)
    def test_no_enemies_does_not_hit_hero(self):
        g=self.game();self.basher(g);g._gain_armor(0,1);g._settle();self.assertEqual(g.players[1].health,30)
    def test_two_bashers_reselect_after_first_kill(self):
        g=self.game();a=self.basher(g);b=self.basher(g);x=a.attack;y=b.attack
        g._summon(1,'EDR_851t');g._summon(1,'EDR_851t');g._gain_armor(0,1);g._settle()
        self.assertFalse(g.players[1].minions);self.assertEqual((a.attack,b.attack),(x+2,y+2))
    def test_warrior_power_publishes_gain(self):
        g=self.game();m=self.basher(g);a=m.attack;g.step(Action('power'))
        self.assertEqual(m.attack,a+2);self.assertEqual(g.players[0].armor,2)
    def test_druid_power_publishes_gain(self):
        g=self.game();g.players[0].hero_class='DRUID';m=self.basher(g);a=m.attack;g.step(Action('power'))
        self.assertEqual(m.attack,a+2);self.assertEqual(g.players[0].armor,1)
    def test_spell_armor_publishes_gain(self):
        g=self.game();m=self.basher(g);a=m.attack;self.play(g,'CORE_EX1_606');self.assertEqual(m.attack,a+2)
    def test_deathrattle_armor_publishes_gain(self):
        g=self.game();m=self.basher(g);a=m.attack;x=g._summon(0,'CORE_LOOT_413');x.health=0;g._settle()
        self.assertEqual(m.attack,a+2);self.assertEqual(g.players[0].armor,3)
    def test_hero_card_armor_publishes_gain(self):
        g=self.game();m=self.basher(g);a=m.attack;self.play(g,'TLC_513t');self.assertEqual(m.attack,a+2)
    def test_opponent_turn_gain_keeps_controller(self):
        g=self.game();m=self.basher(g,1);e=g._summon(0,'EDR_851t');g._gain_armor(1,3);g._settle()
        self.assertNotIn(e,g.players[0].board);self.assertEqual(g.current,0);self.assertEqual(m.attacks,0)
    def test_armor_chain_can_trigger_same_basher_again(self):
        g=self.game()
        for owner in (0,1):
            m=g._summon(owner,'EDR_471');m.health=m.max_health=30
            self.basher(g,owner)
        bashers=[p.minions[1] for p in g.players]
        before=[m.attack for m in bashers]
        with patch.object(g.rng,'choice',side_effect=lambda values:values[0]):
            g._gain_armor(0,1);g._settle()
        self.assertGreater(bashers[0].attack,before[0]+2)
        self.assertGreater(bashers[1].attack,before[1])
        self.assertTrue(all(m.attacks==0 for p in g.players for m in p.minions))

if __name__=='__main__':unittest.main()
