import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class DeckKeywordSummonTests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('PALADIN',31),random_deck('MAGE',53)],seed=71)
        g.step(Action('mulligan'));g.step(Action('mulligan'))
        for p in g.players:p.hand=[];p.deck=['CORE_CS2_029']*20;p.mana=p.max_mana=10
        return g
    def recruiter(self,g):
        c=Card(g._new_id(),'JAIL_516');g.players[0].hand.append(c);g.step(Action('play',c.uid,position=0))
    def test_recruiter_draws_distinct_physical_minions_without_battlecry(self):
        g=self.game();g.players[0].deck=['CORE_EX1_319','CORE_EX1_319','CORE_CS2_029'];self.recruiter(g)
        recruits=g.players[0].minions[1:];self.assertEqual(len(recruits),2)
        self.assertTrue(all('RUSH' in m.keywords for m in recruits));self.assertEqual(g.players[0].health,30)
        self.assertEqual(g.players[0].deck,['CORE_CS2_029'])
    def test_rush_allows_minions_not_hero_immediately(self):
        g=self.game();g.players[0].deck=['CORE_EX1_319'];enemy=g._summon(1,'CS3_025');self.recruiter(g)
        m=g.players[0].minions[-1];self.assertIn(Action('attack',m.uid,enemy.uid),g.legal_actions())
        self.assertNotIn(Action('attack',m.uid,-2),g.legal_actions())
    def test_cost_setting_in_deck_is_respected(self):
        g=self.game();c=Card(g._new_id(),'CS3_025',2,3);g._set_card_cost(c,1);g.players[0].deck=[c];self.recruiter(g)
        m=g.players[0].minions[-1];self.assertEqual((m.card_id,m.attack,m.health),('CS3_025',5,9))
    def test_one_board_slot_leaves_second_card_in_deck(self):
        g=self.game()
        for _ in range(5):g._summon(0,'CS3_025')
        g.players[0].deck=['CORE_EX1_319']*2;self.recruiter(g)
        self.assertEqual(len(g.players[0].board),7);self.assertEqual(g.players[0].deck,['CORE_EX1_319'])
    def test_animancer_summons_beast_in_death_slot_and_grants_lifesteal(self):
        g=self.game();left=g._summon(0,'CS3_025');a=g._summon(0,'DINO_131');right=g._summon(0,'CS3_025')
        g.players[0].deck=['DINO_132','CORE_EX1_319'];g.players[0].health=10
        a.health=0;g._settle();m=g.players[0].minions[1]
        self.assertEqual([x.uid for x in g.players[0].minions],[left.uid,m.uid,right.uid])
        self.assertEqual(m.card_id,'DINO_132');self.assertIn('LIFESTEAL',m.keywords)
        self.assertEqual(g.players[0].deck,['CORE_EX1_319'])
        m.summoned_turn=-1;g.step(Action('attack',m.uid,-2));self.assertEqual(g.players[0].health,16)
    def test_animancer_silence_and_no_beasts(self):
        for silence in (False,True):
            g=self.game();a=g._summon(0,'DINO_131');g.players[0].deck=['DINO_132'] if silence else ['CORE_EX1_319']
            before=list(g.players[0].deck)
            if silence:g._silence(a)
            a.health=0;g._settle();self.assertEqual(g.players[0].minions,[]);self.assertEqual(g.players[0].deck,before)
