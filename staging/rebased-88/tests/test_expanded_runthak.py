import unittest
from unittest.mock import patch
from expanded import Game,Action,random_deck
from expanded.game import Card

class RunthakTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('WARRIOR',31),random_deck('MAGE',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
        for p in self.g.players:p.hand=[];p.deck=['CORE_CS2_029']*10;p.mana=p.max_mana=10
        self.a=self.g._summon(0,'CS3_025');self.b=self.g._summon(1,'CS3_025')
        self.held=Card(self.g._new_id(),'CS3_025');self.p.hand.append(self.held)
    def attack(self):self.g.step(Action('attack',self.a.uid,self.b.uid))
    def test_buff_occurs_before_damage_and_only_for_minions(self):
        spell=Card(self.g._new_id(),'CORE_CS2_029');self.p.hand.append(spell)
        resolve=self.g._resolve_combat
        def checked(*args):
            self.assertEqual((self.held.attack_bonus,self.held.health_bonus),(1,1))
            self.assertEqual(self.a.health,6);self.assertEqual(self.b.health,6)
            return resolve(*args)
        with patch.object(self.g,'_resolve_combat',side_effect=checked):self.attack()
        self.assertEqual((spell.attack_bonus,spell.health_bonus),(0,0))
        self.assertEqual((self.held.attack_bonus,self.held.health_bonus),(1,1))
    def test_lethal_retaliation_does_not_erase_buff(self):
        self.b.attack=10;self.attack();self.assertNotIn(self.a,self.p.board)
        self.assertEqual(self.held.attack_bonus,1)
    def test_silence_suppresses_trigger(self):
        self.g._silence(self.a);self.a.summoned_turn=-1;self.attack()
        self.assertEqual(self.held.attack_bonus,0)
    def test_other_friendly_attack_does_not_trigger(self):
        other=self.g._summon(0,'CORE_CS2_179');other.summoned_turn=-1
        self.g.step(Action('attack',other.uid,self.b.uid));self.assertEqual(self.held.attack_bonus,0)
    def test_rush_cannot_attack_hero_on_summon_turn(self):
        self.assertNotIn(Action('attack',self.a.uid,-2),self.g.legal_actions())
    def test_repeated_attacks_each_buff_once(self):
        self.a.keywords.add('WINDFURY');self.b.health=self.b.max_health=20;self.b.attack=0
        self.attack();self.attack();self.assertEqual(self.held.attack_bonus,2)
    def test_cancelled_attack_has_no_attack_event(self):
        with patch.object(self.g,'_secret_event',return_value=True):self.attack()
        self.assertEqual(self.held.attack_bonus,0);self.assertEqual(self.a.attacks,0)
