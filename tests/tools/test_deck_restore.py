import importlib.util
from pathlib import Path
from dataclasses import dataclass,asdict
import unittest

ROOT=Path(__file__).resolve().parents[2]
@dataclass(frozen=True)
class Deck:
 hero_class:str
 cards:tuple
 runes:tuple
 beatrix_minion:str=None
 contraband_beasts:tuple=()

class DeckRestoreTests(unittest.TestCase):
 def loaders(self):
  for name in ('stress_candidate','compare_candidate_decks'):
   spec=importlib.util.spec_from_file_location(name,ROOT/'tools'/f'{name}.py')
   module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
   yield module.restore_deck
 def test_roundtrip_preserves_construction_choices(self):
  original=Deck('PALADIN',('JAIL_397',),(0,0,0),'CORE_EX1_162',('a','b','c'))
  for restore in self.loaders():
   data=asdict(original);data['contraband_beasts']=list(data['contraband_beasts'])
   self.assertEqual(restore(data,Deck),original)
 def test_legacy_deck_inputs_keep_default_choices(self):
  for restore in self.loaders():
   self.assertEqual(restore(dict(hero_class='MAGE',cards=['a'],runes=[0,0,0]),Deck),Deck('MAGE',('a',),(0,0,0)))
