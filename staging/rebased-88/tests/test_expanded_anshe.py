import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class AnsheTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('PRIEST',31),random_deck('PRIEST',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players;self.p.hand=[];self.p.mana=self.p.max_mana=10
    def play(self):
        c=Card(self.g._new_id(),'CORE_BAR_313');self.p.hand.append(c)
        self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid))
        return next(m for m in self.p.minions if m.card_id=='CORE_BAR_313')
    def check(self,bonus):
        m=self.play();d=self.g.cards[m.card_id]
        self.assertEqual((m.attack,m.health),(d['attack']+bonus,d['health']+bonus))
        self.assertIn('TAUNT',m.keywords)
    def test_no_healing_no_buff(self):self.check(0)
    def test_healing_enemy_activates(self):
        self.q.health=25;self.g.step(Action('power',target=-2));self.check(3)
    def test_healing_full_health_does_not_activate(self):
        self.g.step(Action('power',target=-1));self.check(0)
    def test_enemy_healing_you_does_not_activate(self):
        self.p.health=25;self.g._heal(-1,2,healer=1);self.check(0)
    def test_healing_minion_activates(self):
        m=self.g._summon(0,'CORE_BT_510');m.health-=2
        self.g.step(Action('power',target=m.uid));self.check(3)
    def test_silence_removes_battlecry_buff(self):
        self.p.health=25;self.g.step(Action('power',target=-1));m=self.play()
        self.g._silence(m);self.g._settle();d=self.g.cards[m.card_id]
        self.assertEqual((m.attack,m.health),(d['attack'],d['health']))
