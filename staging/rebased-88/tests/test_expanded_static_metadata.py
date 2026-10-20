import unittest,json
from copy import deepcopy
from unittest.mock import patch
import test_expanded_generation as fixtures
from expanded.static_metadata import freeze,thaw
class StaticMetadataTests(unittest.TestCase):
 def test_frozen_records_preserve_json_and_share_deepcopy(self):
  record=freeze({'mechanics':['TAUNT'],'runeCost':{'blood':1}})
  self.assertIs(deepcopy(record),record);self.assertEqual(json.loads(json.dumps(record)),{'mechanics':['TAUNT'],'runeCost':{'blood':1}})
  for mutation in (lambda:record.update(cost=2),lambda:record['mechanics'].append('RUSH'),lambda:record['runeCost'].clear()):
   with self.assertRaises(TypeError):mutation()
 def test_failed_action_restores_rng_zones_and_mutable_overlay(self):
  g=fixtures.GenerationTests().game();c=g._add(0,'CORE_CS2_029');g.cards['fixture']={'nested':[1]}
  rng=g.rng.getstate();health=g.players[0].health;hand=deepcopy(g.players[0].hand);shared=g.cards['CORE_CS2_029']
  action=next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid)
  def fail(a):
   g.rng.random();g.players[0].health=1;g.players[0].hand.clear();g.cards['fixture']['nested'].append(2);g.cards['extra']={};raise RuntimeError('injected')
  with patch.object(g,'_play',side_effect=fail):
   with self.assertRaisesRegex(RuntimeError,'injected'):g.step(action)
  self.assertEqual(g.rng.getstate(),rng);self.assertEqual(g.players[0].health,health);self.assertEqual(g.players[0].hand,hand);self.assertEqual(g.cards['fixture'],{'nested':[1]});self.assertNotIn('extra',g.cards);self.assertIs(g.cards['CORE_CS2_029'],shared)
 def test_copies_share_static_records_but_not_state(self):
  g=fixtures.GenerationTests().game();clone=deepcopy(g)
  self.assertIs(g.cards['CORE_CS2_029'],clone.cards['CORE_CS2_029']);clone.players[0].health=1;self.assertEqual(g.players[0].health,30)

 def test_mutable_derived_record_does_not_change_frozen_original(self):
  original=freeze({'mechanics':['TAUNT'],'runeCost':{'blood':1}});derived=thaw(original)
  derived['mechanics'].append('RUSH');derived['runeCost']['blood']=2
  self.assertEqual(original,{'mechanics':['TAUNT'],'runeCost':{'blood':1}})
