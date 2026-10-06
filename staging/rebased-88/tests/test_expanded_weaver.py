import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class WeaverTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('PRIEST',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players;self.p.hand=[];self.p.mana=self.p.max_mana=10
        self.card=self.give('EDR_472')
    def give(self,cid):
        c=Card(self.g._new_id(),cid);self.p.hand.append(c);return c
    def actions(self):return [a for a in self.g.legal_actions() if a.kind=='play' and a.source==self.card.uid]
    def test_no_held_spell_has_no_target(self):
        actions=self.actions();self.assertEqual({a.target for a in actions},{0})
        self.g.step(actions[0]);self.assertEqual(self.q.health,30)
    def test_expensive_minion_does_not_activate(self):
        self.give('EDR_471');self.assertEqual({a.target for a in self.actions()},{0})
    def test_qualified_spell_requires_target_and_deals_damage(self):
        self.give('CORE_OG_211');actions=self.actions()
        self.assertNotIn(0,{a.target for a in actions})
        self.g.step(next(a for a in actions if a.target==-2));self.assertEqual(self.q.health,27)
    def test_discount_changes_legal_target_requirement(self):
        c=self.give('CORE_OG_211');c.cost_delta=-4
        self.assertEqual({a.target for a in self.actions()},{0})
    def test_battlecry_ignores_elusive_but_not_enemy_stealth(self):
        self.give('CORE_OG_211')
        elusive=self.g._summon(1,'EDR_471');hidden=self.g._summon(1,'TLC_840')
        targets={a.target for a in self.actions()}
        self.assertIn(elusive.uid,targets);self.assertNotIn(hidden.uid,targets)
    def test_spell_damage_does_not_boost_battlecry(self):
        self.give('CORE_OG_211');self.g._summon(0,'TIME_856')
        self.g.step(next(a for a in self.actions() if a.target==-2));self.assertEqual(self.q.health,27)
