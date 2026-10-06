import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card
from expanded.cards import COLLECTIBLE_IDS

class WaterElementalTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('MAGE',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
        for p in self.g.players:p.hand=[];p.deck=['CORE_CS2_029']*10;p.mana=p.max_mana=10
    def water(self,owner=0):
        m=self.g._summon(owner,'CS2_033');m.summoned_turn=-1;return m
    def test_deep_freeze_summons_two_generated_elementals(self):
        c=Card(self.g._new_id(),'CORE_BT_072');self.p.hand.append(c)
        self.g.step(Action('play',c.uid,-2))
        self.assertGreaterEqual(self.q.frozen_until,self.g.turn)
        self.assertEqual([(m.card_id,m.attack,m.health) for m in self.p.minions],[('CS2_033',3,6)]*2)
        self.assertNotIn('CS2_033',COLLECTIBLE_IDS)
    def test_attacking_hero_freezes_even_when_armor_absorbs_damage(self):
        m=self.water();self.q.armor=10;self.g.step(Action('attack',m.uid,-2))
        self.assertEqual(self.q.health,30);self.assertEqual(self.q.armor,7)
        self.assertGreaterEqual(self.q.frozen_until,self.g.turn)
    def test_retaliation_freezes_attacker_even_if_elemental_dies(self):
        m=self.g._summon(0,'CS3_025');m.attack=10
        w=self.water(1);self.g.step(Action('attack',m.uid,w.uid))
        self.assertGreaterEqual(m.frozen_until,self.g.turn);self.assertNotIn(w,self.q.board)
    def test_shield_prevents_freezing(self):
        m=self.water();target=self.g._summon(1,'CS3_025');target.keywords.add('DIVINE_SHIELD')
        self.g.step(Action('attack',m.uid,target.uid));self.assertEqual(target.frozen_until,-1)
    def test_silence_disables_damage_freeze(self):
        m=self.water();self.g._silence(m);self.g.step(Action('attack',m.uid,-2))
        self.assertEqual(self.q.frozen_until,-1)
    def test_effect_damage_from_elemental_uses_same_rule(self):
        m=self.water();self.g._deal_effect(-2,1,dict(owner=0,source=m,bonus=0))
        self.assertGreaterEqual(self.q.frozen_until,self.g.turn)
    def test_prevented_effect_damage_does_not_freeze(self):
        m=self.water();target=self.g._summon(1,'CS3_025');target.keywords.add('IMMUNE')
        self.g._deal_effect(target.uid,1,dict(owner=0,source=m,bonus=0));self.assertEqual(target.frozen_until,-1)
    def test_full_board_still_freezes_target(self):
        for _ in range(7):self.water()
        c=Card(self.g._new_id(),'CORE_BT_072');self.p.hand.append(c);self.g.step(Action('play',c.uid,-2))
        self.assertEqual(len(self.p.board),7);self.assertGreaterEqual(self.q.frozen_until,self.g.turn)
