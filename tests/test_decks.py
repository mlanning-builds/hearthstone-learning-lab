import random
import unittest
from lab import RUNE_PROFILES, eligible, load_cards, population, random_deck, validate

class DeckTests(unittest.TestCase):
    def setUp(self):
        self.cards = load_cards()

    def test_population_all_profiles(self):
        decks = population(self.cards, per_profile=100)
        self.assertEqual(len(decks), 1000)
        for d in decks:
            self.assertEqual(validate(d['cards'], self.cards, tuple(d['runes'].values())), [])

    def test_seed_reproducibility(self):
        self.assertEqual(population(self.cards), population(self.cards))
        self.assertNotEqual(population(self.cards), population(self.cards, seed=43))

    def test_reject_bad_runes(self):
        for p in [(1,1,0), (-1,2,2), (1,1,1.0)]:
            with self.assertRaises(ValueError):
                eligible(self.cards, p)

    def test_incompatible_and_unknown_cards(self):
        triple_blood = next(c for c in self.cards if c.get('runeCost', {}).get('blood') == 3)
        self.assertTrue(validate([triple_blood['id']] * 30, self.cards, (0,3,0)))
        self.assertTrue(validate(['unknown'] * 30, self.cards, (1,1,1)))

    def test_copy_limits(self):
        for rarity in ['LEGENDARY', 'COMMON']:
            c = next(c for c in eligible(self.cards, (1,1,1)) if c['rarity'] == rarity)
            self.assertTrue(any('Too many copies' in e for e in validate([c['id']] * 30, self.cards, (1,1,1))))

if __name__ == '__main__':
    unittest.main()
