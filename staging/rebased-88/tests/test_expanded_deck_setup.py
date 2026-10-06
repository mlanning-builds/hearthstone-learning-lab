import unittest
from unittest.mock import patch
import test_expanded_generation as fixtures
from engine.game import Card
from expanded.decks import Deck,validate
from expanded import decks,cards,deck_setup
from standard.catalog import load_catalog

class DeckSetupTests(unittest.TestCase):
 def setUp(self):
  self.fx=fixtures.GenerationTests();self.g=self.fx.game();self.p,self.q=self.g.players
  self.g.cards.update({c['id']:c for c in load_catalog() if c['id'] in ('JAIL_397','JAIL_430','JAIL_509','EDR_000')})
 def prepare(self):
  self.g._prepare_constructed_decks([Deck('MAGE',tuple(self.p.starting_deck),beatrix_minion='CORE_EX1_162' if 'JAIL_397' in self.p.starting_deck else None),Deck('HUNTER',tuple(self.q.starting_deck))])
 def test_beatrix_adds_ten_unique_copies_before_opening_hand(self):
  self.p.starting_deck=['JAIL_397'];self.p.deck=['CORE_CS2_029']*30;self.prepare()
  copies=[c for c in self.p.deck if isinstance(c,Card)];self.assertEqual(len(self.p.deck),40);self.assertEqual(len(copies),10);self.assertEqual(len({c.uid for c in copies}),10);self.assertTrue(all(c.card_id=='CORE_EX1_162' for c in copies))
 def test_azalina_copies_twenty_positions_without_removing_enemy_cards(self):
  self.p.starting_deck=['JAIL_430'];self.p.deck=['JAIL_430']+['CORE_CS2_029']*19
  self.q.deck=[Card(self.g._new_id(),'CORE_EX1_162') for _ in range(30)];before=list(self.q.deck);self.prepare()
  self.assertEqual(len(self.p.deck),40);self.assertEqual(self.q.deck,before);self.assertEqual(self.p.health,40);self.assertEqual(self.p.max_health,40)
  copies=[c for c in self.p.deck if isinstance(c,Card)];self.assertEqual(len({c.uid for c in copies}),20);self.assertTrue(all(not self.g._started_in_deck(c,0) for c in copies));self.assertTrue(all(self.g._copied_from_opponent(c,0) for c in copies))
 def test_two_azalinas_use_simultaneous_snapshots(self):
  for p in self.g.players:p.starting_deck=['JAIL_430'];p.deck=['JAIL_430']+['CORE_EX1_162']*19
  self.prepare();self.assertEqual([len(p.deck) for p in self.g.players],[40,40]);self.assertEqual([len(p.copied_opening_ids) for p in self.g.players],[20,20])
 def test_copied_godfrey_enables_start_effect_without_changing_original_deck(self):
  self.p.starting_deck=['JAIL_430'];self.q.deck=['JAIL_509']+['CORE_EX1_162']*19;self.prepare();self.g._starting_rules()
  self.assertTrue(self.p.overdraw_return_active);self.assertEqual(self.p.starting_deck,['JAIL_430'])
 def test_copied_ysera_increases_both_mana_capacities(self):
  self.p.starting_deck=['JAIL_430'];self.q.starting_deck=[];self.q.deck=['EDR_000']+['CORE_EX1_162']*19;self.prepare();self.g._starting_rules();self.assertEqual([p.mana_capacity for p in self.g.players],[15,15])
 def test_azalina_battlecry_fills_available_hand_slots(self):
  self.p.deck=['CORE_CS2_029']*20;self.g._add(0,'TOKEN_COIN');self.fx.run_ops(self.g,deck_setup.RULES['JAIL_430'][1]);self.assertEqual(len(self.p.hand),10);self.assertEqual(len(self.p.deck),11)
 def test_beatrix_requires_explicit_selection(self):
  errors=validate(Deck('MAGE',('JAIL_397',)),self.g.cards);self.assertTrue(any('selection' in e for e in errors))
 def test_orphan_selection_rejected(self):
  errors=validate(Deck('MAGE',(),beatrix_minion='CORE_EX1_162'),self.g.cards);self.assertTrue(any('requires Commander' in e for e in errors))
 def test_azalina_expected_size_is_twenty(self):
  errors=validate(Deck('PRIEST',('JAIL_430',)),self.g.cards);self.assertTrue(any('exactly 20' in e for e in errors))
 def test_azalina_conflicting_size_rejected(self):
  errors=validate(Deck('PRIEST',('JAIL_430','TIME_005')),self.g.cards);self.assertTrue(any('conflicting' in e for e in errors))
 def test_hogger_respects_deck_limit(self):
  self.p.starting_deck=['JAIL_384'];self.p.deck=['JAIL_384']*98;self.p.hand=[Card(self.g._new_id(),'EDR_000')];self.g._starting_rules();self.assertEqual(len(self.p.deck),99)
 def test_full_constructor_azalina_opens_with_forty_total_cards(self):
  from expanded import Game,random_deck
  from expanded import game
  ordinary=random_deck('PRIEST',121)
  selected=ordinary.cards[:19]+('JAIL_430',)
  probe=Deck('PRIEST',selected)
  opponent=random_deck('HUNTER',122)
  metadata=dict(self.g.cards)
  with patch.object(decks,'COLLECTIBLE_IDS',set(decks.COLLECTIBLE_IDS)|{'JAIL_430'}),patch.object(game,'registry',return_value=metadata),patch.dict(cards.RULES,deck_setup.RULES):
   g=Game([probe,opponent],seed=9)
  self.assertEqual(g.players[0].health,40);self.assertEqual(len(g.players[0].hand)+len(g.players[0].deck),40)
  self.assertEqual(len(g.players[0].starting_deck),20);self.assertEqual(len(g.players[0].copied_opening_ids),20)
 def test_copied_hamuul_uses_original_spell_condition(self):
  import gzip,json
  with gzip.open('data/standard/all_cards.json.gz','rt') as f:self.g.cards.update({c['id']:c for c in json.load(f) if c['id'] in ('EDR_845','EDR_851p')})
  self.p.starting_deck=['JAIL_430'];self.q.deck=['EDR_845']+['CORE_CS2_029']*19
  self.prepare();self.p.imbue_start_checked=False;self.g._imbue_start_game(0)
  self.assertTrue(self.p.hamuul_active);self.assertEqual(self.p.starting_deck,['JAIL_430'])
