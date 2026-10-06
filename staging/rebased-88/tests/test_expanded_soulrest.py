import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class SoulrestTests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('DEATHKNIGHT',31),random_deck('MAGE',53)],seed=71)
        g.step(Action('mulligan'));g.step(Action('mulligan'))
        for p in g.players:p.hand=[];p.deck=['CORE_CS2_029']*20;p.mana=p.max_mana=10
        return g
    def cast(self,g):
        c=Card(g._new_id(),'DINO_417');g.players[0].hand.append(c);g.step(Action('play',c.uid))
    def test_rush_attack_then_end_turn_destruction(self):
        g=self.game();m=g._summon(0,'CORE_EX1_319');enemy=g._summon(1,'DINO_132');self.cast(g)
        self.assertEqual(m.attack,4);self.assertIn(Action('attack',m.uid,enemy.uid),g.legal_actions())
        self.assertNotIn(Action('attack',m.uid,-2),g.legal_actions());g.step(Action('end'))
        self.assertNotIn(m,g.players[0].minions);self.assertIn(enemy,g.players[1].minions)
    def test_later_summons_are_not_marked(self):
        g=self.game();early=g._summon(0,'CORE_EX1_319');self.cast(g);late=g._summon(0,'CORE_EX1_319')
        g.step(Action('end'));self.assertEqual(g.players[0].minions,[late]);self.assertFalse(late.expires)
    def test_silence_removes_buff_rush_and_expiry(self):
        g=self.game();m=g._summon(0,'CORE_EX1_319');self.cast(g);g._silence(m);g.step(Action('end'))
        self.assertIn(m,g.players[0].minions);self.assertEqual(m.attack,3);self.assertNotIn('RUSH',m.keywords)
    def test_destruction_bypasses_shield_and_immune(self):
        g=self.game();m=g._summon(0,'CORE_EX1_319');m.keywords.update(('DIVINE_SHIELD','IMMUNE'));self.cast(g);g.step(Action('end'))
        self.assertNotIn(m,g.players[0].minions)
    def test_deathrattle_resolves_and_corpse_is_gained(self):
        g=self.game();m=g._summon(0,'DINO_131');g.players[0].deck=['DINO_132'];before=g.players[0].corpses;self.cast(g);g.step(Action('end'))
        self.assertEqual([m.card_id for m in g.players[0].minions],['DINO_132'])
        self.assertEqual(g.players[0].corpses,before+1)
    def test_counterspell_prevents_all_parts(self):
        g=self.game();m=g._summon(0,'CORE_EX1_319');g.players[1].secrets.append(Card(g._new_id(),'CORE_EX1_287'));self.cast(g)
        self.assertEqual(m.attack,3);self.assertFalse(m.expires);self.assertNotIn('RUSH',m.keywords)
