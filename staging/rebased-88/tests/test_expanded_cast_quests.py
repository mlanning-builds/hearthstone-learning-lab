"""Quest placement and history-dependent targeting during automatic casting."""
import unittest
from expanded import Game,Action,random_deck
from engine.game import Card
from expanded.quests import QUESTS
from expanded.secrets import SECRETS

class CastQuestsTests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('MAGE',31),random_deck('ROGUE',53)],seed=71)
        g.step(Action('mulligan'));g.step(Action('mulligan'))
        for p in g.players:
            p.hand=[];p.board=[];p.deck=['CORE_CS2_029']*20;p.health=30;p.mana=p.max_mana=10
            p.quest=None;p.quests_played=0;p.secrets=[]
        return g
    def cast(self,g,cid,physical=None):
        op=('cast_zone_spell','hand',physical.uid,'random') if physical else ('cast_fixed_spell',cid,'random')
        g._start_play_effects([op],dict(owner=0,source=None,target=0,bonus=0,lifesteal=False))
    def secrets(self,g,count):
        g.players[0].secrets=[Card(g._new_id(),cid) for cid in list(SECRETS)[:count]]
    def test_all_existing_quests_can_start_without_paid_play(self):
        for cid in QUESTS:
            with self.subTest(cid=cid):
                g=self.game();self.cast(g,cid);p=g.players[0]
                self.assertEqual(p.quest['card_id'],cid);self.assertEqual(p.quest['progress'],0)
                self.assertEqual(p.quests_played,0);self.assertEqual(p.mana,10)
    def test_five_secrets_reject_quest(self):
        g=self.game();self.secrets(g,5);self.cast(g,'TLC_433')
        self.assertIsNone(g.players[0].quest);self.assertEqual(len(g.players[0].secrets),5)
    def test_four_secrets_allow_quest_but_block_fifth_secret(self):
        g=self.game();self.secrets(g,4);self.cast(g,'TLC_433')
        remaining=list(SECRETS)[4];self.cast(g,remaining)
        self.assertEqual(len(g.players[0].secrets),4);self.assertEqual(g.players[0].quest['card_id'],'TLC_433')
    def test_existing_quest_progress_survives_duplicate_and_other_quest(self):
        g=self.game();self.cast(g,'TLC_433');p=g.players[0];p.quest['progress']=7;old=p.quest
        self.cast(g,'TLC_433');self.cast(g,'TLC_239')
        self.assertIs(p.quest,old);self.assertEqual(p.quest['progress'],7)
    def test_rejected_physical_quest_is_still_consumed(self):
        g=self.game();self.secrets(g,5);c=g._add(0,'TLC_433');self.cast(g,c.card_id,c)
        self.assertNotIn(c,g.players[0].hand);self.assertIsNone(g.players[0].quest)
    def test_corpse_progress_and_reward_after_internal_placement(self):
        g=self.game();self.cast(g,'TLC_433');g.players[0].corpses=15;g._spend_corpses(0,15)
        self.assertIsNone(g.players[0].quest);self.assertEqual(g.players[0].hand[0].card_id,'TLC_433t')
    def test_existing_full_board_progress_is_not_double_counted(self):
        g=self.game()
        for _ in range(7):g._summon(0,'AT_037t')
        self.cast(g,'TLC_239');self.assertEqual(g.players[0].quest['progress'],1)
        g._refresh_auras();self.assertEqual(g.players[0].quest['progress'],1)
    def test_repeated_spell_without_play_history_hits_one_character(self):
        g=self.game();self.cast(g,'CATA_557');self.assertEqual(sum(p.health for p in g.players),57)
        self.cast(g,'CATA_557');self.assertEqual(sum(p.health for p in g.players),54)
        self.assertFalse(g.players[0].played_history)
    def test_repeated_spell_with_play_history_hits_all_enemies(self):
        g=self.game();m=g._summon(1,'CS3_020');before=m.health
        g.players[0].played_history=[dict(card_id='CATA_557',cost=3)]
        self.cast(g,'CATA_557');self.assertEqual(g.players[1].health,27)
        self.assertEqual(m.health,before-3);self.assertEqual(g.players[0].health,30)
    def test_opponent_history_does_not_activate_repeat(self):
        g=self.game();g.players[1].played_history=[dict(card_id='CATA_557',cost=3)]
        self.cast(g,'CATA_557');self.assertEqual(sum(p.health for p in g.players),57)
