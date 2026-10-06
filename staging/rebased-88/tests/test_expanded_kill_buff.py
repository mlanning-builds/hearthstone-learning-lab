import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class KillBuffTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('HUNTER',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
        for p in self.g.players:p.hand=[];p.deck=['CORE_CS2_029']*10;p.mana=p.max_mana=10
    def play(self,target):
        c=Card(self.g._new_id(),'END_014');self.p.hand.append(c);self.g.step(Action('play',c.uid,target))
    def test_kill_buffs_one_friendly_minion(self):
        friends=[self.g._summon(0,'CS3_025') for _ in range(2)]
        victim=self.g._summon(1,'CORE_WON_351');self.play(victim.uid)
        self.assertNotIn(victim,self.q.minions)
        self.assertEqual(sorted((m.attack,m.health) for m in friends),[(3,6),(6,9)])
    def test_survival_and_divine_shield_do_not_buff(self):
        friend=self.g._summon(0,'CS3_025');victim=self.g._summon(1,'CS3_025')
        self.play(victim.uid);self.assertEqual((victim.health,friend.attack),(3,3))
        self.p.mana=10;victim.keywords.add('DIVINE_SHIELD');self.play(victim.uid)
        self.assertEqual((victim.health,friend.attack),(3,3))
    def test_empty_friendly_board_is_noop_after_kill(self):
        victim=self.g._summon(1,'CORE_WON_351');self.play(victim.uid);self.assertEqual(self.p.minions,[])
    def test_spell_damage_changes_kill_threshold_not_buff_size(self):
        friend=self.g._summon(0,'CORE_EX1_012');victim=self.g._summon(1,'CS3_025');victim.health=4
        before=(friend.attack,friend.health);self.play(victim.uid)
        self.assertNotIn(victim,self.q.minions);self.assertEqual((friend.attack,friend.health),(before[0]+3,before[1]+3))
    def test_face_damage_and_lethal_termination(self):
        friend=self.g._summon(0,'CS3_025');self.play(-2)
        self.assertEqual((self.q.health,friend.attack),(27,3))
        self.p.mana=10;self.q.health=3;self.play(-2)
        self.assertTrue(self.g.terminal);self.assertEqual(friend.attack,3)
    def test_friendly_targets_are_not_legal(self):
        friend=self.g._summon(0,'CS3_025');c=Card(self.g._new_id(),'END_014');self.p.hand.append(c)
        targets={a.target for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid}
        self.assertNotIn(friend.uid,targets);self.assertNotIn(-1,targets);self.assertIn(-2,targets)
    def test_counterspell_prevents_both_damage_and_buff(self):
        friend=self.g._summon(0,'CS3_025');victim=self.g._summon(1,'CORE_WON_351')
        self.q.secrets.append(Card(self.g._new_id(),'CORE_EX1_287'));self.play(victim.uid)
        self.assertEqual((victim.health,friend.attack),(2,3))
