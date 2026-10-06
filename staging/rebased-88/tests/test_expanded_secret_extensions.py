import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class SecretExtensions(unittest.TestCase):
    def game(self):
        g=Game([random_deck('WARRIOR',1),random_deck('MAGE',2)],seed=9)
        g.step(Action('mulligan'));g.step(Action('mulligan'));g.current=0
        for p in g.players:p.hand=[];p.board=[];p.secrets=[];p.mana=p.max_mana=10;p.health=30;p.armor=0
        return g
    def play(self,g,cid):
        c=Card(g._new_id(),cid);g.players[0].hand.append(c)
        g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid))
    def test_misdirection_cancels_attack_and_replaces_attacker(self):
        g=self.game();g._place_secret(1,'JAIL_315');m=g._summon(0,'EX1_tk34');m.summoned_turn=-1
        g.step(Action('attack',m.uid,g.hero_id(1)))
        self.assertEqual(g.players[1].health,30);self.assertFalse(g.players[1].secrets)
        n=g.players[0].minions[0];self.assertEqual((n.card_id,n.attack,n.health),('CS2_tk1',1,1))
        self.assertNotEqual(n.uid,m.uid)
    def test_misdirection_ignores_hero_attack(self):
        g=self.game();g._place_secret(1,'JAIL_315');g.players[0].temporary_attack=2
        g.step(Action('attack',g.hero_id(0),g.hero_id(1)))
        self.assertEqual(g.players[1].health,28);self.assertEqual(len(g.players[1].secrets),1)
    def test_runes_spills_excess_from_played_minion(self):
        g=self.game();g._place_secret(1,'CORE_LOOT_101');self.play(g,'EDR_851t')
        self.assertFalse(g.players[0].minions);self.assertEqual(g.players[0].health,25)
    def test_runes_ignores_effect_summons(self):
        g=self.game();g._place_secret(1,'CORE_LOOT_101');g._summon(0,'EDR_851t');g._settle()
        self.assertEqual(len(g.players[1].secrets),1);self.assertEqual(g.players[0].health,30)
    def test_runes_uses_current_health_before_divine_shield(self):
        g=self.game();g._place_secret(1,'CORE_LOOT_101');m=g._summon(0,'EDR_851t');m.keywords.add('DIVINE_SHIELD')
        g._secret_event('after_card',0,source=m.uid)
        self.assertEqual(m.health,1);self.assertNotIn('DIVINE_SHIELD',m.keywords)
        self.assertEqual(g.players[0].health,25)
    def test_runes_spell_damage(self):
        g=self.game();g._summon(1,'CORE_EX1_012');g._place_secret(1,'CORE_LOOT_101')
        self.play(g,'EDR_851t');self.assertEqual(g.players[0].health,24)
    def test_runes_does_not_retarget_removed_source(self):
        g=self.game();g._place_secret(1,'CORE_LOOT_101');m=g._summon(0,'EDR_851t');g.players[0].board.remove(m)
        g._summon(0,'EDR_851t');g._secret_event('after_card',0,source=m.uid)
        self.assertEqual(len(g.players[1].secrets),1)
    def test_both_secrets_can_be_cast_and_hidden(self):
        for cid in ('JAIL_315','CORE_LOOT_101'):
            g=self.game();self.play(g,cid)
            self.assertEqual(g.players[0].secrets[0].card_id,cid)
            self.assertNotIn(cid,str(g.observe(1)))
