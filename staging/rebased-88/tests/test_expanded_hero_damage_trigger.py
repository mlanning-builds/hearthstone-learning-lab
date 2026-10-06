import unittest
from expanded import Game,Action,random_deck

class HeroDamageTriggerTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('WARLOCK',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
        for p in self.g.players:p.hand=[];p.deck=['CORE_CS2_029']*10;p.mana=p.max_mana=10
        self.source=self.g._summon(0,'FIR_955')
    def hurt(self,target=-1,amount=1):
        self.g._damage(target,amount);self.g._settle()
    def test_life_tap_triggers_three_minion_damage(self):
        m=self.g._summon(1,'CS3_025');self.g.step(Action('power'))
        self.assertEqual((self.p.health,m.health,self.q.health),(28,3,30))
    def test_armor_damage_triggers(self):
        self.p.armor=5;m=self.g._summon(1,'CS3_025');self.hurt()
        self.assertEqual((self.p.health,self.p.armor,m.health),(30,4,3))
    def test_enemy_turn_and_other_damage_do_not_trigger(self):
        m=self.g._summon(1,'CS3_025');self.hurt(-2);self.hurt(self.source.uid)
        self.assertEqual(m.health,6);self.g.step(Action('end'));self.hurt()
        self.assertEqual(m.health,6)
    def test_zero_damage_immunity_and_replacement_do_not_trigger(self):
        m=self.g._summon(1,'CS3_025');self.hurt(amount=0)
        self.p.hero_immune_expiry_players.append(0);self.hurt()
        self.p.hero_immune_expiry_players.clear();self.g._equip(0,'CORE_BT_781');self.hurt()
        self.assertEqual(m.health,6)
    def test_silenced_and_new_listeners_do_not_trigger(self):
        m=self.g._summon(1,'CS3_025');self.g._silence(self.source);self.hurt();self.assertEqual(m.health,6)
        self.g._damage(-1,1);self.g._summon(0,'FIR_955');self.g._settle();self.assertEqual(m.health,6)
    def test_empty_enemy_board_does_not_hit_hero(self):
        self.hurt();self.assertEqual(self.q.health,30)
    def test_multiple_damage_events_each_trigger(self):
        m=self.g._summon(1,'Core_CS2_200');self.hurt();self.hurt()
        self.assertEqual(m.health,1)
    def test_fatigue_and_multiple_sources(self):
        self.g._summon(0,'FIR_955');m=self.g._summon(1,'Core_CS2_200');self.p.deck=[]
        self.g._draw(0);self.g._settle();self.assertEqual((self.p.fatigue,m.health),(1,1))
