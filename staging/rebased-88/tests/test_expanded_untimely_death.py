import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class UntimelyDeathTests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('HUNTER',1),random_deck('MAGE',2)],seed=19)
        g.step(Action('mulligan'));g.step(Action('mulligan'));g.current=0;g.turn=4
        for p in g.players:p.hand=[];p.board=[];p.secrets=[];p.deck=['EDR_851t']*5;p.mana=p.max_mana=10
        return g
    def victim(self,g,played=3):
        m=g._summon(1,'EDR_851t');m.played_turn=played;return m
    def kill(self,g,m):m.health=0;g._settle(allow_event_choices=True)
    def test_eligible_death_resummons_clean_identity(self):
        g=self.game();g._place_secret(1,'TIME_620');m=self.victim(g);g._buff(m,5,5);m.keywords.add('TAUNT')
        self.kill(g,m);n=g.players[1].minions[0]
        self.assertEqual((n.card_id,n.attack,n.health),('EDR_851t',1,1));self.assertNotEqual(m.uid,n.uid)
        self.assertNotIn('TAUNT',n.keywords);self.assertEqual(n.played_turn,-1);self.assertFalse(g.players[1].secrets)
    def test_summoned_not_played_does_not_trigger(self):
        g=self.game();g._place_secret(1,'TIME_620');self.kill(g,self.victim(g,-1))
        self.assertEqual(len(g.players[1].secrets),1);self.assertFalse(g.players[1].minions)
    def test_wrong_turn_does_not_trigger(self):
        for played in (2,4):
            g=self.game();g._place_secret(1,'TIME_620');self.kill(g,self.victim(g,played))
            self.assertEqual(len(g.players[1].secrets),1)
    def test_owner_turn_does_not_trigger(self):
        g=self.game();g.current=1;g._place_secret(1,'TIME_620');self.kill(g,self.victim(g))
        self.assertEqual(len(g.players[1].secrets),1)
    def test_one_secret_resummons_only_first_simultaneous_death(self):
        g=self.game();g._place_secret(1,'TIME_620');a=self.victim(g);b=self.victim(g)
        a.health=b.health=0;g._settle(allow_event_choices=True)
        self.assertEqual(len(g.players[1].minions),1);self.assertFalse(g.players[1].secrets)
    def test_reborn_and_secret_are_separate_summons(self):
        g=self.game();g._place_secret(1,'TIME_620');m=self.victim(g);m.keywords.add('REBORN')
        self.kill(g,m);self.assertEqual(len(g.players[1].minions),2)
        self.assertTrue(all(x.card_id=='EDR_851t' for x in g.players[1].minions))
    def test_actual_play_and_opponent_turn_death(self):
        g=self.game();g._place_secret(0,'TIME_620');c=Card(g._new_id(),'EDR_851t');g.players[0].hand.append(c)
        g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid))
        m=g.players[0].minions[0];g.step(Action('end'));self.kill(g,m)
        self.assertEqual(len(g.players[0].minions),1);self.assertFalse(g.players[0].secrets)
