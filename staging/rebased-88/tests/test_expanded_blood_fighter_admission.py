import unittest
from expanded import Game, Action, random_deck
from expanded.cards import registry, COLLECTIBLE_IDS
from expanded.decks import Deck, eligible, validate
from expanded.fabled_decks import BUNDLES


class BloodFighterAdmissionTests(unittest.TestCase):
 def game(self):
  records=registry()
  filler=[cid for cid in sorted(COLLECTIBLE_IDS)
          if cid not in BUNDLES and cid not in ('JAIL_397','JAIL_430')
          and eligible(records[cid],'WARRIOR',(0,0,0))][:27]
  deck=Deck('WARRIOR',('TIME_850',)+tuple(filler))
  self.assertEqual(validate(deck),[])
  g=Game([deck,random_deck('MAGE',17)],seed=18)
  g.step(Action('mulligan'));g.step(Action('mulligan'))
  p=g.players[0];p.hand=[];p.deck=[];g.current=0
  p.mana=p.max_mana=10
  return g
 def play(self,g,cid):
  c=g._add(0,cid)
  g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid))
  return next(m for m in g.players[0].minions if m.card_id==cid)
 def test_bundle_contains_three_physical_cards(self):
  g=self.game()
  self.assertIn('TIME_850',COLLECTIBLE_IDS)
  self.assertNotIn('TIME_850t',COLLECTIBLE_IDS)
  self.assertIn('TIME_850t1',g.cards)
 def test_paid_logosh_death_consumes_modified_hand_card_and_attacks(self):
  g=self.game();m=self.play(g,'TIME_850');p=g.players[0]
  c=g._add(0,'TIME_850t');c.attack_bonus=2;c.health_bonus=3
  self.assertEqual(p.mana,3)
  m.health=0;g._settle(allow_event_choices=True)
  recruited=p.minions[0]
  self.assertEqual(recruited.card_id,c.card_id)
  self.assertNotIn(c,p.hand)
  self.assertEqual((recruited.attack,recruited.max_health),(14,15))
  self.assertEqual(g.players[1].health,16)
 def test_paid_broll_death_grants_taunt_to_valeera(self):
  g=self.game();m=self.play(g,'TIME_850t');c=g._add(0,'TIME_850t1')
  m.health=0;g._settle(allow_event_choices=True)
  recruited=g.players[0].minions[0]
  self.assertEqual(recruited.card_id,c.card_id)
  self.assertEqual((recruited.attack,recruited.max_health),(12,12))
  self.assertTrue({'TAUNT','ELUSIVE'}<=recruited.keywords)
 def test_silenced_paid_fighter_preserves_hand_card(self):
  g=self.game();m=self.play(g,'TIME_850t1');c=g._add(0,'TIME_850')
  g._silence(m);m.health=0;g._settle(allow_event_choices=True)
  self.assertIn(c,g.players[0].hand)
  self.assertFalse(g.players[0].minions)
