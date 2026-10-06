import json,unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch
import test_expanded_generation as fixtures
from expanded import Action,cards,leylines as ley
from expanded.game import Card
from expanded.generation_cards import pool
from engine.cards import UnsupportedCard
from standard.catalog import load_all_records

class LeylineTests(unittest.TestCase):
 def setUp(self):
  self.h=fixtures.GenerationTests();self.g=self.h.game();self.p,self.q=self.g.players
  records={d['id']:d for d in load_all_records()}
  self.g.cards.update({cid:records[cid] for cid in ley.RULES.keys()|ley.TOKEN_RULES.keys()})
  for table,items in ((cards.RULES,{**ley.RULES,**ley.TOKEN_RULES}),(cards.DEATH_EFFECTS,ley.DEATH_EFFECTS)):
   p=patch.dict(table,items);p.start();self.addCleanup(p.stop)
 def play(self,cid):
  self.p.mana=10;c=Card(self.g._new_id(),cid);self.p.hand.append(c)
  self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid));return c
 def test_values_match_frozen_tags(self):
  tags=json.loads(Path('data/standard/card_tags.json').read_text())
  self.assertEqual(ley.BASE,{cid:int(tags[cid]['TAG_SCRIPT_DATA_NUM_1']) for cid in ley.LEYLINES})
 def test_seven_bodies_four_admitted(self):
  self.assertEqual(len(ley.RULES),7);self.assertEqual(set(ley.RULES)&cards.COLLECTIBLE_IDS,{'MEND_500','MEND_503','MEND_504','MEND_506'})
 def test_cost_upgrade_applies_to_future_cards_not_other_spells(self):
  self.play('MEND_501');c=Card(990,'MEND_500');self.assertEqual(self.g._cost(c,0),3)
  self.assertEqual(self.g._cost(Card(991,'CORE_CS2_029'),0),4)
 def test_multiple_cost_upgrades_stack_and_floor(self):
  for _ in range(3):self.play('MEND_505t2')
  self.assertEqual(self.g._cost(Card(990,'MEND_500'),0),0)
 def test_discount_belongs_to_owner(self):
  self.play('MEND_501');self.assertEqual(self.g._cost(Card(990,'MEND_500'),1),4)
 def test_death_gets_one_of_complete_family(self):
  self.play('MEND_501');m=self.p.minions[0];self.g._damage(m.uid,99);self.g._settle()
  self.assertEqual(len(self.p.hand),1);self.assertIn(self.p.hand[0].card_id,ley.LEYLINES)
 def test_upgrade_choice_is_not_discover(self):
  self.play('MEND_505');self.assertEqual([c.card_id for c in self.p.hand],list(ley.LEYLINES))
  self.g.step(Action('choose',choices=(2,)));self.assertEqual(self.p.leyline_effect,2);self.assertEqual(self.p.discoveries_total,0)
 def test_all_three_upgrade_choices(self):
  for index,field,expected in ((0,'leyline_repeats',1),(1,'leyline_discount',2),(2,'leyline_effect',2)):
   self.play('MEND_505');self.g.step(Action('choose',choices=(index,)));self.assertEqual(getattr(self.p,field),expected)
 def test_nexus_draws_repeatedly_and_discounts_each(self):
  self.play('MEND_503');self.play('MEND_506');self.play('MEND_504')
  self.assertEqual(len(self.p.hand),2);self.assertTrue(all(c.cost_delta==-2 for c in self.p.hand))
 def test_nexus_overdraw_is_not_added(self):
  self.p.hand=[Card(200+i,'CORE_CS2_029') for i in range(9)];self.p.leyline_repeats=2
  self.play('MEND_504');self.assertEqual(len(self.p.hand),10);self.assertEqual(len(self.p.deck),9)
 def test_crystallized_requires_exact_upgraded_pool(self):
  self.p.leyline_effect=1
  with self.assertRaises(UnsupportedCard):self.play('MEND_502')
  self.assertFalse(self.g.players[0].board)
 def test_crystallized_repeated_summons(self):
  d=deepcopy(self.g.cards['CS3_025']);d.update(id='LEY_FIX',dbfId=-811,cost=7);self.g.cards[d['id']]=d
  self.h.install(self.g,pool(card_type='MINION',minimum=7,maximum=7),['LEY_FIX'])
  self.p.leyline_effect=1;self.p.leyline_repeats=2;self.play('MEND_502');self.assertEqual(len(self.p.board),3)
 def test_burst_excess_hits_hero(self):
  m=self.g._summon(1,'CS3_025');m.health=2;self.play('MEND_500');self.assertEqual(self.q.health,28);self.assertFalse(self.q.board)
 def test_burst_shield_prevents_excess(self):
  m=self.g._summon(1,'CS3_025');m.health=1;m.keywords.add('DIVINE_SHIELD');self.play('MEND_500');self.assertEqual(self.q.health,30);self.assertEqual(m.health,1)
 def test_burst_ignores_spell_bonus(self):
  m=self.g._summon(1,'CS3_025');self.h.run_ops(self.g,[('leyline_cast','MEND_500')],bonus=20,spell=True)
  self.assertEqual(m.health,2)
 def test_burst_no_minions_does_not_hit_face(self):self.play('MEND_500');self.assertEqual(self.q.health,30)
 def test_burst_repetitions_retarget_after_death(self):
  for _ in range(2):self.g._summon(1,'CS3_025').health=1
  self.p.leyline_repeats=2;self.play('MEND_500');self.assertEqual(self.q.health,24);self.assertFalse(self.q.board)
 def test_state_persists_across_turn_and_clone(self):
  self.play('MEND_506');self.g.step(Action('end'));self.g.step(Action('end'));clone=deepcopy(self.g)
  self.assertEqual(clone.players[0].leyline_effect,1);self.assertEqual(self.g.observe(1)['players'][0]['leyline_effect'],1)
 def test_live_nexus_internal_cast_uses_owner_upgrades(self):
  self.p.leyline_effect=2;self.p.leyline_repeats=1
  self.assertTrue(self.g._supports_internal_spell('MEND_504'))
  self.h.run_ops(self.g,[('cast_fixed_spell','MEND_504','random')])
  self.assertEqual(len(self.p.hand),2);self.assertTrue(all(c.cost_delta==-3 for c in self.p.hand))
 def test_live_burst_internal_cast_ignores_spell_damage(self):
  self.g._summon(1,'CS3_025').health=1
  self.h.run_ops(self.g,[('cast_fixed_spell','MEND_500','random')])
  self.assertEqual(self.q.health,27)
