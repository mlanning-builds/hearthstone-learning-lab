import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class ImmuneTargetingTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('MAGE',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
        for p in self.g.players:p.hand=[];p.mana=p.max_mana=10
        self.target=self.g._summon(1,'CORE_EX1_506');self.target.keywords.update({'IMMUNE','TAUNT'})
    def test_immune_taunt_is_not_attackable_and_does_not_block_hero(self):
        m=self.g._summon(0,'CORE_EX1_506');m.summoned_turn=-1
        targets=self.g._attack_targets(m)
        self.assertNotIn(self.target.uid,targets);self.assertIn(-2,targets)
    def test_other_taunt_still_blocks_hero(self):
        other=self.g._summon(1,'CORE_EX1_506');other.keywords.add('TAUNT')
        self.assertEqual(self.g._attack_targets(),[other.uid])
    def test_enemy_spell_power_and_battlecry_targets_exclude_immune(self):
        self.assertNotIn(self.target.uid,self.g._targets_for('CORE_CS2_029',0))
        self.assertNotIn(self.target.uid,self.g._visible_targets(0,magic=False))
        self.assertFalse(any(a.kind=='power' and a.target==self.target.uid for a in self.g.legal_actions()))
    def test_owner_can_select_immune_minion(self):
        self.assertIn(self.target.uid,self.g._visible_targets(1,magic=True))
        self.assertIn(self.target.uid,self.g._visible_targets(1,magic=False))
    def test_untargeted_damage_prevented_but_destruction_still_works(self):
        health=self.target.health
        self.g._effect(('area_damage','enemy_minions',10),dict(owner=0,source=None,target=0,bonus=0,lifesteal=False))
        self.assertEqual(self.target.health,health)
        self.g._effect(('destroy_random_enemy',),dict(owner=0,source=None,target=0,bonus=0,lifesteal=False))
        self.g._settle();self.assertNotIn(self.target,self.q.board)
    def test_illegal_direct_attack_does_not_spend_attack(self):
        m=self.g._summon(0,'CORE_EX1_506');m.summoned_turn=-1
        with self.assertRaises(ValueError):self.g.step(Action('attack',m.uid,self.target.uid))
        self.assertEqual(self.g._find(m.uid).attacks,0)
    def test_losing_immune_restores_taunt(self):
        self.target.keywords.remove('IMMUNE')
        self.assertEqual(self.g._attack_targets(),[self.target.uid])
