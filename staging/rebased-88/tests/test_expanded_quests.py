"""Quest setup, event progress, physical rewards and location death closure."""
import copy
import unittest
from expanded import Game, Action, random_deck
from expanded.game import Card
from expanded.features import SCHEMA, encode_decision

class QuestTests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('DRUID',1),random_deck('HUNTER',2)],seed=83)
        g.step(Action('mulligan'));g.step(Action('mulligan'));g.current=0
        for p in g.players:
            p.hand=[];p.board=[];p.deck=['CORE_CS2_029']*20
            p.mana=p.max_mana=10;p.health=30;p.armor=0;p.quest=None;p.quests_played=0
        return g
    def play(self,g,cid,target=0):
        c=g._enter_hand(0,Card(g._new_id(),cid));g.players[0].mana=10
        g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid and a.target==target))
    def start(self,g,cid='TLC_433'):self.play(g,cid)
    def fill(self,g):
        while len(g.players[0].board)<7:g._summon(0,'EDR_851t')
    def test_opening_quest_replaces_slot_and_keeps_origin(self):
        from expanded.decks import Deck
        for hero,cid in [('DRUID','TLC_239'),('DEATHKNIGHT','TLC_433')]:
            deck=random_deck(hero,13);cards=list(deck.cards)
            if cid not in cards:cards[0]=cid
            deck=Deck(hero,tuple(cards),deck.runes)
            for first in (0,1):
                g=Game([deck,random_deck('HUNTER',2)],first_player=first,seed=8)
                p=g.players[0];quest=next(c for c in p.hand if c.card_id==cid)
                self.assertEqual(len(p.hand),3 if first==0 else 4)
                self.assertEqual(len(p.deck),27 if first==0 else 26)
                self.assertTrue(g._started_in_deck(quest,0));self.assertIsNone(p.quest)
    def test_mulligan_can_return_quest(self):
        g=self.game();p=g.players[0];p.hand=[];self.start(g);p.quest=None
        c=g._enter_hand(0,Card(g._new_id(),'TLC_433'));g.phase='mulligan';g.mulligan_done=set()
        g.step(Action('mulligan',choices=(c.uid,)))
        self.assertNotIn(c,p.hand);self.assertIn(c,p.deck)
    def test_inactive_does_not_count_previous_spending(self):
        g=self.game();p=g.players[0];p.corpses=20;g._spend_corpses(0,5);self.start(g)
        self.assertEqual(p.quest['progress'],0)
    def test_spending_accumulates_and_completes_once(self):
        g=self.game();self.start(g);p=g.players[0];p.corpses=30
        g._spend_corpses(0,7);self.assertEqual(p.quest['progress'],7)
        g._spend_corpses(0,9);self.assertIsNone(p.quest)
        g._spend_corpses(0,1);self.assertEqual([c.card_id for c in p.hand],['TLC_433t'])
    def test_gain_does_not_advance(self):
        g=self.game();self.start(g);g.players[0].corpses+=20;g._settle()
        self.assertEqual(g.players[0].quest['progress'],0)
    def test_enemy_spending_does_not_advance(self):
        g=self.game();self.start(g);g.players[1].corpses=20;g._spend_corpses(1,15)
        self.assertEqual(g.players[0].quest['progress'],0)
    def test_progress_with_recording_off(self):
        g=self.game();self.start(g);g.record=False;g.players[0].corpses=15;g._spend_corpses(0,15)
        self.assertIsNone(g.players[0].quest);self.assertEqual(g.players[0].hand[0].card_id,'TLC_433t')
    def test_full_hand_retains_completed_quest_until_reward_fits(self):
        g=self.game();self.start(g);p=g.players[0]
        for _ in range(10):g._add(0,'CORE_CS2_029')
        p.corpses=15;g._spend_corpses(0,15)
        self.assertEqual(p.quest['progress'],15);self.assertEqual(len(p.hand),10)
        self.assertFalse(any(c.card_id=='TLC_433t' for c in p.hand))
        p.hand.pop();g._settle()
        self.assertIsNone(p.quest);self.assertEqual(sum(c.card_id=='TLC_433t' for c in p.hand),1)
    def test_invalid_spending_leaves_state(self):
        g=self.game();self.start(g);p=g.players[0];p.corpses=1
        for amount in (-1,2,True,1.5):
            with self.assertRaises(ValueError):g._spend_corpses(0,amount)
        self.assertEqual((p.corpses,p.quest['progress']),(1,0))
    def test_previously_unlogged_grave_strength_counts(self):
        g=self.game();self.start(g);p=g.players[0];p.corpses=15
        g._effect(('grave_strength',),dict(owner=0,source=None,target=0))
        self.assertEqual(p.quest['progress'],5)
    def test_previously_unlogged_blood_tap_counts(self):
        g=self.game();self.start(g);p=g.players[0];p.corpses=15
        g._effect(('blood_tap',),dict(owner=0,source=None,target=0))
        self.assertEqual(p.quest['progress'],2)
    def test_secondary_power_payment_counts(self):
        g=self.game();self.start(g);self.play(g,'JAIL_446');p=g.players[0];p.corpses=15
        m=g._summon(0,'EDR_851t');g.step(Action('power',target=m.uid,choices=(1,)))
        self.assertEqual(p.quest['progress'],3)
    def test_countered_quest_not_active_but_was_played(self):
        g=self.game();g.players[1].secrets=[Card(g._new_id(),'CORE_EX1_287')];self.start(g)
        self.assertIsNone(g.players[0].quest);self.assertEqual(g.players[0].quests_played,1)
    def test_second_active_quest_cannot_be_played(self):
        g=self.game();self.start(g);c=g._enter_hand(0,Card(g._new_id(),'TLC_239'))
        self.assertFalse(any(a.kind=='play' and a.source==c.uid for a in g.legal_actions()))
    def test_secret_slots_include_quest(self):
        g=self.game();self.start(g);p=g.players[0]
        p.secrets=[Card(g._new_id(),cid) for cid in ['CORE_EX1_289','CORE_EX1_610','CORE_EX1_611','CORE_GIL_577']]
        c=g._enter_hand(0,Card(g._new_id(),'CORE_EX1_287'))
        self.assertFalse(any(a.kind=='play' and a.source==c.uid for a in g.legal_actions()))
    def test_assistant_no_quest_is_untargeted(self):
        g=self.game();m=g._summon(1,'EX1_tk34');self.play(g,'TLC_987');self.assertEqual(m.health,6)
    def test_assistant_remembers_completed_quest(self):
        g=self.game();self.start(g);p=g.players[0];p.corpses=15;g._spend_corpses(0,15)
        m=g._summon(1,'EX1_tk34');self.play(g,'TLC_987',m.uid);self.assertEqual(m.health,3)
    def test_full_board_counts_once_per_own_turn(self):
        g=self.game();self.start(g,'TLC_239');self.fill(g);p=g.players[0]
        self.assertEqual(p.quest['progress'],1)
        p.board.pop();self.fill(g);g._refresh_auras();self.assertEqual(p.quest['progress'],1)
    def test_enemy_turn_full_board_waits_until_own_turn(self):
        g=self.game();self.start(g,'TLC_239');g.current=1;self.fill(g);p=g.players[0]
        self.assertEqual(p.quest['progress'],0)
        g.current=0;g._begin_turn();self.assertEqual(p.quest['progress'],1)
    def test_full_board_when_quest_played_counts(self):
        g=self.game();self.fill(g);self.start(g,'TLC_239');self.assertEqual(g.players[0].quest['progress'],1)
    def test_three_distinct_turns_award_weapon(self):
        g=self.game();self.start(g,'TLC_239');self.fill(g)
        for _ in range(2):g.turn+=2;g._refresh_auras()
        self.assertIsNone(g.players[0].quest);self.assertEqual(g.players[0].hand[0].card_id,'TLC_239t')
    def test_locations_occupy_full_board_slots(self):
        g=self.game();self.start(g,'TLC_239')
        for _ in range(6):g._summon(0,'EDR_851t')
        g._place_location(0,'JAIL_877');self.assertEqual(g.players[0].quest['progress'],1)
    def test_everbloom_attack_buffs_survivors(self):
        g=self.game();self.play(g,'TLC_239t');m=g._summon(0,'EDR_851t');before=(m.attack,m.health)
        g.step(Action('attack',-1,-2));self.assertEqual((m.attack,m.health),(before[0]+2,before[1]+2))
        self.assertEqual(g.players[0].weapon['durability'],4)
    def test_tyrax_dies_into_location(self):
        g=self.game();m=g._summon(0,'TLC_433t');m.health=0;g._settle()
        self.assertEqual([x.card_id for x in g.players[0].board],['TLC_433t2'])
    def test_silenced_tyrax_no_grave(self):
        g=self.game();m=g._summon(0,'TLC_433t');m.silenced=True;m.health=0;g._settle();self.assertFalse(g.players[0].board)
    def test_grave_two_charges_damage_and_resummon(self):
        g=self.game();loc=g._place_location(0,'TLC_433t2');g.step(Action('activate',loc.uid,-2))
        self.assertEqual((loc.durability,g.players[1].health),(1,26))
        self.assertNotIn(Action('activate',loc.uid,-2),g.legal_actions())
        loc.ready_turn=g.turn;g.step(Action('activate',loc.uid,-2))
        self.assertEqual(g.players[1].health,22);self.assertEqual([m.card_id for m in g.players[0].minions],['TLC_433t'])
    def test_grave_damage_ignores_spell_damage(self):
        g=self.game();g._summon(0,'CORE_EX1_012');loc=g._place_location(0,'TLC_433t2')
        g.step(Action('activate',loc.uid,-2));self.assertEqual(g.players[1].health,26)
    def test_destroy_grave_resummons(self):
        g=self.game();loc=g._place_location(1,'TLC_433t2')
        g._effect(('destroy_location',),dict(owner=0,source=None,target=loc.uid));g._settle()
        self.assertEqual([m.card_id for m in g.players[1].minions],['TLC_433t'])
    def test_final_charge_frees_slot_on_full_board(self):
        g=self.game();loc=g._place_location(0,'TLC_433t2');loc.durability=1;self.fill(g)
        g.step(Action('activate',loc.uid,-2));self.assertEqual(len(g.players[0].board),7)
        self.assertEqual(sum(m.card_id=='TLC_433t' for m in g.players[0].minions),1)
    def test_progress_visible_to_opponent_without_hand_identity(self):
        g=self.game();self.start(g);g.players[0].corpses=2;g._spend_corpses(0,2)
        view=g.observe(1);self.assertEqual(view['players'][0]['quest']['progress'],2)
        self.assertNotIn('hand',view['players'][0]);self.assertEqual(SCHEMA,'visible-action-features-v58')
    def test_progress_changes_features(self):
        g=self.game();self.start(g);g.players[0].corpses=2
        def features():
            obs=g.observe(0);return encode_decision(dict(actor=0,observation=obs,actions=obs['legal_actions']))
        before=features();g._spend_corpses(0,1);self.assertNotEqual(before,features())

    def test_enemy_summon_trigger_spending_counts(self):
        g=self.game();self.start(g);p=g.players[0];p.corpses=10
        g._summon(0,'EDR_815');g._summon(1,'EX1_tk34');g._settle()
        self.assertEqual(p.quest['progress'],2)
    def test_quest_state_rollback_on_illegal_play(self):
        g=self.game();self.start(g);before=copy.deepcopy(g.players[0].quest)
        with self.assertRaises(ValueError):g.step(Action('play',999999))
        self.assertEqual(g.players[0].quest,before)
    def test_destroy_all_does_not_destroy_new_tyrax(self):
        g=self.game();g._place_location(0,'TLC_433t2');g._summon(0,'EDR_851t')
        g._effect(('destroy_battlefield',),dict(owner=0,source=None,target=0));g._settle()
        self.assertEqual([m.card_id for m in g.players[0].minions],['TLC_433t'])
