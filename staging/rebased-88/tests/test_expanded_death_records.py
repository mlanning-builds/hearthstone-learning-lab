import unittest
from expanded import Game,Action,random_deck

class DeathRecordTests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('PALADIN',31),random_deck('MAGE',53)],seed=71)
        g.step(Action('mulligan'));g.step(Action('mulligan'))
        for p in g.players:
            p.hand=[];p.board=[];p.deck=['CORE_CS2_029']*20
        return g
    def test_records_position_and_independent_state(self):
        g=self.game();g._summon(0,'CS2_033');m=g._summon(0,'CORE_WON_351');m.attack=9;m.health=0;g._settle()
        record=g.players[0].death_records[-1]
        self.assertEqual(record['position'],1);self.assertEqual(record['entity'].attack,9)
        m.attack=1;self.assertEqual(record['entity'].attack,9)
        self.assertEqual(g.players[0].death_history[-1],record['card_id'])
    def test_silence_record_does_not_invent_deathrattle(self):
        g=self.game();m=g._summon(0,'CORE_EX1_096');g._silence(m);m.health=0;g._settle()
        record=g.players[0].death_records[-1]
        self.assertTrue(record['entity'].silenced);self.assertEqual(record['operations'],())
    def test_death_effects_preserved_after_resolution(self):
        g=self.game();m=g._summon(0,'CORE_EX1_096');m.health=0;g._settle()
        self.assertEqual(g.players[0].death_records[-1]['operations'],(('draw',1),))
        self.assertEqual(len(g.players[0].hand),1)
    def test_reborn_is_not_a_second_death(self):
        g=self.game();m=g._summon(0,'CS2_033');m.keywords.add('REBORN');m.health=0;g._settle()
        self.assertEqual(len(g.players[0].death_records),1)
        self.assertIn('REBORN',g.players[0].death_records[0]['entity'].keywords)
        self.assertNotIn('REBORN',g.players[0].minions[0].keywords)
    def test_internal_records_not_in_observation(self):
        g=self.game();m=g._summon(0,'CS2_033');m.health=0;g._settle()
        for viewer in (0,1):
            self.assertNotIn('death_records',g.observe(viewer)['players'][0])

    def test_silenced_record_retains_separate_printed_definition(self):
        g=self.game();m=g._summon(0,'CORE_EX1_096');g._silence(m);m.health=0;g._settle()
        record=g.players[0].death_records[-1]
        self.assertEqual(record['operations'],())
        self.assertEqual(record['printed_operations'],(('draw',1),))
    def test_plain_minion_has_no_printed_deathrattle(self):
        g=self.game();self.assertEqual(g._printed_death_operations('CS2_033'),())
    def test_special_case_deathrattles_share_printed_lookup(self):
        g=self.game()
        self.assertEqual(g._printed_death_operations('CORE_EX1_110'),(('death_summon','TOKEN_BAINE',1),))
        self.assertEqual(g._printed_death_operations('CORE_LOOT_413'),(('armor',3),))
