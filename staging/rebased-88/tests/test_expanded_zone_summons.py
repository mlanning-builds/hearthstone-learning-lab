import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class ZoneSummonTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('WARLOCK',31),random_deck('MAGE',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
        for p in self.g.players:p.hand=[];p.deck=['CORE_CS2_029']*10;p.mana=p.max_mana=10
    def give(self,cid):
        c=Card(self.g._new_id(),cid);self.p.hand.append(c);return c
    def play(self):
        c=self.give('CORE_SCH_181');self.g.step(Action('play',c.uid,position=len(self.p.board)))
    def test_summons_one_demon_from_each_zone_without_battlecries(self):
        self.give('CORE_EX1_319');self.p.deck=['CORE_LOOT_013','CORE_CS2_029'];health=self.p.health
        self.play();self.assertEqual([m.card_id for m in self.p.minions],['CORE_SCH_181','CORE_EX1_319','CORE_LOOT_013'])
        self.assertEqual(self.p.hand,[]);self.assertEqual(self.p.deck,['CORE_CS2_029']);self.assertEqual(self.p.health,health)
    def test_non_demons_are_not_removed_and_missing_zone_does_not_stop_other(self):
        held=self.give('CORE_CS2_179');self.p.deck=['CORE_EX1_319'];self.play()
        self.assertEqual(self.p.hand,[held]);self.assertEqual(self.p.deck,[])
        self.assertEqual(self.p.minions[-1].card_id,'CORE_EX1_319')
    def test_stat_enchantments_follow_cards_from_both_zones(self):
        hand=self.give('CORE_EX1_319');hand.attack_bonus=2;hand.health_bonus=3
        deck=Card(self.g._new_id(),'CORE_LOOT_013');deck.attack_bonus=4;deck.health_bonus=5;self.p.deck=[deck]
        self.play()
        for entity,card in zip(self.p.minions[1:],(hand,deck)):
            data=self.g.cards[card.card_id]
            self.assertEqual((entity.attack,entity.max_health),(data['attack']+card.attack_bonus,data['health']+card.health_bonus))
    def test_full_board_does_not_remove_cards(self):
        for _ in range(6):self.g._summon(0,'CORE_CS2_179')
        hand=self.give('CORE_EX1_319');self.p.deck=['CORE_LOOT_013'];self.play()
        self.assertEqual(self.p.hand,[hand]);self.assertEqual(self.p.deck,['CORE_LOOT_013'])
    def test_one_remaining_slot_current_hand_priority(self):
        for _ in range(5):self.g._summon(0,'CORE_CS2_179')
        self.give('CORE_EX1_319');self.p.deck=['CORE_LOOT_013'];self.play()
        self.assertEqual(self.p.minions[-1].card_id,'CORE_EX1_319');self.assertEqual(self.p.deck,['CORE_LOOT_013'])
    def test_empty_sources_are_safe(self):
        self.p.deck=[];self.play();self.assertEqual(len(self.p.minions),1)
