import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class FelfireBlazeTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('DEMONHUNTER',31),random_deck('MAGE',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
        for p in self.g.players:p.hand=[];p.deck=['CORE_CS2_029']*10;p.mana=p.max_mana=10
    def play(self,cid,target=0):
        c=Card(self.g._new_id(),cid);self.p.hand.append(c);self.g.step(Action('play',c.uid,target))
    def test_fel_destroys_source_and_hits_only_enemies(self):
        b=self.g._summon(0,'FIR_904');ally=self.g._summon(0,'CS3_025');enemy=self.g._summon(1,'CS3_025')
        self.play('CORE_BT_035')
        self.assertNotIn(b,self.p.minions);self.assertEqual((self.p.health,self.q.health,ally.health,enemy.health),(30,28,6,4))
        self.assertEqual(len(self.p.hand),1)
    def test_wrong_school_and_opponent_do_not_trigger(self):
        b=self.g._summon(0,'FIR_904');self.play('TOKEN_COIN')
        self.g._queue_event('spell_cast',owner=1,card_id='CORE_BT_035',cost=2);self.g._settle()
        self.assertIn(b,self.p.minions);self.assertEqual(self.q.health,30)
    def test_silenced_source_does_not_trigger(self):
        b=self.g._summon(0,'FIR_904');self.g._silence(b);self.play('CORE_BT_035')
        self.assertIn(b,self.p.minions);self.assertEqual(self.q.health,30)
    def test_countered_spell_does_not_trigger(self):
        b=self.g._summon(0,'FIR_904');self.q.secrets.append(Card(self.g._new_id(),'CORE_EX1_287'));self.play('CORE_BT_035')
        self.assertIn(b,self.p.minions);self.assertEqual(self.q.health,30)
    def test_two_sources_each_trigger_once(self):
        self.g._summon(0,'FIR_904');self.g._summon(0,'FIR_904');self.play('CORE_BT_035')
        self.assertEqual(len(self.p.minions),0);self.assertEqual(self.q.health,26)
        self.play('CORE_BT_035');self.assertEqual(self.q.health,26)
    def test_destruction_ignores_shield_and_immune(self):
        b=self.g._summon(0,'FIR_904');b.keywords.update({'DIVINE_SHIELD','IMMUNE'})
        enemy=self.g._summon(1,'CS3_025');enemy.keywords.add('DIVINE_SHIELD');self.play('CORE_BT_035')
        self.assertNotIn(b,self.p.minions);self.assertEqual(enemy.health,6);self.assertNotIn('DIVINE_SHIELD',enemy.keywords)
    def test_spell_that_kills_source_has_no_after_cast_trigger(self):
        b=self.g._summon(0,'FIR_904');self.play('CORE_BT_801',b.uid)
        self.assertNotIn(b,self.p.minions);self.assertEqual(self.q.health,30)
