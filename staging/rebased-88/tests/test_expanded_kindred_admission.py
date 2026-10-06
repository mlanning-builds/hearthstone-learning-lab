import unittest
from expanded import Game,Action,random_deck
from expanded.cards import registry,COLLECTIBLE_IDS
from expanded.decks import Deck,eligible,validate
from expanded.fabled_decks import BUNDLES

class KindredAdmissionTests(unittest.TestCase):
 def game(self):
  r=registry();ids=[c for c in sorted(COLLECTIBLE_IDS) if c not in BUNDLES and c not in ('JAIL_397','JAIL_430','TLC_251') and eligible(r[c],'SHAMAN',(0,0,0))][:29]
  d=Deck('SHAMAN',('TLC_251',)+tuple(ids));self.assertEqual(validate(d),[])
  g=Game([d,random_deck('MAGE',25)],seed=26);g.step(Action('mulligan'));g.step(Action('mulligan'))
  g.current=0
  for p in g.players:p.hand=[];p.deck=['CORE_CS2_029']*25;p.mana=p.max_mana=p.mana_capacity=10
  return g
 def play(self,g,cid,target=0):
  c=g._add(0,cid);g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid and a.target==target))
 def test_paid_challenger_primes_visible_charge(self):
  g=self.game();self.play(g,'TLC_251')
  self.assertTrue(g.players[0].kindred_twice)
  self.assertTrue(g.observe(1)['players'][0]['kindred_twice'])
  self.assertEqual(g.players[0].mana,10-g.cards['TLC_251']['cost'])
 def test_inactive_kindred_and_other_cards_preserve_charge(self):
  g=self.game();self.play(g,'TLC_251');self.play(g,'TOKEN_COIN');self.play(g,'TLC_440',g.hero_id(1))
  self.assertTrue(g.players[0].kindred_twice)
  self.assertEqual(len(g.players[0].hand),1)
 def test_next_active_kindred_doubles_bonus_draw_once(self):
  g=self.game();self.play(g,'CORE_CS2_024',g.hero_id(1));self.play(g,'TLC_251')
  g.step(Action('end'));g.step(Action('end'));g.players[0].hand=[]
  self.play(g,'TLC_440',g.hero_id(1));self.assertEqual(len(g.players[0].hand),3)
  self.assertFalse(g.players[0].kindred_twice)
  self.play(g,'TLC_440',g.hero_id(1));self.assertEqual(len(g.players[0].hand),5)
 def test_active_kindred_discount_applies_twice_before_payment(self):
  g=self.game();self.play(g,'TLC_251')
  self.play(g,'CORE_EX1_043');g.step(Action('end'));g.step(Action('end'))
  self.play(g,'TLC_600',g.hero_id(1))
  self.assertEqual(g.players[0].last_paid_cost,2)
  self.assertEqual(g.players[0].mana,8)
  self.assertEqual(g.players[0].armor,5)
  self.assertFalse(g.players[0].kindred_twice)
