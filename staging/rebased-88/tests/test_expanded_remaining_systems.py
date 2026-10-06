import unittest,gzip,json
from pathlib import Path
from copy import deepcopy
from unittest.mock import patch
import test_expanded_generation as fixtures
from expanded import cards,Action,transformations,temporary_control
from expanded.game import Card
from expanded.generation_cards import pool
from expanded.pools import GenerationPool
from expanded.features import encode_decision
from engine.cards import UnsupportedCard

class RemainingSystemTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with gzip.open(Path(__file__).resolve().parents[1]/'data/standard/all_cards.json.gz','rt') as f:cls.records={c['id']:c for c in json.load(f)}
 def setUp(self):
  self.g=fixtures.GenerationTests().game();self.g._generation_pools={}
  self.g.cards.update({cid:deepcopy(self.records[cid]) for cid in ('TIME_030','TIME_707','TIME_217','CATA_496','JAIL_509')})
  p=patch.dict(cards.RULES,{**transformations.RULES,**temporary_control.RULES});p.start();self.addCleanup(p.stop)
 @property
 def p(self):return self.g.players[0]
 @property
 def q(self):return self.g.players[1]
 def op(self,*ops,target=0):self.g._start_play_effects(ops,dict(owner=0,source=None,target=target,bonus=0,lifesteal=False));self.g._settle(allow_event_choices=True)
 def test_split_rounds_odd_stats_up_and_preserves_physical_original(self):
  c=self.g._enter_hand(0,Card(self.g._new_id(),'NEW1_034'));c.attack_bonus=1;c.health_bonus=1;c.set_cost=5;uid=c.uid
  self.op(('mutation_split_minion',));self.assertEqual(len(self.p.hand),2);self.assertEqual(self.p.hand[0].uid,uid)
  self.assertEqual([self.g._cost(x,0) for x in self.p.hand],[3,3]);self.assertEqual([x.attack_bonus for x in self.p.hand],[-1,-1]);self.assertEqual([x.health_bonus for x in self.p.hand],[0,0])
 def test_split_full_hand_keeps_one_half_and_does_not_overfill(self):
  self.g._enter_hand(0,Card(self.g._new_id(),'NEW1_034'))
  for _ in range(9):self.g._enter_hand(0,Card(self.g._new_id(),'CORE_CS2_029'))
  self.op(('mutation_split_minion',));self.assertEqual(len(self.p.hand),10);self.assertEqual(self.p.hand[0].attack_bonus,-2)
 def test_split_without_minion_is_noop(self):
  c=self.g._enter_hand(0,Card(self.g._new_id(),'CORE_CS2_029'));self.op(('mutation_split_minion',));self.assertEqual(self.p.hand,[c])
 def alternate_pool(self):
  cid='TEST_PAST_CHOOSE';self.g.cards[cid]=dict(id=cid,name=cid,type='SPELL',cost=4,mechanics=['CHOOSE_ONE'],cardClass='DRUID',set='EXPERT1',collectible=True)
  self.g._generation_pools[(pool(era='past',mechanic='CHOOSE_ONE'),self.p.hero_class)]=GenerationPool('fixture',(cid,),'Controlled historical membership')
  return cid
 def test_alternate_reality_keeps_zone_sizes_and_replaces_identity(self):
  cid=self.alternate_pool();self.g._enter_hand(0,Card(self.g._new_id(),'CORE_CS2_029'));before=(len(self.p.hand),len(self.p.deck));self.op(('mutation_alternate_reality',))
  self.assertEqual((len(self.p.hand),len(self.p.deck)),before);self.assertTrue(all(c.card_id==cid and c.cost_delta==-1 for c in self.p.hand+self.p.deck))
 def test_alternate_reality_missing_pool_does_not_mutate_zones(self):
  old=list(self.p.deck)
  with self.assertRaises(UnsupportedCard):self.op(('mutation_alternate_reality',))
  self.assertEqual(self.p.deck,old)
 def test_stormrook_replaces_nature_damage_without_consuming_shield(self):
  m=self.g._summon(0,'TIME_217');m.keywords.add('DIVINE_SHIELD');self.g.cards['TEST_NATURE']=dict(id='TEST_NATURE',type='SPELL',spellSchool='NATURE')
  self.g.cards['TEST_FIVE']=dict(id='TEST_FIVE',name='Five',type='MINION',cost=5,attack=1,health=1,cardClass='NEUTRAL')
  r=pool(card_type='MINION',minimum=5,maximum=5);self.g._generation_pools[(r,self.p.hero_class)]=GenerationPool('fixture',('TEST_FIVE',),'Controlled membership')
  self.assertEqual(self.g._deal_effect(m.uid,100,dict(owner=0,source=None,spell=True,card_id='TEST_NATURE')),0);self.g._settle(allow_event_choices=True)
  self.assertEqual(m.health,5);self.assertIn('DIVINE_SHIELD',m.keywords);self.assertEqual(len(self.p.minions),2)
 def test_stormrook_non_nature_damage_is_normal(self):
  m=self.g._summon(0,'TIME_217');self.g._deal_effect(m.uid,1,dict(owner=0,source=None,spell=True,card_id='CORE_CS2_029'));self.assertEqual(m.health,4)
 def godfrey(self):
  self.p.starting_deck=['JAIL_509'];self.g._starting_rules()
  for _ in range(10):self.g._enter_hand(0,Card(self.g._new_id(),'CORE_CS2_029'))
 def test_godfrey_preserves_burned_physical_card_and_discounts_once(self):
  self.godfrey();c=Card(self.g._new_id(),'NEW1_034');self.g._receive_draw(0,c)
  self.assertEqual(self.p.overdraw_cache,[c]);self.assertEqual(c.cost_delta,-1);self.p.hand.pop();self.g._refresh_auras()
  self.assertIs(self.p.hand[-1],c);self.assertFalse(self.p.overdraw_cache);self.assertEqual(c.cost_delta,-1)
 def test_godfrey_multiple_returns_keep_fifo_order(self):
  self.godfrey();a=Card(self.g._new_id(),'NEW1_034');b=Card(self.g._new_id(),'CORE_CS2_029')
  self.g._receive_draw(0,a);self.g._receive_draw(0,b);self.p.hand[:]=self.p.hand[:-2];self.g._refresh_auras();self.assertEqual(self.p.hand[-2:],[a,b])
 def test_godfrey_generated_burn_is_not_overdraw(self):
  self.godfrey();self.g._add(0,'NEW1_034');self.assertFalse(self.p.overdraw_cache)
 def test_godfrey_generated_copy_does_not_enable_starting_rule(self):
  self.g._summon(0,'JAIL_509');self.assertFalse(self.p.overdraw_return_active)
 def test_godfrey_cache_identity_private_and_clone_safe(self):
  self.godfrey();self.g._receive_draw(0,Card(self.g._new_id(),'NEW1_034'));clone=deepcopy(self.g)
  self.assertEqual(self.g.observe(0),clone.observe(0));self.assertIn('overdraw_cache',self.g.observe(0)['players'][0]);self.assertNotIn('overdraw_cache',self.g.observe(1)['players'][0])
 def steal(self):
  m=self.g._summon(1,'NEW1_034');self.op(('temporary_control',),target=m.uid);return m
 def test_control_prohibits_charge_attack_on_cast_turn(self):
  m=self.steal();m.keywords.add('CHARGE');self.assertEqual(m.owner,0);self.assertIn('CANT_ATTACK',self.g._effective_keywords(m))
 def test_control_returns_after_enemy_turn_not_caster_turn(self):
  m=self.steal();self.g.step(Action('end'));self.assertEqual(m.owner,0);self.g.step(Action('end'));self.assertEqual(m.owner,1)
 def test_silence_does_not_cancel_control_deadline(self):
  m=self.steal();self.g._silence(m);self.g.step(Action('end'));self.g.step(Action('end'));self.assertEqual(m.owner,1)
 def test_transform_retains_control_deadline(self):
  m=self.steal();m=self.g._transform(m,'NEW1_034');self.g.step(Action('end'));self.g.step(Action('end'));self.assertEqual(m.owner,1)
 def test_copied_minion_does_not_inherit_control_deadline(self):
  m=self.steal();copy=self.g._summon(0,m.card_id,copy_from=m);self.assertFalse(hasattr(copy,'_control_return'))
 def test_return_to_full_board_destroys_stolen_minion(self):
  m=self.steal()
  for _ in range(7):self.g._summon(1,'NEW1_034')
  self.g.step(Action('end'));self.g.step(Action('end'));self.assertNotIn(m,self.p.board);self.assertNotIn(m,self.q.board)
 def test_control_timer_is_public(self):
  self.steal();view=self.g.observe(0);self.assertEqual(view['players'][0]['board'][0]['control_return']['to'],'opponent')
