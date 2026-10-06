import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class ShuffleHistoryTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('ROGUE',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
    def test_setup_and_mulligan_not_recorded(self):
        self.assertEqual([p.shuffle_history for p in self.g.players],[[],[]])
    def test_actor_and_destination_distinct(self):
        p=self.g.players[1];c=p.hand[0]
        self.g._shuffle_hand_card(1,c,actor=0)
        self.assertEqual(p.shuffle_history[-1],dict(turn=self.g.turn,actor=0,destination=1,count=1,kind='shuffle'))
        self.assertEqual(self.g.players[0].shuffle_history,[])
    def test_trade_is_separate_from_normal_shuffle(self):
        p=self.g.players[0];p.mana=10;c=Card(self.g._new_id(),'CORE_SW_066');p.hand=[c]
        self.g.step(Action('trade',source=c.uid))
        self.assertEqual(p.shuffle_history[-1]['kind'],'trade')
    def test_history_does_not_expose_card_identity(self):
        p=self.g.players[0];self.g._shuffle_hand_card(0,p.hand[0])
        history=self.g.observe(1)['players'][0]['shuffle_history']
        self.assertEqual(set(history[0]),{'turn','actor','destination','count','kind'})
        history[0]['count']=99;self.assertEqual(p.shuffle_history[0]['count'],1)
    def test_batch_count_is_one_event(self):
        self.g._record_deck_insertion(0,0,10,'shuffle')
        self.assertEqual(len(self.g.players[0].shuffle_history),1)
        self.assertEqual(self.g.players[0].shuffle_history[0]['count'],10)
    def test_invalid_event_rejected_without_history_mutation(self):
        with self.assertRaises(ValueError):self.g._record_deck_insertion(0,0,0,'shuffle')
        self.assertEqual(self.g.players[0].shuffle_history,[])
