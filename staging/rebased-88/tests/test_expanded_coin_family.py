import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card
from expanded.cards import COIN_IDS,COLLECTIBLE_IDS,registry

class CoinFamilyTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('ROGUE',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
        for p in self.g.players:p.hand=[];p.deck=['CORE_CS2_029']*10;p.mana=p.max_mana=10
    def give(self,cid):
        c=Card(self.g._new_id(),cid);self.p.hand.append(c);return c
    def test_all_variants_reviewed_and_not_collectible(self):
        cards=registry();self.assertEqual(len(COIN_IDS),63)
        self.assertFalse(COIN_IDS&COLLECTIBLE_IDS);self.assertTrue(COIN_IDS<=set(cards))
    def test_every_variant_shares_temporary_mana_behavior(self):
        for cid in sorted(COIN_IDS):
            c=self.give(cid);self.p.mana=3
            self.g.step(Action('play',c.uid));self.assertEqual(self.p.mana,4)
            self.assertEqual(self.p.max_mana,10)
    def test_whip_counts_variants_and_floors_cost(self):
        whip=self.give('JAIL_503')
        for cid in ('TOKEN_COIN','GAME_005','AT_COIN','JAIL_COIN1'):self.give(cid)
        self.assertEqual(self.g._cost(whip,0),0)
    def test_unrelated_zero_cost_spell_does_not_count(self):
        whip=self.give('JAIL_503');other=self.give('CORE_CS2_029');other.cost_delta=-10
        self.assertEqual(self.g._cost(other,0),0);self.assertEqual(self.g._cost(whip,0),3)
    def test_playing_coin_changes_discount_and_payment(self):
        whip=self.give('JAIL_503');coin=self.give('GAME_005');self.p.mana=2
        self.assertEqual(self.g._cost(whip,0),2);self.g.step(Action('play',coin.uid))
        self.assertEqual(self.g._cost(whip,0),3);self.g.step(Action('play',whip.uid))
        self.assertEqual(self.p.mana,0)
    def test_weapon_last_charge_draws(self):
        self.g._equip(0,'JAIL_503');self.p.weapon['durability']=1
        self.g.step(Action('attack',-1,-2))
        self.assertIsNone(self.p.weapon);self.assertEqual(len(self.p.hand),1)
