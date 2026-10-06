import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class ResourceSummonTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('WARRIOR',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
        for p in self.g.players:p.hand=[];p.deck=['CORE_CS2_029']*30;p.mana=p.max_mana=10
    def play(self,cid):
        c=Card(self.g._new_id(),cid);self.p.hand.append(c);self.g.step(Action('play',c.uid))
    def test_mossbinding_spends_only_mana_remaining_after_payment(self):
        old=self.g._summon(0,'CATA_135t');self.play('CATA_135')
        self.assertEqual(self.p.mana,0);self.assertEqual(self.p.max_mana,10)
        self.assertEqual((old.attack,old.health),(1,2))
        self.assertEqual([(m.attack,m.health) for m in self.p.minions[1:]],[(9,10),(9,10)])
    def test_mossbinding_with_no_extra_mana_summons_base_stats(self):
        self.p.mana=2;self.play('CATA_135')
        self.assertEqual([(m.attack,m.health) for m in self.p.minions],[(1,2),(1,2)])
    def test_mossbinding_buffs_only_available_summon(self):
        for _ in range(6):self.g._summon(0,'Core_CS2_200')
        self.p.mana=4;self.play('CATA_135')
        self.assertEqual(len(self.p.board),7)
        self.assertEqual((self.p.minions[-1].attack,self.p.minions[-1].health),(3,4))
    def test_chow_down_spends_eight_once_and_grants_rush_only_to_new_drakes(self):
        old=self.g._summon(0,'CATA_465t');self.p.corpses=10;self.play('CATA_465')
        self.assertEqual(self.p.corpses,2);self.assertEqual(len(self.p.minions),6)
        self.assertNotIn('RUSH',old.keywords)
        self.assertTrue(all('RUSH' in m.keywords for m in self.p.minions[1:]))
    def test_chow_down_insufficient_corpses_preserves_resource(self):
        self.p.corpses=7;self.play('CATA_465')
        self.assertEqual(self.p.corpses,7);self.assertEqual(len(self.p.minions),5)
        self.assertTrue(all('RUSH' not in m.keywords for m in self.p.minions))
