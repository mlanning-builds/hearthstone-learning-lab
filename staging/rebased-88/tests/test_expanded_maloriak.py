import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class MaloriakTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('WARLOCK',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
        for p in self.g.players:p.hand=[];p.deck=[];p.mana=p.max_mana=10
        self.m=self.g._summon(0,'CATA_494')
    def give(self,cid,owner=0):
        c=Card(self.g._new_id(),cid);self.g.players[owner].hand.append(c);return c
    def discard(self,cid,owner=0):
        c=self.give(cid,owner);self.g._discard_card(owner,c);self.g._settle();return c
    def test_only_friendly_minions_trigger(self):
        self.discard('CORE_CS2_029');self.discard('CORE_EX1_506',1)
        self.assertEqual(len(self.p.minions),1)
        self.discard('CORE_EX1_506');self.assertEqual(len(self.p.minions),2)
    def test_summon_skips_battlecry_and_does_not_count_as_death(self):
        self.give('CORE_CS2_029');self.discard('CATA_490')
        self.assertEqual(len(self.p.hand),1);self.assertIsNone(self.g.pending_choice)
        self.assertEqual(self.p.death_history,[]);self.assertEqual(self.p.corpses,0)
    def test_hand_buffs_stripped_per_general_graveyard_rule(self):
        c=self.give('CORE_EX1_506');c.attack_bonus=8;c.health_bonus=8
        self.g._discard_card(0,c);self.g._settle();m=self.p.minions[-1];d=self.g.cards[c.card_id]
        self.assertEqual((m.attack,m.health),(d['attack'],d['health']))
    def test_discarded_duke_gets_current_dynamic_bonus(self):
        self.discard('CATA_493');m=self.p.minions[-1]
        self.assertEqual((m.attack,m.health),(4,4))
    def test_silence_and_full_board_prevent_summons(self):
        self.g._silence(self.m);self.discard('CORE_EX1_506');self.assertEqual(len(self.p.minions),1)
        self.g._summon(0,'CATA_494')
        while len(self.p.board)<7:self.g._summon(0,'CORE_EX1_506')
        self.discard('CORE_EX1_506');self.assertEqual(len(self.p.board),7)
    def test_discarded_maloriak_not_listener_for_same_batch(self):
        self.give('CATA_494');self.give('CORE_EX1_506')
        self.g._discard_random(0,2);self.g._settle()
        self.assertEqual(len(self.p.minions),3)
        self.assertEqual(sum(m.card_id=='CORE_EX1_506' for m in self.p.minions),1)
    def test_multiple_existing_listeners_each_summon(self):
        self.g._summon(0,'CATA_494');self.discard('CORE_EX1_506')
        self.assertEqual(sum(m.card_id=='CORE_EX1_506' for m in self.p.minions),2)
