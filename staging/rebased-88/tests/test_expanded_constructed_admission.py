"""Normal-registry construction and paid-action checks for opening effects."""
import unittest
from expanded import Game, Action, random_deck
from expanded.decks import Deck, eligible, validate
from expanded.cards import registry, COLLECTIBLE_IDS
from expanded.fabled_decks import BUNDLES

class ConstructedAdmissionTests(unittest.TestCase):
 def deck(self,hero,root,size,selection=None):
  cards=registry()
  ids=[c for c in sorted(COLLECTIBLE_IDS) if c not in BUNDLES and c not in ('JAIL_397','JAIL_430') and eligible(cards[c],hero,(0,0,0))]
  d=Deck(hero,(root,)+tuple(ids[:size-1]),beatrix_minion=selection)
  self.assertEqual(validate(d),[])
  return d
 def test_beatrix_opens_with_ten_distinct_added_copies(self):
  d=self.deck('PALADIN','JAIL_397',30,'CORE_EX1_162')
  g=Game([d,random_deck('WARRIOR',31)],seed=33)
  p=g.players[0];physical=p.hand+p.deck
  copies=[c for c in physical if c.card_id=='CORE_EX1_162']
  self.assertEqual(len(physical),40);self.assertEqual(len(copies),10+d.cards.count('CORE_EX1_162'))
  self.assertEqual(len({c.uid for c in copies}),len(copies))
  self.assertTrue(all(g._started_in_deck(c,0) for c in copies))
 def test_two_azalinas_copy_original_positions_once(self):
  d=self.deck('PRIEST','JAIL_430',20)
  g=Game([d,d],seed=34)
  for p in g.players:
   self.assertEqual(p.health,40);self.assertEqual(p.max_health,40)
   self.assertEqual(len(p.hand)+len(p.deck),40)
   self.assertEqual(len(p.starting_deck),20);self.assertEqual(len(p.copied_opening_ids),20)
   copies=[c for c in p.hand+p.deck if getattr(c,'_copied_opening_effect',False)]
   self.assertEqual(len(copies),20);self.assertEqual(len({c.uid for c in copies}),20)
 def test_azalina_paid_battlecry_fills_hand(self):
  g=Game([self.deck('PRIEST','JAIL_430',20),random_deck('WARRIOR',35)],seed=36)
  g.step(Action('mulligan'));g.step(Action('mulligan'));g.current=0
  p=g.players[0];p.hand=[];p.mana=p.max_mana=10
  card=g._add(0,'JAIL_430');before=len(p.deck)
  g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==card.uid))
  self.assertEqual(len(p.hand),10);self.assertEqual(len(p.deck),before-10)
  self.assertEqual(p.mana,3)
 def test_random_decks_supply_legal_deterministic_opening_choices(self):
  seen=set()
  for hero,root in (('PALADIN','JAIL_397'),('PRIEST','JAIL_430')):
   for seed in range(80):
    d=random_deck(hero,seed);self.assertEqual(validate(d),[])
    self.assertEqual(d,random_deck(hero,seed))
    if root in d.cards:
     seen.add(root)
     if root=='JAIL_397':self.assertIsNotNone(d.beatrix_minion)
     else:self.assertEqual(len(d.cards),20)
  self.assertEqual(seen,{'JAIL_397','JAIL_430'})
