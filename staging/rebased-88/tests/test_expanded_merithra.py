import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class MerithraTests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('SHAMAN',31),random_deck('MAGE',53)],seed=71)
        g.step(Action('mulligan'));g.step(Action('mulligan'))
        for p in g.players:p.hand=[];p.deck=['CORE_CS2_029']*20;p.mana=p.max_mana=10
        return g
    def play(self,g):
        c=Card(g._new_id(),'EDR_238');g.players[0].hand.append(c);g.step(Action('play',c.uid,position=0))
    def test_distinct_eight_plus_friendly_only(self):
        g=self.game();g.players[0].death_history=['DINO_132','DINO_132','DINO_421','CS3_025'];g.players[1].death_history=['TIME_705'];self.play(g)
        self.assertCountEqual([m.card_id for m in g.players[0].minions],['EDR_238','DINO_132','DINO_421'])
    def test_fresh_stats_after_real_buffed_death(self):
        g=self.game();m=g._summon(0,'DINO_132');g._buff(m,4,4);m.keywords.add('RUSH');g._freeze(m.uid);m.health=0;g._settle();self.play(g)
        resurrected=g.players[0].minions[-1];self.assertEqual((resurrected.attack,resurrected.health),(6,12))
        self.assertNotIn('RUSH',resurrected.keywords);self.assertEqual(resurrected.frozen_until,-1)
    def test_board_capacity_and_history_not_consumed(self):
        g=self.game()
        for _ in range(5):g._summon(0,'CS3_025')
        g.players[0].death_history=['DINO_132','DINO_421'];before=list(g.players[0].death_history);self.play(g)
        self.assertEqual(len(g.players[0].minions),7);self.assertEqual(g.players[0].death_history,before)
    def test_empty_history_and_summon_do_not_resurrect(self):
        g=self.game();self.play(g);self.assertEqual(len(g.players[0].minions),1)
        g=self.game();g.players[0].death_history=['DINO_132'];g._summon(0,'EDR_238');self.assertEqual(len(g.players[0].minions),1)
    def test_copy_aliases_share_one_identity(self):
        g=self.game();g.cards['TEST_COPY']=dict(g.cards['DINO_132'],id='TEST_COPY',countAsCopyOfDbfId=g.cards['DINO_132']['dbfId'])
        g.players[0].death_history=['DINO_132','TEST_COPY'];self.play(g)
        self.assertEqual(len(g.players[0].minions),2)
