import unittest,json,gzip
from pathlib import Path
from unittest.mock import patch
from dataclasses import replace
from expanded import Game,random_deck
from expanded.decks import Deck,validate
from expanded.fabled_decks import BUNDLES,COMPANION_ROOT,expand_bundle_ids,deck_size,sample_bundle_slots
from expanded import cards
from engine.cards import UnsupportedCard

class FabledDeckTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.root=Path(__file__).resolve().parents[1]
  with gzip.open(cls.root/'data/standard/all_cards.json.gz','rt') as f:cls.archive={c['id']:c for c in json.load(f)}
 def test_all_eleven_bundles_match_named_pinned_tags(self):
  inventory=json.loads((self.root/'../../docs/engine-audit/fabled-source-inventory.json').read_text())
  expected={f['root']['card_id']:tuple(f['named_bundle_tag_candidates']) for f in inventory['families']}
  self.assertEqual(BUNDLES,expected);self.assertEqual(len(BUNDLES),11);self.assertEqual(len(COMPANION_ROOT),29)
 def test_regular_bundles_occupy_three_slots(self):
  for cid in BUNDLES.keys()-{'TIME_005'}:
   with self.subTest(cid=cid):
    ids=expand_bundle_ids((cid,)+tuple('filler'+str(i) for i in range(27)))
    self.assertEqual(len(ids),30);self.assertEqual(deck_size(ids),30)
 def test_rafaam_has_ten_rafaams_inside_forty_cards(self):
  ids=expand_bundle_ids(('TIME_005',)+tuple('filler'+str(i) for i in range(30)))
  self.assertEqual(len(ids),40);self.assertEqual(deck_size(ids),40);self.assertEqual(sum(c.startswith('TIME_005') for c in ids),10)
 def test_expansion_is_idempotent(self):
  for root in BUNDLES:
   ids=expand_bundle_ids((root,));self.assertEqual(expand_bundle_ids(ids),ids)
 def test_partially_expanded_input_adds_only_missing_companions(self):
  ids=expand_bundle_ids(('TIME_852','TIME_852t1'));self.assertEqual(ids,('TIME_852','TIME_852t1','TIME_852t3'))
 def test_orphan_companion_is_rejected(self):
  with self.assertRaisesRegex(ValueError,'requires its root'):expand_bundle_ids(('TIME_852t1',))
 def test_duplicate_root_rejected(self):
  with self.assertRaisesRegex(ValueError,'only once'):expand_bundle_ids(('TIME_852','TIME_852'))
 def test_duplicate_companion_rejected(self):
  with self.assertRaisesRegex(ValueError,'only once'):expand_bundle_ids(('TIME_852','TIME_852t1','TIME_852t1'))
 def test_secondary_portals_and_empowered_locations_are_not_starting_companions(self):
  self.assertNotIn('TIME_020t3',COMPANION_ROOT);self.assertNotIn('TIME_211t1t',COMPANION_ROOT)
 def test_unimplemented_root_not_admitted_by_bundle_metadata(self):
  d=Deck('MAGE',('TIME_852',)+random_deck('MAGE',11).cards[:27]);errors=validate(d,self.archive)
  self.assertTrue(any('Effect not implemented: TIME_852' in e for e in errors))
 def fixture_deck(self):
  d=Deck('MAGE',('TIME_852',)+random_deck('MAGE',11).cards[:27]);metadata=cards.registry();metadata.update({cid:self.archive[cid] for cid in ('TIME_852',)+BUNDLES['TIME_852']})
  return d,metadata
 def test_metadata_only_companions_still_rejected(self):
  d,metadata=self.fixture_deck()
  with patch('expanded.decks.COLLECTIBLE_IDS',set(cards.COLLECTIBLE_IDS)|{'TIME_852'}):
   errors=validate(d,metadata)
  self.assertTrue(any('Effect not implemented: TIME_852t1' in e for e in errors))
 def test_controlled_executable_bundle_validates(self):
  d,metadata=self.fixture_deck()
  with patch('expanded.decks.COLLECTIBLE_IDS',set(cards.COLLECTIBLE_IDS)|{'TIME_852'}),patch.dict(cards.RULES,{cid:('none',[]) for cid in BUNDLES['TIME_852']}):self.assertEqual(validate(d,metadata),[])
 def test_thirty_selected_cards_plus_companions_is_not_legal(self):
  d,metadata=self.fixture_deck();d=replace(d,cards=d.cards+('TOKEN_COIN','TOKEN_COIN'))
  self.assertTrue(any('including Fabled companions; got 32' in e for e in validate(d,metadata)))
 def test_wrong_class_still_rejected(self):
  d,metadata=self.fixture_deck();d=replace(d,hero_class='WARRIOR')
  with patch('expanded.decks.COLLECTIBLE_IDS',set(cards.COLLECTIBLE_IDS)|{'TIME_852'}),patch.dict(cards.RULES,{cid:('none',[]) for cid in BUNDLES['TIME_852']}):self.assertTrue(any('Class or rune mismatch: TIME_852' in e for e in validate(d,metadata)))
 def test_game_uses_expanded_starting_deck_before_mulligan(self):
  d,metadata=self.fixture_deck();other=random_deck('HUNTER',1)
  with patch('expanded.game.registry',return_value=metadata),patch('expanded.decks.COLLECTIBLE_IDS',set(cards.COLLECTIBLE_IDS)|{'TIME_852'}),patch.dict(cards.RULES,{cid:('none',[]) for cid in ('TIME_852',)+BUNDLES['TIME_852']}):g=Game([d,other],seed=1)
  self.assertEqual(len(g.players[0].starting_deck),30)
  physical=g.players[0].deck+g.players[0].hand
  for cid in BUNDLES['TIME_852']:
   c=next(c for c in physical if c.card_id==cid);self.assertTrue(g._started_in_deck(c,0))
 def test_game_rejects_orphan_before_state_creation(self):
  d=Deck('MAGE',('TIME_852t1',)+random_deck('MAGE',1).cards[:29])
  with self.assertRaisesRegex(UnsupportedCard,'requires its root'):Game([d,random_deck('HUNTER',2)])
 def test_sampler_respects_bundle_slots_and_seed(self):
  slots=['TIME_852']+['filler'+str(i) for i in range(40)]
  for seed in range(20):
   chosen=sample_bundle_slots(slots,seed);self.assertEqual(chosen,sample_bundle_slots(slots,seed));self.assertEqual(len(expand_bundle_ids(chosen)),30)
 def test_sampler_rafaam_uses_forty_when_selected(self):
  slots=['TIME_005']+['filler'+str(i) for i in range(40)];seen=False
  for seed in range(20):
   chosen=sample_bundle_slots(slots,seed);ids=expand_bundle_ids(chosen);self.assertEqual(len(ids),deck_size(ids));seen|='TIME_005' in chosen
  self.assertTrue(seen)
 def test_sampler_rejects_standalone_companions_and_insufficient_slots(self):
  with self.assertRaises(ValueError):sample_bundle_slots(['TIME_852t1'],0)
  with self.assertRaises(ValueError):sample_bundle_slots(['TIME_852'],0)
 def test_sampler_azalina_respects_twenty_slots_and_conflicts(self):
  slots=['JAIL_430','TIME_005','REV_018','TIME_852']+['filler'+str(i) for i in range(60)]
  seen=False
  for seed in range(100):
   chosen=sample_bundle_slots(slots,seed);expanded=expand_bundle_ids(chosen)
   self.assertEqual(len(expanded),deck_size(expanded))
   self.assertEqual(chosen,sample_bundle_slots(slots,seed))
   if 'JAIL_430' in chosen:
    seen=True;self.assertNotIn('TIME_005',chosen);self.assertNotIn('REV_018',chosen)
  self.assertTrue(seen)
