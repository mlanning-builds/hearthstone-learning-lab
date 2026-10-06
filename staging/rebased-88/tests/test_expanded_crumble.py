import json
import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class CrumbleTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('WARRIOR',31),random_deck('MAGE',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players;self.p.hand=[];self.p.mana=self.p.max_mana=10
    def play(self,cid='END_034'):
        c=Card(self.g._new_id(),cid);self.p.hand.append(c)
        self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid))
    def test_destroys_each_enemy_type(self):
        self.g._summon(1,'CORE_EX1_506');self.g._place_location(1,'CORE_REV_990');self.g._equip(1,'EDR_457t')
        self.play();self.assertEqual(self.q.board,[]);self.assertIsNone(self.q.weapon)
    def test_destroys_only_one_of_each_type(self):
        for _ in range(2):self.g._summon(1,'CORE_EX1_506');self.g._place_location(1,'CORE_REV_990')
        self.play();self.assertEqual(len(self.q.minions),1);self.assertEqual(len(self.q.locations),1)
    def test_no_enemies_is_legal(self):
        self.play();self.assertEqual(len(self.p.minions),1)
    def test_friendly_location_and_weapon_untouched(self):
        location=self.g._place_location(0,'CORE_REV_990');self.g._equip(0,'EDR_457t')
        self.play();self.assertIn(location,self.p.board);self.assertIsNotNone(self.p.weapon)
    def test_minion_destruction_triggers_reborn(self):
        m=self.g._summon(1,'CORE_RLK_745');self.play()
        self.assertEqual(len(self.q.minions),1);self.assertNotEqual(self.q.minions[0].uid,m.uid)
        self.assertEqual(self.q.minions[0].health,1)
    def test_existing_top_removal_serializes_modified_deck_card(self):
        c=Card(self.g._new_id(),'CORE_EX1_506');c.attack_bonus=3;self.q.deck=[c]
        self.play('CORE_ICC_407');self.assertEqual(self.q.deck,[])
        json.dumps(self.g.observe(0))
        event=next(e for e in self.g.events if e['event']=='remove_deck_card')
        self.assertEqual(event['card'],'CORE_EX1_506')
