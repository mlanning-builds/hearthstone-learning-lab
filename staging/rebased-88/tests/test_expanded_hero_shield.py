import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class HeroShieldTests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('PALADIN',31),random_deck('MAGE',53)],seed=71)
        g.step(Action('mulligan'));g.step(Action('mulligan'))
        for p in g.players:
            p.hand=[];p.board=[];p.deck=['CORE_CS2_029']*20;p.health=20;p.mana=p.max_mana=10
        return g
    def test_protector_heals_and_shields(self):
        g=self.game();c=Card(g._new_id(),'TIME_015');g.players[0].hand.append(c)
        g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid))
        self.assertEqual(g.players[0].health,23);self.assertTrue(g.players[0].divine_shield)
        self.assertIn('DIVINE_SHIELD',g.players[0].minions[0].keywords)
    def test_damage_consumes_shield_before_armor(self):
        g=self.game();p=g.players[0];p.divine_shield=True;p.armor=4
        self.assertEqual(g._damage(g.hero_id(0),9),0)
        self.assertFalse(p.divine_shield);self.assertEqual((p.health,p.armor),(20,4))
        g._damage(g.hero_id(0),9);self.assertEqual((p.health,p.armor),(15,0))
    def test_zero_damage_keeps_shield(self):
        g=self.game();g.players[0].divine_shield=True
        g._damage(g.hero_id(0),0);self.assertTrue(g.players[0].divine_shield)
    def test_prevented_damage_does_not_lifesteal(self):
        g=self.game();g.players[1].divine_shield=True
        g._deal_effect(g.hero_id(1),5,dict(owner=0,source=None,lifesteal=True))
        self.assertEqual(g.players[0].health,20)
    def test_cumulus_grants_at_owner_end(self):
        g=self.game();m=g._summon(0,'EDR_942');g.step(Action('end'))
        self.assertTrue(g.players[0].divine_shield)
        g._damage(g.hero_id(0),1);g.step(Action('end'))
        self.assertFalse(g.players[0].divine_shield)
        g._silence(m);g.step(Action('end'));self.assertFalse(g.players[0].divine_shield)
    def test_public_to_both_players(self):
        g=self.game();g.players[0].divine_shield=True
        for viewer in (0,1):self.assertTrue(g.observe(viewer)['players'][0]['divine_shield'])
