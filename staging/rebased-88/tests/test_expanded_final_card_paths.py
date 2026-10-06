"""Integration fixtures for the final staged bodies; not client certification."""
import gzip,json,unittest
from copy import deepcopy
from unittest.mock import patch
import test_expanded_generation as fixtures
from engine.game import Card
from engine.cards import UnsupportedCard
from expanded import Action,cards,locations,secrets
from expanded import (replacements,genn,stat_rules,tiny_pal,healing_replacement,hand_investigations,
 remaining_setup,kindred,titanographer,dragon_soul,counterfeits,random_targets,morchie,
 custom_builders,minion_forge,exceptional_finish)
MODULES=(replacements,genn,stat_rules,tiny_pal,healing_replacement,hand_investigations,
 remaining_setup,kindred,titanographer,dragon_soul,counterfeits,random_targets,morchie,
 custom_builders,minion_forge,exceptional_finish)
class FinalCardPathsTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with gzip.open('data/standard/all_cards.json.gz','rt') as f:all_records={d['id']:d for d in json.load(f)}
  ids=set(genn.POWERS.values())|{'AT_132_ROGUEt','JAIL_443t','CATA_EVENT_110t6t','CFM_621_m2','JAIL_504tt01','CS2_065','TTN_737t2','TTN_862t4','TTN_960t5','DINO_136t'}
  for mod in MODULES:
   for name in ('RULES','TOKEN_RULES'):ids.update(getattr(mod,name,{}))
  ids.update(cid for cid in all_records if cid.startswith(('CAP_405','TLC_100')))
  cls.records={cid:all_records[cid] for cid in ids}
 def setUp(self):
  self.fx=fixtures.GenerationTests();self.g=self.fx.game();self.p,self.q=self.g.players;self.g.cards.update(deepcopy(self.records))
  for mod in MODULES:
   for table,name in ((cards.RULES,'RULES'),(cards.RULES,'TOKEN_RULES'),(cards.DEATH_EFFECTS,'DEATH_EFFECTS'),(cards.WEAPON_TRIGGERS,'WEAPON_TRIGGERS'),(locations.LOCATION_RULES,'LOCATION_RULES')):
    change=patch.dict(table,getattr(mod,name,{}));change.start();self.addCleanup(change.stop)
 def ops(self,*ops,**ctx):self.fx.run_ops(self.g,ops,**ctx)
 def play(self,cid,target=None):
  c=self.g._add(0,cid);self.p.mana=10
  actions=[a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid and (target is None or a.target==target)]
  self.assertTrue(actions,cid);self.g.step(actions[0]);return c
 def choose(self,index=0):self.g.step(next(a for a in self.g.legal_actions() if a.kind=='choose' and a.choices==(index,)))
 def test_khadgar_doubles_effect_summons(self):
  self.g._summon(0,'CORE_DAL_575');self.ops(('summon','CORE_EX1_162',1));self.assertEqual(len(self.p.minions),3)
 def test_khadgar_does_not_duplicate_hand_play(self):
  self.g._summon(0,'CORE_DAL_575');self.play('CORE_EX1_162');self.assertEqual(len(self.p.minions),2)
 def test_khadgar_silence_disables_replacement(self):
  m=self.g._summon(0,'CORE_DAL_575');self.g._silence(m);self.ops(('summon','CORE_EX1_162',1));self.assertEqual(len(self.p.minions),2)
 def test_deios_repeats_battlecry(self):
  self.g.cards['CORE_EX1_162']=dict(self.g.cards['CORE_EX1_162'],mechanics=['BATTLECRY']);cards.RULES['CORE_EX1_162']=('none',[('draw',1)])
  self.g._summon(0,'TIME_064');self.play('CORE_EX1_162');self.assertEqual(len(self.p.hand),2)
 def test_deios_repeats_base_hero_power(self):
  self.g._summon(0,'TIME_064');self.g.step(Action('power',target=-2));self.assertEqual(self.q.health,28)
 def test_living_plague_replaces_hero_damage(self):
  m=self.g._summon(0,'JAIL_443');before=len(self.q.deck);self.g._damage(-2,4,damage_source=m,damage_owner=0);self.assertEqual(self.q.health,30);self.assertEqual(len(self.q.deck),before+4)
 def test_living_plague_still_damages_minions(self):
  m=self.g._summon(0,'JAIL_443');enemy=self.g._summon(1,'CORE_EX1_162');self.g._damage(enemy.uid,1,damage_source=m,damage_owner=0);self.assertEqual(enemy.health,1)
 def test_genn_parity_checkpoint(self):
  c=self.g._add(0,'CATA_615');self.g._add(0,'CORE_CS2_029');self.g._settle();self.assertEqual(c.card_id,'CATA_615t')
 def test_genn_replaces_primary_only(self):
  self.p.secondary_power=dict(card_id='JAIL_446hp',used=False);self.ops(('genn_upgrade',));self.assertEqual(self.p.primary_power['cost'],1);self.assertEqual(self.p.secondary_power['card_id'],'JAIL_446hp')
 def test_champion_buff_once_per_gain(self):
  m=self.g._summon(0,'JAIL_330');a,h=m.attack,m.max_health;self.g._buff(m,2,2);self.assertEqual((m.attack,m.max_health),(a+3,h+3));self.g._champion_checkpoint();self.assertEqual(m.attack,a+3)
 def test_champion_hand_gain(self):
  c=self.g._add(0,'JAIL_330');c.attack_bonus=2;self.g._champion_checkpoint();self.assertEqual((c.attack_bonus,c.health_bonus),(3,1))
 def test_vyranoth_wrong_total_no_stats(self):
  self.p.starting_deck=['CORE_EX1_162'];self.ops(('vyranoth_stats',));self.assertTrue(all(isinstance(c,str) for c in self.p.deck))
 def test_vyranoth_distributes_one_hundred_stats(self):
  self.p.starting_deck=['TIME_064']*10;self.g.cards['TIME_064']=dict(self.g.cards['TIME_064'],cost=10);self.p.deck=[Card(self.g._new_id(),'CORE_EX1_162') for _ in range(4)];self.ops(('vyranoth_stats',));self.assertEqual(sum(c.attack_bonus+c.health_bonus for c in self.p.deck),100)
 def test_tiny_pal_preserves_weapon_identity(self):
  self.play('JAIL_458');uid=self.p.equipped_card.uid;self.choose();self.assertEqual(self.p.equipped_card.uid,uid);self.assertEqual(self.p.weapon['card_id'],'JAIL_458t1')
 def test_tiny_pal_excludes_previous_ammunition(self):
  self.g._equip(0,'JAIL_458t1');self.ops(('tiny_choose','JAIL_458t1'));self.assertNotIn('JAIL_458t1',[o['card_id'] for o in self.g.pending_choice['options']])
 def test_ruby_converts_full_health_healing(self):
  self.ops(('ruby_sanctum',),('heal_own_hero',5));self.assertEqual(self.p.health,25)
 def test_ruby_consumes_one_effect(self):
  self.p.health=20;self.ops(('ruby_sanctum',),('heal_own_hero',3),('heal_own_hero',2));self.assertEqual(self.p.health,19)
 def test_ruby_all_targets_share_effect(self):
  m=self.g._summon(0,'TIME_064');h=m.health;self.ops(('ruby_sanctum',),('area_heal',2));self.assertEqual((self.p.health,m.health),(28,h-2))
 def test_holmes_choice_is_private(self):
  self.g._add(1,'CORE_CS2_029');self.ops(('investigate_hand',));self.assertTrue(self.g.observe(1)['pending_choice']['waiting']);self.assertEqual(self.g.observe(0)['pending_choice']['options'][0]['card_id'],'CORE_CS2_029')
 def test_holmes_matches_next_turn_name_once(self):
  c=self.g._add(1,'CORE_CS2_029');self.ops(('investigate_hand',));self.choose();self.g.current=1;self.q.turns_taken+=1;self.g._investigation_played(1,c);self.g._drain_events(allow_choices=True);self.assertEqual(len(self.p.hand),3);self.g._investigation_played(1,c);self.g._drain_events();self.assertEqual(len(self.p.hand),3)
 def test_forefather_correct_guess_gains_health(self):
  self.g._add(1,'CORE_CS2_029');self.g._generation_pools={(hand_investigations.DECOYS,'HUNTER'):__import__('expanded.pools',fromlist=['GenerationPool']).GenerationPool('fixture',('CORE_EX1_162',),'test')};m=self.g._summon(0,'TIME_041');h=m.max_health;self.ops(('guess_hand',),source=m);index=next(i for i,o in enumerate(self.g.pending_choice['options']) if o['card_id']=='CORE_CS2_029');self.choose(index);self.assertEqual(m.max_health,h+4)
 def test_nozdormu_requires_both_decks(self):
  from expanded.decks import Deck
  self.p.starting_deck=['CS3_035'];self.g._remaining_setup([Deck('MAGE',()),Deck('HUNTER',())]);self.assertIsNone(self.g.turn_time_limit);self.q.starting_deck=['CS3_035'];self.g._remaining_setup([Deck('MAGE',()),Deck('HUNTER',())]);self.assertEqual(self.g.turn_time_limit,15)
 def test_clock_timeout_ends_turn(self):
  self.g.turn_time_limit=15;turn=self.g.turn;self.assertFalse(self.g.elapse_decision_time(14));self.assertTrue(self.g.elapse_decision_time(1));self.assertEqual(self.g.turn,turn+1);self.assertEqual(self.g.current,1)
 def test_clock_rejects_nan_without_mutation(self):
  with self.assertRaises(ValueError):self.g.elapse_decision_time(float('nan'))
 def test_underbelly_choice_discount(self):
  self.p.contraband_beasts=('CORE_EX1_162',);self.ops(('contraband_discover',));self.choose();self.assertEqual(self.p.hand[0].cost_delta,-3);self.assertEqual(self.p.discoveries_total,1)
 def test_generated_underbelly_fails_without_contract(self):
  with self.assertRaises(UnsupportedCard):self.ops(('contraband_discover',))
 def test_informant_swap_changes_class(self):
  c=self.g._add(0,'CATA_614');self.ops(('informant_swap',c.uid));self.assertNotEqual(c.rule_state['informant_class'],'MAGE')
 def test_kindred_wrapper_doubles_only_kindred(self):
  self.ops(('draw',1),('kindred',[('armor',3)]),kindred=True,kindred_repeats=2);self.assertEqual(len(self.p.hand),1);self.assertEqual(self.p.armor,6)
 def test_kindred_consumes_only_when_active(self):
  self.ops(('kindred_twice_next',));self.assertEqual(kindred.consume_repetition(self.g,0,'TLC_440',False),1);self.assertTrue(self.p.kindred_twice);self.assertEqual(kindred.consume_repetition(self.g,0,'TLC_440',True),2);self.assertFalse(self.p.kindred_twice)
 def test_osk_enters_hand_as_form(self):
  c=self.g._add(0,'TLC_452');self.assertIn(c.card_id,titanographer.FORMS)
 def test_osk_draw_sets_three_values(self):
  self.p.deck=['CORE_EX1_162'];self.ops(('osk_draw_twos',));c=self.p.hand[0];self.assertEqual(tuple(self.g._card_stat(c,k,0) for k in ('attack','health','cost')),(2,2,2))
 def test_osk_control_has_no_health_restriction(self):
  m=self.g._summon(1,'TIME_064');self.ops(('osk_control',),target=m.uid);self.assertIn(m,self.p.minions)
 def test_osk_remove_is_not_death(self):
  m=self.g._summon(1,'CORE_EX1_162');self.ops(('osk_remove_pair',),target=m.uid);self.assertNotIn(m,self.q.board);self.assertFalse(self.q.death_history)
 def test_essence_split_preserves_original_deck(self):
  self.p.starting_deck=[dragon_soul.ROOT];self.p.deck=[dragon_soul.ROOT];self.g._essence_setup();self.assertEqual(len(self.p.deck),6);self.assertEqual(self.p.starting_deck,[dragon_soul.ROOT])
 def test_essence_neighbors_stop_at_other_card(self):
  a=self.g._add(0,dragon_soul.ESSENCES[3]);b=self.g._add(0,dragon_soul.ESSENCES[2]);self.g._add(0,'TOKEN_COIN');c=self.g._add(0,dragon_soul.ESSENCES[1]);self.assertEqual(self.g._essence_neighbors(a,0),(b.uid,));self.assertNotIn(c.uid,self.g._essence_neighbors(a,0))
 def test_essence_paid_chain_pays_once(self):
  self.g._add(0,dragon_soul.ESSENCES[3]);c=self.g._add(0,dragon_soul.ESSENCES[5]);self.p.mana=10;self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid));self.assertEqual(self.p.mana,4);self.assertEqual(self.p.armor,12);self.assertEqual(self.q.health,30);self.assertFalse(self.p.hand)
 def test_aya_single_owner_goes_second(self):
  self.p.starting_deck=['JAIL_504'];self.assertEqual(self.g._aya_setup(),1)
 def test_aya_replaces_existing_and_future_coins(self):
  c=self.g._add(0,'TOKEN_COIN');self.ops(('counterfeit_choose',));self.choose(1);self.assertEqual(c.card_id,'JAIL_504t2');future=self.g._add(0,'TOKEN_COIN');self.assertEqual(future.card_id,'JAIL_504t2');self.assertEqual(len(self.p.hand),5)
 def test_jade_grows_and_silence_keeps_base(self):
  self.ops(('counterfeit_jade',),('counterfeit_jade',));m=self.p.minions[-1];self.g._silence(m);self.assertEqual((m.attack,m.health),(2,2))
 def test_noggenfogger_never_attacks_self(self):
  m=self.g._summon(0,'CORE_CFM_670');targets={self.g._random_attack_target(m.uid,-2) for _ in range(40)};self.assertNotIn(m.uid,targets);self.assertIn(-1,targets)
 def test_morchie_does_not_offer_rewind_or_repay(self):
  from expanded import rewind
  change=patch.dict(cards.RULES,rewind.RULES);change.start();self.addCleanup(change.stop)
  with gzip.open('data/standard/all_cards.json.gz','rt') as f:self.g.cards.update({d['id']:d for d in json.load(f) if d['id']=='TIME_001'})
  self.g._summon(0,'END_036');self.play('TIME_001');self.assertEqual(self.q.health,18);self.assertIsNone(self.g.pending_choice);self.assertEqual(self.p.cards_played,1)
 def test_trial_choice_stores_both_parts_and_delay(self):
  self.ops(('craft_trial',));self.choose();self.choose();self.choose(2);card=self.p.hand[0];self.assertEqual(card.card_id,'CAP_405tb3');self.assertEqual(card.rule_state['crafted_ops'][0][1],4)
 def test_trial_immediate_draw_and_armor(self):
  self.ops(('trial_wait',0,(('draw',1),('armor',3))));self.assertEqual((len(self.p.hand),self.p.armor),(1,3))
 def test_trial_delayed_does_not_resolve_early(self):
  self.ops(('trial_wait',1,(('armor',3),)));self.assertEqual(self.p.armor,0);self.assertEqual(self.p.scheduled_effects[-1]['due'],self.p.turns_taken+1)
 def test_elise_predicate_uses_distinct_costs(self):
  self.p.starting_deck=['CORE_EX1_162']*10;self.ops(('craft_location',));self.assertIsNone(self.g.pending_choice)
 def test_elise_low_tier_excludes_copy(self):
  for _ in range(10):self.g._craft_location_parts(0,1,[]);self.assertNotIn('TLC_100t17',[o['card_id'] for o in self.g.pending_choice['options']])
 def test_custom_location_carries_operations_and_deathrattle(self):
  c=Card(self.g._new_id(),'TLC_100t1');c.rule_state=dict(crafted_location_ops=(('armor',3),),crafted_location_death=(('area_damage','enemies',1),));self.g._enter_hand(0,c);self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid));loc=self.p.locations[0];self.g.step(Action('activate',loc.uid));self.assertEqual(self.p.armor,3);self.g._remove_location(loc);self.g._settle();self.assertEqual(self.q.health,29)
 def test_forge_without_full_contract_fails(self):
  with self.assertRaises(UnsupportedCard):self.ops(('forge_dragon',))
 def test_forge_combines_stats_and_silence_preserves_them(self):
  part=minion_forge.ForgePart('CORE_EX1_162',source='fixture')
  self.g.forge_contracts={('dragon',1):(part,),('dragon',2):(part,)};self.ops(('forge_dragon',));self.choose();self.choose();c=self.p.hand[0];self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid));m=self.p.minions[0];self.g._silence(m);self.assertEqual((m.attack,m.health),(4,4))
 def test_sidequest_counts_dual_tribe_once(self):
  self.ops(('forge_sidequest',));c=Card(self.g._new_id(),'ICC_828t');self.g._forge_played(0,c);self.assertEqual(self.p.forge_sidequests[0]['progress'],1)
 def test_pack_requires_distribution_before_rng(self):
  before=self.g.rng.getstate()
  with self.assertRaises(UnsupportedCard):self.ops(('standard_pack',))
  self.assertEqual(before,self.g.rng.getstate())
 def test_pack_plays_generated_cards_without_paying(self):
  self.g.standard_pack_contract=dict(source='fixture',outcomes=((1,('CORE_EX1_162',)*5),));mana=self.p.mana;self.ops(('standard_pack',));self.assertEqual(len(self.p.minions),5);self.assertFalse(self.p.hand);self.assertEqual(self.p.mana,mana)
 def test_pack_full_hand_burns_generated_cards(self):
  for _ in range(10):self.g._add(0,'TOKEN_COIN')
  self.g.standard_pack_contract=dict(source='fixture',outcomes=((1,('CORE_EX1_162',)*5),));self.ops(('standard_pack',));self.assertEqual(len(self.p.hand),10);self.assertFalse(self.p.minions)
 def test_fire_damage_immunity_and_silence(self):
  m=self.g._summon(1,'FIR_959');health=m.health;ctx=dict(card_id='CORE_CS2_029',spell=True,target=m.uid);self.ops(('damage',6),**ctx);self.assertEqual(m.health,health);self.g._silence(m);self.ops(('damage',1),**ctx);self.assertEqual(m.health,health-1)
 def test_fire_nondamage_target_immunity(self):
  m=self.g._summon(1,'FIR_959');self.ops(('destroy',),card_id='CORE_CS2_029',spell=True,target=m.uid);self.assertGreater(m.health,0)
 def test_fire_unreviewed_bulk_replacement_fails(self):
  self.g._summon(1,'FIR_959')
  self.g._summon(0,'NEW1_034')
  with self.assertRaises(UnsupportedCard):self.ops(('mutation_board',1,True),card_id='CORE_CS2_029',spell=True)
 def test_fyrakk_budget_does_not_spend_player_mana(self):
  self.fx.install(self.g,exceptional_finish.FIRE,['CORE_CS2_029']);mana=self.p.mana;self.ops(('fyrakk_budget',8,0));self.assertEqual(self.q.health,18);self.assertEqual(self.p.mana,mana)
 def test_suspicious_option_exposes_modified_stats_privately(self):
  self.fx.install(self.g,exceptional_finish.MINIONS,['CORE_EX1_162']);self.g.suspicious_mutation_contract=dict(source='fixture',mutations=({'field':'attack','delta':1},));m=self.g._summon(0,'JAIL_EVENT_100');a=m.attack;self.ops(('suspicious_discover',),source=m);self.assertEqual(self.g.observe(0)['pending_choice']['options'][0]['attack'],3);self.assertTrue(self.g.observe(1)['pending_choice']['waiting']);self.choose();self.assertEqual(self.p.hand[0].attack_bonus,1);self.assertEqual(m.attack,a+1)
 def test_suspicious_unsupported_mutations_fail_explicitly(self):
  self.fx.install(self.g,exceptional_finish.MINIONS,['CORE_EX1_162']);self.g.suspicious_mutation_contract=dict(source='fixture',mutations=({'field':'name','delta':1},))
  with self.assertRaises(UnsupportedCard):self.ops(('suspicious_discover',))
 def test_public_observations_still_serialize(self):
  self.g._add(0,'TLC_452');self.ops(('kindred_twice_next',),('ruby_sanctum',));json.dumps(self.g.observe(0),allow_nan=False);json.dumps(self.g.observe(1),allow_nan=False)

def osk_form_case(cid):
 def check(self):
  self.g.cards['CORE_EX1_162']=dict(self.g.cards['CORE_EX1_162'],cost=6)
  self.fx.install(self.g,titanographer.SIX,['CORE_EX1_162'])
  self.fx.install(self.g,titanographer.DR,['LOOT_368'])
  self.fx.install(self.g,titanographer.pool(card_type='SPELL',mechanic='SECRET',classes='MAGE'),['CORE_EX1_287'])
  self.p.deck=['CORE_EX1_162']*12;self.p.health=18
  source=self.g._summon(0,cid);enemy=self.g._summon(1,'CORE_EX1_162');self.g._summon(1,'CORE_EX1_162')
  mode,operations=titanographer.TOKEN_RULES[cid]
  self.fx.run_ops(self.g,operations,source=source,card_id=cid,target=enemy.uid if mode!='none' else 0)
  for _ in range(8):
   if self.g.pending_choice is None:break
   self.choose()
  self.assertIsNone(self.g.pending_choice)
  self.g.assert_invariants()
 return check
for identity in titanographer.FORMS:setattr(FinalCardPathsTests,'test_osk_form_'+identity,osk_form_case(identity))
