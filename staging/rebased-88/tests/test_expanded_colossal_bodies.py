"""Body behavior with explicitly installed staged card tables and test pools."""
import gzip,json,unittest
from pathlib import Path
from copy import deepcopy
from unittest.mock import patch
import test_expanded_generation as fixtures
from expanded import cards,Action
from expanded import herald,colossal_bodies
from expanded.colossals import LAYOUTS
from expanded.generation_cards import pool
from expanded.pools import GenerationPool
from engine.game import Card
from engine.cards import UnsupportedCard

class ColossalBodyTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with gzip.open(Path(__file__).resolve().parents[1]/'data/standard/all_cards.json.gz','rt') as f:cls.records={c['id']:c for c in json.load(f)}
 def setUp(self):
  self.g=fixtures.GenerationTests().game();self.g._generation_pools={}
  ids=set(colossal_bodies.RULES)|set(herald.ARMY_OF)
  ids.update(cid for parent in colossal_bodies.RULES for cid,side in LAYOUTS[parent])
  self.g.cards.update({cid:deepcopy(self.records[cid]) for cid in ids})
  for table,values in ((cards.RULES,colossal_bodies.RULES),(cards.END_EFFECTS,{**herald.END_EFFECTS,**colossal_bodies.END_EFFECTS}),(cards.TRIGGERS,colossal_bodies.TRIGGERS),(cards.DEATH_EFFECTS,{**herald.DEATH_EFFECTS,**colossal_bodies.DEATH_EFFECTS})):
   context=patch.dict(table,values);context.start();self.addCleanup(context.stop)
 @property
 def p(self):return self.g.players[0]
 @property
 def q(self):return self.g.players[1]
 def op(self,*ops,source=None):
  self.g._start_play_effects(ops,dict(owner=0,source=source,target=0,bonus=0,lifesteal=False));self.g._settle(allow_event_choices=True)
 def summon(self,cid):return self.g._summon(0,cid)
 def contract(self,request,ids):self.g._generation_pools[(request,self.p.hero_class)]=GenerationPool('fixture',tuple(ids),'Controlled test pool, not complete Standard membership')
 def play(self,cid,target=0):
  self.p.mana=10;c=Card(self.g._new_id(),cid);self.g._enter_hand(0,c)
  self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid and a.target==target));return c
 def test_body_declarations_remain_staged(self):self.assertFalse(set(colossal_bodies.RULES)&cards.COLLECTIBLE_IDS)
 def test_ragnaros_triggers_both_hands_without_killing_them(self):
  body=self.summon('CATA_150');self.g._end_turn()
  self.assertEqual(self.q.health,26);self.assertEqual(len(self.p.minions),3);self.assertIn(body,self.p.board)
 def test_ragnaros_uses_upgraded_hand_magnitudes(self):
  self.p.herald_count=4;self.summon('CATA_150');self.g._end_turn();self.assertEqual(self.q.health,14)
 def test_ragnaros_triggers_other_minion_deathrattles(self):
  m=self.summon('NEW1_034');m.attached_death_effects=[('draw',1)];self.summon('CATA_150');self.g._end_turn()
  self.assertEqual(len(self.p.hand),1);self.assertIn(m,self.p.board)
 def test_silenced_ragnaros_does_not_trigger(self):
  body=self.summon('CATA_150');self.g._silence(body);self.g._end_turn();self.assertEqual(self.q.health,30)
 def test_silenced_hand_printed_deathrattle_is_excluded(self):
  self.summon('CATA_150');self.g._silence(self.p.minions[0]);self.g._end_turn();self.assertEqual(self.q.health,28)
 def test_deathrattle_group_uses_each_minion_as_source(self):
  m=self.summon('NEW1_034');m.attached_death_effects=[('buff_self',2,2)];self.op(('colossal_friendly_deathrattles',))
  self.assertEqual(m.attack,self.records[m.card_id]['attack']+2)
 def test_group_does_not_include_newly_summoned_deathrattles(self):
  m=self.summon('NEW1_034');m.attached_death_effects=[('summon','CATA_580t',1)]
  self.op(('colossal_friendly_deathrattles',));self.assertEqual(len(self.p.minions),2);self.assertEqual(self.q.health,30)
 def test_departed_later_deathrattle_source_is_skipped(self):
  m=self.summon('CATA_580t');m.health=0;self.op(('colossal_live_deathrattle',m.uid))
  # Its real death triggers once during settlement; the requested replay does not.
  self.assertEqual(self.q.health,28)
 def test_azshara_grants_two_hero_attacks(self):
  self.summon('CATA_151');self.g._settle(allow_event_choices=True)
  for _ in range(2):self.g.step(next(a for a in self.g.legal_actions() if a.kind=='attack' and a.source==-1 and a.target==-2))
  self.assertEqual(self.q.health,26);self.assertFalse(any(a.kind=='attack' and a.source==-1 for a in self.g.legal_actions()))
 def test_silence_removes_second_hero_attack(self):
  body=self.summon('CATA_151');self.g._settle(allow_event_choices=True);self.p.hero_attacks=1;self.g._silence(body)
  self.assertFalse(any(a.kind=='attack' and a.source==-1 for a in self.g.legal_actions()))
 def test_azshara_does_not_grant_opponent_windfury(self):
  self.summon('CATA_151');self.assertEqual(self.g._hero_attack_limit(1),1)
 def test_two_azsharas_do_not_stack_into_four_attacks(self):
  self.summon('CATA_151');self.summon('CATA_151');self.assertEqual(self.g._hero_attack_limit(0),2)
 def test_dead_azshara_loses_aura_before_removal(self):
  m=self.summon('CATA_151');m.health=0;self.assertEqual(self.g._hero_attack_limit(0),1)
 def test_alakir_uses_attack_after_appendage_aura(self):
  # Base 4 Attack plus the immediately adjacent Hand in the candidate layout.
  base=self.records['CATA_153']['attack'];cost=base+1
  cid='TEST_ALAKIR';self.g.cards[cid]=dict(id=cid,name=cid,type='MINION',cost=cost,attack=1,health=1,cardClass='NEUTRAL')
  self.contract(pool(card_type='MINION',minimum=cost,maximum=cost),[cid]);self.play('CATA_153')
  self.assertEqual([c.card_id for c in self.p.hand],[cid,cid]);self.assertTrue(all(self.g._cost(c,0)==1 for c in self.p.hand))
 def test_alakir_uses_buffed_current_attack(self):
  m=self.summon('CATA_153');self.g._buff(m,2,0);cost=m.attack;cid='TEST_BUFFED'
  self.g.cards[cid]=dict(id=cid,name=cid,type='MINION',cost=cost,attack=1,health=1,cardClass='NEUTRAL');self.contract(pool(card_type='MINION',minimum=cost,maximum=cost),[cid])
  self.op(('colossal_attack_cost',),source=m);self.assertEqual(len(self.p.hand),2)
 def test_recruited_alakir_does_not_execute_battlecry(self):
  self.summon('CATA_153');self.g._settle(allow_event_choices=True);self.assertFalse(self.p.hand)
 def test_missing_exact_cost_pool_rolls_back_play_and_limbs(self):
  c=Card(self.g._new_id(),'CATA_153');self.g._enter_hand(0,c);before=(self.p.mana,self.g.rng.getstate())
  with self.assertRaises(UnsupportedCard):self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid))
  self.assertFalse(self.p.board);self.assertEqual((self.p.mana,self.g.rng.getstate()),before)
 def test_vulcanos_damages_other_minions_and_spawns_fire_rewards(self):
  self.contract(colossal_bodies.FIRE,['CORE_CS2_029']);body=self.summon('CATA_488');enemy=self.g._summon(1,'NEW1_034');health=body.health
  self.g._end_turn();self.assertEqual(body.health,health);self.assertNotIn(enemy,self.q.board)
  self.assertEqual(len(self.p.hand),2);self.assertTrue(all(c.cost_delta==-3 for c in self.p.hand))
 def test_plume_surviving_damage_produces_one_reward(self):
  self.contract(colossal_bodies.FIRE,['CORE_CS2_029']);m=self.summon('CATA_488t');self.g._damage(m.uid,1);self.g._settle(allow_event_choices=True)
  self.assertEqual(len(self.p.hand),1)
 def test_plume_shield_prevents_reward(self):
  self.contract(colossal_bodies.FIRE,['CORE_CS2_029']);m=self.summon('CATA_488t');m.keywords.add('DIVINE_SHIELD');self.g._damage(m.uid,1);self.g._settle(allow_event_choices=True)
  self.assertFalse(self.p.hand)
 def test_silenced_plume_does_not_generate(self):
  m=self.summon('CATA_488t');self.g._silence(m);self.g._damage(m.uid,1);self.g._settle(allow_event_choices=True);self.assertFalse(self.p.hand)
 def test_missing_fire_contract_fails_instead_of_filtering(self):
  m=self.summon('CATA_488t');self.g._damage(m.uid,1)
  with self.assertRaises(UnsupportedCard):self.g._settle(allow_event_choices=True)
 def test_deathrattle_group_resumes_after_choice_without_repeating(self):
  first=self.summon('NEW1_034');first.attached_death_effects=[('companions_choose',)]
  self.summon('CATA_580t');self.op(('colossal_friendly_deathrattles',))
  self.assertIsNotNone(self.g.pending_choice);self.assertEqual(self.q.health,30)
  self.g.step(Action('choose',choices=(0,)));self.assertIsNone(self.g.pending_choice)
  self.assertEqual(self.q.health,28);self.assertEqual(len(self.p.minions),3)
 def test_lethal_plume_damage_still_generates(self):
  self.contract(colossal_bodies.FIRE,['CORE_CS2_029']);m=self.summon('CATA_488t')
  self.g._damage(m.uid,m.health);self.g._settle(allow_event_choices=True)
  self.assertNotIn(m,self.p.board);self.assertEqual(len(self.p.hand),1)
 def test_azshara_added_after_first_attack_unlocks_one_more(self):
  self.p.hero_attacks=1;self.summon('CATA_151');self.g._settle(allow_event_choices=True)
  self.assertTrue(any(a.kind=='attack' and a.source==-1 for a in self.g.legal_actions()))
 def test_reviewed_empty_exact_cost_pool_does_not_substitute_cost(self):
  m=self.summon('CATA_153');cost=m.attack
  self.contract(pool(card_type='MINION',minimum=cost,maximum=cost),[])
  self.op(('colossal_attack_cost',),source=m);self.assertFalse(self.p.hand)
 def test_vulcanos_silence_stops_end_turn_damage(self):
  body=self.summon('CATA_488');self.g._silence(body);enemy=self.g._summon(1,'NEW1_034')
  self.g._end_turn();self.assertIn(enemy,self.q.board);self.assertFalse(self.p.hand)
 def sinestra(self):
  self.p.hero_class='ROGUE';self.contract(pool(card_type='SPELL',classes='other'),['CORE_CS2_029'])
  body=self.summon('CATA_154');self.g._settle(allow_event_choices=True);self.p.hand=[];return body
 def target_dummy(self):
  self.g.cards['TEST_DUMMY']=dict(id='TEST_DUMMY',name='Dummy',type='MINION',cardClass='NEUTRAL',cost=1,attack=0,health=100,mechanics=[])
  return self.g._summon(1,'TEST_DUMMY')
 def test_sinestra_other_class_spell_repeats_with_one_payment_and_history(self):
  self.sinestra();self.play('CORE_CS2_029',-2)
  self.assertEqual(self.q.health,18);self.assertEqual(self.p.mana,6);self.assertEqual(len(self.p.spells_turn),1)
 def test_sinestra_internal_cast_repeats_without_hand_play(self):
  self.sinestra();self.op(('cast_fixed_spell','CORE_CS2_029','enemies'))
  self.assertEqual(self.q.health,18);self.assertFalse(self.p.spells_turn)
 def test_sinestra_silence_stops_repetition(self):
  body=self.sinestra();self.g._silence(body);self.play('CORE_CS2_029',-2);self.assertEqual(self.q.health,24)
 def test_sinestra_dead_body_does_not_repeat(self):
  body=self.sinestra();body.health=0;self.assertFalse(self.g._colossal_repeats_spell(0,'CORE_CS2_029'))
 def test_sinestra_own_and_neutral_classes_excluded(self):
  self.sinestra()
  for values in ({'cardClass':'ROGUE'},{'cardClass':'NEUTRAL'},{'classes':['ROGUE','MAGE']}):
   self.g.cards['TEST_SPELL']=dict(id='TEST_SPELL',type='SPELL',cost=0,**values)
   self.assertFalse(self.g._colossal_repeats_spell(0,'TEST_SPELL'))
 def test_sinestra_multiple_sources_fail_closed_until_reviewed(self):
  self.sinestra();self.summon('CATA_154');self.g._settle(allow_event_choices=True);self.p.hand=[]
  with self.assertRaisesRegex(UnsupportedCard,'stacking'):self.play('CORE_CS2_029',-2)
  self.assertEqual(self.q.health,30);self.assertEqual(self.p.mana,10)
 def test_sinestra_other_double_effect_fails_closed_until_reviewed(self):
  self.sinestra();self.p.spell_repeat_charges=1
  with self.assertRaisesRegex(UnsupportedCard,'stacking'):self.play('CORE_CS2_029',-2)
  self.assertEqual(self.q.health,30);self.assertEqual(self.p.spell_repeat_charges,1)
 def test_black_blood_actual_heal_attacks_once_without_spending_attack(self):
  body=self.summon('CATA_300');target=self.target_dummy();self.p.health=20
  self.g._heal(-1,3,healer=0);self.g._settle(allow_event_choices=True)
  self.assertEqual(target.health,95);self.assertEqual(body.attacks,0)
 def test_black_blood_no_overheal_trigger(self):
  self.summon('CATA_300');target=self.target_dummy();self.g._heal(-1,3,healer=0);self.g._settle(allow_event_choices=True)
  self.assertEqual(target.health,100)
 def test_black_blood_partially_effective_heal_is_one_event(self):
  self.summon('CATA_300');target=self.target_dummy();self.p.health=29
  self.g._heal(-1,10,healer=0);self.g._settle(allow_event_choices=True);self.assertEqual(target.health,95)
 def test_black_blood_healing_enemy_character_counts(self):
  self.summon('CATA_300');target=self.target_dummy();self.q.health=20
  self.g._heal(-2,3,healer=0);self.g._settle(allow_event_choices=True);self.assertEqual(target.health,95)
 def test_black_blood_opponent_healer_does_not_trigger(self):
  self.summon('CATA_300');target=self.target_dummy();self.p.health=20
  self.g._heal(-1,3,healer=1);self.g._settle(allow_event_choices=True);self.assertEqual(target.health,100)
 def test_black_blood_unknown_healer_does_not_assign_credit(self):
  self.summon('CATA_300');target=self.target_dummy();self.p.health=20
  self.g._heal(-1,3);self.g._settle(allow_event_choices=True);self.assertEqual(target.health,100)
 def test_black_blood_each_heal_event_triggers_separately(self):
  self.summon('CATA_300');target=self.target_dummy();self.p.health=20
  self.g._heal(-1,1,healer=0);self.g._heal(-1,1,healer=0);self.g._settle(allow_event_choices=True);self.assertEqual(target.health,90)
 def test_black_blood_does_not_attack_enemy_hero(self):
  self.summon('CATA_300');self.p.health=20;self.g._heal(-1,3,healer=0);self.g._settle(allow_event_choices=True);self.assertEqual(self.q.health,30)
 def test_black_blood_source_dies_before_callback(self):
  body=self.summon('CATA_300');target=self.target_dummy();self.p.health=20
  self.g._heal(-1,3,healer=0);body.health=0;self.g._settle(allow_event_choices=True);self.assertEqual(target.health,100)
 def test_black_blood_silence_suppresses_callback(self):
  body=self.summon('CATA_300');target=self.target_dummy();self.p.health=20
  self.g._heal(-1,3,healer=0);self.g._silence(body);self.g._settle(allow_event_choices=True);self.assertEqual(target.health,100)
 def test_black_blood_heals_can_trigger_off_turn(self):
  self.summon('CATA_300');target=self.target_dummy();self.g.current=1;self.p.health=20
  self.g._heal(-1,3,healer=0);self.g._settle(allow_event_choices=True);self.assertEqual(target.health,95)
 def test_three_body_heals_trigger_three_attacks(self):
  self.summon('CATA_300');target=self.target_dummy();self.p.health=20;self.g._end_turn()
  self.assertEqual(self.p.health,29);self.assertEqual(target.health,85)
 def test_full_healing_stops_later_body_triggers(self):
  self.summon('CATA_300');target=self.target_dummy();self.p.health=29;self.g._end_turn()
  self.assertEqual(self.p.health,30);self.assertEqual(target.health,95)
 def test_body_heals_damaged_minions_and_excludes_enemy(self):
  limb=self.summon('CATA_300t1');limb.health=1;target=self.target_dummy();target.health=50
  self.op(('colossal_heal_damaged',3));self.assertEqual(limb.health,2);self.assertEqual(target.health,50)
 def test_multiple_black_blood_sources_each_attack(self):
  self.summon('CATA_300');self.summon('CATA_300');target=self.target_dummy();self.p.health=20
  self.g._heal(-1,3,healer=0);self.g._settle(allow_event_choices=True);self.assertEqual(target.health,90)

 def chogall(self):
  self.p.hero_class='WARLOCK';return self.summon('CATA_726')
 def test_chogall_arms_remove_two_deck_minions_without_board_deaths(self):
  self.chogall();self.q.deck=['NEW1_034','CORE_CS2_029','NEW1_034'];self.g._end_turn()
  self.assertFalse(self.q.deck);self.assertEqual([c.card_id for c in self.q.hand],['CORE_CS2_029']);self.assertEqual(len(self.p.minions),3)
  self.assertEqual([m.attack for m in self.p.minions[1:]],[3,3])
 def test_chogall_keeps_friendly_right_neighbor_alive(self):
  self.chogall();source=self.p.minions[1];victim=self.p.minions[2];self.q.deck=['NEW1_034']
  self.op(('herald_consume_right',),source=source);self.assertIn(victim,self.p.board);self.assertFalse(self.q.deck)
 def test_chogall_no_eligible_minion_does_not_buff_or_consume_friendly(self):
  self.chogall();source=self.p.minions[1];before=(source.attack,source.max_health);self.q.deck=['CORE_CS2_029']
  self.op(('herald_consume_right',),source=source)
  self.assertEqual((source.attack,source.max_health),before);self.assertEqual(len(self.p.minions),3)
 def test_chogall_supports_physical_card_objects(self):
  self.chogall();source=self.p.minions[1];spell=Card(self.g._new_id(),'CORE_CS2_029');minion=Card(self.g._new_id(),'NEW1_034')
  self.q.deck=[spell,minion];self.op(('herald_consume_right',),source=source);self.assertEqual(self.q.deck,[spell])
 def test_chogall_silence_restores_right_neighbor_consumption(self):
  body=self.chogall();self.g._silence(body);source=self.p.minions[1];victim=self.p.minions[2];self.q.deck=['NEW1_034']
  self.op(('herald_consume_right',),source=source);self.assertNotIn(victim,self.p.board);self.assertEqual(self.q.deck,['NEW1_034'])
 def test_chogall_replacement_applies_to_soldiers(self):
  self.chogall();source=self.summon('CATA_725t');self.q.deck=['NEW1_034'];self.op(('herald_consume_right',),source=source)
  self.assertFalse(self.q.deck);self.assertEqual(source.attack,3)
 def test_chogall_uses_existing_herald_snapshot(self):
  self.p.herald_count=4;self.chogall();source=self.p.minions[1];before=source.attack;self.q.deck=['NEW1_034']
  self.op(('herald_consume_right',),source=source);self.assertEqual(source.attack,before+8)
 def test_chogall_silenced_arm_does_not_destroy_deck_card(self):
  self.chogall();source=self.p.minions[1];self.g._silence(source);self.q.deck=['NEW1_034']
  self.op(('herald_consume_right',),source=source);self.assertEqual(self.q.deck,['NEW1_034'])

 def test_wickerfang_all_four_legs_grow_at_end_turn(self):
  body=self.summon('CATA_139');self.g._end_turn()
  self.assertEqual((body.attack,body.max_health),(4,9))
  self.assertEqual([(m.attack,m.max_health) for m in self.p.minions[1:]],[(1,3)]*4)
 def test_wickerfang_copies_positive_attack_and_health_independently(self):
  body=self.summon('CATA_139');leg=self.p.minions[1];self.g._buff(leg,3,0);self.g._buff(leg,0,2)
  self.assertEqual((body.attack,body.max_health),(3,7))
 def test_wickerfang_damage_and_healing_are_not_stat_gains(self):
  body=self.summon('CATA_139');leg=self.p.minions[1];self.g._damage(leg.uid,1);self.g._heal(leg.uid,1,healer=0);self.g._settle()
  self.assertEqual((body.attack,body.max_health),(0,5))
 def test_wickerfang_stat_setting_is_seen_once(self):
  body=self.summon('CATA_139');leg=self.p.minions[1];self.g._set_entity_stats(leg,5,6);self.g._settle();self.g._refresh_auras()
  self.assertEqual((body.attack,body.max_health),(5,9))
 def test_wickerfang_stat_reductions_are_not_copied(self):
  body=self.summon('CATA_139');leg=self.p.minions[1];self.g._buff(leg,3,3);self.g._buff(leg,-2,-2)
  self.assertEqual((body.attack,body.max_health),(3,8))
 def test_wickerfang_silenced_body_does_not_copy(self):
  body=self.summon('CATA_139');self.g._silence(body);self.g._buff(self.p.minions[1],2,2)
  self.assertEqual((body.attack,body.max_health),(0,5))
 def test_wickerfang_silenced_leg_can_receive_external_buff(self):
  body=self.summon('CATA_139');leg=self.p.minions[1];self.g._silence(leg);self.g._buff(leg,2,2)
  self.assertEqual((body.attack,body.max_health),(2,7))
 def test_wickerfang_enemy_leg_does_not_feed_friendly_body(self):
  body=self.summon('CATA_139');leg=self.g._summon(1,'CATA_139t');self.g._buff(leg,2,2)
  self.assertEqual(body.attack,0)
 def test_wickerfang_standalone_leg_feeds_all_friendly_bodies(self):
  first=self.g._create_minion(0,'CATA_139');second=self.g._create_minion(0,'CATA_139');leg=self.summon('CATA_139t')
  self.g._buff(leg,2,3);self.assertEqual([(m.attack,m.max_health) for m in (first,second)],[(2,8),(2,8)])
 def test_wickerfang_aura_gain_is_not_repeated_on_refresh(self):
  body=self.summon('CATA_139');leg=self.p.minions[1]
  with patch.dict(cards.AURAS,{'TEST_AURA':('others',2,1)}):
   self.g.cards['TEST_AURA']=dict(id='TEST_AURA',name='Aura',type='MINION',attack=1,health=1,cost=1)
   self.summon('TEST_AURA');before=(body.attack,body.max_health);self.g._refresh_auras()
   self.assertEqual((body.attack,body.max_health),before);self.assertEqual(before,(10,10))

 def onyxia(self):
  self.g.cards['NEW1_034']=dict(self.g.cards['NEW1_034'],cost=2)
  self.p.hero_class='DEATHKNIGHT';self.contract(pool(card_type='MINION',minimum=2,maximum=2),['NEW1_034'])
  body=self.summon('CATA_155');self.g._settle(allow_event_choices=True);return body
 def test_onyxia_damage_replacement_preserves_missing_health(self):
  self.onyxia();self.p.health=12;dealt=self.g._damage(-1,5)
  self.assertEqual((self.p.health,self.p.max_health,dealt),(17,35,0));self.assertEqual(self.p.healing_done_turn,0)
 def test_onyxia_only_replaces_damage_past_armor(self):
  self.onyxia();self.p.armor=3;dealt=self.g._damage(-1,5)
  self.assertEqual((self.p.health,self.p.max_health,self.p.armor,dealt),(32,32,0,3))
 def test_onyxia_full_armor_absorption_does_not_grow_health(self):
  self.onyxia();self.p.armor=8;self.g._damage(-1,5);self.assertEqual((self.p.health,self.p.max_health,self.p.armor),(30,30,3))
 def test_onyxia_does_not_replace_enemy_turn_loss(self):
  self.onyxia();self.g.current=1;self.g._damage(-1,5);self.assertEqual((self.p.health,self.p.max_health),(25,30))
 def test_onyxia_silence_removes_replacement(self):
  body=self.onyxia();self.g._silence(body);self.g._damage(-1,5);self.assertEqual(self.p.health,25)
 def test_onyxia_dead_source_does_not_replace(self):
  body=self.onyxia();body.health=0;self.g._damage(-1,5);self.assertEqual(self.p.health,25)
 def test_onyxia_health_payment_bypasses_armor_and_grows_health(self):
  self.onyxia();card=self.p.hand[0];self.p.armor=10;self.g._pay_card(card,0,2)
  self.assertEqual((self.p.health,self.p.max_health,self.p.armor),(32,32,10))
 def test_onyxia_allows_health_payment_above_current_health(self):
  self.onyxia();self.p.health=1;card=self.p.hand[0];self.assertTrue(self.g._can_pay(card,0))
  self.g._pay_card(card,0,2);self.assertEqual((self.p.health,self.p.max_health),(3,32))
 def test_onyxia_payment_exception_ends_with_silence(self):
  body=self.onyxia();self.p.health=1;self.g._silence(body);self.assertFalse(self.g._can_pay(self.p.hand[0],0))
 def test_onyxia_two_bodies_do_not_double_replacement(self):
  self.onyxia();self.g._create_minion(0,'CATA_155');self.g._damage(-1,4);self.assertEqual(self.p.max_health,34)
 def test_onyxia_shield_prevents_damage_before_replacement(self):
  self.onyxia();self.p.divine_shield=True;self.g._damage(-1,4);self.assertEqual(self.p.max_health,30)
 def test_onyxia_generated_cards_play_through_normal_action(self):
  self.onyxia();self.p.health=1;card=self.p.hand[0]
  self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==card.uid))
  self.assertEqual((self.p.health,self.p.max_health),(3,32))

 def test_chromatus_each_head_removes_only_its_keyword(self):
  for cid,keyword in colossal_bodies.HEADS.items():
   with self.subTest(cid=cid):
    self.p.board.clear();body=self.summon('CATA_432');head=next(m for m in self.p.minions if m.card_id==cid)
    head.health=0;self.g._settle();self.assertNotIn(keyword,body.keywords)
    self.assertTrue((set(colossal_bodies.HEADS.values())-{keyword})<=body.keywords)
 def test_chromatus_silenced_head_does_not_remove_keyword(self):
  body=self.summon('CATA_432');head=self.p.minions[1];self.g._silence(head);head.health=0;self.g._settle();self.assertIn('TAUNT',body.keywords)
 def test_chromatus_standalone_head_removes_from_all_friendly_bodies(self):
  first=self.g._create_minion(0,'CATA_432');second=self.g._create_minion(0,'CATA_432');head=self.summon('CATA_432t1')
  head.health=0;self.g._settle();self.assertFalse('TAUNT' in first.keywords or 'TAUNT' in second.keywords)
 def test_chromatus_enemy_head_does_not_strip_our_body(self):
  body=self.summon('CATA_432');head=self.g._summon(1,'CATA_432t1');head.health=0;self.g._settle();self.assertIn('TAUNT',body.keywords)
 def test_chromatus_keyword_can_be_granted_again(self):
  body=self.summon('CATA_432');head=self.p.minions[1];head.health=0;self.g._settle();body.keywords.add('TAUNT')
  self.g._refresh_auras();self.assertIn('TAUNT',self.g._effective_keywords(body))
 def test_chromatus_replaying_head_deathrattle_does_not_require_death(self):
  body=self.summon('CATA_432');head=self.p.minions[1];self.op(('colossal_live_deathrattle',head.uid))
  self.assertIn(head,self.p.board);self.assertNotIn('TAUNT',body.keywords)

 def test_magmaw_initial_six_appendages_and_finite_queue(self):
  body=self.summon('CATA_550');self.assertEqual(len(self.p.board),7);self.assertEqual(body.rule_state['colossal_remaining'],93)
  self.assertEqual([m.card_id for m in self.p.minions[1:]],list(colossal_bodies.MAGMA_PARTS))
 def test_magmaw_replaces_dead_appendage_and_resolves_buff(self):
  body=self.summon('CATA_550');limb=self.p.minions[1];limb.health=0;self.g._settle()
  self.assertNotIn(limb,self.p.board);self.assertEqual(len(self.p.board),7);self.assertEqual(body.rule_state['colossal_remaining'],92)
  self.assertEqual(sum(m.attack for m in self.p.minions),16)
 def test_magmaw_simultaneous_limb_deaths_refill_six_slots(self):
  body=self.summon('CATA_550')
  for m in self.p.minions[1:]:m.health=0
  self.g._settle();self.assertEqual(body.rule_state['colossal_remaining'],87);self.assertEqual(len(self.p.board),7);self.assertEqual(body.attack,14)
 def test_magmaw_dying_with_limbs_does_not_replenish(self):
  self.summon('CATA_550')
  for m in self.p.minions:m.health=0
  self.g._settle();self.assertFalse(self.p.board)
 def test_magmaw_silence_stops_replenishment(self):
  body=self.summon('CATA_550');self.g._silence(body);self.p.minions[1].health=0;self.g._settle();self.assertEqual(len(self.p.board),6)
 def test_magmaw_refills_after_non_death_departure(self):
  body=self.summon('CATA_550');self.p.board.pop();self.g._settle();self.assertEqual(len(self.p.board),7);self.assertEqual(body.rule_state['colossal_remaining'],92)
 def test_magmaw_only_remaining_appendages_can_be_summoned(self):
  body=self.summon('CATA_550');body.rule_state['colossal_remaining']=1
  for m in self.p.minions[1:]:m.health=0
  self.g._settle();self.assertEqual(len(self.p.board),2);self.assertEqual(body.rule_state['colossal_remaining'],0)
  self.p.minions[1].health=0;self.g._settle();self.assertEqual(self.p.minions,[body])
 def test_magmaw_full_99_budget_eventually_exhausts(self):
  body=self.summon('CATA_550');total=6
  while len(self.p.minions)>1:
   for m in self.p.minions[1:]:m.health=0
   self.g._settle();total+=len(self.p.minions)-1
  self.assertEqual(total,99);self.assertEqual(body.rule_state['colossal_remaining'],0)
 def test_magmaw_copy_starts_fresh_appendage_budget(self):
  body=self.summon('CATA_550');self.p.board[:]=[body];body.rule_state['colossal_remaining']=4
  copied=self.g._summon(0,'CATA_550',copy_from=body)
  self.assertEqual(copied.rule_state['colossal_remaining'],94);self.assertEqual(body.rule_state['colossal_remaining'],4)
 def test_magmaw_missing_late_dependency_fails_before_entry(self):
  del self.g.cards['CATA_550t6']
  with self.assertRaisesRegex(UnsupportedCard,'Missing Colossal'):self.summon('CATA_550')
  self.assertFalse(self.p.board)
 def test_all_magmaw_appendages_share_deathrattle(self):
  for cid in colossal_bodies.MAGMA_PARTS:
   self.assertEqual(self.g._printed_death_operations(cid),(('colossal_random_buff',2,0),))
