import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class CounterCostTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('SHAMAN',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
        for p in self.g.players:p.hand=[];p.deck=['CORE_CS2_029']*10;p.mana=p.max_mana=10
    def give(self,cid):
        c=Card(self.g._new_id(),cid);self.p.hand.append(c);return c
    def test_remnant_counts_both_sides_once(self):
        c=self.give('END_004');base=self.g._cost(c,0)
        for owner in (0,1):self.g._summon(owner,'CORE_EX1_506').health=0
        self.g._settle();self.g._settle()
        self.assertEqual(self.g._cost(c,0),max(0,base-2))
        self.assertEqual([p.minions_died_turn for p in self.g.players],[1,1])
    def test_remnant_battlecry_draws_two(self):
        c=self.give('END_004')
        self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid))
        self.assertEqual(len(self.p.hand),2)
    def test_coyote_counts_hits_not_amount_and_includes_armor(self):
        c=self.give('TIME_047');base=self.g._cost(c,0);self.q.armor=20
        self.g._damage(-2,5);self.g._damage(-2,1)
        self.assertEqual(self.q.health,30);self.assertEqual(self.g._cost(c,0),max(0,base-2))
    def test_coyote_ignores_own_hero_and_zero_damage(self):
        c=self.give('TIME_047');base=self.g._cost(c,0)
        self.g._damage(-1,2);self.g._damage(-2,0)
        self.assertEqual(self.g._cost(c,0),base)
    def test_turn_counters_reset_for_both_players(self):
        for p in self.g.players:p.minions_died_turn=2;p.hero_damage_events_turn=3
        self.g.step(Action('end'))
        self.assertTrue(all(p.minions_died_turn==p.hero_damage_events_turn==0 for p in self.g.players))
    def test_overload_total_updates_on_play_and_persists(self):
        c=self.give('END_030');base=self.g._cost(c,0);spell=self.give('CORE_EX1_238')
        self.g.step(Action('play',spell.uid,-2))
        self.assertEqual(self.p.overloaded_total,1);self.assertEqual(self.g._cost(c,0),base-1)
        self.g.step(Action('end'));self.g.step(Action('end'))
        self.assertEqual(self.p.overloaded_total,1);self.assertEqual(self.p.locked_mana,1)
    def test_overload_counter_is_owner_specific(self):
        c=self.give('END_030');base=self.g._cost(c,0);self.q.overloaded_total=10
        self.assertEqual(self.g._cost(c,0),base)
    def test_counterspell_does_not_add_overload(self):
        self.q.secrets.append(Card(self.g._new_id(),'CORE_EX1_287'))
        spell=self.give('CORE_EX1_238');self.g.step(Action('play',spell.uid,-2))
        self.assertEqual(self.p.overloaded_total,0)
    def test_public_counters_are_copies_not_mutable_state(self):
        view=self.g.observe(1);view['players'][0]['rule_counters']['overloaded_total']=99
        self.assertEqual(self.p.overloaded_total,0)
