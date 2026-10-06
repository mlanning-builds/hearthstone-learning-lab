import unittest
from collections import Counter
from itertools import islice
from expanded import random_deck,validate
from expanded.deck_search import rune_profiles,single_card_neighbors,sample_neighbors
from expanded.cards import registry
from standard.catalog import CLASSES

class DeckSearchTests(unittest.TestCase):
    def test_all_classes_have_legal_one_card_neighbors(self):
        for hero in CLASSES:
            deck=random_deck(hero,31);before=Counter(deck.cards)
            candidates=list(islice(single_card_neighbors(deck,experimental=True),12))
            self.assertEqual(len(candidates),12)
            for candidate in candidates:
                self.assertEqual(validate(candidate),[])
                after=Counter(candidate.cards)
                self.assertEqual(sum((before-after).values()),1)
                self.assertEqual(sum((after-before).values()),1)
                self.assertEqual(candidate.hero_class,hero);self.assertEqual(candidate.runes,deck.runes)
    def test_all_ten_death_knight_rune_profiles(self):
        profiles=rune_profiles('DEATHKNIGHT');self.assertEqual(len(set(profiles)),10)
        for runes in profiles:
            self.assertEqual(sum(runes),3)
            deck=random_deck('DEATHKNIGHT',31,runes)
            neighbor=next(single_card_neighbors(deck,experimental=True))
            self.assertEqual(neighbor.runes,runes);self.assertEqual(validate(neighbor),[])
    def test_sampling_reproducible_unique_and_preserves_parent(self):
        deck=random_deck('MAGE',31);before=deck.cards
        a=sample_neighbors(deck,count=8,seed=73,experimental=True)
        b=sample_neighbors(deck,count=8,seed=73,experimental=True)
        self.assertEqual(a,b);self.assertEqual(len(set(a)),8);self.assertEqual(deck.cards,before)
    def test_legendary_copy_limits(self):
        cards=registry();deck=random_deck('WARLOCK',31)
        for candidate in islice(single_card_neighbors(deck,experimental=True),100):
            counts=Counter(candidate.cards)
            self.assertTrue(all(count<=1 for cid,count in counts.items() if cards[cid].get('rarity')=='LEGENDARY'))
    def test_full_standard_mode_stays_gated(self):
        with self.assertRaisesRegex(RuntimeError,'Full Standard is not ready'):next(single_card_neighbors(random_deck('MAGE',31)))
    def test_invalid_parent_rejected(self):
        from expanded import Deck
        with self.assertRaises(ValueError):next(single_card_neighbors(Deck('MAGE',()),experimental=True))

    def test_mixed_alias_parent_has_one_neighbor_per_composition(self):
        from unittest.mock import patch
        from contextlib import ExitStack
        from expanded import Deck
        cards={f'CARD_{i:02}':dict(id=f'CARD_{i:02}',dbfId=i,cardClass='NEUTRAL',rarity='COMMON') for i in range(16)}
        cards['ALIAS']=dict(id='ALIAS',dbfId=99,countAsCopyOfDbfId=0,cardClass='NEUTRAL',rarity='COMMON')
        parent=Deck('MAGE',tuple(['ALIAS','CARD_00']+[f'CARD_{i:02}' for i in range(1,15) for _ in range(2)]))
        before=parent.cards
        def composition(deck):
            return tuple(sorted(Counter(cards[c].get('countAsCopyOfDbfId',cards[c]['dbfId']) for c in deck.cards).items()))
        with ExitStack() as stack:
            stack.enter_context(patch('expanded.deck_search.registry',return_value=cards))
            stack.enter_context(patch('expanded.deck_search.COLLECTIBLE_IDS',set(cards)))
            stack.enter_context(patch('expanded.decks.COLLECTIBLE_IDS',set(cards)))
            neighbors=list(single_card_neighbors(parent,experimental=True))
            self.assertEqual(len(neighbors),15)
            self.assertEqual(len({composition(d) for d in neighbors}),15)
            for candidate in neighbors:self.assertEqual(validate(candidate,cards),[])
            sample=sample_neighbors(parent,count=100,seed=71,experimental=True)
            self.assertEqual(sample,neighbors)
        self.assertEqual(parent.cards,before)
