import unittest
from expanded import Game,Action,random_deck

class CombatCardTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('WARRIOR',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
    def summon(self,owner,cid):
        m=self.g._summon(owner,cid);m.summoned_turn=-1;return m
    def test_tunneler_attack_deals_extra_two(self):
        m=self.summon(0,'TLC_840');self.g.step(Action('attack',m.uid,-2))
        self.assertEqual(self.q.health,26);self.assertNotIn('STEALTH',m.keywords)
    def test_tunneler_lethal_retaliation_still_triggers(self):
        m=self.summon(0,'TLC_840');e=self.summon(1,'CORE_BT_510')
        e.attack=4;self.g.step(Action('attack',m.uid,e.uid))
        self.assertEqual(self.q.health,28);self.assertNotIn(m,self.p.board)
    def test_brute_hits_all_enemies_when_attacked(self):
        b=self.summon(1,'CORE_BT_510');m=self.summon(0,'TLC_840');other=self.summon(0,'TLC_840')
        self.g.step(Action('attack',m.uid,b.uid))
        self.assertEqual(self.p.health,29);self.assertEqual(other.health,3)
        self.assertNotIn(m,self.p.board)
    def test_brute_trigger_survives_lethal_hit(self):
        b=self.summon(1,'CORE_BT_510');b.health=1
        self.p.temporary_attack=1;self.g.step(Action('attack',-1,b.uid))
        self.assertEqual(self.p.health,26);self.assertNotIn(b,self.q.board)
    def test_brute_does_not_trigger_on_spell_damage(self):
        b=self.summon(1,'CORE_BT_510');self.g._damage(b.uid,1);self.g._settle()
        self.assertEqual(self.p.health,30)
    def test_silenced_brute_does_not_trigger(self):
        b=self.summon(1,'CORE_BT_510');self.g._silence(b)
        self.p.temporary_attack=1;self.g.step(Action('attack',-1,b.uid))
        self.assertEqual(self.p.health,27)
    def test_tortolla_gains_per_damage_event(self):
        m=self.summon(0,'EDR_471')
        for _ in range(2):self.g._damage(m.uid,2);self.g._settle()
        self.assertEqual((m.health,m.attack,self.p.armor),(26,3,2))
    def test_tortolla_shield_prevents_trigger(self):
        m=self.summon(0,'EDR_471');m.keywords.add('DIVINE_SHIELD')
        self.g._damage(m.uid,2);self.g._settle()
        self.assertEqual((m.health,m.attack,self.p.armor),(30,1,0))
    def test_tortolla_silence_removes_trigger(self):
        m=self.summon(0,'EDR_471');self.g._silence(m)
        self.g._damage(m.uid,2);self.g._settle()
        self.assertEqual((m.attack,self.p.armor),(1,0))
