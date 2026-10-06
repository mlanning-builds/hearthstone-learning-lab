import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class KronaTests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('DRUID',31),random_deck('MAGE',53)],seed=71)
        g.step(Action('mulligan'));g.step(Action('mulligan'))
        for p in g.players:p.hand=[];p.deck=['CORE_CS2_029']*7;p.mana=p.max_mana=10
        return g
    def play(self,g):
        p=g.players[0];p.mana=10;c=Card(g._new_id(),'TIME_705');p.hand.append(c)
        g.step(Action('play',c.uid,position=0))
    def test_only_bottom_five_and_owner(self):
        g=self.game();self.play(g)
        self.assertEqual([g._card_stat(c,'cost') for c in g.players[0].deck],[1]*5+[4]*2)
        self.assertEqual(g.players[1].deck,['CORE_CS2_029']*7)
    def test_drawing_preserves_cost_and_payment(self):
        g=self.game();g.players[0].deck=['CORE_CS2_029'];self.play(g);c=g._draw(0)
        self.assertEqual(g._cost(c,0),1);g.players[0].mana=1
        g.step(Action('play',c.uid,-2));self.assertEqual(g.players[0].mana,0)
    def test_empty_short_and_zero_cost_decks(self):
        for deck in ([],['TOKEN_COIN'],['CORE_CS2_029']*3):
            g=self.game();g.players[0].deck=deck;self.play(g)
            self.assertEqual(len(g.players[0].deck),len(deck))
            self.assertTrue(all(g._card_stat(c,'cost')==1 for c in g.players[0].deck))
    def test_physical_cards_keep_identity_and_stats(self):
        g=self.game();c=Card(g._new_id(),'TIME_048',attack_bonus=2,health_bonus=3);c.cost_delta=-2
        g.players[0].deck=[c];self.play(g)
        self.assertIs(g.players[0].deck[0],c)
        self.assertEqual((c.attack_bonus,c.health_bonus,c.cost_delta,c.set_cost),(2,3,0,1))
    def test_later_discount_and_repeated_set(self):
        g=self.game();self.play(g);c=g.players[0].deck[0];c.cost_delta=-1
        self.assertEqual(g._card_stat(c,'cost'),0);self.play(g)
        self.assertEqual(g._card_stat(c,'cost'),1)
    def test_summon_does_not_run_battlecry(self):
        g=self.game();g._summon(0,'TIME_705')
        self.assertEqual(g.players[0].deck,['CORE_CS2_029']*7)
    def test_private_deck_and_visible_drawn_enchantment(self):
        g=self.game();g.players[0].deck=['CORE_CS2_029'];self.play(g);c=g._draw(0)
        own=g.observe(0);other=g.observe(1)
        held=next(h for h in own['players'][0]['hand'] if h['uid']==c.uid)
        self.assertEqual((held['cost'],held['set_cost']),(1,1))
        self.assertNotIn('hand',other['players'][0]);self.assertNotIn('deck',own['players'][0])
