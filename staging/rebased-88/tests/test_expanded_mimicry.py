import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class MimicryTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('ROGUE',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
        for p in self.g.players:p.hand=[];p.deck=['CORE_CS2_029']*10;p.mana=p.max_mana=10
    def play(self):
        c=Card(self.g._new_id(),'EDR_522');self.p.hand.append(c);self.g.step(Action('play',c.uid))
    def test_both_receive_same_cards_with_distinct_entities(self):
        self.q.deck=['CORE_AT_055','CORE_CS2_029'];self.play()
        self.assertEqual([c.card_id for c in self.p.hand],['CORE_CS2_029','CORE_AT_055'])
        self.assertEqual([c.card_id for c in self.q.hand],[c.card_id for c in self.p.hand])
        self.assertFalse(set(c.uid for c in self.p.hand)&set(c.uid for c in self.q.hand))
    def test_opponent_full_hand_burns_but_caster_gets_copies(self):
        self.q.hand=[Card(self.g._new_id(),'CORE_AT_055') for _ in range(10)];self.play()
        self.assertEqual((len(self.q.hand),len(self.p.hand),len(self.q.deck)),(10,2,8))
    def test_caster_capacity_does_not_stop_opponent_draws(self):
        self.p.hand=[Card(self.g._new_id(),'CORE_AT_055') for _ in range(9)];self.play()
        self.assertEqual((len(self.p.hand),len(self.q.hand)),(10,2))
    def test_empty_deck_fatigues_without_copies(self):
        self.q.deck=[];self.play();self.assertEqual((self.q.fatigue,self.q.health,len(self.p.hand)),(2,27,0))
    def test_one_card_then_fatigue_copies_only_the_card(self):
        self.q.deck=['CORE_AT_055'];self.play()
        self.assertEqual((self.q.fatigue,len(self.p.hand)),(1,1));self.assertEqual(self.p.hand[0].card_id,'CORE_AT_055')
    def test_lethal_fatigue_stops_sequence(self):
        self.q.deck=[];self.q.health=1;self.play();self.assertTrue(self.g.terminal);self.assertEqual(self.q.fatigue,1)
    def test_copy_preserves_supported_modifiers_without_aliasing(self):
        c=Card(self.g._new_id(),'CS3_025',attack_bonus=2,health_bonus=3);c.cost_delta=-1
        self.q.deck=[c];self.play();copy=self.p.hand[0]
        self.assertEqual((copy.attack_bonus,copy.health_bonus,copy.cost_delta),(2,3,-1))
        copy.attack_bonus=99;self.assertEqual(self.q.hand[0].attack_bonus,2)
    def test_counterspell_prevents_draws(self):
        self.q.secrets.append(Card(self.g._new_id(),'CORE_EX1_287'));self.play()
        self.assertEqual((len(self.p.hand),len(self.q.hand),len(self.q.deck)),(0,0,10))
