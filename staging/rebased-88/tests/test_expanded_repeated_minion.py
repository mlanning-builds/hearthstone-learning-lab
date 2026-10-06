import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class RepeatedMinionTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('ROGUE',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
        for p in self.g.players:p.hand=[];p.deck=['CORE_CS2_029']*10;p.mana=p.max_mana=10
    def play(self,cid='CORE_WON_351'):
        self.p.mana=10;c=Card(self.g._new_id(),cid);self.p.hand.append(c)
        self.g.step(Action('play',c.uid,position=len(self.p.board)))
    def test_first_play_no_draw_second_and_third_each_draw(self):
        self.g._summon(0,'EDR_540');self.play();self.assertEqual(len(self.p.hand),0)
        self.play();self.assertEqual(len(self.p.hand),1);self.play();self.assertEqual(len(self.p.hand),2)
    def test_history_before_listener_is_counted(self):
        self.play();self.g._summon(0,'EDR_540');self.play();self.assertEqual(len(self.p.hand),1)
    def test_summons_are_not_plays(self):
        self.g._summon(0,'EDR_540');self.g._summon(0,'CORE_WON_351');self.play()
        self.assertEqual(len(self.p.hand),0)
    def test_does_not_trigger_on_its_own_play(self):
        self.play('EDR_540');self.play('EDR_540')
        self.assertEqual(len(self.p.hand),1)
    def test_silence_disables_listener(self):
        m=self.g._summon(0,'EDR_540');self.g._silence(m);self.play();self.play()
        self.assertEqual(len(self.p.hand),0)
    def test_opponent_history_does_not_count(self):
        self.q.played_history.append(dict(card_id='CORE_WON_351',cost=1))
        self.g._summon(0,'EDR_540');self.play();self.assertEqual(len(self.p.hand),0)
    def test_multiple_listeners_each_draw(self):
        self.play();self.g._summon(0,'EDR_540');self.g._summon(0,'EDR_540');self.play()
        self.assertEqual(len(self.p.hand),2)
    def test_identity_alias_uses_pinned_copy_identity(self):
        from copy import deepcopy
        self.g.cards=deepcopy(self.g.cards)
        original=self.g.cards['CORE_WON_351'];alias=dict(original,id='TEST_ALIAS',countAsCopyOfDbfId=original.get('countAsCopyOfDbfId',original['dbfId']),dbfId=-123)
        self.g.cards['TEST_ALIAS']=alias;self.p.played_history.append(dict(card_id='TEST_ALIAS',cost=1))
        self.g._summon(0,'EDR_540');self.play();self.assertEqual(len(self.p.hand),1)
