import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class AirSupportTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('SHAMAN',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
        for p in self.g.players:p.hand=[];p.mana=p.max_mana=10
        self.m=self.g._summon(0,'CORE_EX1_506');self.m.summoned_turn=-1
        self.enemy=self.g._summon(1,'CORE_EX1_506');self.enemy.attack=0;self.enemy.health=self.enemy.max_health=100
    def play(self):
        c=Card(self.g._new_id(),'CATA_564');self.p.hand.append(c)
        self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid and a.target==self.m.uid))
    def attacks(self):return [a for a in self.g.legal_actions() if a.kind=='attack' and a.source==self.m.uid]
    def test_four_attacks_and_no_fifth(self):
        self.play()
        for _ in range(4):self.g.step(Action('attack',self.m.uid,self.enemy.uid))
        self.assertEqual(self.m.attacks,4);self.assertEqual(self.attacks(),[])
    def test_cannot_attack_hero_even_with_charge(self):
        self.m.keywords.add('CHARGE');self.play()
        self.assertFalse(any(a.target<0 for a in self.attacks()))
        with self.assertRaises(ValueError):self.g.step(Action('attack',self.m.uid,-2))
    def test_does_not_grant_rush(self):
        self.m.summoned_turn=self.g.turn;self.play();self.assertEqual(self.attacks(),[])
    def test_prior_attack_counts_toward_four(self):
        self.g.step(Action('attack',self.m.uid,self.enemy.uid));self.play()
        for _ in range(3):self.g.step(Action('attack',self.m.uid,self.enemy.uid))
        self.assertEqual(self.attacks(),[])
    def test_silence_removes_both_keywords(self):
        self.play();self.g._silence(self.m)
        self.assertNotIn('MEGA_WINDFURY',self.m.keywords);self.assertNotIn('CANT_ATTACK_HERO',self.m.keywords)
        self.assertTrue(any(a.target==-2 for a in self.attacks()))
    def test_copy_preserves_restriction_and_attack_limit(self):
        self.play();copy=self.g._summon(0,self.m.card_id,copy_from=self.m);copy.summoned_turn=-1
        self.assertTrue({'MEGA_WINDFURY','CANT_ATTACK_HERO'}<=copy.keywords)
        for _ in range(4):self.g.step(Action('attack',copy.uid,self.enemy.uid))
        self.assertFalse(any(a.kind=='attack' and a.source==copy.uid for a in self.g.legal_actions()))
    def test_mega_windfury_takes_precedence_over_windfury(self):
        self.m.keywords.add('WINDFURY');self.play();self.m.attacks=3
        self.assertTrue(self.attacks())
