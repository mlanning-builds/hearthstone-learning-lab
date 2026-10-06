import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class HeroDamageTurnTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('WARRIOR',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players;self.p.hand=[];self.p.mana=self.p.max_mana=10
    def play(self):
        c=Card(self.g._new_id(),'END_019');self.p.hand.append(c)
        self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid))
        return next(m for m in self.p.minions if m.card_id=='END_019')
    def stats(self,m,bonus):
        d=self.g.cards['END_019'];self.assertEqual((m.attack,m.health),(d['attack']+bonus,d['health']+bonus))
    def test_existing_missing_health_does_not_count(self):
        self.p.health=20;self.stats(self.play(),0)
    def test_damage_then_healing_still_counts(self):
        self.g._damage(-1,2);self.g._heal(-1,2);self.stats(self.play(),3)
    def test_damage_absorbed_by_armor_counts(self):
        self.p.armor=4;self.g._damage(-1,2);self.stats(self.play(),3)
        self.assertEqual(self.p.health,30)
    def test_other_hero_damage_does_not_count(self):
        self.g._damage(-2,2);self.stats(self.play(),0)
    def test_zero_damage_does_not_count(self):
        self.g._damage(-1,0);self.stats(self.play(),0)
    def test_counter_resets_for_both_players_each_turn(self):
        self.g._damage(-1,2);self.g._damage(-2,3);self.g.step(Action('end'))
        self.assertEqual([p.hero_damage_taken_turn for p in self.g.players],[0,0])
    def test_counter_is_visible_to_policy(self):
        self.g._damage(-1,2)
        self.assertEqual(self.g.observe(0)['players'][0]['rule_counters']['hero_damage_taken_turn'],2)
