"""Untouchable board occupancy, free hand consumption and resumable summons."""
import copy
import json
import unittest
from unittest.mock import patch
from expanded import Game,Action,random_deck
from expanded.game import Card
from expanded.permanents import Permanent,RIFT,FEL_BEASTS
from expanded.cards import TRIGGERS
from expanded.features import encode_decision,SCHEMA
from engine.cards import UnsupportedCard

class PermanentTests(unittest.TestCase):
    def game(self,seed=71):
        g=Game([random_deck('WARLOCK',31),random_deck('MAGE',53)],seed=seed)
        g.step(Action('mulligan'));g.step(Action('mulligan'));g.current=0
        for p in g.players:
            p.hand=[];p.board=[];p.deck=['CORE_CS2_029']*20;p.mana=p.max_mana=10;p.health=30;p.armor=0;p.corpses=0;p.quest=None
        return g
    def hold(self,g,cid='CORE_CS2_029',temporary=False):
        c=g._enter_hand(0,Card(g._new_id(),cid))
        if temporary:g._make_temporary(c)
        return c
    def play(self,g,cid=None,card=None,target=0):
        c=card or self.hold(g,cid);g.players[0].mana=10
        g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid and a.target==target))
    def rift(self,g,owner=0):return g._place_permanent(owner,RIFT)
    def activate(self,g,obj,card=None):
        c=card or self.hold(g);g.step(Action('activate',obj.uid,c.uid));return c
    def test_opening_hand_reserves_new_quest(self):
        from expanded import Deck
        d=random_deck('WARLOCK',17);cards=list(d.cards)
        if 'TLC_446' not in cards:cards[0]='TLC_446'
        g=Game([Deck('WARLOCK',tuple(cards)),random_deck('MAGE',2)])
        self.assertIn('TLC_446',[c.card_id for c in g.players[0].hand]);self.assertEqual(len(g.players[0].hand),3)
    def test_six_temporary_plays_award_pinned_reward(self):
        g=self.game();self.play(g,'TLC_446')
        for i in range(6):
            self.play(g,card=self.hold(g,'TOKEN_COIN',True))
            if i<5:self.assertEqual(g.players[0].quest['progress'],i+1)
        self.assertIsNone(g.players[0].quest);self.assertEqual([c.card_id for c in g.players[0].hand],['TLC_446t'])
        self.assertEqual(g.cards['TLC_446t']['cost'],5)
    def test_normal_play_does_not_advance(self):
        g=self.game();self.play(g,'TLC_446');self.play(g,'TOKEN_COIN');self.assertEqual(g.players[0].quest['progress'],0)
    def test_prior_temporary_plays_not_retroactive(self):
        g=self.game();self.play(g,card=self.hold(g,'TOKEN_COIN',True));self.play(g,'TLC_446');self.assertEqual(g.players[0].quest['progress'],0)
    def test_temporary_expiry_does_not_count_as_play(self):
        g=self.game();self.play(g,'TLC_446');self.hold(g,temporary=True);g.step(Action('end'))
        self.assertEqual(g.players[0].quest['progress'],0)
    def test_countered_temporary_spell_counts_as_play(self):
        g=self.game();self.play(g,'TLC_446');g.players[1].secrets=[Card(g._new_id(),'CORE_EX1_287')]
        self.play(g,card=self.hold(g,'TOKEN_COIN',True));self.assertEqual(g.players[0].quest['progress'],1)
    def test_rift_spell_opens_one_untouchable_object(self):
        g=self.game();self.play(g,'TLC_446t');p=g.players[0]
        self.assertEqual(len(p.board),1);self.assertIsInstance(p.board[0],Permanent)
        self.assertEqual(p.minions,[]);self.assertEqual(p.all_minions,[]);self.assertEqual(p.locations,[])
        self.assertEqual(p.mana,5)
    def test_full_board_spell_does_not_overfill(self):
        g=self.game()
        for _ in range(7):g._summon(0,'EDR_851t')
        self.play(g,'TLC_446t');self.assertEqual(len(g.players[0].board),7);self.assertFalse(g.players[0].permanents)
    def test_cannot_construct_portal_as_ordinary_minion(self):
        g=self.game()
        with self.assertRaises(UnsupportedCard):g._summon(0,RIFT)
        self.assertFalse(g.players[0].board)
    def test_portal_spell_can_be_countered(self):
        g=self.game();g.players[1].secrets=[Card(g._new_id(),'CORE_EX1_287')];self.play(g,'TLC_446t')
        self.assertFalse(g.players[0].board)
    def test_activation_is_free_and_consumes_only_chosen_card(self):
        g=self.game();obj=self.rift(g);a=self.hold(g);b=self.hold(g,'TOKEN_COIN');g.players[0].mana=0
        self.activate(g,obj,a);self.assertNotIn(a,g.players[0].hand);self.assertIn(b,g.players[0].hand)
        self.assertEqual(g.players[0].mana,0);self.assertEqual(len(g.players[0].minions),2)
    def test_card_removal_not_play_discard_destroy_or_draw(self):
        g=self.game();obj=self.rift(g);self.play(g,'TLC_446');c=self.hold(g,temporary=True)
        before=(g.players[0].cards_played,list(g.players[0].played_history),len(g.players[0].deck))
        events=len(g.events);self.activate(g,obj,c);p=g.players[0]
        self.assertEqual((p.cards_played,p.played_history,len(p.deck)),before);self.assertFalse(p.discard_history)
        self.assertEqual(p.quest['progress'],0)
        self.assertFalse(any(e['event'] in ('play','discard','destroy_hand_card','draw') for e in g.events[events:]))
    def test_no_discard_listener_trigger(self):
        g=self.game();listener=g._summon(0,'CATA_494');obj=self.rift(g);c=self.hold(g,'EX1_tk34')
        self.activate(g,obj,c);self.assertEqual(len(g.players[0].minions),3)
        self.assertFalse(any(m.card_id=='EX1_tk34' for m in g.players[0].minions))
    def test_once_per_own_turn(self):
        g=self.game();obj=self.rift(g);self.activate(g,obj);c=self.hold(g)
        self.assertNotIn(Action('activate',obj.uid,c.uid),g.legal_actions());g.step(Action('end'))
        self.assertFalse(g._public_entity(obj)['ready']);g.step(Action('end'))
        self.assertIn(Action('activate',obj.uid,c.uid),g.legal_actions())
    def test_duplicate_rifts_have_separate_use_limits(self):
        g=self.game();a=self.rift(g);b=self.rift(g);self.activate(g,a);self.activate(g,b)
        self.assertEqual(len(g.players[0].minions),4);self.assertEqual(len(g.players[0].permanents),2)
    def test_empty_hand_has_no_activation(self):
        g=self.game();obj=self.rift(g);self.assertFalse(any(a.kind=='activate' and a.source==obj.uid for a in g.legal_actions()))
    def test_enemy_rift_not_activatable(self):
        g=self.game();obj=self.rift(g,1);c=self.hold(g);self.assertNotIn(Action('activate',obj.uid,c.uid),g.legal_actions())
    def test_locked_card_can_be_thrown_in(self):
        g=self.game();obj=self.rift(g);c=self.hold(g);c.play_lock=dict(owner=0,until=999)
        self.assertIn(Action('activate',obj.uid,c.uid),g.legal_actions());self.activate(g,obj,c)
    def test_full_board_activation_consumes_without_overfill(self):
        g=self.game();obj=self.rift(g)
        for _ in range(6):g._summon(0,'EDR_851t')
        c=self.activate(g,obj);self.assertEqual(len(g.players[0].board),7);self.assertNotIn(c,g.players[0].hand)
    def test_one_free_slot_summons_only_one(self):
        g=self.game();obj=self.rift(g)
        for _ in range(5):g._summon(0,'EDR_851t')
        self.activate(g,obj);self.assertEqual(sum(m.card_id in FEL_BEASTS for m in g.players[0].minions),1)
    def test_fixed_pool_all_outcomes_and_duplicates(self):
        seen=set();duplicate=False
        for seed in range(20):
            g=self.game(seed);self.activate(g,self.rift(g));ids=[m.card_id for m in g.players[0].minions]
            seen.update(ids);duplicate|=len(set(ids))==1
        self.assertEqual(seen,set(FEL_BEASTS));self.assertTrue(duplicate)
    def test_missing_pool_dependency_restores_card_and_rng(self):
        g=self.game();obj=self.rift(g);c=self.hold(g);del g.cards[FEL_BEASTS[0]];before=copy.deepcopy(g.__dict__)
        with self.assertRaises(UnsupportedCard):g.step(Action('activate',obj.uid,c.uid))
        self.assertEqual(g.players,before['players']);self.assertEqual(g.rng.getstate(),before['rng'].getstate())
    def test_failed_late_validation_rolls_back_full_activation(self):
        g=self.game();obj=self.rift(g);c=self.hold(g);before=copy.deepcopy(g.__dict__)
        with patch.object(Game,'assert_invariants',side_effect=RuntimeError('injected')):
            with self.assertRaises(RuntimeError):g.step(Action('activate',obj.uid,c.uid))
        self.assertEqual(g.players,before['players']);self.assertEqual(g.rng.getstate(),before['rng'].getstate());self.assertIsNone(g.pending_frame)
    def test_untouchable_not_targetable_by_combat_spells_or_locations(self):
        g=self.game();obj=self.rift(g,1);self.hold(g);g._place_location(0,'TLC_433t2');g._summon(0,'TLC_446t3')
        self.assertNotIn(obj.uid,g._characters());self.assertNotIn(obj.uid,g._visible_targets(0))
        self.assertFalse(any(a.target==obj.uid for a in g.legal_actions()))
        self.assertEqual(g._damage(obj.uid,99),0)
    def test_board_wipes_and_buffs_ignore_permanent(self):
        g=self.game();obj=self.rift(g);g._summon(0,'EDR_851t')
        for op in [('board_buff',3,3),('destroy_battlefield',)]:g._effect(op,dict(owner=0,source=None,target=0,bonus=0,lifesteal=False));g._settle()
        self.assertEqual(g.players[0].board,[obj]);self.assertEqual(g.players[0].corpses,1)
    def test_permanent_interrupts_adjacency(self):
        g=self.game();left=g._summon(0,'EDR_851t');self.rift(g);g._summon(0,'CORE_EX1_162');right=g._summon(0,'EDR_851t')
        self.assertEqual(left.attack,1);self.assertEqual(right.attack,2)
    def test_permanent_counts_for_full_board_quest(self):
        g=self.game();self.play(g,'TLC_239');self.rift(g)
        for _ in range(6):g._summon(0,'EDR_851t')
        self.assertEqual(g.players[0].quest['progress'],1)
    def test_opening_permanent_does_not_emit_minion_summon(self):
        g=self.game();g._summon(1,'EDR_815');g.players[1].corpses=4;self.play(g,'TLC_446t')
        self.assertEqual(g.players[1].corpses,4)
    def test_fel_beasts_emit_individual_summon_events(self):
        g=self.game();g._summon(1,'EDR_815');g.players[1].corpses=4;obj=self.rift(g)
        with patch.object(g.rng,'choice',return_value='TLC_446t2'):self.activate(g,obj)
        self.assertEqual(g.players[1].corpses,0);self.assertFalse(g.players[0].minions);self.assertEqual(g.players[0].corpses,2)
    def test_first_summon_choice_pauses_second_without_double_payment(self):
        g=self.game();g._summon(0,'CORE_EX1_509');obj=self.rift(g);c=self.hold(g)
        rule=(('summon','friendly','BEAST'),[('choose_fixed_summon',('EDR_851t',))])
        with patch.dict(TRIGGERS,{'CORE_EX1_509':rule}):
            self.activate(g,obj,c);self.assertEqual(g.phase,'choice');self.assertNotIn(c,g.players[0].hand)
            self.assertEqual(sum(m.card_id in FEL_BEASTS for m in g.players[0].minions),1)
            g.step(Action('choose',choices=(0,)));self.assertEqual(g.phase,'choice')
            g.step(Action('choose',choices=(0,)));self.assertEqual(g.phase,'play');self.assertIsNone(g.pending_frame)
            self.assertEqual(sum(m.card_id in FEL_BEASTS for m in g.players[0].minions),2)
    def test_observation_and_features_keep_consumed_identity_private(self):
        g=self.game();obj=self.rift(g);c=self.hold(g,'DREAM_03');view=g.observe(0)
        self.assertEqual(view['players'][0]['board'][0]['type'],'PERMANENT')
        rows=encode_decision(dict(actor=0,observation=view,actions=view['legal_actions']));self.assertTrue(rows)
        self.activate(g,obj,c);enemy=g.observe(1)
        self.assertNotIn('DREAM_03',json.dumps(enemy));self.assertEqual(SCHEMA,'visible-action-features-v58')
    def test_fel_beast_printed_keywords_work(self):
        g=self.game();a=g._summon(0,'TLC_446t2');b=g._summon(0,'TLC_446t3');c=g._summon(0,'TLC_446t4')
        self.assertEqual((a.attack,a.health),(5,3));self.assertTrue({'RUSH','LIFESTEAL'}<=g._effective_keywords(a))
        self.assertEqual((b.attack,b.health),(4,4));self.assertIn(Action('attack',b.uid,-2),g.legal_actions())
        self.assertTrue({'TAUNT','REBORN'}<=g._effective_keywords(c));c.health=0;g._settle()
        reborn=next(m for m in g.players[0].minions if m.card_id=='TLC_446t4');self.assertEqual(reborn.health,1)
