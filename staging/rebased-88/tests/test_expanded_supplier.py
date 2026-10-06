import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class SupplierTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('ROGUE',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
        self.p.hand=[];self.p.deck=['CORE_CS2_029']*5
        self.p.mana=self.p.max_mana=10
        card=Card(self.g._new_id(),'CAP_003');self.p.hand.append(card)
        self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==card.uid))
        self.m=next(m for m in self.p.minions if m.card_id=='CAP_003')
    def test_play_cost_stealth_and_summoning_sickness(self):
        self.assertEqual(self.p.mana,8)
        self.assertEqual((self.m.attack,self.m.health),(1,3))
        self.assertIn('STEALTH',self.m.keywords)
        self.assertFalse(any(a.kind=='attack' and a.source==self.m.uid for a in self.g.legal_actions()))
        self.assertEqual(self.p.hand,[])
    def attack(self,target=-2):
        self.m.summoned_turn=-1
        self.g.step(Action('attack',self.m.uid,target))
    def test_attack_draws_and_loses_stealth(self):
        self.attack();self.assertEqual(len(self.p.hand),1)
        self.assertNotIn('STEALTH',self.m.keywords)
    def test_lethal_retaliation_still_draws(self):
        other=self.g._summon(1,'CORE_EX1_506');other.attack=3
        self.attack(other.uid)
        self.assertEqual(len(self.p.hand),1);self.assertNotIn(self.m,self.p.board)
    def test_silence_removes_draw(self):
        self.g._silence(self.m);self.attack();self.assertEqual(self.p.hand,[])
    def test_defending_does_not_draw(self):
        self.g.step(Action('end'))
        # Reveal the Supplier so it is a legal defending target.
        self.m.keywords.discard('STEALTH')
        other=self.g._summon(1,'CORE_EX1_506');other.summoned_turn=-1
        self.g.step(Action('attack',other.uid,self.m.uid))
        self.assertEqual(self.p.hand,[])
    def test_full_hand_burns_one_draw(self):
        self.p.hand=[Card(self.g._new_id(),'CORE_CS2_029') for _ in range(10)]
        self.attack();self.assertEqual(len(self.p.hand),10);self.assertEqual(len(self.p.deck),4)
