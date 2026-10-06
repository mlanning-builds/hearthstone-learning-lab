import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class HandAdjacencyCostTests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('MAGE',31),random_deck('MAGE',53)],seed=71)
        g.step(Action('mulligan'));g.step(Action('mulligan'))
        for p in g.players:
            p.hand=[];p.board=[];p.deck=['CORE_CS2_029']*20;p.mana=p.max_mana=10
        return g
    def hand(self,g,*ids):return [g._add(0,cid) for cid in ids]
    def play(self,g,c):g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid))
    def test_saboteur_adds_to_opponent(self):
        g=self.game();c=g._add(0,'CATA_186');self.play(g,c)
        self.assertEqual([c.card_id for c in g.players[1].hand],['CATA_186t']);self.assertFalse(g.players[0].hand)
    def test_both_neighbors_only(self):
        g=self.game();a,b,c,d=self.hand(g,'TOKEN_COIN','TOKEN_COIN','CATA_186t','TOKEN_COIN')
        self.assertEqual([g._cost(x,0) for x in (a,b,c,d)],[0,1,2,1])
    def test_two_sabotages_stack_on_middle(self):
        g=self.game();a,b,c=self.hand(g,'CATA_186t','TOKEN_COIN','CATA_186t');self.assertEqual(g._cost(b,0),2)
    def test_sabotages_tax_each_other(self):
        g=self.game();a,b=self.hand(g,'CATA_186t','CATA_186t');self.assertEqual((g._cost(a,0),g._cost(b,0)),(3,3))
    def test_playing_sabotage_removes_tax(self):
        g=self.game();a,b=self.hand(g,'CATA_186t','TOKEN_COIN');self.play(g,a)
        self.assertEqual(g.players[0].mana,8);self.assertEqual(g._cost(b,0),0);self.assertEqual(getattr(b,'cost_delta',0),0)
    def test_neighbor_removal_changes_adjacency(self):
        g=self.game();a,b,c=self.hand(g,'CATA_186t','TOKEN_COIN','TOKEN_COIN')
        self.assertEqual(g._cost(c,0),0);self.play(g,b);self.assertEqual(g._cost(c,0),1)
    def test_token_burn_at_full_opponent_hand(self):
        g=self.game()
        for _ in range(10):g._add(1,'TOKEN_COIN')
        self.play(g,g._add(0,'CATA_186'));self.assertEqual(len(g.players[1].hand),10)
        self.assertNotIn('CATA_186t',[c.card_id for c in g.players[1].hand])
    def test_cost_cap_does_not_reduce_other_expensive_cards(self):
        g=self.game();a,b=self.hand(g,'CATA_186t','CORE_CS2_029')
        b.set_cost=10;self.assertEqual(g._cost(b,0),10)
        b.set_cost=12;self.assertEqual(g._cost(b,0),12)
    def test_unrelated_tax_still_exceeds_ten(self):
        g=self.game();a,b=self.hand(g,'CATA_186t','CORE_CS2_029');b.set_cost=10
        g.players[0].timed_cost_increases=[dict(selector='SPELL',amount=1,start=g.turn,end=g.turn+1)]
        self.assertEqual(g._cost(b,0),11)
    def test_cost_used_by_legality_and_payment(self):
        g=self.game();a,b=self.hand(g,'CATA_186t','TOKEN_COIN');g.players[0].mana=0
        self.assertFalse(any(x.kind=='play' and x.source==b.uid for x in g.legal_actions()))
        g.players[0].mana=1;self.play(g,b);self.assertEqual(g.players[0].mana,1)
    def test_copied_card_does_not_keep_adjacency_tax(self):
        g=self.game();a,b=self.hand(g,'CATA_186t','TOKEN_COIN');copy=g._clone_hand_card(1,b,source_owner=0)
        self.assertEqual(g._cost(copy,1),0)
    def test_spell_counter_still_removes_sabotage_from_hand(self):
        g=self.game();a,b=self.hand(g,'CATA_186t','TOKEN_COIN');g.players[1].secrets.append(Card(g._new_id(),'CORE_EX1_287'));self.play(g,a)
        self.assertEqual(g._cost(b,0),0);self.assertEqual(g.players[0].mana,8)

if __name__=='__main__':unittest.main()
