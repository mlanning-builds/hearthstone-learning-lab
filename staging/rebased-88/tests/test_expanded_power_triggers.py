import unittest
from expanded import Game,Action,random_deck

class PowerTriggerTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('WARRIOR',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
        for p in self.g.players:p.hand=[];p.deck=['CORE_CS2_029']*30;p.mana=p.max_mana=10
    def test_roach_refreshes_spent_mana_without_refreshing_power(self):
        self.g._summon(0,'END_008');self.g.step(Action('power'))
        self.assertEqual(self.p.mana,10);self.assertTrue(self.p.power_used)
        self.assertFalse(any(a.kind=='power' for a in self.g.legal_actions()))
    def test_multiple_roaches_do_not_unlock_overloaded_crystals(self):
        self.p.locked_mana=3;self.p.mana=7
        self.g._summon(0,'END_008');self.g._summon(0,'END_008')
        self.g.step(Action('power'));self.assertEqual(self.p.mana,7)
    def test_enemy_and_silenced_listeners_do_not_trigger(self):
        a=self.g._summon(0,'EDR_470');b=self.g._summon(1,'EDR_470')
        self.g._silence(a);before=(a.max_health,b.max_health)
        self.g.step(Action('power'));self.assertEqual((a.max_health,b.max_health),before)
    def test_sentinel_health_buff_preserves_existing_damage(self):
        m=self.g._summon(0,'EDR_470');m.health-=1;before=m.max_health
        self.g.step(Action('power'));self.assertEqual((m.max_health,m.health),(before+2,before+1))
    def test_dragonbane_hits_hero_when_no_enemy_minions(self):
        self.g._summon(0,'CORE_DRG_256');self.g.step(Action('power'))
        self.assertEqual(self.q.health,25)
    def test_listener_killed_by_power_does_not_trigger(self):
        self.p.hero_class='MAGE';m=self.g._summon(0,'CORE_DRG_256');m.health=1
        self.g.step(Action('power',target=m.uid));self.assertEqual(self.q.health,30)
    def test_after_use_trigger_runs_before_lethal_sequence_check(self):
        self.p.hero_class='HUNTER';self.q.health=2
        m=self.g._summon(0,'EDR_470');before=m.max_health
        self.g.step(Action('power'))
        self.assertEqual(m.max_health,before+2);self.assertTrue(self.g.terminal)
        self.assertEqual(self.g._power_sequence_depth,0)

    def test_refresh_never_consumes_temporary_mana_above_crystal_cap(self):
        self.p.max_mana=2;self.p.mana=6
        self.g._summon(0,'END_008');self.g.step(Action('power'))
        self.assertEqual(self.p.mana,4)
