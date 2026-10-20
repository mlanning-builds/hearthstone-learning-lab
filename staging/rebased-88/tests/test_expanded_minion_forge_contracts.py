"""Explicit component contracts must fail before offers or physical mutation."""
import random, unittest
from types import SimpleNamespace
from expanded.minion_forge import MinionForge, ForgePart
from engine.cards import UnsupportedCard
from engine.game import Card

class ForgeHarness(MinionForge):
 def __init__(self):
  self.cards={'A':dict(type='MINION',cost=4,attack=2,health=3),'B':dict(type='MINION',cost=2,attack=1,health=2)}
  self.forge_contracts={('dragon',1):(ForgePart('A',source='Controlled fixture'),),('dragon',2):(ForgePart('B',source='Controlled fixture'),)}
  self.rng=random.Random(71);self.pending_choice=None

class MinionForgeContractTests(unittest.TestCase):
 def test_complete_fixture_offer_preserves_explicit_members(self):
  g=ForgeHarness();g._forge_offer(0,'dragon',0)
  self.assertEqual(g.pending_choice['options'],[dict(card_id='A')])
 def test_missing_second_pool_rejected_before_random(self):
  g=ForgeHarness();del g.forge_contracts['dragon',2];before=g.rng.getstate()
  with self.assertRaises(UnsupportedCard):g._forge_offer(0,'dragon',0)
  self.assertEqual(before,g.rng.getstate());self.assertIsNone(g.pending_choice)
 def test_unfinishable_first_offer_rejected_before_random(self):
  g=ForgeHarness();g.cards['B']['cost']=8;before=g.rng.getstate()
  with self.assertRaisesRegex(UnsupportedCard,'no legal second'):g._forge_offer(0,'dragon',0)
  self.assertEqual(before,g.rng.getstate())
 def test_duplicate_member_rejected_without_reweighting(self):
  g=ForgeHarness();part=g.forge_contracts['dragon',1][0];g.forge_contracts['dragon',1]=(part,part)
  with self.assertRaisesRegex(UnsupportedCard,'Duplicate'):g._forge_pool('dragon',1,0)
 def test_malformed_operation_rejected(self):
  g=ForgeHarness();g.forge_contracts['dragon',1]=(ForgePart('A',operations=('damage',),source='Controlled fixture'),)
  with self.assertRaisesRegex(UnsupportedCard,'operation'):g._forge_pool('dragon',1,0)
 def test_noninteger_stats_rejected(self):
  g=ForgeHarness();g.cards['A']['attack']=True
  with self.assertRaisesRegex(UnsupportedCard,'statistics'):g._forge_pool('dragon',1,0)
 def test_existing_decision_not_overwritten(self):
  g=ForgeHarness();existing=dict(kind='other');g.pending_choice=existing;before=g.rng.getstate()
  with self.assertRaisesRegex(UnsupportedCard,'overwrite'):g._forge_offer(0,'dragon',0)
  self.assertIs(g.pending_choice,existing);self.assertEqual(before,g.rng.getstate())
 def test_unoffered_component_rejected(self):
  g=ForgeHarness();g._forge_offer(0,'dragon',0)
  with self.assertRaisesRegex(UnsupportedCard,'not offered'):g._forge_choice(g.pending_choice,dict(card_id='B'))
 def test_unbound_composite_is_not_vanilla_body(self):
  g=ForgeHarness()
  with self.assertRaisesRegex(UnsupportedCard,'physical component'):g._forge_entry(SimpleNamespace(),Card(4,'CATA_470t1'))
