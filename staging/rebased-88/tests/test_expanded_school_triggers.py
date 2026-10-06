import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card
from expanded.cards import COLLECTIBLE_IDS

class SchoolTriggerTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('PALADIN',31),random_deck('MAGE',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
        for p in self.g.players:p.hand=[];p.deck=['CORE_CS2_029']*10;p.mana=p.max_mana=10
    def play(self,cid,target=0):
        c=Card(self.g._new_id(),cid);self.p.hand.append(c);self.g.step(Action('play',c.uid,target))
    def test_holy_spell_summons_lifesteal_medic(self):
        self.g._summon(0,'CORE_BAR_878');self.play('CORE_AT_055',-1)
        m=self.p.minions[-1];self.assertEqual((m.card_id,m.attack,m.health),('BAR_878t',2,2))
        self.assertIn('LIFESTEAL',m.keywords);self.assertNotIn('BAR_878t',COLLECTIBLE_IDS)
        self.p.health=20;m.summoned_turn=-1;self.g.step(Action('attack',m.uid,-2));self.assertEqual(self.p.health,22)
    def test_wrong_school_and_owner_do_not_trigger(self):
        self.g._summon(0,'CORE_BAR_878');self.play('TOKEN_COIN')
        self.g._queue_event('spell_cast',owner=1,card_id='CORE_AT_055',cost=1);self.g._settle()
        self.assertEqual(len(self.p.minions),1)
    def test_silence_and_full_board(self):
        m=self.g._summon(0,'CORE_BAR_878');self.g._silence(m);self.play('CORE_AT_055',-1)
        self.assertEqual(len(self.p.minions),1)
        self.p.board=[];self.g._summon(0,'CORE_BAR_878')
        for _ in range(6):self.g._summon(0,'CS3_025')
        self.play('CORE_AT_055',-1);self.assertEqual(len(self.p.minions),7)
    def test_countered_holy_spell_has_no_trigger(self):
        self.g._summon(0,'CORE_BAR_878');self.q.secrets.append(Card(self.g._new_id(),'CORE_EX1_287'))
        self.play('CORE_AT_055',-1);self.assertEqual(len(self.p.minions),1)
    def test_deathchiller_hits_two_distinct_enemies(self):
        self.g._summon(0,'CORE_RLK_083');m=self.g._summon(1,'CS3_025');self.play('TOKEN_COIN')
        self.assertEqual((self.q.health,m.health),(29,5))
    def test_deathchiller_single_enemy_is_hit_only_once(self):
        self.g._summon(0,'CORE_RLK_083');self.play('TOKEN_COIN');self.assertEqual(self.q.health,29)
    def test_deathchiller_silence_and_opponent_spell(self):
        m=self.g._summon(0,'CORE_RLK_083')
        self.g._queue_event('spell_cast',owner=1,card_id='TOKEN_COIN',cost=0);self.g._settle()
        self.assertEqual(self.q.health,30);self.g._silence(m);self.play('TOKEN_COIN');self.assertEqual(self.q.health,30)
