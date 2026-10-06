import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class CallWildTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('HUNTER',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p=self.g.players[0];self.p.hand=[];self.p.mana=self.p.max_mana=10
    def play(self):
        c=Card(self.g._new_id(),'CORE_OG_211');self.p.hand.append(c)
        self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid))
    def test_order_stats_and_charge(self):
        rng=self.g.rng.getstate();self.play()
        self.assertEqual([m.card_id for m in self.p.minions],['NEW1_034','NEW1_033','NEW1_032'])
        self.assertEqual([(m.attack,m.health) for m in self.p.minions],[(5,2),(2,4),(5,4)])
        self.assertEqual(self.p.mana,2);self.assertEqual(self.g.rng.getstate(),rng)
        attackers={a.source for a in self.g.legal_actions() if a.kind=='attack'}
        self.assertEqual(attackers,{self.p.minions[0].uid})
    def test_one_slot_only_huffer(self):
        for _ in range(6):self.g._summon(0,'TOKEN_SCOUT')
        self.play();self.assertEqual(self.p.minions[-1].card_id,'NEW1_034')
        self.assertEqual(len(self.p.board),7);self.assertEqual(self.p.minions[-1].attack,4)
    def test_two_slots_huffer_then_leokk(self):
        for _ in range(5):self.g._summon(0,'TOKEN_SCOUT')
        self.play();self.assertEqual([m.card_id for m in self.p.minions[-2:]],['NEW1_034','NEW1_033'])
        self.assertEqual(self.p.minions[-2].attack,5)
    def test_silencing_leokk_removes_only_its_aura(self):
        self.play();self.g._silence(self.p.minions[1]);self.g._settle()
        self.assertEqual([m.attack for m in self.p.minions],[4,2,4])
