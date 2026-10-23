"""Deck construction and scheduling only; no gameplay or learning."""
from collections import Counter
import json
from pathlib import Path
import tempfile
import unittest
from hearthstone_sim.neural.deck_continuum import build_panel
from hearthstone_sim.neural.decks import load_panel
from hearthstone_sim.neural.runner import match_schedule

class ContinuumTests(unittest.TestCase):
    def test_all_classes_have_distinct_legal_published_variant_random_decks(self):
        anchors=Path(__file__).resolve().parents[1]/'configs/neural_all_classes.json'
        with tempfile.TemporaryDirectory() as folder:
            target=Path(folder)/'panel.json'
            build_panel(anchors,target,5703)
            before=target.read_bytes();build_panel(anchors,target,5703)
            self.assertEqual(before,target.read_bytes())
            decks,_=load_panel(target)
            self.assertEqual(len(decks),176)
            self.assertEqual(set(Counter(d.hero_class for d in decks.values()).values()),{16})
            entries=json.loads(before)['decks']
            self.assertEqual(Counter(e['kind'] for e in entries),{'published-anchor':11,'legal-variant':77,'legal-random':88})
            for hero in {d.hero_class for d in decks.values()}:
                lists=[tuple(sorted(d.cards)) for d in decks.values() if d.hero_class==hero]
                self.assertEqual(len(set(lists)),16)
            original,_=load_panel(anchors)
            for key,value in original.items():self.assertEqual(value,decks[key])
            other=Path(folder)/'next.json';build_panel(anchors,other,5704)
            self.assertNotEqual(before,other.read_bytes())

    def test_cached_schedule_preserves_original_order_and_pair_coverage(self):
        import itertools,random
        names=['a','b','c'];expected=list(itertools.product(names,names,(0,1),(0,1)))
        random.Random(71).shuffle(expected)
        self.assertEqual([match_schedule(names,i,71) for i in range(36)],expected)

if __name__=='__main__':unittest.main()
