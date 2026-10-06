"""Draw-transition, privacy, and listener integration checks."""
import unittest
from copy import deepcopy
from unittest.mock import patch
from expanded import Game, Action, random_deck
from expanded.game import Card

class DrawEventTests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('PALADIN',31),random_deck('MAGE',53)],seed=71)
        g.step(Action('mulligan'));g.step(Action('mulligan'))
        for p in g.players:
            p.hand=[];p.board=[];p.deck=['CORE_CS2_029']*25;p.health=30;p.mana=p.max_mana=10;p.armor=0
        return g
    def put(self,g,cid,owner=0):
        c=Card(g._new_id(),cid);g.players[owner].hand.append(c);return c
    def play_card(self,g,c,target=None,choice=None):
        g.players[g.current].mana=10
        actions=[a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid and (target is None or a.target==target) and (choice is None or a.choices==(choice,))]
        self.assertTrue(actions,(c.card_id,target,choice));first=actions[0];g.step(max((a for a in actions if a.target==first.target and a.choices==first.choices),key=lambda a:a.position));return c
    def play(self,g,cid,target=None,choice=None):return self.play_card(g,self.put(g,cid,g.current),target,choice)
    def choose(self,g,i=0):g.step(Action('choose',choices=(i,)))
    def cycle(self,g):g.step(Action('end'));g.step(Action('end'))
    def kill(self,g,m):m.health=0;g._settle(allow_event_choices=True)
    def attack(self,g,m,target):
        m.summoned_turn=g.turn-1
        g.step(next(a for a in g.legal_actions() if a.kind=='attack' and a.source==m.uid and a.target==target))
    def test_deceptor_successful_draw_summons_rush_demon(self):
        g=self.game();g._summon(0,'CORE_TTN_843');g._draw(0);g._settle()
        m=g.players[0].minions[-1];self.assertEqual((m.card_id,m.attack,m.health),('TTN_843t1',1,1));self.assertIn('RUSH',m.keywords)
    def test_deceptor_opponent_draw_no_summon(self):
        g=self.game();g._summon(0,'CORE_TTN_843');g._draw(1);g._settle();self.assertEqual(len(g.players[0].minions),1)
    def test_burn_is_not_draw(self):
        g=self.game();g._summon(0,'CORE_TTN_843');g._summon(1,'CORE_SCH_717')
        for _ in range(10):self.put(g,'EDR_851t')
        n=len(g.players[0].deck);g._draw(0);g._settle()
        self.assertEqual(len(g.players[0].deck),n-1);self.assertEqual(len(g.players[0].minions),1);self.assertFalse(g.players[1].hand)
    def test_fatigue_is_not_draw(self):
        g=self.game();g._summon(0,'CORE_TTN_843');g.players[0].deck=[];g._draw(0);g._settle()
        self.assertEqual(g.players[0].health,29);self.assertEqual(len(g.players[0].minions),1)
    def test_opening_draw_is_private_without_trigger(self):
        g=self.game();g._summon(0,'CORE_TTN_843');g._draw(0,private=True);g._settle();self.assertEqual(len(g.players[0].minions),1)
    def test_alabaster_copies_opponent_draw_cost_one(self):
        g=self.game();g._summon(1,'CORE_SCH_717');g._draw(0);g._settle()
        c=g.players[1].hand[0];self.assertEqual(c.card_id,'CORE_CS2_029');self.assertEqual(g._cost(c,1),1)
    def test_alabaster_own_draw_no_copy(self):
        g=self.game();g._summon(0,'CORE_SCH_717');g._draw(0);g._settle();self.assertEqual(len(g.players[0].hand),1)
    def test_generated_copy_is_not_draw_recursive(self):
        g=self.game();g._summon(0,'CORE_SCH_717');g._summon(1,'CORE_SCH_717');g._summon(1,'CORE_TTN_843');g._draw(0);g._settle()
        self.assertEqual([len(p.hand) for p in g.players],[1,1]);self.assertEqual(len(g.players[1].minions),2)
    def test_alabaster_full_hand_burns_generated_copy(self):
        g=self.game();g._summon(1,'CORE_SCH_717')
        for _ in range(10):self.put(g,'EDR_851t',1)
        g._draw(0);g._settle();self.assertEqual(len(g.players[1].hand),10)
    def test_silenced_listeners_do_not_trigger(self):
        g=self.game();g._silence(g._summon(0,'CORE_TTN_843'));g._silence(g._summon(1,'CORE_SCH_717'));g._draw(0);g._settle()
        self.assertEqual(len(g.players[0].minions),1);self.assertFalse(g.players[1].hand)
    def test_listener_entering_after_draw_does_not_observe_it(self):
        g=self.game();g._draw(0);g._summon(0,'CORE_TTN_843');g._summon(1,'CORE_SCH_717');g._settle()
        self.assertEqual(len(g.players[0].minions),1);self.assertFalse(g.players[1].hand)
    def test_draw_snapshot_is_independent_of_later_changes(self):
        g=self.game();g._summon(1,'CORE_SCH_717');c=Card(g._new_id(),'EDR_851t',attack_bonus=3);g.players[0].deck=[c]
        g._draw(0);c.attack_bonus=10;g._settle();copy=g.players[1].hand[0]
        self.assertEqual(copy.attack_bonus,3);self.assertNotEqual(copy.uid,c.uid);self.assertEqual(c.attack_bonus,10)
    def test_filtered_draw_uses_same_transition(self):
        g=self.game();g._summon(0,'CORE_TTN_843');g.players[0].deck=['CORE_CS2_029','EDR_851t'];g._draw_filtered(0,(('type','eq','MINION'),));g._settle()
        self.assertEqual(g.players[0].hand[0].card_id,'EDR_851t');self.assertEqual(len(g.players[0].minions),2)
    def test_failed_filtered_draw_no_fatigue_or_event(self):
        g=self.game();g._summon(0,'CORE_TTN_843');g.players[0].deck=[];g._draw_filtered(0,(('type','eq','MINION'),));g._settle()
        self.assertEqual(g.players[0].health,30);self.assertEqual(len(g.players[0].minions),1)
    def test_deck_discover_put_is_not_draw(self):
        g=self.game();g._summon(0,'CORE_TTN_843');self.play(g,'JAIL_734');self.choose(g)
        self.assertEqual(len(g.players[0].minions),2);self.assertEqual(len(g.players[0].hand),1)
    def test_draw_two_notifies_between_cards(self):
        g=self.game();g._summon(0,'CORE_TTN_843');seen=[];original=g._receive_draw
        def receive(owner,value,**kwargs):
            seen.append(len(g.players[0].minions));return original(owner,value,**kwargs)
        with patch.object(g,'_receive_draw',side_effect=receive):self.play(g,'CAP_102')
        self.assertEqual(seen,[1,2]);self.assertEqual(len(g.players[0].minions),5)
    def test_turn_start_draw_notifies_once(self):
        g=self.game();g._summon(1,'CORE_TTN_843');g.step(Action('end'));self.assertEqual(len(g.players[1].minions),2)
    def test_burn_return_for_cost_queries_does_not_notify(self):
        g=self.game();g._summon(0,'CORE_TTN_843')
        for _ in range(10):self.put(g,'EDR_851t')
        c=g._draw(0,include_burned=True);g._settle();self.assertEqual(c.card_id,'CORE_CS2_029');self.assertEqual(len(g.players[0].minions),1)
    def test_draw_card_identity_does_not_leak_to_opponent(self):
        g=self.game();g.players[0].deck=['CORE_SCH_717'];g._draw(0)
        self.assertNotIn('CORE_SCH_717',str(g.observe(1)));g._settle();self.assertNotIn('CORE_SCH_717',str(g.observe(1)))
    def test_queued_draw_state_deepcopies_and_replays(self):
        g=self.game();g._summon(1,'CORE_SCH_717');g._draw(0);copy=deepcopy(g);g._settle();copy._settle()
        self.assertEqual(g.observe(1),copy.observe(1));self.assertEqual(g.rng.getstate(),copy.rng.getstate())
    def test_full_board_prevents_demon_but_preserves_draw(self):
        g=self.game();g._summon(0,'CORE_TTN_843')
        for _ in range(6):g._summon(0,'EDR_851t')
        g._draw(0);g._settle();self.assertEqual(len(g.players[0].minions),7);self.assertEqual(len(g.players[0].hand),1)
    def test_draw_transfer_notifies_recipient(self):
        g=self.game();g._summon(1,'CORE_TTN_843');g._summon(0,'CORE_SCH_717');g._take_deck_draw(0,-1,recipient=1);g._settle()
        self.assertEqual(len(g.players[1].minions),2);self.assertEqual([len(p.hand) for p in g.players],[1,1])
    def test_draw_pick_waits_for_each_draw_trigger_before_choice(self):
        g=self.game();g._summon(0,'CORE_TTN_843');self.play(g,'TIME_770')
        self.assertEqual(len(g.players[0].minions),3);self.assertEqual(len(g.pending_choice['options']),2)
        self.choose(g);self.assertEqual(sorted(g._cost(c,0) for c in g.players[0].hand),[2,4])
    def test_captured_draw_choice_replay_does_not_repeat_draws(self):
        g=self.game();g._summon(0,'CORE_TTN_843');self.play(g,'TIME_770');copy=deepcopy(g);self.choose(g);self.choose(copy)
        self.assertEqual(len(g.players[0].minions),3);self.assertEqual(g.observe(0),copy.observe(0))
    def test_filtered_draw_group_notifies_between_cards(self):
        g=self.game();g._summon(0,'CORE_TTN_843');g.players[0].deck=['EDR_851t']*3;seen=[];original=g._receive_draw
        def receive(owner,value,**kwargs):
            seen.append(len(g.players[0].minions));return original(owner,value,**kwargs)
        ctx=dict(owner=0,source=None,target=0,bonus=0,lifesteal=False)
        with patch.object(g,'_receive_draw',side_effect=receive):g._start_play_effects([('filtered_draw',(('type','eq','MINION'),),2)],ctx)
        self.assertEqual(seen,[1,2]);self.assertEqual(len(g.players[0].hand),2)
    def test_conditional_draw_group_checks_empty_only_once(self):
        g=self.game();ctx=dict(owner=0,source=None,target=0,bonus=0,lifesteal=False)
        g._start_play_effects([('draw_empty',2)],ctx);self.assertEqual(len(g.players[0].hand),2)
    def test_failed_conditional_draw_no_event(self):
        g=self.game();g._summon(0,'CORE_TTN_843');self.put(g,'EDR_851t');ctx=dict(owner=0,source=None,target=0,bonus=0,lifesteal=False)
        g._start_play_effects([('draw_empty',2)],ctx);self.assertEqual(len(g.players[0].hand),1);self.assertEqual(len(g.players[0].minions),1)
    def test_terminal_fatigue_stops_remaining_group(self):
        g=self.game();g.players[0].deck=[];g.players[0].health=1;ctx=dict(owner=0,source=None,target=0,bonus=0,lifesteal=False)
        g._start_play_effects([('draw',3)],ctx);self.assertTrue(g.terminal);self.assertEqual(g.players[0].fatigue,1)
    def draw_board_sizes(self,g,callback):
        seen=[];original=g._receive_draw
        def receive(owner,value,**kwargs):
            seen.append(len(g.players[owner].minions));return original(owner,value,**kwargs)
        with patch.object(g,'_receive_draw',side_effect=receive):callback()
        return seen
    def test_bottom_draw_checkpoints_and_order(self):
        g=self.game();g._summon(0,'CORE_TTN_843');g.players[0].deck=['EDR_851t','CATA_551t','CORE_CS2_029']
        seen=self.draw_board_sizes(g,lambda:self.play(g,'TIME_023'))
        self.assertEqual(seen,[1,2]);self.assertEqual([c.card_id for c in g.players[0].hand],['EDR_851t','CATA_551t'])
    def test_distinct_cost_draws_checkpoints(self):
        g=self.game();g._summon(0,'CORE_TTN_843');g.players[0].deck=['EDR_851t','CATA_551t','CORE_CS2_029']
        seen=self.draw_board_sizes(g,lambda:self.play(g,'TIME_031'))
        self.assertEqual(seen,[1,2,3]);self.assertEqual(len(g.players[0].hand),3)
    def test_distinct_cost_stops_without_eligible_identity(self):
        g=self.game();g._summon(0,'CORE_TTN_843');g.players[0].deck=['EDR_851t']*3
        self.play(g,'TIME_031');self.assertEqual(len(g.players[0].hand),1);self.assertEqual(len(g.players[0].deck),2)
    def test_distinct_cost_empty_does_not_fatigue(self):
        g=self.game();g.players[0].deck=[];self.play(g,'TIME_031');self.assertEqual(g.players[0].health,30)
    def test_cheap_repeat_notifies_between_draws(self):
        g=self.game();g._summon(0,'CORE_TTN_843');g.players[0].deck=['CORE_CS2_029','EDR_851t']
        seen=self.draw_board_sizes(g,lambda:self.play(g,'JAIL_377'));self.assertEqual(seen,[1,2])
    def test_expensive_first_does_not_repeat(self):
        g=self.game();g._summon(0,'CORE_TTN_843');self.play(g,'JAIL_377');self.assertEqual(len(g.players[0].hand),1)
    def test_cascading_discount_checkpoints(self):
        g=self.game();g._summon(0,'CORE_TTN_843');g.players[0].deck=['CORE_CS2_029']*3
        seen=self.draw_board_sizes(g,lambda:self.play(g,'CATA_570'))
        self.assertEqual(seen,[2,3,4]);self.assertEqual([g._cost(c,0) for c in g.players[0].hand],[0,0,2])
    def test_zero_cost_discount_chain_ends_at_fatigue(self):
        g=self.game();g.players[0].deck=['EDR_851t']*2;self.play(g,'CATA_570')
        self.assertEqual(len(g.players[0].hand),2);self.assertEqual(g.players[0].fatigue,1);self.assertEqual(g.players[0].health,29)
    def test_fill_hand_draw_checkpoints(self):
        g=self.game();g._summon(0,'CORE_TTN_843')
        seen=self.draw_board_sizes(g,lambda:self.play(g,'TIME_601'));self.assertEqual(seen,[2,3,4])
    def test_excess_damage_draws_after_death_checkpoint(self):
        g=self.game();g._summon(0,'CORE_TTN_843');victim=g._summon(1,'EDR_851t')
        seen=self.draw_board_sizes(g,lambda:self.play(g,'TIME_858',victim.uid))
        self.assertEqual(seen,[2,3,4,5]);self.assertFalse(g.players[1].minions);self.assertEqual(len(g.players[0].hand),4)
    def test_aoe_dead_draws_checkpoints(self):
        g=self.game();g._summon(0,'CORE_TTN_843');g._summon(1,'EDR_851t');g._summon(1,'EDR_851t')
        seen=self.draw_board_sizes(g,lambda:self.play(g,'CATA_526'));self.assertEqual(seen,[1,2]);self.assertEqual(len(g.players[0].hand),2)
    def test_random_kill_draws_checkpoints(self):
        g=self.game();g._summon(0,'CORE_TTN_843');g._summon(1,'EDR_851t');g._summon(1,'EDR_851t')
        seen=self.draw_board_sizes(g,lambda:self.play(g,'CORE_CATA_007'));self.assertEqual(seen,[1,2])
    def test_intermediate_choice_suspends_draw_group(self):
        from expanded.cards import TRIGGERS
        g=self.game();g._summon(0,'CORE_TTN_843')
        with patch.dict(TRIGGERS,{'CORE_TTN_843':('friendly_card_drawn',[('discover_deck',)])}):
            self.play(g,'CAP_102');self.assertEqual(len(g.players[0].hand),1);self.assertEqual(g.phase,'choice')
            copy=deepcopy(g);self.choose(g);self.choose(copy)
            self.assertEqual(len(g.players[0].hand),3);self.assertEqual(g.phase,'choice');self.assertEqual(g.observe(0),copy.observe(0))
            self.choose(g);self.assertEqual(len(g.players[0].hand),4);self.assertEqual(g.phase,'play');self.assertEqual(len(g.players[0].minions),3)
    def test_damage_then_choice_resumes_count_once(self):
        from expanded.cards import TRIGGERS
        g=self.game();g._summon(0,'CORE_TTN_843');target=g._summon(1,'EDR_851t')
        with patch.dict(TRIGGERS,{'CORE_TTN_843':('friendly_card_drawn',[('discover_deck',)])}):
            self.play(g,'TIME_858',target.uid)
            for i in range(4):
                self.assertEqual(g.phase,'choice');self.choose(g)
            self.assertEqual(g.phase,'play');self.assertEqual(len(g.players[0].hand),8);self.assertEqual(g.players[1].death_history.count('EDR_851t'),1)
