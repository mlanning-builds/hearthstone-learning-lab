"""Leeches transfer Health independently of damage and healing."""
import unittest
from expanded import Game, Action, random_deck
from expanded.game import Card

class LeechTests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('PALADIN',31),random_deck('MAGE',53)],seed=71)
        g.step(Action('mulligan'));g.step(Action('mulligan'))
        for p in g.players:
            p.hand=[];p.board=[];p.deck=['CORE_CS2_029']*25;p.health=30;p.mana=p.max_mana=10;p.armor=0
        return g
    def play(self,g,cid,target=None):
        c=Card(g._new_id(),cid);g.players[g.current].hand.append(c)
        actions=[a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid and (target is None or a.target==target)]
        self.assertTrue(actions);g.step(max(actions,key=lambda a:a.position))
    def test_husk_summons_leeches_and_boosts_while_alive(self):
        g=self.game();self.play(g,'EDR_810');g.step(Action('end'))
        self.assertEqual((g.players[0].health,g.players[0].max_health),(34,34))
        self.assertEqual((g.players[1].health,g.players[1].max_health),(26,26))
    def test_breath_damage_then_leech(self):
        g=self.game();self.play(g,'EDR_814',g.hero_id(1));self.assertEqual(g.players[1].health,28)
        self.assertEqual([m.card_id for m in g.players[0].minions],['EDR_810t'])
    def test_infestation_draws_two_and_summons_two(self):
        g=self.game();self.play(g,'EDR_817');self.assertEqual(len(g.players[0].hand),2)
        self.assertEqual([m.card_id for m in g.players[0].minions],['EDR_810t']*2)
    def test_steal_bypasses_armor_shield_and_immunity(self):
        g=self.game();g._summon(0,'EDR_810t');q=g.players[1];q.armor=10;q.divine_shield=True;q.hero_immune_expiry_players=[1]
        g.step(Action('end'));self.assertEqual(q.health,29);self.assertEqual(q.armor,10);self.assertTrue(q.divine_shield)
    def test_not_healing_or_damage_events(self):
        g=self.game();g._summon(0,'EDR_810t');p=g.players[0];p.health=20;p.permanent_healing_bonus=8;p.healing_block_expiry_players=[1]
        g.step(Action('end'));self.assertEqual((p.health,p.max_health),(21,31))
        self.assertEqual(p.healing_done_turn,0);self.assertFalse(any(e.get('event')=='damage' for e in g.events))
    def test_minion_transfer_and_death_checkpoint(self):
        g=self.game();g._summon(0,'EDR_810t');g._summon(0,'EDR_810t');victim=g._summon(1,'EDR_851t');victim.keywords.add('DIVINE_SHIELD')
        g.step(Action('end'));self.assertFalse(g.players[1].minions);self.assertEqual(g.players[1].health,29)
        self.assertEqual(g.players[0].health,32);self.assertEqual(g.players[1].corpses,1)
    def test_silenced_and_dead_husks_do_not_boost(self):
        for dead in (False,True):
            g=self.game();h=g._summon(0,'EDR_810');g._summon(0,'EDR_810t')
            if dead:h.health=0;g._settle(allow_event_choices=True)
            else:g._silence(h)
            g.step(Action('end'));self.assertEqual(g.players[0].health,31)
    def test_two_husks_stack(self):
        g=self.game();g._summon(0,'EDR_810');g._summon(0,'EDR_810');g._summon(0,'EDR_810t')
        g.step(Action('end'));self.assertEqual(g.players[0].health,33)
    def test_silenced_leech_does_not_steal(self):
        g=self.game();l=g._summon(0,'EDR_810t');g._silence(l);g.step(Action('end'));self.assertEqual(g.players[0].health,30)
    def test_opponent_leech_waits_for_own_end(self):
        g=self.game();g._summon(1,'EDR_810t');g.step(Action('end'));self.assertEqual(g.players[0].health,30)
        g.step(Action('end'));self.assertEqual(g.players[0].health,29);self.assertEqual(g.players[1].health,31)
