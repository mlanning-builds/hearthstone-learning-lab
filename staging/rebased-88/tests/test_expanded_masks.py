import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class MaskTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('WARRIOR',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
        for p in self.g.players:p.hand=[];p.deck=['CORE_CS2_029']*30;p.mana=p.max_mana=10
    def play(self,cid,target):
        c=Card(self.g._new_id(),cid);self.p.hand.append(c)
        self.g.step(Action('play',c.uid,target))
    def test_devil_mask_replaces_buffs_and_grants_immediate_attack(self):
        m=self.g._summon(0,'Core_CS2_200');self.g._buff(m,5,5);m.health-=3
        self.play('DINO_403',m.uid)
        self.assertEqual((m.attack,m.health,m.max_health),(8,8,8))
        self.assertIn('CHARGE',m.keywords)
        self.assertTrue(any(a.kind=='attack' and a.source==m.uid for a in self.g.legal_actions()))
    def test_panther_mask_sets_stats_stealth_and_draws_two(self):
        m=self.g._summon(0,'Core_CS2_200');m.health=1
        self.play('DINO_432',m.uid)
        self.assertEqual((m.attack,m.health,m.max_health),(5,4,4))
        self.assertIn('STEALTH',m.keywords);self.assertEqual(len(self.p.hand),2)
    def test_mark_uses_target_owner(self):
        a=self.g._summon(0,'Core_CS2_200');b=self.g._summon(1,'Core_CS2_200')
        self.play('EDR_252',a.uid);self.play('EDR_252',b.uid)
        self.assertEqual((a.attack,a.health),(3,3));self.assertEqual((b.attack,b.health),(1,1))
    def test_mark_preserves_external_aura_and_silence_restores_identity(self):
        self.g._summon(0,'CORE_CS2_222');m=self.g._summon(0,'Core_CS2_200')
        self.g._refresh_auras();self.play('EDR_252',m.uid)
        self.assertEqual((m.attack,m.health),(4,4))
        self.g._silence(m)
        self.assertEqual((m.attack,m.max_health),(7,8))

    def test_replaced_temporary_attack_does_not_expire_twice(self):
        m=self.g._summon(0,'Core_CS2_200')
        m.attack+=3;m.temporary_attack=3
        self.play('EDR_252',m.uid)
        self.g.step(Action('end'))
        self.assertEqual(m.attack,3)
