"""Stored physical cards survive only their explicit zone/identity contracts."""
import copy,json,unittest
import test_expanded_generation as fixtures
from expanded import Action
from expanded.cards import COLLECTIBLE_IDS,registry
from expanded.stored_cards import RULES,TOKEN_IDS
from engine.game import Card

class StoredCardTests(unittest.TestCase):
    def setUp(self):self.h=fixtures.GenerationTests();self.g=self.h.game()
    def add(self,cid,owner=0):
        c=Card(self.g._new_id(),cid);self.g._enter_hand(owner,c);return c
    def play_card(self,c,target=0):
        self.g.players[0].mana=10
        self.g.step(max((a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid and a.target==target),key=lambda a:a.position))
    def play(self,cid,target=0):
        c=self.add(cid);self.play_card(c,0 if cid=='EDR_454' else target)
        if cid=='EDR_454' and target:self.g.step(Action('activate',self.g.players[0].locations[-1].uid,target))
        return c
    def kill(self,m):m.health=0;self.g._settle()
    def cycle(self):self.g.step(Action('end'));self.g.step(Action('end'))
    def test_live_registry_and_tokens(self):
        self.assertTrue(set(RULES)-TOKEN_IDS<=COLLECTIBLE_IDS);self.assertTrue(TOKEN_IDS<=registry().keys())
    def test_slime_captures_each_players_original_minions(self):
        self.g._summon(0,'CORE_CS2_188');self.g._summon(1,'CORE_EX1_012')
        self.play('CAP_805')
        self.assertFalse(self.g.players[0].minions+self.g.players[1].minions)
        self.assertEqual(self.g.players[0].hand[-1]._resummon_ids,['CORE_CS2_188'])
        self.assertEqual(self.g.players[1].hand[-1]._resummon_ids,['CORE_EX1_012'])
        self.play_card(self.g.players[0].hand[-1]);self.assertEqual(self.g.players[0].minions[0].card_id,'CORE_CS2_188')
    def test_slime_resummons_base_stats_without_battlecry(self):
        m=self.g._summon(0,'TIME_004');self.g._buff(m,3,3);self.play('CAP_805');self.play_card(self.g.players[0].hand[-1])
        self.assertEqual(self.g.players[0].minions[0].attack,self.g.cards['TIME_004']['attack'])
        self.assertEqual(self.g.players[1].health,30);self.assertIsNone(self.g.pending_choice)
    def test_slime_does_not_capture_dormant_minions(self):
        m=self.g._summon(1,'EDR_851t');self.g._sleep_minion(m,2);self.play('CAP_805')
        self.assertIn(m,self.g.players[1].board);self.assertEqual(self.g.players[1].hand[-1]._resummon_ids,[])
    def test_plain_ectoplasm_has_no_invented_payload(self):
        self.play('CAP_805t');self.assertFalse(self.g.players[0].minions)
    def test_slime_created_spell_copy_keeps_payload(self):
        self.g._summon(0,'EDR_851t');self.play('CAP_805')
        c=self.g._copy_card(self.g.players[0].hand[-1]);self.g._enter_hand(0,c);self.play_card(c)
        self.assertEqual(len(self.g.players[0].minions),1)
    def test_iso_devours_without_discard_and_returns_after_death(self):
        for cid in ('CORE_CS2_029','CORE_CS2_188','TOKEN_COIN'):self.add(cid,1)
        self.play('CATA_481');m=self.g.players[0].all_minions[0]
        self.assertEqual(m.dormant,2);self.assertEqual(len(self.g.players[1].hand),1)
        self.assertFalse(self.g.players[1].discard_history)
        self.g._awaken(m);self.kill(m);self.assertEqual(len(self.g.players[1].hand),3)
    def test_iso_awakens_after_two_owner_starts(self):
        self.play('CATA_481');m=self.g.players[0].all_minions[0]
        self.cycle();self.assertEqual(m.dormant,1);self.cycle();self.assertFalse(m.dormant)
    def test_iso_returns_physical_enchantments(self):
        c=self.add('CORE_CS2_188',1);c.attack_bonus=4;c.cost_delta=-1
        self.play('CATA_481');m=self.g.players[0].all_minions[0];self.g._awaken(m);self.kill(m)
        returned=self.g.players[1].hand[0];self.assertEqual((returned.attack_bonus,returned.cost_delta),(4,-1))
    def test_iso_silence_erases_bound_cards(self):
        self.add('CORE_CS2_188',1);self.play('CATA_481');m=self.g.players[0].all_minions[0]
        self.g._awaken(m);self.g._silence(m);self.kill(m);self.assertFalse(self.g.players[1].hand)
    def test_iso_does_not_publish_devoured_card_identity(self):
        self.add('CORE_CS2_188',1);self.play('CATA_481')
        view=self.g.observe(0);self.assertEqual(view['players'][0]['board'][0]['devoured_count'],1)
        self.assertNotIn('_devoured_cards',json.dumps(view));self.assertNotIn('CORE_CS2_188',json.dumps(view['players'][0]['board']))
    def test_egg_only_targets_friendly_dragons(self):
        dragon=self.g._summon(0,'EDR_453');other=self.g._summon(0,'EDR_851t');enemy=self.g._summon(1,'EDR_453')
        self.play('EDR_454');targets=[a.target for a in self.g.legal_actions() if a.kind=='activate']
        self.assertEqual(set(targets),{dragon.uid})
    def test_egg_copies_snapshot_not_later_target_changes(self):
        m=self.g._summon(0,'EDR_453');self.g._buff(m,2,3);self.play('EDR_454',m.uid)
        egg=self.g.players[0].minions[-1];self.g._buff(m,9,9);self.kill(egg)
        copy_m=self.g.players[0].minions[-1];self.assertEqual((copy_m.attack,copy_m.max_health),(14,10))
    def test_egg_silence_removes_bound_summon(self):
        m=self.g._summon(0,'EDR_453');self.play('EDR_454',m.uid);egg=self.g.players[0].minions[-1]
        self.g._silence(egg);self.kill(egg);self.assertEqual(len(self.g.players[0].minions),1)
    def test_copied_egg_retains_bound_summon(self):
        m=self.g._summon(0,'EDR_453');self.play('EDR_454',m.uid);egg=self.g.players[0].minions[-1]
        cloned=self.g._summon(0,egg.card_id,copy_from=egg);self.kill(cloned)
        self.assertEqual(sum(x.card_id=='EDR_453' for x in self.g.players[0].minions),2)
    def test_toru_replaces_only_minions_preserving_positions(self):
        a=self.add('CORE_CS2_188');b=self.add('TOKEN_COIN');c=self.add('CORE_EX1_012');self.play('TLC_841')
        self.assertEqual([x.card_id for x in self.g.players[0].hand],['TLC_841t','TOKEN_COIN','TLC_841t'])
        self.assertEqual(self.g._cost(self.g.players[0].hand[0],0),1)
    def test_toru_releases_buffed_minion_without_battlecry(self):
        c=self.add('TIME_004');c.attack_bonus=2;self.play('TLC_841');jar=self.g.players[0].hand[0];self.play_card(jar)
        self.kill(self.g.players[0].minions[-1]);m=self.g.players[0].minions[-1]
        self.assertEqual(m.card_id,'TIME_004');self.assertEqual(m.attack,self.g.cards[m.card_id]['attack']+2)
        self.assertEqual(self.g.players[1].health,30);self.assertIsNone(self.g.pending_choice)
    def test_toru_can_jar_another_jar(self):
        self.add('EDR_851t');self.play('TLC_841');self.play('TLC_841');self.play_card(self.g.players[0].hand[0])
        jar=self.g.players[0].minions[-1];self.kill(jar)
        inner=self.g.players[0].minions[-1];self.assertEqual(inner.card_id,'TLC_841t');self.kill(inner)
        self.assertEqual(self.g.players[0].minions[-1].card_id,'EDR_851t')
    def test_plain_jar_is_empty(self):
        m=self.g._summon(0,'TLC_841t');self.kill(m);self.assertFalse(self.g.players[0].minions)
    def test_togwaggle_preserves_both_hand_sizes_and_total_cards(self):
        for cid in ('TOKEN_COIN','CORE_CS2_029'):self.add(cid)
        for cid in ('CORE_CS2_188','CORE_EX1_012','EDR_851t'):self.add(cid,1)
        before={c.uid for p in self.g.players for c in p.hand};self.play('JAIL_852')
        self.assertEqual([len(p.hand) for p in self.g.players],[2,3])
        self.assertEqual({c.uid for p in self.g.players for c in p.hand},before)
        self.assertTrue(all(not p.shuffle_history and not p.discard_history for p in self.g.players))
    def test_togwaggle_keeps_enchantments(self):
        c=self.add('CORE_CS2_188');c.attack_bonus=5;self.play('JAIL_852')
        self.assertEqual(self.g.players[0].hand[0].attack_bonus,5)
    def test_fins_restores_exact_original_hand(self):
        self.g.players[0]._starting_hand=[Card(50000,'TOKEN_COIN'),Card(50001,'EDR_851t')]
        original=self.add('CORE_CS2_188');original.attack_bonus=3
        self.play('TIME_706');self.assertEqual([c.card_id for c in self.g.players[0].hand],['TOKEN_COIN','EDR_851t'])
        self.play_card(self.g.players[0].hand[0]);self.g.step(Action('end'))
        self.assertEqual(self.g.players[0].hand,[original]);self.assertEqual(original.attack_bonus,3)
    def test_fins_snapshot_excludes_first_turn_draw(self):
        g=self.h.game()
        self.assertEqual(sorted(len(getattr(p,'_starting_hand')) for p in g.players),[3,5])
    def test_starting_hand_and_set_aside_cards_are_private(self):
        self.g.players[0]._starting_hand=[Card(50000,'EDR_851t')];self.add('CORE_CS2_188');self.play('TIME_706')
        own=self.g.observe(0)['players'][0];enemy=self.g.observe(1)['players'][0]
        self.assertEqual(own['set_aside_cards'][0]['cards'],['CORE_CS2_188'])
        self.assertNotIn('set_aside_cards',enemy);self.assertNotIn('starting_hand',enemy)
        json.dumps(self.g.observe(0));json.dumps(self.g.observe(1))
    def test_runi_returns_after_two_owner_starts_with_buffs(self):
        c=self.add('CORE_CS2_188');c.attack_bonus=2;coin=self.add('TOKEN_COIN');self.play('TIME_EVENT_998')
        self.assertEqual(self.g.players[0].hand,[coin]);self.cycle();self.assertNotIn(c,self.g.players[0].hand)
        self.cycle();self.assertIn(c,self.g.players[0].hand);self.assertEqual((c.attack_bonus,c.health_bonus),(7,5))
    def test_runi_delayed_cards_do_not_trigger_discard(self):
        self.add('CORE_CS2_188');self.play('TIME_EVENT_998');self.assertFalse(self.g.players[0].discard_history)
    def test_nythendra_beetle_count_uses_attack(self):
        m=self.g._summon(0,'EDR_818');self.g._set_minion_attack(m,3);self.kill(m)
        self.assertEqual([x.card_id for x in self.g.players[0].minions],['EDR_818t']*3)
    def test_nythendra_reforms_using_surviving_beetle_stats(self):
        m=self.g._summon(0,'EDR_818');self.g._set_minion_attack(m,3);self.kill(m)
        beetles=list(self.g.players[0].minions);self.kill(beetles[0]);self.g._buff(beetles[1],2,3);self.cycle()
        self.assertEqual(len(self.g.players[0].minions),1);m=self.g.players[0].minions[0]
        self.assertEqual((m.card_id,m.attack,m.health),('EDR_818',4,5))
        self.assertFalse(any(a.kind=='attack' and a.source==m.uid for a in self.g.legal_actions()))
    def test_beetle_reform_does_not_make_corpses_or_deaths(self):
        self.g._summon(0,'EDR_818t');self.g._summon(0,'EDR_818t');before=self.g.players[0].corpses
        self.cycle();self.assertEqual(self.g.players[0].corpses,before);self.assertFalse(self.g.players[0].death_history)
    def test_silencing_all_beetles_stops_reform(self):
        m=self.g._summon(0,'EDR_818t');self.g._silence(m);self.cycle();self.assertEqual(m.card_id,'EDR_818t')
    def test_reborn_history_records_actual_rebirth_only(self):
        m=self.g._summon(0,'EDR_851t');m.keywords.add('REBORN');self.kill(m)
        self.assertEqual(self.g.players[0].reborn_history,['EDR_851t'])
        self.kill(self.g.players[0].minions[0]);self.assertEqual(self.g.players[0].reborn_history,['EDR_851t'])
    def test_raith_summons_reborn_history_and_attacks_minions(self):
        self.g.players[0].reborn_history=['EDR_851t','EDR_851t'];enemy=self.g._summon(1,'EX1_tk34')
        self.play('CAP_806');self.assertEqual(enemy.health,4)
        self.assertEqual(self.g.players[1].health,30)
    def test_raith_no_enemy_minions_does_not_attack_hero(self):
        self.g.players[0].reborn_history=['CORE_CS2_188'];self.play('CAP_806')
        self.assertEqual(len(self.g.players[0].minions),2);self.assertEqual(self.g.players[1].health,30)
    def test_frostmourne_remembers_final_hit_before_break(self):
        self.play('CORE_RLK_086');self.g.players[0].weapon['durability']=1
        m=self.g._summon(1,'EDR_851t');self.g.step(Action('attack',self.g.hero_id(0),m.uid))
        self.assertIsNone(self.g.players[0].weapon);self.assertEqual([x.card_id for x in self.g.players[0].minions],['EDR_851t'])
    def test_frostmourne_does_not_remember_shielded_survivor(self):
        self.play('CORE_RLK_086');self.g.players[0].weapon['durability']=1
        m=self.g._summon(1,'EDR_851t');m.keywords.add('DIVINE_SHIELD')
        self.g.step(Action('attack',self.g.hero_id(0),m.uid));self.assertFalse(self.g.players[0].minions)
    def test_frostmourne_replacement_releases_kills(self):
        self.play('CORE_RLK_086');m=self.g._summon(1,'EDR_851t');self.g.step(Action('attack',self.g.hero_id(0),m.uid))
        self.play('CORE_RLK_086');self.assertEqual([x.card_id for x in self.g.players[0].minions],['EDR_851t'])
        self.assertFalse(self.g.players[0].weapon.get('stored_kills'))
    def light_fire(self,card):
        self.play('CATA_EVENT_001')
        index=next(i for i,o in enumerate(self.g.pending_choice['options']) if o['uid']==card.uid)
        self.g.step(Action('choose',choices=(index,)))
    def test_phoenix_discards_at_third_owner_end(self):
        card=self.add('CORE_CS2_188');self.light_fire(card)
        self.cycle();self.assertIn(card,self.g.players[0].hand)
        self.cycle();self.assertIn(card,self.g.players[0].hand)
        self.g.step(Action('end'));self.assertNotIn(card,self.g.players[0].hand)
        self.assertEqual(self.g.players[0].discard_history,['CORE_CS2_188'])
        self.assertEqual(sum(m.card_id=='CATA_EVENT_001' for m in self.g.players[0].minions),2)
    def test_phoenix_playing_burning_card_cancels_its_timer(self):
        c=self.add('TOKEN_COIN');self.light_fire(c);self.play_card(c)
        for _ in range(3):self.cycle()
        self.assertFalse(self.g.players[0].discard_history)
        self.assertEqual(sum(m.card_id=='CATA_EVENT_001' for m in self.g.players[0].minions),1)
    def test_phoenix_payload_survives_source_death(self):
        c=self.add('TOKEN_COIN');self.light_fire(c);self.kill(self.g.players[0].minions[0])
        for _ in range(3):self.cycle()
        self.assertEqual(sum(m.card_id=='CATA_EVENT_001' for m in self.g.players[0].minions),1)
    def test_phoenix_empty_hand_has_no_choice(self):
        self.play('CATA_EVENT_001');self.assertIsNone(self.g.pending_choice)
    def test_phoenix_choices_and_hidden_snapshot_do_not_leak(self):
        c=self.add('CORE_CS2_188');self.play('CATA_EVENT_001')
        self.assertEqual(self.g.observe(1)['pending_choice'],{'owner':0,'waiting':True})
        json.dumps(self.g.observe(0));json.dumps(self.g.observe(1))
        self.g.step(Action('choose',choices=(0,)))
        self.assertEqual(self.g.observe(0)['players'][0]['hand'][0]['phoenix_turns_remaining'],[3])
        self.assertNotIn('_phoenix_fires',json.dumps(self.g.observe(0)))
    def test_phoenix_timer_not_duplicated_by_end_turn_repeat(self):
        c=self.add('TOKEN_COIN');self.light_fire(c)
        self.g.players[0].end_repeat_expiries=[100];self.cycle()
        self.assertEqual(c._phoenix_fires[0]['remaining'],2)
    def test_location_can_activate_twice_with_normal_cooldown(self):
        dragon=self.g._summon(0,'EDR_453');self.play('EDR_454',dragon.uid)
        location=self.g.players[0].locations[0]
        self.assertFalse(any(a.kind=='activate' and a.source==location.uid for a in self.g.legal_actions()))
        self.cycle();self.assertFalse(any(a.kind=='activate' and a.source==location.uid for a in self.g.legal_actions()))
        self.cycle();self.g.step(Action('activate',location.uid,dragon.uid))
        self.assertNotIn(location,self.g.players[0].board)
        self.assertEqual(sum(m.card_id=='EDR_454t' for m in self.g.players[0].minions),2)
    def test_bound_jar_counts_as_deathrattle_in_hand_and_board(self):
        self.add('EDR_851t');self.play('TLC_841');jar=self.g.players[0].hand[0]
        self.assertIn('DEATHRATTLE',self.g._card_mechanics(jar));self.play_card(jar)
        self.assertIn('DEATHRATTLE',self.g._effective_keywords(self.g.players[0].minions[-1]))
    def test_stored_views_are_encoded_for_learning(self):
        from expanded.features import encode_decision,SCHEMA
        self.g.players[0].reborn_history=['EDR_851t'];self.add('CORE_CS2_188');self.play('TIME_EVENT_998')
        view=self.g.observe(0)
        rows=encode_decision(dict(observation=view,actor=0,actions=view['legal_actions']))
        self.assertIn('set_aside_cards',str(rows));self.assertIn('reborn_history',str(rows))
        self.assertEqual(SCHEMA,'visible-action-features-v58')
    def test_clone_retains_private_delayed_hand_and_timer(self):
        c=self.add('CORE_CS2_188');self.play('TIME_EVENT_998');clone=copy.deepcopy(self.g)
        for g in (self.g,clone):
            for _ in range(4):g.step(Action('end'))
        self.assertEqual(self.g.observe(0),clone.observe(0))
    def test_runi_burns_returns_when_hand_full(self):
        c=self.add('CORE_CS2_188');self.play('TIME_EVENT_998')
        for _ in range(10):self.add('TOKEN_COIN')
        self.cycle();self.cycle();self.assertNotIn(c,self.g.players[0].hand)
        self.assertEqual(len(self.g.players[0].hand),10)
