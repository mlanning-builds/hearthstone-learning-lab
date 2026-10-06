"""Held counters and expiry through actual play, turn and payment paths."""
import unittest
from unittest.mock import patch
from expanded import Game,Action,random_deck
from expanded.game import Card

class HeldUpgradeTests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('PALADIN',31),random_deck('MAGE',53)],seed=71)
        g.step(Action('mulligan'));g.step(Action('mulligan'))
        for p in g.players:
            p.hand=[];p.board=[];p.deck=['CORE_CS2_029']*25;p.health=30;p.armor=0;p.mana=p.max_mana=p.mana_capacity=10
        return g
    def put(self,g,cid,owner=0):return g._enter_hand(owner,Card(g._new_id(),cid))
    def play(self,g,c,target=None):
        actions=[a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid and (target is None or a.target==target)]
        self.assertTrue(actions,(c.card_id,target,g.players[g.current].mana));g.step(max(actions,key=lambda a:a.position))
        return next((m for m in reversed(g.players[g.current].minions) if m.card_id==c.card_id),None)
    def cycle(self,g):g.step(Action('end'));g.step(Action('end'))
    def age(self,c):return getattr(c,'rule_state',{}).get('held_turn_ends',0)
    def spent(self,c):return getattr(c,'rule_state',{}).get('held_mana_spent',0)
    def test_mana_spent_on_other_card_advances_both_thresholds(self):
        g=self.game();a=self.put(g,'CATA_131');b=self.put(g,'CATA_132');self.play(g,self.put(g,'CORE_CS2_029'),g.hero_id(1))
        self.assertEqual((self.spent(a),self.spent(b)),(4,4))
    def test_zero_cost_coin_does_not_advance(self):
        g=self.game();c=self.put(g,'CATA_131');self.play(g,self.put(g,'TOKEN_COIN'));self.assertEqual(self.spent(c),0)
    def test_hero_power_payment_advances(self):
        g=self.game();c=self.put(g,'CATA_131');g.step(next(a for a in g.legal_actions() if a.kind=='power'));self.assertEqual(self.spent(c),2)
    def test_only_actual_discounted_payment_counts(self):
        g=self.game();c=self.put(g,'CATA_131');spell=self.put(g,'CORE_CS2_029');spell.cost_delta=-3;self.play(g,spell,g.hero_id(1));self.assertEqual(self.spent(c),1)
    def test_other_player_payment_does_not_advance(self):
        g=self.game();c=self.put(g,'CATA_131');g._b60_spend_mana(1,8);self.assertEqual(self.spent(c),0)
    def test_new_card_does_not_inherit_prior_spend(self):
        g=self.game();g._b60_spend_mana(0,8);c=self.put(g,'CATA_132');self.assertEqual(self.spent(c),0)
    def test_thresholds_saturate(self):
        g=self.game();a=self.put(g,'CATA_131');b=self.put(g,'CATA_132');g._b60_spend_mana(0,30);self.assertEqual((self.spent(a),self.spent(b)),(4,8))
    def test_treant_own_payment_does_not_complete_it(self):
        g=self.game();p=g.players[0];p.mana=p.max_mana=5;c=self.put(g,'CATA_131');g._b60_spend_mana(0,2);self.play(g,c)
        self.assertEqual((p.mana,p.max_mana),(4,5))
    def test_ready_treant_gains_full_permanent_crystal(self):
        g=self.game();p=g.players[0];p.mana=p.max_mana=5;c=self.put(g,'CATA_131');g._b60_spend_mana(0,4);self.play(g,c)
        self.assertEqual((p.mana,p.max_mana),(4,6));self.cycle(g);self.assertEqual(p.max_mana,7)
    def test_temporary_treant_does_not_ramp_next_turn(self):
        g=self.game();p=g.players[0];p.mana=p.max_mana=5;self.play(g,self.put(g,'CATA_131'));self.cycle(g);self.assertEqual(p.max_mana,6)
    def test_ready_treant_at_cap_does_not_refresh_spent_mana(self):
        g=self.game();c=self.put(g,'CATA_131');g._b60_spend_mana(0,4);self.play(g,c);self.assertEqual(g.players[0].mana,8)
    def test_broodwatcher_unready_adds_two_playable_whelps(self):
        g=self.game();self.play(g,self.put(g,'CATA_132'));w=[c for c in g.players[0].hand if c.card_id=='CATA_132t'];self.assertEqual(len(w),2)
        m=self.play(g,w[0]);self.assertEqual((m.attack,m.health),(3,3));self.assertIn('TAUNT',m.keywords)
    def test_broodwatcher_ready_summons_two_without_hand_entries(self):
        g=self.game();c=self.put(g,'CATA_132');g._b60_spend_mana(0,8);self.play(g,c)
        self.assertEqual([m.card_id for m in g.players[0].minions],['CATA_132','CATA_132t','CATA_132t']);self.assertFalse(g.players[0].hand)
    def test_broodwatcher_ready_respects_board_capacity(self):
        g=self.game()
        for _ in range(5):g._summon(0,'EDR_851t')
        c=self.put(g,'CATA_132');g._b60_spend_mana(0,8);self.play(g,c);self.assertEqual(len(g.players[0].board),7)
        self.assertEqual(sum(m.card_id=='CATA_132t' for m in g.players[0].minions),1)
    def test_broodwatcher_unready_hand_limit(self):
        g=self.game();c=self.put(g,'CATA_132')
        for _ in range(9):self.put(g,'TOKEN_COIN')
        self.play(g,c);self.assertEqual(len(g.players[0].hand),10);self.assertEqual(sum(x.card_id=='CATA_132t' for x in g.players[0].hand),1)
    def test_turn_upgrade_only_owner_end(self):
        g=self.game();a=self.put(g,'FIR_911');b=self.put(g,'FIR_914',1);g.step(Action('end'))
        self.assertEqual((self.age(a),self.age(b)),(1,0));g.step(Action('end'));self.assertEqual((self.age(a),self.age(b)),(1,1))
    def test_smoldering_discard_third_owner_end(self):
        for cid in ('FIR_911','FIR_914','FIR_916'):
            with self.subTest(cid=cid):
                g=self.game();c=self.put(g,cid);self.cycle(g);self.cycle(g);self.assertIn(c,g.players[0].hand)
                g.step(Action('end'));self.assertNotIn(c,g.players[0].hand);self.assertIn(cid,g.players[0].discard_history)
    def test_repeated_tick_same_turn_is_idempotent(self):
        g=self.game();c=self.put(g,'FIR_911');ctx=dict(owner=0);op=('held_tick',c.uid,c.card_id)
        g._held_effect(op,ctx);g._held_effect(op,ctx);self.assertEqual(self.age(c),1)
    def test_card_outside_hand_does_not_tick(self):
        g=self.game();c=self.put(g,'FIR_911');g.players[0].hand.remove(c);g.players[0].deck.append(c)
        self.cycle(g);self.assertEqual(self.age(c),0)
    def test_stale_tick_does_not_upgrade_transformed_card(self):
        g=self.game();c=self.put(g,'FIR_911');op=('held_tick',c.uid,c.card_id);g._b60_transform_card(c,'CORE_CS2_029')
        g._held_effect(op,dict(owner=0));self.assertEqual(self.age(c),0)
    def test_new_end_turn_draw_does_not_join_existing_timer_snapshot(self):
        g=self.game();g.players[0].deck=['FIR_911'];g._summon(0,'CORE_ULD_133');g.step(Action('end'))
        c=next(c for c in g.players[0].hand if c.card_id=='FIR_911');self.assertEqual(self.age(c),0)
    def test_grove_draw_count_upgrades(self):
        for age in (0,1,2):
            with self.subTest(age=age):
                g=self.game();c=self.put(g,'FIR_911');g._b60_state(c)['held_turn_ends']=age;self.play(g,c);self.assertEqual(len(g.players[0].hand),age+1)
    def test_grove_multiple_draws_have_separate_checkpoints(self):
        g=self.game();c=self.put(g,'FIR_911');g._b60_state(c)['held_turn_ends']=2
        with patch.object(g,'_draw',wraps=g._draw) as draw:self.play(g,c);self.assertEqual(draw.call_count,3)
    def test_strength_upgraded_buff_persists_after_turn(self):
        g=self.game();m=g._summon(0,'EDR_851t');c=self.put(g,'FIR_914');g._b60_state(c)['held_turn_ends']=2;self.play(g,c,m.uid);self.cycle(g)
        self.assertEqual((m.attack,m.health),(4,4))
    def test_ascent_spell_damage_and_enemy_only(self):
        g=self.game();a=g._summon(0,'CS2_033');b=g._summon(1,'CS2_033');g._summon(0,'CORE_EX1_012');c=self.put(g,'FIR_916');g._b60_state(c)['held_turn_ends']=1
        hp=b.health;self.play(g,c);self.assertEqual(b.health,hp-3);self.assertEqual(a.health,hp)
    def test_last_stand_does_not_expire(self):
        g=self.game();c=self.put(g,'CATA_498')
        for _ in range(4):self.cycle(g)
        self.assertIn(c,g.players[0].hand);self.assertEqual(self.age(c),4)
    def test_last_stand_hits_two_distinct_minions(self):
        g=self.game();enemies=[g._summon(1,'CS2_033') for _ in range(3)];c=self.put(g,'CATA_498');g._b60_state(c)['held_turn_ends']=1;hp=enemies[0].health;self.play(g,c)
        self.assertEqual(sorted(hp-m.health for m in enemies),[0,3,3])
    def test_last_stand_one_enemy_hit_once(self):
        g=self.game();m=g._summon(1,'CS2_033');hp=m.health;self.play(g,self.put(g,'CATA_498'));self.assertEqual(m.health,hp-2)
    def test_last_stand_empty_board_can_play(self):
        g=self.game();self.play(g,self.put(g,'CATA_498'));self.assertEqual(g.players[1].health,30)
    def test_copies_preserve_counter_independently(self):
        g=self.game();c=self.put(g,'CATA_132');g._b60_spend_mana(0,3);clone=g._clone_hand_card(0,c);g._b60_state(clone)['held_mana_spent']=7
        self.assertEqual(self.spent(c),3);self.assertEqual(self.spent(clone),7)
    def test_shuffle_resets_held_upgrades(self):
        g=self.game();c=self.put(g,'FIR_911');g._b60_state(c)['held_turn_ends']=2;clean=g._shuffle_hand_card(0,c);self.assertEqual(self.age(clean),0)
    def test_picklock_numbers_follow_remaining_mana(self):
        g=self.game();c=self.put(g,'JAIL_501')
        for mana in (0,1,4,10):
            g.players[0].mana=mana;expected=max(1,mana);self.assertEqual(g._cost(c,0),expected);self.assertEqual(g._card_stat(c,'attack',0),expected);self.assertEqual(g._card_stat(c,'health',0),expected)
    def test_picklock_zero_mana_is_not_playable(self):
        g=self.game();c=self.put(g,'JAIL_501');g.players[0].mana=0;self.assertFalse(any(a.kind=='play' and a.source==c.uid for a in g.legal_actions()))
    def test_picklock_snapshots_before_payment(self):
        g=self.game();enemy=g._summon(1,'CS2_033');hp=enemy.health;c=self.put(g,'JAIL_501');g.players[0].mana=4;m=self.play(g,c,enemy.uid)
        self.assertEqual((m.attack,m.health,g.players[0].mana),(4,4,0));self.assertEqual(enemy.health,hp-4)
        g.players[0].mana=9;self.assertEqual((m.attack,m.health),(4,4))
    def test_picklock_handbuff_and_discount_do_not_change_damage_value(self):
        g=self.game();enemy=g._summon(1,'CS2_033');hp=enemy.health;c=self.put(g,'JAIL_501');c.attack_bonus=2;c.health_bonus=3;c.cost_delta=-2;g.players[0].mana=4
        m=self.play(g,c,enemy.uid);self.assertEqual((m.attack,m.health,g.players[0].mana),(6,7,2));self.assertEqual(enemy.health,hp-4)
    def test_picklock_deck_stats_are_printed(self):
        g=self.game();c=Card(g._new_id(),'JAIL_501');g.players[0].deck=[c];self.assertEqual(g._card_stat(c,'attack',0),1)
    def test_picklock_bounce_recalculates(self):
        g=self.game();c=self.put(g,'JAIL_501');g.players[0].mana=3;m=self.play(g,c);g._bounce(m);held=g.players[0].hand[-1];g.players[0].mana=7
        self.assertEqual(g._card_stat(held,'attack',0),7);self.assertEqual(g._cost(held,0),7)
    def test_held_progress_visible_to_owner_only(self):
        g=self.game();c=self.put(g,'CATA_131');g._b60_spend_mana(0,3);view=g.observe(0);self.assertEqual(view['players'][0]['hand'][0]['rule_state']['held_mana_spent'],3)
        self.assertNotIn('hand',g.observe(1)['players'][0])
    def test_smoldering_expiry_publishes_discard_event(self):
        g=self.game();c=self.put(g,'FIR_911');g._b60_state(c)['held_turn_ends']=2
        with patch.object(g,'_event_frame',wraps=g._event_frame) as event_frame:
            g.step(Action('end'))
            self.assertTrue(any(call.args[0][0]=='discard' for call in event_frame.call_args_list))
    def test_smoldering_expiry_updates_discard_scaling(self):
        g=self.game();scaled=self.put(g,'CATA_493');before=g._card_stat(scaled,'attack',0);c=self.put(g,'FIR_914');g._b60_state(c)['held_turn_ends']=2;g.step(Action('end'))
        self.assertEqual(g._card_stat(scaled,'attack',0),before+2)
    def test_countered_spell_still_spends_mana_for_held_progress(self):
        g=self.game();c=self.put(g,'CATA_131');g._effect(('secret','CORE_EX1_287'),dict(owner=1));self.play(g,self.put(g,'CORE_CS2_029'),g.hero_id(1))
        self.assertEqual(self.spent(c),4);self.assertEqual(g.players[1].health,30)
    def test_picklock_invalid_target_rolls_back_snapshot(self):
        g=self.game();c=self.put(g,'JAIL_501');before=dict(c.__dict__)
        with self.assertRaises(Exception):g.step(Action('play',source=c.uid,target=999999))
        self.assertEqual(g.players[0].hand[0].__dict__,before);self.assertEqual(g.players[0].mana,10)
    def test_copied_smoldering_card_keeps_age(self):
        g=self.game();c=self.put(g,'FIR_911');g._b60_state(c)['held_turn_ends']=2;copy=g._clone_hand_card(0,c);g.step(Action('end'))
        self.assertNotIn(c,g.players[0].hand);self.assertNotIn(copy,g.players[0].hand);self.assertEqual(g.players[0].discard_history.count('FIR_911'),2)
