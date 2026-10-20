"""Production random-Murloc contract, paid generation and outcome closure."""
import unittest
from unittest.mock import patch
import test_expanded_generation as fixtures
import test_expanded_passive_admission as admission
from expanded import Action,cards
from expanded.generation_cards import pool
from expanded.generation_families import reviewed_contract
from expanded.murloc_generation import MURLOC_IDS
from expanded.selectors import HERO_CLASSES,has_tribe
from engine.cards import UnsupportedCard
from standard.catalog import load_catalog
REQUEST=pool(card_type='MINION',tribe='MURLOC')
class MurlocGenerationAdmissionTests(unittest.TestCase):
 def game(self):
  g=fixtures.GenerationTests().game();g._generation_pools={};return g
 def play(self,g,cid):
  c=g._add(0,cid);g.players[0].mana=10
  g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid));return c
 def test_greenfin_starts_in_a_valid_standard_deck(self):
  g=admission.PassiveAdmissionTests().game('MAGE','EDR_999')
  self.assertIn('EDR_999',g.players[0].starting_deck)
 def test_literal_membership_is_entire_frozen_collectible_murloc_pool(self):
  expected={c['id'] for c in load_catalog() if c['type']=='MINION' and has_tribe(c,'MURLOC')}
  self.assertEqual(set(MURLOC_IDS),expected);self.assertEqual(len(MURLOC_IDS),22)
  self.assertTrue(set(MURLOC_IDS)<=cards.COLLECTIBLE_IDS)
  self.assertIn('DINO_435',MURLOC_IDS);self.assertIn('EDR_999',MURLOC_IDS)
 def test_all_hero_classes_get_same_reviewed_pool(self):
  g=self.game()
  for hero in HERO_CLASSES:
   g.players[0].hero_class=hero
   self.assertEqual(g._generation_candidates(REQUEST,0),MURLOC_IDS)
 def test_only_exact_request_is_approved(self):
  for r in (pool(tribe='MURLOC'),pool(card_type='MINION',tribe='MURLOC',classes='own'),pool(card_type='MINION',tribe='MURLOC',maximum=2),pool(card_type='MINION',tribe='MURLOC',era='past')):
   self.assertIsNone(reviewed_contract(r,'MAGE'))
 def test_paid_greenfin_generates_every_outcome_as_fresh_physical_card(self):
  for cid in (c for c in MURLOC_IDS if c!='EDR_999'):
   with self.subTest(cid=cid):
    g=self.game()
    with patch.object(g.rng,'choice',return_value=cid) as choose:source=self.play(g,'EDR_999')
    self.assertEqual(choose.call_args.args[0],tuple(c for c in MURLOC_IDS if c!='EDR_999'))
    self.assertEqual(g.players[0].mana,9);self.assertEqual(len(g.players[0].hand),1)
    generated=g.players[0].hand[0];self.assertEqual(generated.card_id,cid)
    self.assertNotEqual(generated.uid,source.uid);self.assertEqual(generated.cost_delta,0)
 def test_every_generated_body_has_a_normal_paid_play_path(self):
  for cid in MURLOC_IDS:
   with self.subTest(cid=cid):
    g=self.game();self.play(g,cid)
    if g.pending_choice is not None:
     g.step(next(a for a in g.legal_actions() if a.kind=='choose'))
    g.assert_invariants()
 def test_creator_is_excluded_before_random_selection(self):
  g=self.game();seen=[]
  def choose(values):
   seen.append(tuple(values));self.assertNotIn('EDR_999',values);return values[0]
  with patch.object(g.rng,'choice',side_effect=choose):self.play(g,'EDR_999')
  self.assertEqual(len(seen),1);self.assertEqual(len(seen[0]),21)
 def test_explicit_creator_provenance_excludes_creator(self):
  g=self.game();source=g._summon(0,'EDR_999')
  self.assertEqual(g._generation_created_candidates(REQUEST,dict(owner=0,source=source,generation_creator_id='EDR_999')),tuple(c for c in MURLOC_IDS if c!='EDR_999'))
 def test_effect_bearer_does_not_override_explicit_creator(self):
  g=self.game();bearer=g._summon(0,'EDR_999')
  self.assertEqual(g._generation_created_candidates(REQUEST,dict(owner=0,source=bearer,card_id='TLC_442')),MURLOC_IDS)
 def test_canonical_alias_is_excluded_from_random_and_discover(self):
  g=self.game();alias='CORE_EX1_509'
  g.cards[alias]=dict(g.cards[alias],countAsCopyOfDbfId=g.cards['EDR_999']['dbfId'])
  fixtures.GenerationTests().install(g,REQUEST,[alias,'TLC_429'])
  ctx=dict(owner=0,card_id='EDR_999')
  self.assertEqual(g._generation_created_candidates(REQUEST,ctx),('TLC_429',))
  self.assertEqual(g._generation_discover_candidates(REQUEST,ctx),('TLC_429',))
 def test_creator_only_contract_is_noop_without_rng(self):
  g=self.game();fixtures.GenerationTests().install(g,REQUEST,['EDR_999']);before=g.rng.getstate()
  self.play(g,'EDR_999');self.assertEqual(g.players[0].hand,[]);self.assertEqual(g.rng.getstate(),before)
 def test_paid_card_frees_one_slot_in_an_otherwise_full_hand(self):
  g=self.game()
  for _ in range(9):g._add(0,'CORE_CS2_029')
  self.play(g,'EDR_999');self.assertEqual(len(g.players[0].hand),10)
 def test_generation_into_full_hand_burns_the_outcome(self):
  g=self.game()
  for _ in range(10):g._add(0,'CORE_CS2_029')
  fixtures.GenerationTests().run_ops(g,[('generate_random',REQUEST,1,'hand',())])
  self.assertEqual([c.card_id for c in g.players[0].hand],['CORE_CS2_029']*10)
 def test_unrelated_generation_still_fails_closed(self):
  g=self.game();del g.cards['CORE_EX1_162'];state=g.rng.getstate()
  with self.assertRaises(UnsupportedCard):g._generation_candidates(pool(card_type='MINION'),0)
  self.assertEqual(g.rng.getstate(),state)
 def test_missing_reviewed_member_rejected_before_paid_mutation(self):
  g=self.game();g.cards.pop('TLC_429');c=g._add(0,'EDR_999');before=g.rng.getstate();mana=g.players[0].mana
  with self.assertRaises(UnsupportedCard):g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid))
  self.assertEqual(g.players[0].mana,mana);self.assertIn(c,g.players[0].hand);self.assertEqual(g.rng.getstate(),before)
if __name__=='__main__':unittest.main()
