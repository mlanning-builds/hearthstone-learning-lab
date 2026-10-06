import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class TichondriusTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('DEMONHUNTER',31),random_deck('MAGE',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
        for p in self.g.players:p.hand=[];p.deck=['CORE_CS2_029']*10;p.mana=p.max_mana=10
    def give(self,cid):
        c=Card(self.g._new_id(),cid);self.p.hand.append(c);return c
    def play(self,cid):
        c=self.give(cid);self.g.step(Action('play',c.uid,position=len(self.p.board)));return self.p.board[-1]
    def test_aura_works_on_summon_without_battlecry(self):
        self.g._summon(0,'CORE_CATA_001');self.assertTrue(self.g._hero_immune(0));self.assertFalse(self.g._hero_immune(1))
        self.assertEqual(self.p.cost_effects,[]);self.assertEqual(self.g._damage(-1,9),0)
        self.assertNotIn(-1,self.g._visible_targets(1));self.assertTrue(self.g.observe(1)['players'][0]['immune'])
    def test_silence_and_last_source_removal_end_aura(self):
        a=self.g._summon(0,'CORE_CATA_001');b=self.g._summon(0,'CORE_CATA_001')
        self.g._silence(a);self.assertTrue(self.g._hero_immune(0))
        b.health=0;self.g._settle();self.assertFalse(self.g._hero_immune(0));self.assertEqual(self.g._damage(-1,2),2)
    def test_timed_immunity_remains_after_aura_removed(self):
        m=self.g._summon(0,'CORE_CATA_001');self.p.hero_immune_expiry_players=[0]
        self.g._silence(m);self.assertTrue(self.g._hero_immune(0))
    def test_next_demon_is_free_and_consumes_effect(self):
        self.play('CORE_CATA_001');c=self.give('CORE_EX1_310');other=self.give('CORE_EX1_319')
        self.assertEqual(self.g._cost(c,0),0);self.assertEqual(self.g._cost(other,0),0)
        self.g.step(Action('play',other.uid,position=len(self.p.board)))
        self.assertEqual(self.p.mana,1);self.assertEqual(self.g._cost(c,0),5);self.assertEqual(self.p.cost_effects,[])
    def test_non_demon_does_not_consume_and_effect_expires(self):
        self.play('CORE_CATA_001');coin=self.give('TOKEN_COIN');self.g.step(Action('play',coin.uid))
        self.assertTrue(self.p.cost_effects);self.g.step(Action('end'));self.assertEqual(self.p.cost_effects,[])
    def test_zero_cost_set_handles_prior_card_modifier(self):
        self.play('CORE_CATA_001');c=self.give('CORE_EX1_310');c.cost_delta=40
        self.assertEqual(self.g._cost(c,0),0)
    def test_battlecry_effect_survives_source_silence(self):
        m=self.play('CORE_CATA_001');self.g._silence(m);c=self.give('CORE_EX1_310')
        self.assertFalse(self.g._hero_immune(0));self.assertEqual(self.g._cost(c,0),0)
