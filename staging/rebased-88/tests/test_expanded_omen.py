import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class OmenTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('WARRIOR',31),random_deck('MAGE',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players;self.p.hand=[];self.p.deck=[];self.p.mana=self.p.max_mana=10
    def play(self):
        c=Card(self.g._new_id(),'END_035');self.p.hand.append(c)
        self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid))
    def test_destroys_top_five_preserving_bottom_order(self):
        self.q.deck=['CORE_CS2_029','CORE_EX1_506']+['CORE_CS2_179']*5
        self.play();self.assertEqual(self.q.deck,['CORE_CS2_029','CORE_EX1_506'])
    def test_nonempty_own_deck_prevents_effect(self):
        self.p.deck=['CORE_EX1_506'];before=list(self.q.deck);self.play();self.assertEqual(self.q.deck,before)
    def test_short_deck_does_not_cause_fatigue(self):
        self.q.deck=['CORE_EX1_506'];health=self.q.health;self.play()
        self.assertEqual(self.q.deck,[]);self.assertEqual(self.q.fatigue,0);self.assertEqual(self.q.health,health)
    def test_empty_enemy_deck_does_not_cause_fatigue(self):
        self.q.deck=[];self.play();self.assertEqual(self.q.fatigue,0)
    def test_enchanted_entities_are_removed_without_drawing(self):
        c=Card(self.g._new_id(),'CORE_EX1_506');c.attack_bonus=5;self.q.deck=[c]
        hand=list(self.q.hand);self.play();self.assertEqual(self.q.hand,hand);self.assertEqual(self.q.deck,[])
    def test_destruction_is_not_minion_death(self):
        self.q.deck=['CORE_RLK_745'];corpses=self.q.corpses;history=list(self.q.death_history)
        self.play();self.assertEqual(self.q.corpses,corpses);self.assertEqual(self.q.death_history,history)
        self.assertEqual(self.q.minions,[])
