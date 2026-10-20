"""Real frozen aliases and fail-closed generation contracts."""
import json
from pathlib import Path
import unittest
from expanded.identities import canonical_identity,core_aliases
from expanded.historical_generation import validate_past_candidates
from expanded.generation_cards import pool
from engine.cards import UnsupportedCard
from standard.catalog import load_all_records
import test_expanded_generation as fixtures

class IdentityTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.records={d['id']:d for d in load_all_records()}
 def test_all_explicit_core_pairs_resolve_to_original(self):
  pairs=json.loads((Path(__file__).resolve().parents[1]/'expanded/core_identities.json').read_text())['pairs']
  self.assertEqual(len(pairs),257);self.assertEqual(len(core_aliases()),257)
  for pair in pairs:
   with self.subTest(card=pair['core']):self.assertEqual(canonical_identity(self.records[pair['core']],self.records),canonical_identity(self.records[pair['original']],self.records))
 def test_legacy_standard_counterpart_is_not_a_past_outcome(self):
  with self.assertRaisesRegex(UnsupportedCard,'Standard cards'):validate_past_candidates(('CS2_074',),self.records)
 def game_with_poison(self):
  f=fixtures.GenerationTests();g=f.game();g.cards['CS2_074']=self.records['CS2_074'];return f,g
 def test_duplicate_core_and_original_rejected_before_rng(self):
  f,g=self.game_with_poison();request=pool(card_type='SPELL');f.install(g,request,('CORE_CS2_074','CS2_074'));state=g.rng.getstate()
  with self.assertRaisesRegex(UnsupportedCard,'duplicate canonical'):g._generation_candidates(request,0)
  self.assertEqual(g.rng.getstate(),state);self.assertFalse(g.players[0].hand)
 def test_creator_excludes_other_frozen_version(self):
  f,g=self.game_with_poison();request=pool(card_type='SPELL');f.install(g,request,('CS2_074',))
  self.assertEqual(g._generation_created_candidates(request,dict(owner=0,card_id='CORE_CS2_074')),())
 def test_explicit_chain_can_end_at_core_alias(self):
  records=dict(self.records);records['fixture']={'id':'fixture','dbfId':-101,'countAsCopyOfDbfId':69522}
  self.assertEqual(canonical_identity(records['fixture'],records),459)
 def test_unrelated_same_name_is_not_merged(self):
  d=dict(self.records['CS2_074'],id='fixture',dbfId=-101)
  self.assertEqual(canonical_identity(d,{'fixture':d}),-101)
 def test_cycles_fail_closed(self):
  a={'id':'a','dbfId':-101,'countAsCopyOfDbfId':-102};b={'id':'b','dbfId':-102,'countAsCopyOfDbfId':-101}
  with self.assertRaisesRegex(UnsupportedCard,'Cyclic'):canonical_identity(a,{'a':a,'b':b})
 def test_explicit_raptor_herald_alias_without_original_prefix(self):
  self.assertEqual(canonical_identity(self.records['CORE_EDR_004_2026'],self.records),119798)
 def test_real_starting_core_card_retains_origin_under_its_original_identity(self):
  import test_expanded_passive_admission as admission
  g=admission.PassiveAdmissionTests().game('MAGE','CORE_CS2_029')
  c=next(c for c in g.players[0].deck+g.players[0].hand if c.card_id=='CORE_CS2_029')
  self.assertTrue(g._started_in_deck(c,0));self.assertEqual(c._starting_identity,315)
  g.cards['CS2_029']=self.records['CS2_029'];c.card_id='CS2_029'
  self.assertTrue(g._started_in_deck(c,0));self.assertFalse(g._started_in_deck(g._copy_card(c),0))
 def test_resurrection_deduplicates_real_core_and_legacy_sleepy_dragons(self):
  import test_expanded_merithra as merithra
  case=merithra.MerithraTests();g=case.game()
  g.players[0].death_history=['LOOT_137','CORE_LOOT_137'];case.play(g)
  self.assertEqual(len(g.players[0].minions),2)
 def test_dark_gift_rejects_real_duplicate_versions_before_rng(self):
  from expanded.dark_gift_generators import request
  from expanded.pools import GenerationPool
  _,g=self.game_with_poison();req=request(classes='any')
  g._dark_generation_pools={(req,g.players[0].hero_class):GenerationPool('fixture',('LOOT_137','CORE_LOOT_137'),'Real frozen duplicate identities')}
  state=g.rng.getstate()
  with self.assertRaisesRegex(UnsupportedCard,'Duplicate canonical'):g._dark_global_candidates(req,0)
  self.assertEqual(g.rng.getstate(),state)

if __name__=='__main__':unittest.main()
