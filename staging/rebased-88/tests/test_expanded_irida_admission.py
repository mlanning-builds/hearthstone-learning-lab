import unittest
from copy import deepcopy
from expanded import Game,Action,random_deck
from expanded.cards import registry,COLLECTIBLE_IDS
from expanded.decks import Deck,eligible,validate
from expanded.fabled_decks import BUNDLES
from engine.game import Card

class IridaAdmissionTests(unittest.TestCase):
 def game(self):
  r=registry();ids=[c for c in sorted(COLLECTIBLE_IDS) if c not in BUNDLES and c not in ('JAIL_397','JAIL_430','JAIL_719') and eligible(r[c],'DEMONHUNTER',(0,0,0))][:29]
  d=Deck('DEMONHUNTER',('JAIL_719',)+tuple(ids));self.assertEqual(validate(d),[])
  g=Game([d,random_deck('WARRIOR',89)],seed=90);g.step(Action('mulligan'));g.step(Action('mulligan'))
  p=g.players[0];p.hand=[];p.deck=[Card(g._new_id(),'CORE_CS2_029') for _ in range(6)]
  for c in p.deck:c.cost_delta=-1
  p.mana=p.max_mana=p.mana_capacity=10;g.current=0
  return g
 def play(self,g):
  c=g._add(0,'JAIL_719');g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid))
 def test_paid_battlecry_captures_actual_deck_cards(self):
  g=self.game();p=g.players[0];original=p.deck[:];self.play(g)
  entries=[e for e in g._stored_payloads.values() if e['kind']=='void']
  self.assertEqual(len(entries),1);self.assertEqual(len(p.deck),1)
  self.assertEqual({c.uid for c in p.deck+entries[0]['values']},{c.uid for c in original})
  self.assertEqual(p.last_paid_cost,g.cards['JAIL_719']['cost'])
 def test_owner_start_returns_two_after_source_silence_and_death(self):
  g=self.game();self.play(g);p=g.players[0];m=next(m for m in p.minions if m.card_id=='JAIL_719')
  g._silence(m);m.health=0;g._settle(allow_event_choices=True)
  g.step(Action('end'));self.assertFalse(p.hand);g.step(Action('end'))
  self.assertEqual(len(p.hand),3);self.assertTrue(all(c.cost_delta==-1 for c in p.hand))
  self.assertEqual(g.observe(0)['players'][0]['void_remaining'],3)
 def test_finite_storage_does_not_replace_fatigue(self):
  g=self.game();self.play(g);p=g.players[0]
  for _ in range(3):g.step(Action('end'));g.step(Action('end'))
  self.assertEqual(len(p.hand),6);self.assertEqual(p.fatigue,2)
  self.assertEqual(g.observe(0)['players'][0]['void_remaining'],0)
  self.assertEqual(p.health,27)
 def test_clone_storage_does_not_share_physical_cards(self):
  g=self.game();self.play(g);clone=deepcopy(g)
  g.step(Action('end'));g.step(Action('end'))
  self.assertEqual(clone.observe(0)['players'][0]['void_remaining'],5)
  for viewer in (0,1):self.assertNotIn('CORE_CS2_029',str(clone.observe(viewer)['players'][0].get('set_aside_cards')))
