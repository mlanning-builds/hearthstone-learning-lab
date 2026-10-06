"""Local-only scenarios for the first staged 200-card milestone group."""
import unittest
from unittest.mock import patch
from expanded import Game, Action, random_deck
from expanded.game import Card
from expanded.cards import COLLECTIBLE_IDS


class MilestoneTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('WARRIOR',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
        for p in self.g.players:
            p.hand=[];p.deck=['CORE_CS2_029']*10;p.mana=p.max_mana=10

    def give(self,cid,owner=0):
        c=Card(self.g._new_id(),cid);self.g.players[owner].hand.append(c);return c

    def play(self,cid,target=0):
        c=self.give(cid)
        position=len(self.p.board) if self.g.cards[cid]['type'] in ('MINION','LOCATION') else -1
        self.g.step(Action('play',c.uid,target,position));return c

    def summon(self,cid='Core_CS2_200',owner=0):return self.g._summon(owner,cid)

    def kill(self,m):m.health=0;self.g._settle()

    def test_zero_attack_tutor_uses_deck_enchantments(self):
        buffed=Card(self.g._new_id(),'TLC_237',attack_bonus=1)
        self.p.deck=[buffed,'DINO_130','CORE_CS2_029']
        self.play('DINO_411')
        self.assertEqual([c.card_id for c in self.p.hand],['DINO_130'])
        self.assertIn(buffed,self.p.deck)

    def test_filtered_death_draws_select_correct_type_and_cost(self):
        self.p.deck=['EDR_476','FIR_778','Core_CS2_200','CORE_CS2_029']
        self.kill(self.summon('EDR_571'));self.kill(self.summon('EDR_485'))
        self.assertEqual([c.card_id for c in self.p.hand],['EDR_476','FIR_778'])

    def test_empty_filtered_draw_does_not_fatigue(self):
        self.p.deck=[];self.play('DINO_411');self.kill(self.summon('EDR_571'))
        self.assertEqual(self.p.fatigue,0);self.assertEqual(self.p.hand,[])

    def test_dragon_death_draw_discounts_only_drawn_cards(self):
        self.p.deck=['CATA_478','CATA_999','CORE_CS2_029']
        self.kill(self.summon('EDR_572'))
        self.assertEqual({c.card_id for c in self.p.hand},{'CATA_478','CATA_999'})
        self.assertTrue(all(self.g._cost(c,0)==4 for c in self.p.hand))

    def test_ten_mana_draw_buff_and_threshold(self):
        self.p.max_mana=9;self.p.mana=9;self.p.deck=['Core_CS2_200']*4
        self.play('JAIL_866')
        self.assertTrue(all(c.attack_bonus==0 for c in self.p.hand))
        self.p.max_mana=10;self.p.mana=10;self.play('JAIL_866')
        self.assertEqual([c.attack_bonus for c in self.p.hand],[0,0,3,3])

    def test_distinct_cost_draws_do_not_draw_same_cost_twice(self):
        self.p.deck=['CORE_CS2_029']*4+['Core_CS2_200','TOKEN_COIN']
        self.play('TIME_031')
        self.assertEqual({self.g.cards[c.card_id]['cost'] for c in self.p.hand},{0,4,6})
        self.assertEqual(len(self.p.hand),3)

    def test_bottom_draw_preserves_remaining_order(self):
        self.p.deck=['TOKEN_COIN','Core_CS2_200','CORE_CS2_029']
        self.play('TIME_023')
        self.assertEqual([c.card_id for c in self.p.hand],['TOKEN_COIN','Core_CS2_200'])
        self.assertEqual(self.p.deck,['CORE_CS2_029'])

    def test_bottom_draw_empty_deck_fatigues_twice(self):
        self.p.deck=[];self.play('TIME_023')
        self.assertEqual((self.p.fatigue,self.p.health),(2,27))

    def test_cheap_draw_chain_stops_after_second(self):
        self.p.deck=['TOKEN_COIN']*3;self.play('JAIL_377')
        self.assertEqual(len(self.p.hand),2);self.assertEqual(len(self.p.deck),1)

    def test_barnabus_checks_buffed_attack_and_adds_health_and_armor(self):
        c=Card(self.g._new_id(),'DINO_130',attack_bonus=5)
        self.p.deck=[c];self.play('TLC_231')
        self.assertEqual(c.health_bonus,5);self.assertEqual(self.p.armor,5)

    def test_all_zone_buff_preserves_deck_order_and_non_beasts(self):
        beast=self.give('EDR_492');spell=self.give('CORE_CS2_029')
        board=self.summon('DINO_130t');other=self.summon()
        self.p.deck=['EDR_492','CORE_CS2_029','DINO_130']
        self.play('TLC_828')
        self.assertEqual((beast.attack_bonus,beast.health_bonus),(2,2))
        self.assertEqual(spell.health_bonus,0)
        self.assertEqual((board.attack,board.health,other.attack),(5,5,6))
        self.assertEqual([self.g._card_data(v)['id'] for v in self.p.deck],['EDR_492','CORE_CS2_029','DINO_130'])
        self.assertEqual(self.p.deck[0].attack_bonus,2)
        self.assertEqual(self.p.deck[1],'CORE_CS2_029')

    def test_top_three_minions_skip_spells_and_keep_order(self):
        self.p.deck=['Core_CS2_200','DINO_130','CORE_CS2_029','EDR_492','CATA_999']
        self.play('EDR_230')
        self.assertIsInstance(self.p.deck[0],str)
        self.assertEqual([self.g._card_stat(v,'attack') for v in self.p.deck],[6,4,0,6,8])

    def test_left_hand_shuffle_keeps_enchantments_and_death_draws(self):
        card=self.give('DINO_130');card.attack_bonus=3
        self.give('CORE_CS2_029');self.p.deck=[]
        self.play('DINO_408')
        self.assertEqual(self.p.deck,[card]);self.assertEqual(card.attack_bonus,3)
        self.kill(self.p.minions[0])
        self.assertIn(card,self.p.hand);self.assertEqual(self.p.fatigue,1)

    def test_lowest_beast_copy_gets_new_identity_and_keeps_buffs(self):
        cheap=self.give('DINO_130');cheap.health_bonus=4
        self.give('EDR_492');self.play('FIR_960')
        clone=self.p.hand[-1]
        self.assertEqual(clone.card_id,'DINO_130');self.assertNotEqual(clone.uid,cheap.uid)
        self.assertEqual(clone.health_bonus,4)

    def test_conflagrate_draws_for_target_owner_after_death(self):
        target=self.summon('DINO_130t',1)
        self.play('FIR_954',target.uid)
        self.assertNotIn(target,self.q.board);self.assertEqual(len(self.q.hand),1)
        self.assertEqual(self.p.hand,[])

    def test_fire_breath_buffs_only_surviving_friendly_elementals(self):
        elemental=self.summon('TLC_249');beast=self.summon('DINO_130t')
        self.play('DINO_406',-2)
        self.assertEqual(self.q.health,26);self.assertEqual((elemental.attack,elemental.health),(3,2))
        self.assertEqual(beast.attack,3)

    def test_source_health_damage_has_lifesteal(self):
        self.p.health=20;target=self.summon(owner=1)
        c=self.give('TIME_427');c.health_bonus=2
        self.g.step(Action('play',c.uid,target.uid,0))
        self.assertEqual((target.health,self.p.health),(2,25))

    def test_source_health_heal_uses_hand_buff(self):
        self.p.health=20;c=self.give('TIME_431');c.health_bonus=2
        self.g.step(Action('play',c.uid,-1,0));self.assertEqual(self.p.health,26)

    def test_heir_counts_damaged_minions_on_both_sides(self):
        a=self.summon();b=self.summon(owner=1);a.health=4;b.health=5
        self.play('TIME_871');heir=self.p.minions[-1]
        self.assertEqual((heir.attack,heir.health),(6,10))

    def test_hatchery_uses_pre_buff_attack_and_skips_self(self):
        small=self.summon('TLC_249');big=self.summon()
        self.play('TLC_233');helper=self.p.minions[-1]
        self.assertEqual((small.attack,small.health),(3,2));self.assertIn('TAUNT',small.keywords)
        self.assertEqual(big.attack,6);self.assertNotIn('TAUNT',helper.keywords)

    def test_non_paladin_destroy_includes_own_minions(self):
        friendly=self.summon();paladin=self.summon('CATA_478',1)
        self.play('JAIL_118')
        self.assertNotIn(friendly,self.p.board);self.assertIn(paladin,self.q.board)
        self.assertEqual([m.card_id for m in self.p.minions],['JAIL_118'])

    def test_nether_removes_locations_before_deathrattle_summons(self):
        self.g._place_location(0,'CORE_REV_990');self.g._place_location(1,'CORE_REV_990')
        self.summon('DINO_130');self.summon(owner=1)
        self.play('CORE_EX1_312')
        self.assertEqual(self.p.locations+self.q.locations,[])
        self.assertEqual([m.card_id for m in self.p.minions],['DINO_130t'])
        self.assertEqual(self.q.board,[])

    def test_renovator_targets_only_enemy_locations(self):
        own=self.g._place_location(0,'CORE_REV_990');enemy=self.g._place_location(1,'CORE_REV_990')
        minion=self.summon(owner=1);c=self.give('CORE_REV_023')
        targets={a.target for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid}
        self.assertEqual(targets,{enemy.uid})
        self.g.step(Action('play',c.uid,enemy.uid,len(self.p.board)))
        self.assertIn(own,self.p.board);self.assertNotIn(enemy,self.q.board);self.assertIn(minion,self.q.board)
        self.assertEqual(self.q.corpses,0)

    def test_chronochiller_skips_only_automatic_draw_until_silenced(self):
        chiller=self.summon('TIME_617');self.p.deck=[]
        for _ in range(2):self.g.step(Action('end'))
        self.assertEqual(self.p.fatigue,0)
        self.g._draw(0);self.assertEqual(self.p.fatigue,1)
        self.g._silence(chiller)
        for _ in range(2):self.g.step(Action('end'))
        self.assertEqual(self.p.fatigue,2)

    def test_prisoner_empty_minion_condition_ignores_locations(self):
        c=self.give('JAIL_204');self.g._place_location(0,'CORE_REV_990')
        self.assertEqual(self.g._cost(c,0),2)
        self.summon(owner=1);self.assertEqual(self.g._cost(c,0),5)

    def test_atlas_counts_itself_in_hand_for_cost(self):
        for _ in range(3):self.give('CORE_CS2_029')
        c=self.give('JAIL_514');self.assertEqual(self.g._cost(c,0),6)
        self.g.step(Action('play',c.uid));self.assertEqual(self.p.mana,4)
        self.assertEqual(len(self.p.hand),6)

    def test_baleful_blazer_targeting_requires_prior_fire_spell(self):
        target=self.summon(owner=1);c=self.give('CATA_EVENT_002')
        self.assertEqual({a.target for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid},{0})
        self.play('CORE_CS2_029',-2)
        self.g.step(Action('play',c.uid,target.uid,0))
        self.assertNotIn(target,self.q.board)

    def test_deadly_bribe_combo_gives_both_players_coins(self):
        self.play('TOKEN_COIN');target=self.summon(owner=1)
        self.play('CATA_EVENT_402',target.uid)
        self.assertEqual([c.card_id for c in self.p.hand],['TOKEN_COIN'])
        self.assertEqual([c.card_id for c in self.q.hand],['TOKEN_COIN'])
        self.assertNotIn(target,self.q.board)

    def test_egg_basher_cannot_save_lethally_damaged_target(self):
        target=self.summon('TLC_249');self.play('EDR_468',target.uid)
        self.assertNotIn(target,self.p.board);self.assertEqual(self.q.health,28)

    def test_devastator_spares_self_then_death_hits_only_enemy_minions(self):
        own=self.summon();enemy=self.summon(owner=1)
        self.play('EDR_459');source=self.p.minions[-1]
        self.assertEqual((own.health,source.health,enemy.health),(4,6,7))
        self.kill(source);self.assertEqual((own.health,enemy.health,self.q.health),(4,4,30))

    def test_crocolisks_summon_for_opponent_at_board_limit(self):
        for _ in range(6):self.summon(owner=1)
        self.play('TIME_873')
        self.assertEqual(self.p.armor,10);self.assertEqual(len(self.q.board),7)
        self.assertEqual(self.q.minions[-1].card_id,'TIME_873t')

    def test_stingers_deal_damage_and_summon_rush_grubs(self):
        self.play('TLC_902');c=self.p.hand[0]
        self.assertEqual([x.card_id for x in self.p.hand],['TLC_630t']*2)
        self.g.step(Action('play',c.uid,-2))
        self.assertEqual(self.q.health,28);self.assertEqual(self.p.minions[0].card_id,'TLC_903t')
        self.assertIn('RUSH',self.p.minions[0].keywords)
        self.assertNotIn('TLC_630t',COLLECTIBLE_IDS)

    def test_wasp_gets_stinger_on_damage(self):
        m=self.summon('TLC_630');self.g._damage(m.uid,1);self.g._settle()
        self.assertEqual([c.card_id for c in self.p.hand],['TLC_630t'])

    def test_weapon_final_charge_still_summons_grub(self):
        self.play('TLC_833');self.p.weapon['durability']=1
        self.g.step(Action('attack',-1,-2))
        self.assertIsNone(self.p.weapon)
        self.assertEqual(self.p.minions[-1].card_id,'TLC_903t')

    def test_corpse_cannon_ghoul_has_charge_and_expires(self):
        self.play('JAIL_450');self.g.step(Action('attack',-1,-2))
        ghoul=self.p.minions[0]
        self.assertIn('CHARGE',ghoul.keywords);self.assertTrue(ghoul.expires)
        self.g.step(Action('end'));self.assertNotIn(ghoul,self.p.board)

    def test_animal_companion_uses_complete_fixed_pool(self):
        for cid in ('NEW1_032','NEW1_033','NEW1_034'):
            with self.subTest(cid=cid):
                with patch.object(self.g.rng,'choice',return_value=cid):self.play('CORE_NEW1_031')
        misha,leokk,huffer=self.p.minions
        self.assertIn('TAUNT',misha.keywords);self.assertIn('CHARGE',huffer.keywords)
        self.assertEqual((misha.attack,leokk.attack,huffer.attack),(5,2,5))

    def test_bronze_redeemer_uses_current_damaged_stats(self):
        m=self.summon('CATA_478');self.g._buff(m,2,2);m.health=3
        self.g.step(Action('end'));dragon=self.p.minions[-1]
        self.assertEqual((dragon.card_id,dragon.attack,dragon.health),('CATA_478t',5,3))

    def test_stonecarver_only_buffs_other_damaged_minions(self):
        source=self.summon('TLC_623');source.health=2
        target=self.summon();target.health=2;healthy=self.summon()
        self.g.step(Action('end'))
        self.assertEqual((target.attack,target.health),(8,4))
        self.assertEqual((source.attack,source.health),(1,2));self.assertEqual(healthy.attack,6)

    def test_nozdormu_buffs_existing_shields_and_grants_new_ones(self):
        shielded=self.summon('TIME_100');plain=self.summon()
        self.summon('CATA_473');self.g.step(Action('end'))
        self.assertEqual((shielded.attack,shielded.health),(5,7))
        self.assertEqual(plain.attack,6);self.assertIn('DIVINE_SHIELD',plain.keywords)

    def test_ball_and_chain_buffs_only_damaged_survivors(self):
        hurt=self.summon();hurt.health=2;healthy=self.summon()
        self.kill(self.summon('JAIL_376'))
        self.assertEqual((hurt.attack,hurt.health),(7,4));self.assertEqual(healthy.attack,6)

    def test_held_condition_keywords_and_silence(self):
        self.give('EDR_476');self.give('CATA_999')
        self.play('FIR_961');self.play('TIME_062')
        pixie,dragon=self.p.minions
        self.assertTrue({'DIVINE_SHIELD','LIFESTEAL'}<=pixie.keywords)
        self.assertTrue({'DIVINE_SHIELD','TAUNT'}<=dragon.keywords)
        self.g._silence(dragon);self.assertFalse(dragon.keywords)

    def test_blighspawn_equips_then_buffs_existing_weapon(self):
        self.kill(self.summon('END_002'))
        self.assertEqual((self.p.weapon['card_id'],self.p.weapon['attack']),('CS2_082',1))
        self.kill(self.p.minions[0]);self.assertEqual(self.p.weapon['attack'],3)

    def test_cannot_attack_keyword_survives_turn_and_silence_removes_it(self):
        m=self.summon('JAIL_942');m.summoned_turn=-1
        self.assertFalse(any(a.kind=='attack' and a.source==m.uid for a in self.g.legal_actions()))
        self.g._silence(m)
        self.assertTrue(any(a.kind=='attack' and a.source==m.uid for a in self.g.legal_actions()))

    def test_large_deck_attack_updates_after_draw(self):
        self.p.deck=['CORE_CS2_029']*25;m=self.summon('JAIL_311')
        self.assertEqual(m.attack,7)
        self.g._draw(0);self.assertEqual(m.attack,2)

    def test_pickpocket_draw_threshold(self):
        self.p.deck=['CORE_CS2_029']*25
        self.play('JAIL_456');self.assertEqual(len(self.p.hand),1)
        self.play('JAIL_456');self.assertEqual(len(self.p.hand),1)

    def test_fumigate_hits_shared_tribes_on_both_sides(self):
        beast=self.summon('DINO_130t');enemy=self.summon('DINO_130t',1)
        other=self.summon(owner=1);self.play('TLC_901',beast.uid)
        self.assertNotIn(beast,self.p.board);self.assertNotIn(enemy,self.q.board)
        self.assertEqual(other.health,7)

    def test_excess_draw_uses_actual_damage_and_shield_prevents_it(self):
        target=self.summon('DINO_130t',1);self.play('TIME_858',target.uid)
        self.assertEqual(len(self.p.hand),2)
        self.p.mana=10;shield=self.summon('TIME_100',1);self.play('TIME_858',shield.uid)
        self.assertEqual(len(self.p.hand),2);self.assertEqual(shield.health,4)

    def test_aoe_draw_counts_original_deaths_not_reborn_bodies(self):
        self.summon('TLC_249');self.summon('TLC_443',1)
        self.play('CATA_526');self.assertEqual(len(self.p.hand),2)
        self.assertEqual({m.card_id for m in self.q.minions},{'TLC_443','TLC_443t'})

    def test_swarm_damage_bonus_and_shield_prevention(self):
        self.summon('CORE_EX1_012');self.play('TLC_221',-2)
        self.assertEqual(sum(m.card_id=='TLC_249' for m in self.p.minions),4)
        self.p.mana=10;shield=self.summon('TIME_100',1)
        self.play('TLC_221',shield.uid)
        self.assertEqual(sum(m.card_id=='TLC_249' for m in self.p.minions),4)

    def test_holy_embrace_generates_playable_shadow_spell(self):
        self.p.health=20;self.play('JAIL_941',-1)
        self.assertEqual(self.p.health,24);c=self.p.hand[0]
        self.assertEqual(c.card_id,'JAIL_941t')
        self.g.step(Action('play',c.uid,-2));self.assertEqual(self.q.health,26)
        self.assertNotIn(c.card_id,COLLECTIBLE_IDS)

    def test_distinct_random_damage_hits_each_enemy_once(self):
        a=self.summon(owner=1);b=self.summon(owner=1)
        self.play('FIR_909')
        self.assertEqual((a.health,b.health,self.q.health),(5,5,28))
        self.kill(self.summon('TLC_401'))
        self.assertEqual(self.q.minions,[]);self.assertEqual(self.q.health,22)

    def test_barrage_excludes_primary_target_from_secondary_hits(self):
        a=self.summon(owner=1);b=self.summon(owner=1)
        self.play('TIME_855',a.uid)
        self.assertEqual((a.health,b.health,self.q.health),(4,5,28))

    def test_timestop_freezes_only_surviving_enemies(self):
        a=self.summon(owner=1);b=self.summon(owner=1);dead=self.summon('DINO_130t',1)
        self.play('TIME_611',dead.uid)
        self.assertNotIn(dead,self.q.board)
        self.assertGreaterEqual(a.frozen_until,0);self.assertGreaterEqual(b.frozen_until,0)
