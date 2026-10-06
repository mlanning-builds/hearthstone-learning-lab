import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class HeroImmunityTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('DEMONHUNTER',31),random_deck('MAGE',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
        for p in self.g.players:p.hand=[];p.deck=['CORE_CS2_029']*10;p.mana=p.max_mana=10
    def give(self,cid,owner=0):
        c=Card(self.g._new_id(),cid);self.g.players[owner].hand.append(c);return c
    def play(self,middle=False):
        self.give('CORE_CS2_029');c=self.give('TIME_021')
        if middle:self.give('CORE_CS2_029')
        self.g.step(Action('play',c.uid,position=0));return self.p.minions[0]
    def test_outcast_only(self):
        self.play(True);self.assertFalse(self.p.hero_immune_expiry_players)
        self.p.mana=10;self.p.hand=[];self.play();self.assertTrue(self.p.hero_immune_expiry_players)
    def test_damage_armor_fatigue_and_bulwark(self):
        self.play();self.p.armor=5;self.g._equip(0,'CORE_BT_781')
        self.assertEqual(self.g._damage(-1,20),0);self.p.deck=[];self.g._draw(0)
        self.assertEqual((self.p.health,self.p.armor,self.p.weapon['durability']),(30,5,4));self.assertEqual(self.p.fatigue,1)
    def test_opponent_cannot_select_hero_but_owner_can(self):
        self.play();self.assertNotIn(-1,self.g._visible_targets(1,True));self.assertIn(-1,self.g._visible_targets(0,True))
        self.g.step(Action('end'));m=self.g._summon(1,'CS3_025');m.summoned_turn=-1
        self.assertNotIn(-1,self.g._attack_targets(m))
        fireball=self.give('CORE_CS2_029',1);self.assertNotIn(Action('play',fireball.uid,-1),self.g.legal_actions())
    def test_persists_through_opponent_turn_then_expires(self):
        self.play();self.g.step(Action('end'));self.assertEqual(self.g._damage(-1,2),0)
        self.g.step(Action('end'));self.assertFalse(self.p.hero_immune_expiry_players);self.assertEqual(self.g._damage(-1,2),2)
    def test_minion_silence_or_death_does_not_remove_player_effect(self):
        m=self.play();self.g._silence(m);m.health=0;self.g._settle();self.assertEqual(self.g._damage(-1,5),0)
    def test_healing_and_armor_gain_remain_possible(self):
        self.p.health=20;self.play();self.assertEqual(self.g._heal(-1,3),3)
        self.g._effect(('armor',2),dict(owner=0,target=0,source=None));self.assertEqual(self.p.armor,2)
    def test_immune_hero_can_attack_without_retaliation_damage(self):
        self.play();self.g._equip(0,'CS2_082');m=self.g._summon(1,'CS3_025')
        self.g.step(Action('attack',-1,m.uid));self.assertEqual(self.p.health,30);self.assertEqual(m.health,5)
    def test_public_state_and_target_features_include_immunity(self):
        from expanded.features import encode_decision,SCHEMA
        import json
        self.play();view=self.g.observe(0);self.assertTrue(view['players'][0]['immune']);self.assertTrue(self.g.observe(1)['players'][0]['immune'])
        actions=view['legal_actions'];rows=encode_decision(dict(actor=0,observation=view,actions=actions))
        self.assertEqual(SCHEMA,'visible-action-features-v58')
        for action,row in zip(actions,rows):
            if action.get('target')==-1:self.assertEqual(row[json.dumps(['target','immune'])],1.0)
