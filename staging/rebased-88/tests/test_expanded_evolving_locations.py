import unittest,gzip,json
from pathlib import Path
from copy import deepcopy
from unittest.mock import patch
import test_expanded_generation as fixtures
from expanded import cards,locations,Action,evolving_locations as rules
from expanded.generation_cards import pool
from expanded.pools import GenerationPool
from engine.cards import UnsupportedCard

class EvolvingLocationTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with gzip.open(Path(__file__).resolve().parents[1]/'data/standard/all_cards.json.gz','rt') as f:cls.records={c['id']:c for c in json.load(f)}
 def setUp(self):
  self.g=fixtures.GenerationTests().game();self.g._generation_pools={}
  ids=set(rules.LOCATION_RULES)|{'CATA_527t2'}
  self.g.cards.update({cid:deepcopy(self.records[cid]) for cid in ids})
  for table,values in ((cards.RULES,rules.RULES),(locations.LOCATION_RULES,rules.LOCATION_RULES),(cards.TRIGGERS,rules.TRIGGERS)):
   c=patch.dict(table,values);c.start();self.addCleanup(c.stop)
 @property
 def p(self):return self.g.players[0]
 @property
 def q(self):return self.g.players[1]
 def place(self,cid):return self.g._place_location(0,cid)
 def activate(self,m,target=0):
  m.ready_turn=self.g.turn;self.g.step(Action('activate',m.uid,target))
 def contract(self,r,ids):self.g._generation_pools[(r,self.p.hero_class)]=GenerationPool('fixture',tuple(ids),'Controlled membership only')
 def test_gnomeregan_advances_and_retains_uid_durability_cooldown(self):
  loc=self.place('TIME_044');m=self.g._summon(0,'NEW1_034');uid=loc.uid;self.activate(loc,m.uid)
  self.assertEqual((loc.card_id,loc.uid,loc.durability,loc.ready_turn),('TIME_044t1',uid,2,self.g.turn+4));self.assertEqual((m.attack,m.max_health),(6,3))
 def test_gnomeregan_stages_attach_deathrattle_and_shield(self):
  loc=self.place('TIME_044');m=self.g._summon(0,'NEW1_034')
  for _ in range(3):self.activate(loc,m.uid)
  self.assertNotIn(loc,self.p.board);self.assertIn('DIVINE_SHIELD',m.keywords);self.assertEqual(len(m.attached_death_effects),2)
  m.health=0;self.g._settle();self.assertEqual(self.q.health,26)
 def test_missing_future_stage_rolls_back_activation(self):
  loc=self.place('TIME_044');m=self.g._summon(0,'NEW1_034');del self.g.cards['TIME_044t2']
  with self.assertRaises(UnsupportedCard):self.activate(loc,m.uid)
  self.assertEqual(loc.durability,3);self.assertEqual(self.p.locations[0].card_id,'TIME_044')
 def dragon_pool(self):
  self.g.cards['TEST_DRAGON']=dict(id='TEST_DRAGON',name='Dragon',type='MINION',cost=5,attack=3,health=3,race='DRAGON',races=['DRAGON'],cardClass='NEUTRAL')
  self.contract(rules.DRAGONS,['TEST_DRAGON'])
 def test_conflux_three_stages_and_final_hand_copy(self):
  self.dragon_pool();loc=self.place('TIME_436');self.activate(loc)
  self.assertEqual(loc.card_id,'TIME_436t1');self.activate(loc);self.assertIsNotNone(self.g.pending_choice)
  self.g.step(Action('choose',choices=(0,)));self.assertEqual(loc.card_id,'TIME_436t2');self.activate(loc);self.g.step(Action('choose',choices=(0,)))
  self.assertEqual(len(self.p.minions),3);self.assertEqual([c.card_id for c in self.p.hand],['TEST_DRAGON']);self.assertEqual(self.p.discoveries_total,2)
 def test_conflux_missing_pool_preserves_charge(self):
  loc=self.place('TIME_436')
  with self.assertRaises(UnsupportedCard):self.activate(loc)
  self.assertEqual(self.p.locations[0].durability,3)
 def test_conflux_choice_clone_resumes_same_stage(self):
  self.dragon_pool();loc=self.place('TIME_436t1');self.activate(loc);clone=deepcopy(self.g)
  self.g.step(Action('choose',choices=(0,)));clone.step(Action('choose',choices=(0,)));self.assertEqual(self.g.observe(0),clone.observe(0))
 def test_silvermoon_excess_and_lowest_target(self):
  loc=self.place('TIME_810t2');a=self.g._summon(1,'NEW1_034');b=self.g._summon(1,'NEW1_034');self.g._buff(b,0,5)
  self.activate(loc);self.assertNotIn(a,self.q.board);self.assertIn(b,self.q.board);self.assertEqual(self.q.health,27)
 def test_silvermoon_shield_does_not_deal_excess(self):
  loc=self.place('TIME_810t1');m=self.g._summon(1,'NEW1_034');m.keywords.add('DIVINE_SHIELD');self.activate(loc)
  self.assertEqual(self.q.health,30);self.assertEqual(m.health,2)
 def test_empty_silvermoon_still_advances(self):
  loc=self.place('TIME_810');self.activate(loc);self.assertEqual(loc.card_id,'TIME_810t1')
 def test_amirdrassil_improves_each_use(self):
  for n in (1,2,3):
   cid='TEST_'+str(n);self.g.cards[cid]=dict(id=cid,name=cid,type='MINION',cost=n,attack=n,health=n,cardClass='NEUTRAL');self.contract(pool(card_type='MINION',minimum=n,maximum=n),[cid])
  loc=self.place('FIR_907');self.p.mana=0
  for _ in range(3):self.activate(loc)
  self.assertEqual(self.p.armor,6);self.assertEqual(len(self.p.hand),6);self.assertEqual(len(self.p.minions),3);self.assertEqual(loc.rule_state['uses'],3)
 def test_nespirah_damage_and_fel_reopen(self):
  loc=self.place('CATA_527');self.activate(loc,-2);self.assertEqual(self.q.health,29)
  self.g.cards['TEST_FEL']=dict(id='TEST_FEL',type='SPELL',spellSchool='FEL');self.g._queue_event('spell_cast',owner=0,card_id='TEST_FEL',cost=1)
  self.assertEqual(loc.ready_turn,self.g.turn)
 def test_nespirah_final_charge_frees_minion(self):
  loc=self.place('CATA_527');loc.durability=1;self.activate(loc,-2)
  self.assertNotIn(loc,self.p.board);self.assertEqual([m.card_id for m in self.p.minions],['CATA_527t2']);self.assertEqual(self.q.health,29)
 def test_freed_nespirah_generates_non_colossal_naga(self):
  self.g.cards['TEST_NAGA']=dict(id='TEST_NAGA',name='Naga',type='MINION',cost=5,attack=1,health=1,race='NAGA',races=['NAGA'],cardClass='NEUTRAL')
  self.contract(rules.NAGAS,['TEST_NAGA']);m=self.g._summon(0,'CATA_527t2')
  self.g._start_play_effects([('evolving_naga',)],dict(owner=0,source=m,target=0));self.assertEqual(self.g._cost(self.p.hand[0],0),1)
