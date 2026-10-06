import unittest
from expanded import Game,Action,random_deck

class HealingOwnerTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('PRIEST',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players;self.p.mana=self.p.max_mana=10
    def test_heal_enemy_counts_for_healer(self):
        self.q.health=25;self.g.step(Action('power',target=-2))
        self.assertEqual((self.p.healing_done_turn,self.q.healing_done_turn),(2,0))
    def test_full_health_heal_does_not_count(self):
        self.g.step(Action('power',target=-1));self.assertEqual(self.p.healing_done_turn,0)
    def test_overhealing_counts_only_restored_amount(self):
        self.p.health=29;self.g.step(Action('power',target=-1));self.assertEqual(self.p.healing_done_turn,1)
    def test_defender_lifesteal_is_attributed_to_defender(self):
        m=self.g._summon(0,'CORE_BT_510');m.summoned_turn=-1
        enemy=self.g._summon(1,'CORE_BT_510');enemy.keywords.add('LIFESTEAL');self.q.health=20
        self.g.step(Action('attack',m.uid,enemy.uid))
        # Three combat damage plus one each to the enemy hero and minion from its trigger.
        self.assertEqual(self.q.healing_done_turn,5);self.assertEqual(self.p.healing_done_turn,0)
    def test_turn_boundary_resets_healing(self):
        self.p.health=25;self.g.step(Action('power',target=-1));self.g.step(Action('end'))
        self.assertEqual([p.healing_done_turn for p in self.g.players],[0,0])
    def test_counter_exposed_to_policy(self):
        self.p.health=25;self.g.step(Action('power',target=-1))
        self.assertEqual(self.g.observe(0)['players'][0]['rule_counters']['healing_done_turn'],2)
