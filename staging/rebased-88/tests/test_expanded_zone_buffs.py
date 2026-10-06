import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class ZoneBuffTests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('WARRIOR',31),random_deck('MAGE',53)],seed=71)
        g.step(Action('mulligan'));g.step(Action('mulligan'))
        for p in g.players:p.hand=[];p.deck=['CORE_CS2_029']*20;p.mana=p.max_mana=10
        return g
    def give(self,g,cid):
        c=Card(g._new_id(),cid);g.players[0].hand.append(c);return c
    def cast(self,g):
        c=self.give(g,'JAIL_387');g.step(Action('play',c.uid))
    def kill_pod(self,g):
        m=g._summon(0,'DINO_421');m.health=0;g._settle()
    def test_rarity_bonus_only_minions_in_own_hand(self):
        g=self.game();normal=self.give(g,'CORE_WON_351');legend=self.give(g,'CS3_025');spell=self.give(g,'CORE_CS2_029')
        enemy=Card(g._new_id(),'CS3_025');g.players[1].hand=[enemy];g.players[0].deck=['CS3_025'];board=g._summon(0,'CS3_025');self.cast(g)
        self.assertEqual((normal.attack_bonus,normal.health_bonus),(1,1))
        self.assertEqual((legend.attack_bonus,legend.health_bonus),(3,2))
        self.assertEqual((spell.attack_bonus,enemy.attack_bonus,board.attack),(0,0,3))
        self.assertEqual(g.players[0].deck,['CS3_025'])
    def test_hand_buff_survives_play_and_silence_removes_it(self):
        g=self.game();c=self.give(g,'CS3_025');self.cast(g)
        g.step(Action('play',c.uid,position=0));m=g.players[0].minions[0]
        self.assertEqual((m.attack,m.health),(6,8));g._silence(m);self.assertEqual((m.attack,m.health),(3,6))
    def test_death_buffs_all_physical_minions_not_spells(self):
        g=self.game();hand=self.give(g,'CORE_WON_351');stored=Card(g._new_id(),'CS3_025',2,1);stored.cost_delta=-1
        g.players[0].deck=['CORE_WON_351','CORE_CS2_029',stored];self.kill_pod(g)
        self.assertEqual((hand.attack_bonus,hand.health_bonus),(3,3))
        self.assertEqual(g.players[0].deck[1],'CORE_CS2_029');self.assertIs(g.players[0].deck[2],stored)
        self.assertEqual((stored.attack_bonus,stored.health_bonus,stored.cost_delta),(5,4,-1))
        c=g._draw(0);self.assertIs(c,stored);g.players[0].mana=10;g.step(Action('play',c.uid,position=0))
        self.assertEqual((g.players[0].minions[0].attack,g.players[0].minions[0].health),(8,10))
    def test_repeated_death_buffs_stack_and_keep_deck_order(self):
        g=self.game();g.players[0].deck=['CORE_WON_351','CS3_025'];self.kill_pod(g);self.kill_pod(g)
        self.assertEqual([c.card_id for c in g.players[0].deck],['CORE_WON_351','CS3_025'])
        self.assertEqual([c.attack_bonus for c in g.players[0].deck],[6,6])
    def test_silenced_death_and_empty_zones(self):
        g=self.game();c=self.give(g,'CS3_025');m=g._summon(0,'DINO_421');g._silence(m);m.health=0;g._settle()
        self.assertEqual(c.attack_bonus,0);g.players[0].hand=[];g.players[0].deck=[];self.kill_pod(g)
        self.assertEqual(g.players[0].hand,[]);self.assertEqual(g.players[0].deck,[])
    def test_counterspell_prevents_hand_buffs(self):
        g=self.game();c=self.give(g,'CS3_025');g.players[1].secrets.append(Card(g._new_id(),'CORE_EX1_287'));self.cast(g)
        self.assertEqual((c.attack_bonus,c.health_bonus),(0,0))
