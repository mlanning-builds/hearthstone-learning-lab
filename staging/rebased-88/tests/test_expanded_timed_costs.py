"""User-run regression checks for persistent next-turn card taxes."""
import unittest
from expanded import Game, Action, random_deck
from expanded.game import Card


class TimedCostTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('MAGE',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
        for p in self.g.players:
            p.hand=[];p.deck=['CORE_CS2_029']*10;p.mana=p.max_mana=10

    def give(self,cid,owner=0):
        c=Card(self.g._new_id(),cid);self.g.players[owner].hand.append(c);return c

    def play(self,cid):
        c=self.give(cid);self.g.step(Action('play',c.uid))

    def test_tax_activates_only_next_turn_then_expires(self):
        c=self.give('CORE_CS2_029',1)
        self.play('TIME_716')
        self.assertEqual(self.g._cost(c,1),4)
        self.g.step(Action('end'));self.assertEqual(self.g._cost(c,1),5)
        self.g.step(Action('end'));self.assertEqual(self.g._cost(c,1),4)
        self.assertEqual(self.q.timed_cost_increases,[])

    def test_tax_changes_legality_and_payment_without_being_consumed(self):
        first=self.give('CORE_CS2_029',1);second=self.give('CORE_CS2_029',1)
        self.play('TIME_716');self.g.step(Action('end'));self.q.mana=4
        action=Action('play',first.uid,-1)
        self.assertNotIn(action,self.g.legal_actions())
        self.q.mana=5;self.assertIn(action,self.g.legal_actions())
        self.g.step(action)
        self.assertEqual(self.q.mana,0);self.assertEqual(self.p.health,24)
        self.assertEqual(self.g._cost(second,1),5)

    def test_tax_applies_to_new_cards_and_all_card_types(self):
        self.play('TIME_716');self.g.step(Action('end'))
        for cid in ('Core_CS2_200','CORE_CS2_029','TLC_EVENT_402','CORE_REV_990','TOKEN_COIN'):
            with self.subTest(cid=cid):
                c=self.give(cid,1)
                self.assertEqual(self.g._cost(c,1),self.g.cards[cid]['cost']+1)
        drawn=self.q.hand[0]
        self.assertEqual(self.g._cost(drawn,1),5)

    def test_wave_damages_enemy_minions_and_taxes_only_minions(self):
        own=self.g._summon(0,'Core_CS2_200');enemy=self.g._summon(1,'Core_CS2_200')
        loc=self.g._place_location(1,'CORE_REV_990')
        self.play('TLC_439')
        self.assertEqual((own.health,enemy.health,self.q.health),(7,5,30))
        self.assertEqual(loc.durability,3)
        self.g.step(Action('end'))
        minion=self.give('Core_CS2_200',1);spell=self.give('CORE_CS2_029',1)
        self.assertEqual((self.g._cost(minion,1),self.g._cost(spell,1)),(8,4))

    def test_stacking_taxes_and_existing_discount(self):
        self.play('TIME_716');self.play('TIME_716');self.play('TLC_439')
        self.g.step(Action('end'))
        minion=self.give('Core_CS2_200',1);spell=self.give('CORE_CS2_029',1)
        self.q.cost_effects.append(dict(selector='SPELL',amount=2,expires=self.g.turn))
        self.assertEqual(self.g._cost(minion,1),10)
        self.assertEqual(self.g._cost(spell,1),4)
        self.assertEqual(self.g._cost(self.give('Core_CS2_200'),0),6)

    def test_countered_spell_adds_no_tax(self):
        self.q.secrets.append(Card(self.g._new_id(),'CORE_EX1_287'))
        self.play('TIME_716');self.g.step(Action('end'))
        self.assertEqual(self.q.timed_cost_increases,[])
        self.assertEqual(self.g._cost(self.give('CORE_CS2_029',1),1),4)

    def test_tax_observation_is_public_without_exposing_hand(self):
        hidden=self.give('Core_CS2_200',1);self.play('TIME_716')
        view=self.g.observe(0)
        self.assertNotIn('hand',view['players'][1])
        public=view['players'][1]['timed_cost_increases']
        self.assertEqual(public,self.q.timed_cost_increases)
        self.assertEqual(set(public[0]),{'selector','amount','start','end'})
        public[0]['amount']=999
        self.assertEqual(self.q.timed_cost_increases[0]['amount'],1)

    def test_invalid_tax_play_preserves_state(self):
        c=self.give('TIME_716');self.p.mana=0
        before=self.g.observe(0);rng=self.g.rng.getstate()
        with self.assertRaises(ValueError):self.g.step(Action('play',c.uid))
        self.assertEqual(self.g.observe(0),before)
        self.assertEqual(self.g.rng.getstate(),rng)
        self.assertEqual(self.q.timed_cost_increases,[])
