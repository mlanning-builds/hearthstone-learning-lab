"""Shared transformation behavior with controlled pools, not production admission."""
import copy,json,unittest
from unittest.mock import patch
import test_expanded_generation as fixtures
from engine.game import Card
from engine.cards import UnsupportedCard
from expanded import Action
from expanded import cards
from expanded.transformations import RULES,START_EFFECTS,TRIGGERS,UNRESOLVED,cost_pool,requests_for
from expanded.generation_cards import pool
from expanded.pools import GenerationPool
from standard.catalog import load_catalog

class TransformationTests(unittest.TestCase):
 def setUp(self):
  self.g=fixtures.GenerationTests().game();self.p=self.g.players[0];self.q=self.g.players[1]
  self.g.cards.update({c['id']:c for c in load_catalog() if c['id'] in RULES})
  self.g._generation_pools={}
  for table,values in ((cards.RULES,RULES),(cards.START_EFFECTS,START_EFFECTS),(cards.TRIGGERS,TRIGGERS)):
   context=patch.dict(table,values);context.start();self.addCleanup(context.stop)
 def install(self,request,ids,owner=0):
  self.g._generation_pools[(request,self.g.players[owner].hero_class)]=GenerationPool('fixture only',tuple(ids),'Controlled test; not complete production membership')
 def fake(self,cid,cost=2,attack=2,health=3,**extra):
  self.g.cards[cid]=dict(id=cid,name=cid,type='MINION',cardClass='NEUTRAL',cost=cost,attack=attack,health=health,mechanics=[],**extra);return cid
 def add(self,cid):
  c=Card(self.g._new_id(),cid);self.g._enter_hand(0,c);return c
 def run_card(self,cid,target=0,source=None):
  self.g._mutation_preflight(cid,0)
  self.g._start_play_effects(RULES[cid][1],dict(owner=0,source=source,card_id=cid,target=target,bonus=0,lifesteal=False));self.g._settle(allow_event_choices=True)
 def op(self,operation,source=None):
  self.g._start_play_effects([operation],dict(owner=0,source=source,target=0,bonus=0,lifesteal=False));self.g._settle(allow_event_choices=True)
 def choose(self,index=0):self.g.step(Action('choose',choices=(index,)))
 def test_family_accounted_for_without_false_admission(self):
  from expanded.pending_definitions import DEFINITIONS
  from expanded.genn import RULES as SHARED_RULES
  self.assertEqual(set(RULES)|set(UNRESOLVED)|set(SHARED_RULES),{cid for cid,d in DEFINITIONS.items() if d['family']=='transformation'})
  self.assertFalse(set(SHARED_RULES)&cards.COLLECTIBLE_IDS)
  self.assertFalse(set(RULES)&cards.COLLECTIBLE_IDS)
 def test_missing_pool_before_board_mutation(self):
  m=self.g._summon(0,'CORE_CS2_188');before=self.g.rng.getstate()
  with self.assertRaises(UnsupportedCard):self.run_card('CATA_567')
  self.assertEqual(self.p.minions,[m]);self.assertEqual(before,self.g.rng.getstate())
 def test_later_member_pool_checked_before_first_transform(self):
  a=self.g._summon(0,'CORE_CS2_188');b=self.g._summon(0,'CORE_EX1_012');self.install(cost_pool(2),['CORE_EX1_012'])
  with self.assertRaises(UnsupportedCard):self.run_card('CATA_567')
  self.assertEqual(self.p.minions,[a,b])
 def test_ascendance_replaces_all_and_preserves_positions(self):
  a=self.g._summon(0,'CORE_CS2_188');b=self.g._summon(0,'CORE_CS2_188');enemy=self.g._summon(1,'CORE_CS2_188')
  self.install(cost_pool(2),['CORE_EX1_012']);self.run_card('CATA_567')
  self.assertEqual([m.card_id for m in self.p.minions],['CORE_EX1_012']*2);self.assertEqual(self.q.minions,[enemy]);self.assertNotIn(a,self.p.minions);self.assertNotIn(b,self.p.minions)
 def test_ascendance_attaches_original_deathrattle(self):
  self.g._summon(0,'CORE_CS2_188');self.install(cost_pool(2),['CORE_EX1_012']);self.run_card('CATA_567')
  self.p.minions[0].health=0;self.g._settle();self.assertEqual([m.card_id for m in self.p.minions],['CORE_CS2_188'])
 def test_transform_not_summon_or_death(self):
  self.g._summon(0,'CORE_CS2_188');self.install(cost_pool(2),['CORE_EX1_012']);before=len(self.g.events);self.run_card('CATA_567')
  self.assertFalse(self.p.death_history);self.assertFalse(any(e['event']=='summon' for e in self.g.events[before:]))
 def test_ascendance_empty_exact_pool_retains_original(self):
  m=self.g._summon(0,'CORE_CS2_188');self.install(cost_pool(2),[]);self.run_card('CATA_567');self.assertEqual(self.p.minions,[m]);self.assertFalse(m.attached_death_effects)
 def test_silence_removes_attached_original(self):
  self.g._summon(0,'CORE_CS2_188');self.install(cost_pool(2),['CORE_EX1_012']);self.run_card('CATA_567');self.g._silence(self.p.minions[0]);self.p.minions[0].health=0;self.g._settle();self.assertFalse(self.p.minions)
 def test_full_board_transforms_without_extra_slots(self):
  for _ in range(7):self.g._summon(0,'CORE_CS2_188')
  self.install(cost_pool(2),['CORE_EX1_012']);self.run_card('CATA_567');self.assertEqual(len(self.p.minions),7);self.assertTrue(all(m.card_id=='CORE_EX1_012' for m in self.p.minions))
 def test_podling_redirects_intended_cost_plus_two(self):
  m=self.g._summon(0,'EDR_529');self.install(cost_pool(4),[self.fake('FIX_FOUR',4)]);result=self.g._transform(m,'CORE_EX1_012');self.assertEqual(result.card_id,'FIX_FOUR')
 def test_podling_missing_pool_preserves_original(self):
  m=self.g._summon(0,'EDR_529');before=self.g.rng.getstate()
  with self.assertRaises(UnsupportedCard):self.g._transform(m,'CORE_EX1_012')
  self.assertIn(m,self.p.minions);self.assertEqual(before,self.g.rng.getstate())
 def test_silenced_podling_uses_normal_transform(self):
  m=self.g._summon(0,'EDR_529');self.g._silence(m);self.assertEqual(self.g._transform(m,'CORE_EX1_012').card_id,'CORE_EX1_012')
 def test_alarashi_retains_stats_cost_identity_and_enchantments(self):
  c=self.add('CORE_CS2_188');c.attack_bonus=4;c.health_bonus=5;c.cost_delta=-1;uid=c.uid
  demon=self.fake('FIX_DEMON',7,8,9,races=['DEMON']);self.install(pool(card_type='MINION',tribe='DEMON'),[demon]);self.run_card('EDR_493')
  self.assertEqual((c.uid,c.card_id),(uid,demon));self.assertEqual((self.g.cards[demon]['attack']+c.attack_bonus,self.g.cards[demon]['health']+c.health_bonus),(5,6));self.assertEqual(self.g._cost(c,0),0)
 def test_alarashi_leaves_spells_and_enemy_hand(self):
  c=self.add('CORE_CS2_029');self.q.hand=[Card(self.g._new_id(),'CORE_CS2_188')];before=copy.deepcopy(self.q.hand)
  self.install(pool(card_type='MINION',tribe='DEMON'),[]);self.run_card('EDR_493');self.assertEqual(self.p.hand,[c]);self.assertEqual(self.q.hand,before)
 def test_deck_transform_keeps_order_and_only_neutrals(self):
  druid=self.fake('FIX_DRUID',3);self.g.cards[druid]['cardClass']='DRUID';self.install(pool(classes='DRUID'),[druid]);self.p.deck=['CORE_CS2_188','CORE_CS2_029','CORE_EX1_012'];self.run_card('EDR_873');self.assertEqual(self.p.deck,[druid,'CORE_CS2_029',druid]);self.assertFalse(self.p.hand)
 def test_deck_physical_cards_retain_enchantments(self):
  druid=self.fake('FIX_DRUID',3);self.g.cards[druid]['cardClass']='DRUID';self.install(pool(classes='DRUID'),[druid]);c=Card(self.g._new_id(),'CORE_CS2_188');c.cost_delta=-1;self.p.deck=[c];self.run_card('EDR_873');self.assertIs(self.p.deck[0],c);self.assertEqual(c.cost_delta,-1)
 def test_life_cycle_enemy_owner_and_position(self):
  a=self.g._summon(1,'CORE_CS2_188');b=self.g._summon(1,'CORE_CS2_188');c=self.g._summon(1,'CORE_CS2_188');replacement=self.fake('FIX_ONE',1);self.install(cost_pool(1),[replacement],1)
  self.run_card('TLC_235',b.uid);self.assertEqual([m.card_id for m in self.q.minions],['CORE_CS2_188',replacement,'CORE_CS2_188']);self.assertEqual([m.uid for m in self.q.minions][::2],[a.uid,c.uid]);self.assertIn(b.card_id,self.q.death_history)
 def test_life_cycle_requires_pool_before_destroy(self):
  m=self.g._summon(1,'CORE_CS2_188')
  with self.assertRaises(UnsupportedCard):self.run_card('TLC_235',m.uid)
  self.assertIn(m,self.q.minions);self.assertEqual(m.health,1)
 def test_life_cycle_empty_pool_still_destroys(self):
  m=self.g._summon(1,'CORE_CS2_188');self.install(cost_pool(1),[],1);self.run_card('TLC_235',m.uid);self.assertFalse(self.q.minions)
 def test_variant_start_turn_hook(self):
  m=self.g._summon(0,'TIME_049');replacement=self.fake('FIX_FIVE',5);self.install(cost_pool(5),[replacement]);self.g.step(Action('end'));self.g.step(Action('end'));self.assertEqual(self.p.minions[0].card_id,replacement)
 def test_variant_silence_blocks_turn_hook(self):
  m=self.g._summon(0,'TIME_049');self.g._silence(m);self.g.step(Action('end'));self.g.step(Action('end'));self.assertIn(m,self.p.minions)
 def test_voyager_surviving_damage_hook(self):
  m=self.g._summon(0,'TIME_055');replacement=self.fake('FIX_SEVEN',7);self.install(cost_pool(7),[replacement]);self.g._damage(m.uid,1);self.g._settle();self.assertEqual(self.p.minions[0].card_id,replacement)
 def test_voyager_lethal_does_not_transform(self):
  m=self.g._summon(0,'TIME_055');self.g._damage(m.uid,100);self.g._settle();self.assertFalse(self.p.minions)
 def test_bribe_summons_for_both_transforms_only_friendly(self):
  two=self.fake('FIX_TWO',2);three=self.fake('FIX_THREE',3)
  for owner in (0,1):self.install(cost_pool(2),[two],owner)
  self.install(cost_pool(3),[three]);self.run_card('JAIL_EVENT_102');self.assertEqual([m.card_id for m in self.p.minions],[three]*2);self.assertEqual([m.card_id for m in self.q.minions],[two]*2)
 def test_bribe_missing_opponent_pool_before_summons(self):
  self.install(cost_pool(2),['CORE_EX1_012']);self.install(cost_pool(3),[])
  with self.assertRaises(UnsupportedCard):self.run_card('JAIL_EVENT_102')
  self.assertFalse(self.p.minions+self.q.minions)
 def test_anomalize_preserves_four_value_multiset(self):
  a=self.fake('FIX_TEN',10,8,9);b=self.fake('FIX_ONE',1,2,3);self.install(cost_pool(10),[a]);self.install(cost_pool(1),[b]);self.run_card('TIME_859');self.assertEqual(sorted(v for m in self.p.minions for v in (m.attack,m.health)),[2,3,8,9])
 def test_anomalize_full_board_safe(self):
  for _ in range(7):self.g._summon(0,'CORE_CS2_188')
  self.install(cost_pool(10),[]);self.install(cost_pool(1),['CORE_CS2_188']);self.run_card('TIME_859');self.assertEqual(len(self.p.minions),7)
 def test_anomalize_requires_both_pools_before_summoning(self):
  a=self.fake('FIX_TEN',10);self.install(cost_pool(10),[a])
  with self.assertRaises(UnsupportedCard):self.run_card('TIME_859')
  self.assertFalse(self.p.minions)
 def test_alchemist_choice_includes_every_held_type(self):
  a=self.add('CORE_CS2_188');b=self.add('CORE_CS2_029');self.install(cost_pool(6,'SPELL'),[]);self.install(cost_pool(9,'SPELL'),[]);self.run_card('JAIL_313');self.assertEqual({o['uid'] for o in self.g.pending_choice['options']},{a.uid,b.uid})
 def test_alchemist_replaces_selected_and_keeps_cost(self):
  c=self.add('CORE_CS2_188');spell=self.fake('FIX_SPELL',6);self.g.cards[spell]['type']='SPELL';self.install(cost_pool(6,'SPELL'),[spell]);self.run_card('JAIL_313');self.choose();self.assertEqual(c.card_id,spell);self.assertEqual(self.g._cost(c,0),1)
 def test_split_choice_only_spells(self):
  self.add('CORE_CS2_188');c=self.add('CORE_CS2_029');self.install(cost_pool(4,'SPELL'),['CORE_CS2_029']);self.run_card('CATA_979');self.assertEqual([o['uid'] for o in self.g.pending_choice['options']],[c.uid])
 def test_split_adds_two_spells_total(self):
  self.add('CORE_CS2_029');self.install(cost_pool(4,'SPELL'),['CORE_CS2_029']);self.run_card('CATA_979');self.choose();self.assertEqual([c.card_id for c in self.p.hand],['CORE_CS2_029']*2)
 def test_split_full_hand_does_not_exceed_limit(self):
  for _ in range(10):self.add('CORE_CS2_029')
  self.install(cost_pool(4,'SPELL'),['CORE_CS2_029']);self.run_card('CATA_979');self.choose();self.assertEqual(len(self.p.hand),10)
 def test_choice_hidden_from_opponent_and_not_discover(self):
  self.add('CORE_CS2_029');self.install(cost_pool(4,'SPELL'),['CORE_CS2_029']);self.run_card('CATA_979');self.assertTrue(self.g.observe(1)['pending_choice']['waiting']);self.choose();self.assertEqual(self.p.discoveries_this_turn,0)
 def test_unknown_outcome_not_silently_filtered(self):
  self.install(pool(card_type='MINION',tribe='DEMON'),['missing']);self.add('CORE_CS2_188')
  with self.assertRaises(UnsupportedCard):self.run_card('EDR_493')
  self.assertEqual(self.p.hand[0].card_id,'CORE_CS2_188')
 def test_observations_remain_json_serializable(self):
  self.add('CORE_CS2_029');self.install(cost_pool(4,'SPELL'),['CORE_CS2_029']);self.run_card('CATA_979');json.dumps(self.g.observe(0));json.dumps(self.g.observe(1))

 def test_hand_podling_redirects_transform(self):
  c=self.add('EDR_529');self.install(cost_pool(4),[self.fake('FIX_FOUR',4)]);self.g._b60_transform_card(c,'CORE_EX1_012');self.assertEqual(c.card_id,'FIX_FOUR')
 def test_alarashi_checks_podling_outcomes_before_changing_hand(self):
  self.add('CORE_CS2_188');self.add('EDR_529');demon=self.fake('FIX_DEMON',7,races=['DEMON']);self.install(pool(card_type='MINION',tribe='DEMON'),[demon]);before=self.g.rng.getstate()
  with self.assertRaises(UnsupportedCard):self.run_card('EDR_493')
  self.assertEqual([c.card_id for c in self.p.hand],['CORE_CS2_188','EDR_529']);self.assertEqual(before,self.g.rng.getstate())
 def test_paid_dynamic_pool_failure_rolls_back_mana_and_hand(self):
  c=self.add('CATA_567');self.g._summon(0,'CORE_CS2_188');before=self.g.rng.getstate();mana=self.p.mana
  action=next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid)
  with self.assertRaises(UnsupportedCard):self.g.step(action)
  self.assertEqual(self.g.players[0].mana,mana);self.assertIn(c.uid,[v.uid for v in self.g.players[0].hand]);self.assertEqual(before,self.g.rng.getstate())
 def test_paid_ascendance_uses_shared_dispatch(self):
  c=self.add('CATA_567');self.g._summon(0,'CORE_CS2_188');self.install(cost_pool(2),['CORE_EX1_012'])
  self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid));self.assertEqual(self.p.minions[0].card_id,'CORE_EX1_012');self.assertNotIn(c,self.p.hand)

 def test_tribute_copy_obeys_podling_replacement(self):
  target=self.g._summon(0,'EDR_529');model=self.g._summon(1,'CORE_EX1_012');self.install(cost_pool(4),[self.fake('FIX_FOUR',4)])
  self.g._entity_choice(dict(kind='entity_tribute',target_uid=target.uid),dict(uid=model.uid));self.assertEqual(self.p.minions[0].card_id,'FIX_FOUR')
 def test_ascendance_podling_checks_redirect_before_rng(self):
  m=self.g._summon(0,'EDR_529');self.install(cost_pool(2),['CORE_EX1_012']);before=self.g.rng.getstate()
  with self.assertRaises(UnsupportedCard):self.run_card('CATA_567')
  self.assertEqual(before,self.g.rng.getstate());self.assertEqual(self.p.minions,[m])
 def test_missing_selected_card_rolls_back_choice(self):
  c=self.add('CORE_CS2_029');self.install(cost_pool(4,'SPELL'),['CORE_CS2_029']);self.run_card('CATA_979');self.p.hand.remove(c)
  with self.assertRaises(UnsupportedCard):self.choose()
  self.assertIsNotNone(self.g.pending_choice)
 def test_anomalize_scramble_can_assign_zero_health(self):
  a=self.g._summon(0,self.fake('FIX_A',1,0,3));b=self.g._summon(0,self.fake('FIX_B',1,2,4))
  with patch.object(self.g.rng,'shuffle',side_effect=lambda values:values.__setitem__(slice(None),[3,0,4,2])):
   self.op(('mutation_scramble',{'summoned':[a.uid,b.uid]}))
  self.assertNotIn(a,self.p.minions);self.assertIn(b,self.p.minions);self.assertEqual((b.attack,b.health),(4,2))
 def test_anomalize_ignores_dormant_entities(self):
  a=self.g._summon(0,self.fake('FIX_A',1,2,3));b=self.g._summon(0,self.fake('FIX_B',1,4,5));b.dormant=True
  self.op(('mutation_scramble',{'summoned':[a.uid,b.uid]}));self.assertEqual((b.attack,b.health),(4,5));self.assertEqual(sorted([a.attack,a.health]),[2,3])
 def test_life_cycle_processes_deathrattle_before_replacement(self):
  target=self.g._summon(1,'CORE_CS2_188');target.attached_death_effects=[('summon','CORE_CS2_188',7)];self.install(cost_pool(1),[self.fake('FIX_REPLACEMENT',1)])
  self.install(cost_pool(1),['FIX_REPLACEMENT'],1);self.run_card('TLC_235',target.uid)
  self.assertEqual(len(self.q.minions),7);self.assertTrue(all(m.card_id=='CORE_CS2_188' for m in self.q.minions))
