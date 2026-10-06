import unittest
from unittest.mock import patch
from expanded.cards import DEATH_EFFECTS
from expanded import Game,Action,random_deck
from expanded.game import Card
from expanded.batch30_cards import RULES


class ThirtyCardBatchTests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('PALADIN',31),random_deck('MAGE',53)],seed=71)
        g.step(Action('mulligan'));g.step(Action('mulligan'))
        for p in g.players:
            p.hand=[];p.board=[];p.deck=['CORE_CS2_029']*20;p.health=30;p.mana=p.max_mana=10;p.armor=0
        return g
    def put(self,g,cid,owner=0):
        c=Card(g._new_id(),cid);g.players[owner].hand.append(c);return c
    def play(self,g,cid,target=None,choice=None):
        g.players[g.current].mana=10;c=self.put(g,cid,g.current)
        options=[a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid]
        if target is not None:options=[a for a in options if a.target==target]
        if choice is not None:options=[a for a in options if a.choices==(choice,)]
        self.assertTrue(options,(cid,target,choice));g.step(options[0]);return c
    def kill(self,g,m):m.health=0;g._settle(allow_event_choices=True)
    def test_batch_has_thirty_new_collectibles(self):self.assertEqual(len(RULES),30)
    def test_barrier_targets_hero_and_buffs_hand(self):
        g=self.game();c=self.put(g,'CS2_033');self.play(g,'TIME_447',g.hero_id(0))
        self.assertTrue(g.players[0].divine_shield);self.assertEqual(c.health_bonus,2)
    def test_legacy_deck_condition(self):
        for has_minion in (False,True):
            g=self.game();c=self.put(g,'CS2_033')
            if has_minion:g.players[0].deck.append('CS2_033')
            self.play(g,'TIME_449');self.assertEqual(g.players[0].temporary_attack,4)
            self.assertEqual(c.attack_bonus,0 if has_minion else 4)
    def test_spirit_power_condition(self):
        for active in (False,True):
            g=self.game();g.players[0].power_used=active;self.play(g,'FIR_777');m=g.players[0].minions[0]
            self.assertEqual(m.attack,g.cards[m.card_id]['attack']+(3 if active else 0))
    def test_chameleon_condition_and_target(self):
        g=self.game();m=g._summon(0,'CS2_033');g.players[0].power_used=True
        self.play(g,'FIR_908',m.uid);self.assertEqual((m.attack,m.health),(4,8));self.assertIn('RUSH',m.keywords)
        g=self.game();m=g._summon(0,'CS2_033');self.play(g,'FIR_908',0);self.assertEqual(m.attack,3)
    def test_wildspeaker_last_turn_condition(self):
        for prior in (False,True):
            g=self.game();g.players[0].minion_played_last_turn=prior;cost=g.cards['MEND_041']['cost']
            self.play(g,'MEND_041');self.assertEqual(g.players[0].mana,min(10,10-cost+(0 if prior else 3)))
    def test_heartroot_last_turn_condition(self):
        for prior in (False,True):
            g=self.game();g.players[0].minion_played_last_turn=prior;self.play(g,'MEND_043')
            self.assertEqual(g.players[0].armor,3 if prior else 6);self.assertEqual(len(g.players[0].hand),1 if prior else 2)
    def test_minion_history_survives_opponent_turn(self):
        g=self.game();self.play(g,'FIR_777');g.step(Action('end'));g.step(Action('end'))
        self.assertTrue(g.players[0].minion_played_last_turn);self.assertFalse(g.players[0].minion_played_this_turn)
    def test_starsurge_death_history(self):
        g=self.game();g.players[0].death_history=['CS2_033']*2;m=g._summon(1,'CS2_033')
        self.play(g,'EDR_941',m.uid);self.assertEqual(m.health,3)
    def test_knockback_shuffle_history(self):
        g=self.game();g._record_deck_insertion(0,0,10,'shuffle');m=g._summon(1,'CS2_033')
        self.play(g,'TLC_517',m.uid);self.assertEqual(m.health,4)
    def test_moonkin_counts_wisps(self):
        g=self.game();self.play(g,'EDR_940');g._summon(0,'EDR_851t');g.step(Action('end'))
        self.assertEqual(g.players[0].armor,2)
    def test_tindral_own_and_enemy_turn(self):
        for turn,amount in ((0,1),(1,4)):
            g=self.game();m=g._summon(0,'FIR_958');g.current=turn;self.kill(g,m)
            self.assertEqual(g.players[1].health,30-amount)
    def test_manifested_timeways_aura_condition(self):
        for active in (False,True):
            g=self.game()
            if active:self.play(g,'TIME_700')
            self.play(g,'TIME_019');self.assertEqual(g.players[1].health,27 if active else 30)
    def test_augur_equalizes_modified_hand_stats(self):
        g=self.game();c=self.put(g,'CS2_033');c.attack_bonus=5;self.play(g,'TIME_429')
        self.assertEqual((g._card_stat(c,'attack'),g._card_stat(c,'health')),(8,8))
    def test_truthseeker_resets_both_hands(self):
        g=self.game();a=self.put(g,'CORE_CS2_029');b=self.put(g,'CS2_033',1);a.cost_delta=-2;g._set_card_cost(b,1)
        self.play(g,'TIME_057');self.assertEqual(g._cost(a,0),g.cards[a.card_id]['cost']);self.assertEqual(g._cost(b,1),g.cards[b.card_id]['cost'])
    def test_ratcatcher_copies_spells_and_draws_one_on_death(self):
        g=self.game();g.players[0].deck=['CORE_CS2_029','CS2_033'];self.play(g,'JAIL_882')
        self.assertEqual([g._card_data(c)['id'] for c in g.players[0].deck].count('CORE_CS2_029'),2)
        self.kill(g,g.players[0].minions[0]);self.assertEqual(g.players[0].hand[0].card_id,'CORE_CS2_029')
    def test_imp_stooge_bottom_cards_and_playability(self):
        g=self.game();m=g._summon(0,'JAIL_399');self.kill(g,m)
        self.assertEqual([c.card_id for c in g.players[0].deck[:2]],['JAIL_399t1']*2)
        self.play(g,'JAIL_399t1');self.assertTrue({'TAUNT','LIFESTEAL'}<=g.players[0].minions[0].keywords)
    def test_detective_clothes_effect(self):
        g=self.game();m=g._summon(0,'JAIL_447');self.kill(g,m);self.assertEqual(g.players[0].hand[0].card_id,'JAIL_447t')
        m=g._summon(0,'CS2_033');self.play(g,'JAIL_447t',m.uid)
        self.assertEqual((m.attack,m.health),(7,10));self.assertIn('RUSH',m.keywords)
    def test_tankgineer_generates_complete_tank(self):
        g=self.game();m=g._summon(0,'TIME_017');self.kill(g,m);tank=g.players[0].minions[0]
        self.assertEqual((tank.card_id,tank.attack,tank.health),('GVG_079',7,7));self.assertIn('DIVINE_SHIELD',tank.keywords)
    def test_harbinger_doomsayer_start_trigger(self):
        g=self.game();m=g._summon(0,'TIME_EVENT_300');self.kill(g,m)
        self.assertEqual(g.players[0].minions[0].card_id,'NEW1_021')
        g.step(Action('end'));g.step(Action('end'));self.assertFalse(g.players[0].board)
    def test_greatwolf_both_choices(self):
        g=self.game();self.play(g,'EDR_263',choice=0);self.assertEqual(g.players[1].health,26)
        g=self.game();self.play(g,'EDR_263',choice=1);self.assertEqual(len(g.players[0].minions),2)
        self.assertTrue(all('RUSH' in m.keywords for m in g.players[0].minions))
    def test_spirit_bond_kill_and_survival(self):
        for health in (2,6):
            g=self.game();m=g._summon(1,'CS2_033');m.health=health;self.play(g,'EDR_262',m.uid)
            self.assertEqual(len(g.players[0].board),1 if health==2 else 0)
    def test_sleep_paralysis_both_choices(self):
        g=self.game();self.play(g,'EDR_490',choice=0)
        self.assertEqual(len(g.players[0].board),2);self.assertTrue(all('CANT_ATTACK' in m.keywords for m in g.players[0].minions))
        g=self.game();m=g._summon(1,'CS2_033');self.play(g,'EDR_490',m.uid,1);self.assertFalse(g.players[1].board)
    def test_web_bounces_then_summons(self):
        g=self.game();m=g._summon(0,'CS2_033');self.play(g,'EDR_523',m.uid)
        self.assertEqual([x.card_id for x in g.players[0].minions],['EDR_523t']);self.assertEqual(g.players[0].hand[0].card_id,'CS2_033')
    def test_divination_requires_friendly_wisp(self):
        g=self.game();m=g._summon(0,'EDR_851t');other=g._summon(0,'CS2_033');c=self.put(g,'EDR_804')
        self.assertEqual({a.target for a in g.legal_actions() if a.kind=='play' and a.source==c.uid},{m.uid})
        self.play(g,'EDR_804',m.uid);self.assertEqual(len(g.players[0].hand),4);self.assertIn(other,g.players[0].board)
    def test_carnassa_full_dependency_chain(self):
        g=self.game();self.play(g,'TLC_826');self.assertEqual(sum(g._card_data(c)['id']=='UNG_920t2' for c in g.players[0].deck),10)
        self.play(g,'UNG_920t2');self.assertEqual(len(g.players[0].hand),1)
    def test_ecologist_generated_spell_both_relations(self):
        g=self.game();m=g._summon(0,'TLC_820');self.kill(g,m);self.assertEqual(g.players[0].hand[0].card_id,'TLC_813')
        a=g._summon(0,'CS2_033');b=g._summon(1,'CS2_033');self.play(g,'TLC_813',a.uid);self.play(g,'TLC_813',b.uid)
        self.assertEqual((a.health,b.health),(8,4))
    def test_charity_copies_only_current_turn(self):
        g=self.game();m=g._summon(0,'CS2_033');self.kill(g,m)
        g.players[0].death_records.append(dict(turn=g.turn-1,card_id='CORE_EX1_509'))
        self.play(g,'MEND_805');self.assertEqual([c.card_id for c in g.players[0].hand],['CS2_033'])
        self.assertEqual((g.players[0].hand[0].attack_bonus,g.players[0].hand[0].health_bonus),(3,3))
    def test_eternus_controls_eligible_target(self):
        g=self.game();m=g._summon(1,'CORE_WON_351');self.play(g,'TIME_435',m.uid)
        self.assertEqual(m.owner,0);self.assertIn(m,g.players[0].board);self.assertEqual(m.summoned_turn,g.turn)
    def test_sentry_deck_condition(self):
        for neutral in (False,True):
            g=self.game()
            if neutral:g.players[0].deck.append('CORE_WON_351')
            self.play(g,'JAIL_035');self.assertEqual(len(g.players[0].board),1 if neutral else 3)
    def test_meadowstrider_bottom_cost(self):
        g=self.game();m=g._summon(0,'EDR_978');self.kill(g,m);c=g.players[0].deck[0]
        self.assertEqual(c.card_id,'EDR_978');self.assertEqual(g._cost(c,0),1)
    def test_widow_chain_complete(self):
        g=self.game();self.play(g,'JAIL_436');self.assertEqual(g.players[0].hand[-1].card_id,'JAIL_436t')
        self.play(g,'JAIL_436t');self.assertEqual(g.players[0].hand[-1].card_id,'JAIL_436t2')
        self.play(g,'JAIL_436t2');self.assertEqual((g.players[0].temporary_attack,g.players[0].armor),(7,7))

    def test_spirit_bond_waits_for_death_choice(self):
        g=self.game();m=g._summon(0,'JAIL_447');m.health=2
        with patch.dict(DEATH_EFFECTS,{'JAIL_447':[('choose_fixed_summon',('CS2_033',))]}):
            self.play(g,'EDR_262',m.uid)
            self.assertIsNotNone(g.pending_choice)
            self.assertFalse(any(x.card_id=='EDR_850pe' for x in g.players[0].minions))
            g.step(next(a for a in g.legal_actions() if a.kind=='choose'))
            self.assertEqual([x.card_id for x in g.players[0].minions].count('EDR_850pe'),1)
    def test_spirit_bond_shield_prevents_kill(self):
        g=self.game();m=g._summon(1,'EDR_851t');m.keywords.add('DIVINE_SHIELD')
        self.play(g,'EDR_262',m.uid);self.assertIn(m,g.players[1].board);self.assertFalse(g.players[0].board)
    def test_charity_burns_excess_copies(self):
        g=self.game()
        for _ in range(3):self.kill(g,g._summon(0,'EDR_851t'))
        for _ in range(9):self.put(g,'CORE_CS2_029')
        self.play(g,'MEND_805');self.assertEqual(len(g.players[0].hand),10)
        self.assertEqual(sum(c.card_id=='EDR_851t' for c in g.players[0].hand),1)
    def test_conditional_summon_splits_without_rechecking_condition(self):
        g=self.game();op,tail=g._split_fixed_summon(('when_state','no_neutral_in_deck',('summon','JAIL_035',2)),{'owner':0})
        self.assertEqual(op,('summon','JAIL_035',1));self.assertEqual(tail,(('summon','JAIL_035',1),))
    def test_eternus_hand_health_buff_allows_larger_target(self):
        g=self.game();m=g._summon(1,'CS2_033');c=self.put(g,'TIME_435');c.health_bonus=10
        action=next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid and a.target==m.uid)
        g.step(action);self.assertEqual(m.owner,0)
