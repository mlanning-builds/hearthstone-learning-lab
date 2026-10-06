import unittest
from expanded import Game,Action,random_deck

class CopyLifetimeTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('HUNTER',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
    def copy(self,m):
        self.g._system_effect(('copy_self_right',1),dict(owner=0,source=m))
        return self.g.players[0].minions[self.g.players[0].minions.index(m)+1]
    def test_temporary_attack_expires_on_both(self):
        m=self.g._summon(0,'CORE_EX1_506');base=m.attack;m.attack+=3;m.temporary_attack=3
        c=self.copy(m);self.assertEqual(c.attack,base+3)
        self.g.step(Action('end'))
        self.assertEqual((m.attack,c.attack),(base,base))
    def test_permanent_buff_remains_after_temporary_expires(self):
        m=self.g._summon(0,'CORE_EX1_506',attack_bonus=2);base=m.attack;m.attack+=3;m.temporary_attack=3
        c=self.copy(m);self.g.step(Action('end'));self.assertEqual(c.attack,base)
    def test_silenced_aura_copy_cannot_restore_aura(self):
        m=self.g._summon(0,'CORE_CS2_122');other=self.g._summon(0,'CORE_EX1_506')
        self.g._silence(m);base=other.attack;c=self.copy(m)
        self.assertTrue(c.silenced);self.assertEqual(other.attack,base)
    def test_expiring_copy_dies_at_end_of_turn(self):
        m=self.g._summon(0,'CORE_EX1_506',expires=True);c=self.copy(m)
        self.assertTrue(c.expires);self.g.step(Action('end'))
        self.assertNotIn(m,self.g.players[0].minions);self.assertNotIn(c,self.g.players[0].minions)
    def test_silenced_health_aura_copy_cannot_heal_other_minion(self):
        m=self.g._summon(0,'CORE_CS2_222');self.g._silence(m)
        other=self.g._summon(0,'CORE_EX1_506');other.health=1
        before=(other.health,other.max_health);self.copy(m)
        self.assertEqual((other.health,other.max_health),before)
    def test_copy_damage_exists_before_aura_application(self):
        aura=self.g._summon(0,'CORE_CS2_222')
        m=self.g._summon(0,'CORE_EX1_506');m.health-=1
        c=self.copy(m)
        self.assertEqual((c.health,c.max_health),(m.health,m.max_health))
        self.g._silence(aura)
        self.assertEqual((c.health,c.max_health),(m.health,m.max_health))
