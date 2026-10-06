import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class TargetedSpellTriggerTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('MAGE',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
        for p in self.g.players:p.hand=[];p.deck=['CORE_CS2_029']*10;p.mana=p.max_mana=10
        self.source=self.g._summon(0,'END_026')
    def play(self,cid,target=0):
        c=Card(self.g._new_id(),cid);self.p.hand.append(c);self.g.step(Action('play',c.uid,target))
    def test_killed_enemy_target_still_counts(self):
        m=self.g._summon(1,'CORE_WON_351');self.play('CORE_CS2_029',m.uid)
        self.assertEqual(len(self.p.hand),1);self.assertNotIn(m,self.q.minions)
    def test_friendly_target_and_self_are_eligible(self):
        self.play('CORE_AT_055',self.source.uid);self.assertEqual(len(self.p.hand),1)
    def test_hero_and_untargeted_spells_do_not_count(self):
        self.play('CORE_CS2_029',-2);self.play('TOKEN_COIN');self.assertEqual(len(self.p.hand),0)
    def test_counterspell_prevents_trigger(self):
        m=self.g._summon(1,'CORE_WON_351');self.q.secrets.append(Card(self.g._new_id(),'CORE_EX1_287'))
        self.play('CORE_CS2_029',m.uid);self.assertEqual(len(self.p.hand),0)
    def test_silenced_or_killed_source_does_not_trigger(self):
        self.g._silence(self.source);m=self.g._summon(1,'CORE_WON_351');self.play('CORE_CS2_029',m.uid)
        self.assertEqual(len(self.p.hand),0)
        self.p.mana=10;self.source=self.g._summon(0,'END_026');self.play('CORE_CS2_029',self.source.uid)
        self.assertEqual(len(self.p.hand),0)
    def test_opponent_spell_does_not_trigger(self):
        self.g._queue_event('spell_cast',owner=1,card_id='CORE_CS2_029',cost=4,targeted_minion=True)
        self.g._settle();self.assertEqual(len(self.p.hand),0)
    def test_multiple_listeners_each_draw_once(self):
        self.g._summon(0,'END_026');m=self.g._summon(1,'CORE_WON_351');self.play('CORE_CS2_029',m.uid)
        self.assertEqual(len(self.p.hand),2)
