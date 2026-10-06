"""Behavioral scenarios for the second 30-card batch; no training."""
import json
import unittest
from copy import deepcopy
from unittest.mock import patch
from expanded import Game,Action,random_deck
from expanded.game import Card
from expanded.composed_cards import RULES
from expanded.cards import DEATH_EFFECTS


class ComposedBatchTests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('PALADIN',31),random_deck('MAGE',53)],seed=71)
        g.step(Action('mulligan'));g.step(Action('mulligan'))
        for p in g.players:
            p.hand=[];p.board=[];p.deck=['CORE_CS2_029']*20;p.health=30;p.mana=p.max_mana=10;p.armor=0
        return g
    def put(self,g,cid,owner=0):
        c=Card(g._new_id(),cid);g.players[owner].hand.append(c);return c
    def play(self,g,cid,target=None,branch=None):
        g.players[g.current].mana=10;c=self.put(g,cid,g.current)
        options=[a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid]
        if target is not None:options=[a for a in options if a.target==target]
        if branch is not None:options=[a for a in options if a.choices==(branch,)]
        self.assertTrue(options,(cid,target,branch));g.step(options[0]);return c
    def choose(self,g,index=0):g.step(Action('choose',choices=(index,)))
    def cycle(self,g):g.step(Action('end'));g.step(Action('end'))
    def kill(self,g,m):m.health=0;g._settle(allow_event_choices=True)
    def test_exact_thirty(self):self.assertEqual(len(RULES),30)
    def test_chronikar_three_own_turns(self):
        g=self.game();self.play(g,'END_006');self.assertEqual(g._hero_attack(0),3)
        for _ in range(2):
            g.step(Action('end'));self.assertEqual(g._hero_attack(0),0)
            g.step(Action('end'));self.assertEqual(g._hero_attack(0),3)
        self.cycle(g);self.assertEqual(g._hero_attack(0),0)
    def test_rotten_apple_heal_and_two_delays(self):
        g=self.game();g.players[0].health=10;self.play(g,'EDR_482');self.assertEqual(g.players[0].health,22)
        self.cycle(g);self.assertEqual(g.players[0].health,19)
        self.cycle(g);self.assertEqual(g.players[0].health,16)
        self.cycle(g);self.assertEqual(g.players[0].health,16)
    def test_fractured_power_two_turn_delay_and_cap(self):
        g=self.game();g.players[0].max_mana=5;self.play(g,'EDR_483');self.assertEqual(g.players[0].max_mana,4)
        self.cycle(g);self.assertEqual(g.players[0].max_mana,5)
        self.cycle(g);self.assertEqual((g.players[0].max_mana,g.players[0].mana),(8,8))
    def test_hourglass_survival_and_lethal(self):
        g=self.game();m=g._summon(0,'TIME_050');g._damage(m.uid,2);g._settle();self.assertEqual((m.attack,m.health),(7,4))
        g._damage(m.uid,4);g._settle();self.assertNotIn(m,g.players[0].board)
    def test_broodmother_refreshes_on_attack(self):
        g=self.game();m=g._summon(0,'CATA_469');enemy=g._summon(1,'CS2_033');g.players[0].mana=0
        g.step(Action('attack',m.uid,enemy.uid));self.assertEqual(g.players[0].mana,2)
    def test_stormdrake_kindred_immune_expires(self):
        g=self.game();g.players[0].previous_tribes={'DRAGON'};self.play(g,'TLC_243');m=g.players[0].minions[0]
        self.assertIn('IMMUNE',g._effective_keywords(m));g._damage(m.uid,99);self.assertEqual(m.health,8)
        g.step(Action('end'));self.assertNotIn('IMMUNE',g._effective_keywords(m))
    def test_nightmare_hand_and_board_attack(self):
        for zone in ('hand','board'):
            g=self.game();target=self.put(g,'CS2_033') if zone=='hand' else g._summon(0,'CS2_033')
            self.play(g,'CATA_161');amount=g.cards['CATA_161']['attack']
            index=next(i for i,o in enumerate(g.pending_choice['options']) if o['uid']==target.uid)
            self.choose(g,index)
            self.assertEqual(target.attack_bonus if zone=='hand' else target.attack-3,amount)
    def test_runeblade_previous_runes(self):
        g=self.game();self.play(g,'EDR_813',branch=0);self.play(g,'EDR_812')
        self.assertEqual((g.players[0].weapon['attack'],g.players[0].weapon['durability']),(3,3))
    def test_truth_seeker_paladin_only(self):
        g=self.game();listener=g._summon(0,'JAIL_035');neutral=g._summon(0,'EDR_851t');self.play(g,'JAIL_329')
        g.step(Action('attack',g.hero_id(0),g.hero_id(1)))
        self.assertEqual(listener.attack,g.cards['JAIL_035']['attack']+2);self.assertEqual(neutral.attack,1)
    def test_overseer_play_not_summon(self):
        g=self.game();g._summon(0,'JAIL_880');self.play(g,'JAIL_399');played=next(m for m in g.players[0].minions if m.card_id=='JAIL_399')
        self.assertIn('RUSH',played.keywords)
        summoned=g._summon(0,'JAIL_399');g._settle();self.assertNotIn('RUSH',summoned.keywords)
    def test_thunderquake_complete_static_shock(self):
        g=self.game();m=g._summon(1,'CS2_033');self.play(g,'TIME_215');self.assertEqual(m.health,5)
        self.assertEqual(g.players[0].hand[-1].card_id,'TIME_218');self.play(g,'TIME_218',m.uid)
        self.assertEqual(m.health,4);self.assertEqual(g.players[0].temporary_attack,1)
    def test_morbid_both_branches_and_insufficient_corpses(self):
        g=self.game();self.play(g,'EDR_813',branch=0);self.assertEqual([m.card_id for m in g.players[0].minions],['EDR_813at']*2)
        for corpses in (1,2):
            g=self.game();m=g._summon(1,'CS2_033');g.players[0].corpses=corpses
            if corpses<2:
                c=self.put(g,'EDR_813');self.assertFalse(any(a.kind=='play' and a.source==c.uid and a.choices==(1,) for a in g.legal_actions()))
            else:self.play(g,'EDR_813',m.uid,1)
            self.assertEqual(m.health,2 if corpses==2 else 6)
            self.assertEqual(g.players[0].corpses,0 if corpses==2 else 1)
    def test_splintered_counts_only_treants(self):
        g=self.game();g.players[0].death_history=['END_009t','END_009t','EDR_851t'];self.play(g,'END_009')
        self.assertEqual([(m.attack,m.health) for m in g.players[0].minions],[(4,4)]*2)
    def test_nab_kill_shuffles_base_copy_cost_two(self):
        g=self.game();m=g._summon(1,'EDR_851t');self.play(g,'JAIL_225',m.uid)
        copied=[c for c in g.players[0].deck if isinstance(c,Card)];self.assertEqual(len(copied),1)
        self.assertEqual((copied[0].card_id,g._cost(copied[0],0)),('EDR_851t',2));self.assertEqual(len(g.players[0].shuffle_history),1)
    def test_searing_reflection_draw_and_set_copy(self):
        g=self.game();g.players[0].deck=['CS2_033'];self.play(g,'FIR_941');m=g.players[0].minions[0]
        self.assertEqual((m.attack,m.health),(8,8));self.assertIn('DIVINE_SHIELD',m.keywords)
        self.assertEqual(g.players[0].hand[0].card_id,'CS2_033')
    def test_infinitizer_restriction_expires(self):
        g=self.game();m=g._summon(0,'EDR_851t');m.summoned_turn=-1;self.play(g,'TIME_043',m.uid)
        self.assertEqual((m.attack,m.health),(8,8));self.assertNotIn(g.hero_id(1),g._attack_targets(m))
        self.cycle(g);self.assertIn(g.hero_id(1),g._attack_targets(m))
    def test_flash_flood_outcast_reselects_edges(self):
        g=self.game();a=g._summon(1,'EDR_851t');b=g._summon(1,'CS2_033');c=g._summon(1,'EDR_851t')
        self.play(g,'CATA_533');self.assertEqual(g.players[1].minions,[b]);self.assertEqual(b.health,1)
    def test_deja_vu_private_copy_preserves_enchantment(self):
        g=self.game();original=self.put(g,'CS2_033',1);original.attack_bonus=4
        self.play(g,'TIME_039');self.assertEqual(g.observe(1)['pending_choice'],{'owner':0,'waiting':True})
        self.choose(g);copy=g.players[0].hand[0];self.assertNotEqual(copy.uid,original.uid);self.assertEqual(copy.attack_bonus,4)
        self.assertEqual(g.players[1].hand,[original])
    def test_intertwined_two_sequential_choices(self):
        g=self.game();g.players[0].deck=['CS2_033'];g.players[1].deck=['EDR_851t'];self.play(g,'TIME_432')
        self.choose(g);self.assertIsNotNone(g.pending_choice);self.choose(g)
        self.assertEqual([c.card_id for c in g.players[0].hand],['CS2_033','EDR_851t'])
        self.assertEqual(g.players[0].deck,['CS2_033']);self.assertEqual(g.players[1].deck,['EDR_851t'])
    def test_eyes_in_sky_reorders_opponent_deck(self):
        g=self.game();g.players[1].deck=['CS2_033','EDR_851t','CORE_CS2_029'];self.play(g,'TLC_521')
        cid=g.pending_choice['options'][0]['card_id'];self.choose(g);self.assertEqual(g._card_data(g.players[1].deck[-1])['id'],cid)
        self.assertEqual(len(g.players[1].deck),3)
    def test_fast_forward_only_drawn_choices(self):
        g=self.game();old=self.put(g,'CORE_CS2_029');g.players[0].deck=['CS2_033','CORE_CS2_029'];self.play(g,'TIME_770')
        self.assertNotIn(old.uid,[o['uid'] for o in g.pending_choice['options']]);uid=g.pending_choice['options'][0]['uid'];self.choose(g)
        chosen=next(c for c in g.players[0].hand if c.uid==uid);self.assertEqual(g._cost(chosen,0),g.cards[chosen.card_id]['cost']-2)
    def test_dark_bribe_transfers_selected_physical_card(self):
        g=self.game();self.play(g,'JAIL_206');uid=g.pending_choice['options'][0]['uid'];self.choose(g)
        self.assertEqual(len(g.players[0].hand),2);self.assertEqual(g.players[1].hand[0].uid,uid)
    def test_chronogor_extremes_from_own_deck(self):
        g=self.game();g.players[0].deck=['EDR_851t','UNG_810','CS2_033','CORE_CS2_029'];enemy=list(g.players[1].deck)
        self.play(g,'TIME_032');self.assertEqual(len(g.players[0].hand),2);self.assertEqual(len(g.players[1].hand),2)
        self.assertIn('EDR_851t',[c.card_id for c in g.players[1].hand]);self.assertEqual(g.players[1].deck,enemy);self.assertFalse(g.players[0].deck)
    def test_lookout_discount_expires(self):
        g=self.game();self.play(g,'EDR_950');c=g.players[0].hand[0];self.assertEqual(g._cost(c,0),3)
        g.step(Action('end'));self.assertEqual(g._cost(c,0),4)
    def test_raptor_all_choices(self):
        for choice in range(3):
            g=self.game();self.play(g,'TLC_245');self.choose(g,choice);m=g.players[0].minions[0]
            if choice==0:self.assertEqual(m.attack,5)
            elif choice==1:self.assertIn('DIVINE_SHIELD',m.keywords)
            else:
                self.kill(g,m);self.assertEqual([m.card_id for m in g.players[0].minions],['UNG_999t2t1']*2)
    def test_pterrordax_all_choices(self):
        for choice,key in enumerate(('STEALTH','ELUSIVE','WINDFURY')):
            g=self.game();self.play(g,'TLC_246');self.choose(g,choice);m=g.players[0].minions[0]
            self.assertIn(key,g._effective_keywords(m))
            if choice==0:
                g.step(Action('end'));self.assertIn(key,g._effective_keywords(m));g.step(Action('end'));self.assertNotIn(key,g._effective_keywords(m))
    def test_steed_granted_deathrattle(self):
        g=self.game();m=g._summon(0,'EDR_851t');self.play(g,'CORE_UNG_952',m.uid)
        self.assertEqual((m.attack,m.health),(3,7));self.assertIn('TAUNT',m.keywords)
        self.kill(g,m);self.assertEqual(g.players[0].minions[0].card_id,'UNG_810')
    def test_sheep_mask_grants_area_death(self):
        g=self.game();m=g._summon(0,'CS2_033');enemy=g._summon(1,'CS2_033');self.play(g,'DINO_429',m.uid)
        self.assertEqual((m.attack,m.health),(1,1));self.kill(g,m);self.assertEqual(enemy.health,4)
    def test_waveshaping_moves_only_rejected_options(self):
        g=self.game();g.players[0].deck=['EDR_851t','CS2_033','CORE_CS2_029'];self.play(g,'TIME_701')
        cid=g.pending_choice['options'][0]['card_id'];self.choose(g)
        self.assertEqual(g.players[0].hand[0].card_id,cid);self.assertEqual(len(g.players[0].deck),2)
    def test_liferender_health_change_not_armor(self):
        for armor in (0,10):
            g=self.game();g.players[0].armor=armor;g._damage(g.hero_id(0),1);m=g._summon(1,'CS2_033')
            self.play(g,'TIME_614',m.uid if not armor else 0);self.assertEqual(m in g.players[1].board,bool(armor))
    def test_granted_death_silence_copy_and_regrant(self):
        g=self.game();m=g._summon(0,'EDR_851t');self.play(g,'CORE_UNG_952',m.uid)
        copy=g._summon(0,m.card_id,copy_from=m);g._silence(m);self.assertFalse(g._death_operations(m));self.assertTrue(g._death_operations(copy))
        self.play(g,'CORE_UNG_952',m.uid);self.assertTrue(g._death_operations(m));self.kill(g,m)
        self.assertIn('UNG_810',[m.card_id for m in g.players[0].minions])
    def test_nab_waits_for_death_choice(self):
        g=self.game();m=g._summon(0,'JAIL_447');m.health=2
        with patch.dict(DEATH_EFFECTS,{'JAIL_447':[('choose_fixed_summon',('EDR_851t',))]}):
            self.play(g,'JAIL_225',m.uid);self.assertIsNotNone(g.pending_choice);self.assertFalse(g.players[0].shuffle_history)
            self.choose(g);self.assertEqual(len(g.players[0].shuffle_history),1)
    def test_private_choice_failure_rolls_back_rng_and_hand(self):
        g=self.game();self.put(g,'CS2_033',1);self.play(g,'TIME_039');before=deepcopy(g.__dict__)
        with patch.object(Game,'assert_invariants',side_effect=RuntimeError('injected')):
            with self.assertRaises(RuntimeError):self.choose(g)
        self.assertEqual(g.pending_choice,before['pending_choice']);self.assertEqual(g.rng.getstate(),before['rng'].getstate());self.assertFalse(g.players[0].hand)
    def test_full_hand_burned_draw_not_offered(self):
        g=self.game()
        for _ in range(9):self.put(g,'EDR_851t')
        self.play(g,'TIME_770');self.assertEqual(len(g.pending_choice['options']),1);self.choose(g);self.assertEqual(len(g.players[0].hand),10)
    def test_new_state_serializes(self):
        g=self.game();self.play(g,'TLC_246');self.choose(g);json.dumps(g.observe(0));json.dumps(g.observe(1))

    def test_rotten_apple_first_tick_is_end_of_play_turn(self):
        g=self.game();g.players[0].health=10;self.play(g,'EDR_482');g.step(Action('end'))
        self.assertEqual(g.players[0].health,19)
    def test_silence_removes_temporary_immunity(self):
        g=self.game();g.players[0].previous_tribes={'DRAGON'};self.play(g,'TLC_243');m=g.players[0].minions[0]
        g._silence(m);self.assertNotIn('IMMUNE',g._effective_keywords(m));g._damage(m.uid,1);self.assertEqual(m.health,7)
    def test_pterrordax_attacking_breaks_temporary_stealth(self):
        g=self.game();self.play(g,'TLC_246');self.choose(g);m=g.players[0].minions[0];m.summoned_turn=-1
        g.step(Action('attack',m.uid,g.hero_id(1)));self.assertNotIn('STEALTH',g._effective_keywords(m))
    def test_liferender_heal_and_turn_reset(self):
        g=self.game();g.players[0].health=20;g._heal(g.hero_id(0),1,healer=0)
        self.assertTrue(g.players[0].hero_health_changed_turn);self.cycle(g);self.assertFalse(g.players[0].hero_health_changed_turn)
    def test_nab_survivor_and_shield_do_not_shuffle(self):
        for shield in (False,True):
            g=self.game();m=g._summon(1,'CS2_033')
            if shield:m.keywords.add('DIVINE_SHIELD')
            self.play(g,'JAIL_225',m.uid);self.assertFalse(g.players[0].shuffle_history)
    def test_copied_granted_death_effects_are_independent(self):
        g=self.game();m=g._summon(0,'EDR_851t');self.play(g,'CORE_UNG_952',m.uid)
        clone=g._summon(0,m.card_id,copy_from=m);g._silence(m);self.kill(g,clone)
        self.assertEqual(sum(x.card_id=='UNG_810' for x in g.players[0].minions),1)
    def test_searing_reflection_does_not_trigger_battlecry(self):
        g=self.game();g.players[0].deck=['END_006'];self.play(g,'FIR_941')
        self.assertEqual(g.players[0].temporary_attack,0);self.assertFalse(g.players[0].scheduled_effects)
    def test_stormdrake_without_kindred(self):
        g=self.game();self.play(g,'TLC_243');self.assertNotIn('IMMUNE',g._effective_keywords(g.players[0].minions[0]))
    def test_empty_zone_choice_continues_to_other_deck(self):
        g=self.game();g.players[0].deck=[];g.players[1].deck=['CS2_033'];self.play(g,'TIME_432')
        self.assertEqual(g.pending_choice['zone_owner'],1);self.choose(g);self.assertEqual(len(g.players[0].hand),1)
    def test_dark_bribe_full_enemy_hand_burns_chosen_card(self):
        g=self.game()
        for _ in range(10):self.put(g,'EDR_851t',1)
        self.play(g,'JAIL_206');self.choose(g);self.assertEqual(len(g.players[0].hand),2);self.assertEqual(len(g.players[1].hand),10)

    def test_reset_cost_replaces_older_temporary_discount(self):
        g=self.game();self.play(g,'EDR_950');card=g.players[0].hand[0]
        self.assertEqual(g._cost(card,0),3);self.play(g,'TIME_057');self.assertEqual(g._cost(card,0),4)
