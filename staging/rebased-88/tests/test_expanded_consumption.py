import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class ConsumptionTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('DEATHKNIGHT',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
        for p in self.g.players:p.hand=[];p.deck=['CORE_CS2_029']*10;p.mana=p.max_mana=10
    def play(self):
        c=Card(self.g._new_id(),'CORE_CATA_007');self.p.hand.append(c);self.g.step(Action('play',c.uid))
    def test_two_kills_draw_two_and_ignore_heroes(self):
        for _ in range(2):self.g._summon(1,'CORE_WON_351')
        self.play();self.assertEqual((len(self.q.minions),len(self.p.hand),self.q.health),(0,2,30))
    def test_one_target_is_not_hit_twice(self):
        m=self.g._summon(1,'CS3_025');self.play()
        self.assertEqual((m.health,len(self.p.hand)),(3,0))
    def test_empty_board_is_legal_noop(self):
        self.play();self.assertEqual((len(self.p.hand),self.q.health),(0,30))
    def test_shield_prevents_damage_and_draw(self):
        shield=self.g._summon(1,'CORE_WON_351');shield.keywords.add('DIVINE_SHIELD')
        self.g._summon(1,'CORE_WON_351');self.play()
        self.assertEqual((shield.health,len(self.p.hand)),(2,1));self.assertNotIn('DIVINE_SHIELD',shield.keywords)
    def test_spell_damage_applies_to_each_selected_minion(self):
        self.g._summon(0,'CORE_EX1_012')
        for _ in range(2):self.g._summon(1,'CS3_025').health=4
        self.play();self.assertEqual((len(self.q.minions),len(self.p.hand)),(0,2))
    def test_exactly_two_distinct_targets_and_only_enemies(self):
        own=self.g._summon(0,'CS3_025');enemies=[self.g._summon(1,'CS3_025') for _ in range(3)]
        self.play();self.assertEqual(sorted(m.health for m in enemies),[3,3,6]);self.assertEqual(own.health,6)
    def test_reborn_original_death_still_draws_one(self):
        m=self.g._summon(1,'CORE_WON_351');m.keywords.add('REBORN');self.play()
        self.assertEqual((len(self.p.hand),len(self.q.minions)),(1,1));self.assertEqual(self.q.minions[0].health,1)
    def test_fatigue_draws_stop_when_hero_dies(self):
        self.p.deck=[];self.p.health=1
        for _ in range(2):self.g._summon(1,'CORE_WON_351')
        self.play();self.assertTrue(self.g.terminal);self.assertEqual(self.p.fatigue,1)
