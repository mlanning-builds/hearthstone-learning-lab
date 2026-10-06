import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class FreePowerTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('DRUID',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
        for p in self.g.players:p.hand=[];p.deck=['CORE_CS2_029']*10;p.mana=p.max_mana=10
    def play(self):
        c=Card(self.g._new_id(),'EDR_847');self.p.hand.append(c);self.g.step(Action('play',c.uid,position=0));return self.p.minions[0]
    def test_battlecry_free_power_then_normal_cost(self):
        self.play();self.p.mana=0
        self.assertIn(Action('power'),self.g.legal_actions());self.g.step(Action('power'))
        self.assertEqual((self.p.mana,self.p.armor,self.g._power_cost(0)),(0,1,2))
        self.assertEqual(self.p.next_power_cost_effects,[])
    def test_deathrattle_grants_new_free_use(self):
        m=self.play();self.g.step(Action('power'));m.health=0;self.g._settle()
        self.assertEqual(self.g._power_cost(0),0)
        self.assertNotIn(Action('power'),self.g.legal_actions())
        self.g.step(Action('end'));self.g.step(Action('end'));self.p.mana=0
        self.g.step(Action('power'));self.assertEqual(self.g._power_cost(0),2)
    def test_summon_has_no_battlecry_but_has_deathrattle(self):
        m=self.g._summon(0,'EDR_847');self.assertEqual(self.g._power_cost(0),2)
        m.health=0;self.g._settle();self.assertEqual(self.g._power_cost(0),0)
    def test_silence_removes_deathrattle_not_existing_discount(self):
        m=self.play();self.g._silence(m);self.assertEqual(self.g._power_cost(0),0)
        self.g.step(Action('power'));m.health=0;self.g._settle();self.assertEqual(self.g._power_cost(0),2)
    def test_repeated_zero_effects_consumed_together(self):
        m=self.play();m.health=0;self.g._settle();self.assertEqual(len(self.p.next_power_cost_effects),2)
        self.g.step(Action('power'));self.assertEqual(self.g._power_cost(0),2)
    def test_creation_order_provisional_and_public_copy(self):
        ctx=dict(owner=1,source=None,target=0,bonus=0,lifesteal=False)
        self.g._effect(('opponent_next_power_cost',2),ctx);self.play();self.assertEqual(self.g._power_cost(0),0)
        self.g._effect(('opponent_next_power_cost',2),ctx);self.assertEqual(self.g._power_cost(0),2)
        view=self.g.observe(1);view['players'][0]['next_power_cost_effects'].clear()
        self.assertEqual(len(self.p.next_power_cost_effects),3)
        self.g.step(Action('power'));self.assertEqual((self.g._power_cost(0),self.p.next_power_increase),(2,0))
    def test_demon_hunter_base_cost_restored(self):
        self.p.hero_class='DEMONHUNTER';self.play();self.g.step(Action('power'))
        self.assertEqual(self.g._power_cost(0),1)
