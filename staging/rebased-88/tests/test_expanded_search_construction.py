import unittest
from itertools import islice
from expanded import random_deck
from expanded.cards import COLLECTIBLE_IDS,registry
from expanded.decks import Deck,eligible,validate
from expanded.deck_search import single_card_neighbors
from expanded.fabled_decks import BUNDLES

class SearchConstructionTests(unittest.TestCase):
 def parent(self,root=True):
  records=registry()
  ids=[c for c in sorted(COLLECTIBLE_IDS) if c not in BUNDLES and c not in ('JAIL_397','JAIL_430') and eligible(records[c],'PALADIN',(0,0,0))]
  return Deck('PALADIN',tuple((['JAIL_397'] if root else [])+ids[:29 if root else 30]),beatrix_minion='CORE_EX1_162' if root else None)
 def test_ordinary_changes_preserve_beatrix_choice(self):
  d=self.parent();xs=list(islice(single_card_neighbors(d,experimental=True),12))
  self.assertEqual(len(xs),12)
  self.assertTrue(all('JAIL_397' in x.cards for x in xs))
  for x in xs:self.assertEqual(x.beatrix_minion,d.beatrix_minion);self.assertEqual(validate(x),[])
 def test_removing_beatrix_clears_orphan_choice(self):
  d=self.parent()
  x=next(x for x in single_card_neighbors(d,experimental=True) if 'JAIL_397' not in x.cards)
  self.assertIsNone(x.beatrix_minion);self.assertEqual(validate(x),[])
 def test_adding_beatrix_enumerates_explicit_legal_choices(self):
  d=self.parent(False)
  xs=list(islice((x for x in single_card_neighbors(d,experimental=True) if 'JAIL_397' in x.cards),2))
  self.assertEqual(len(xs),2);self.assertNotEqual(xs[0].beatrix_minion,xs[1].beatrix_minion)
  for x in xs:self.assertIsNotNone(x.beatrix_minion);self.assertEqual(validate(x),[])
 def test_azalina_neighbors_retain_twenty_card_size(self):
  d=next(random_deck('PRIEST',s) for s in range(100) if 'JAIL_430' in random_deck('PRIEST',s).cards)
  xs=list(islice(single_card_neighbors(d,experimental=True),5))
  self.assertEqual(len(xs),5)
  for x in xs:self.assertEqual(len(x.cards),20);self.assertIn('JAIL_430',x.cards);self.assertEqual(validate(x),[])
