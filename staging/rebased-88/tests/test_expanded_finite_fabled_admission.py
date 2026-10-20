"""Production-registry Fabled deck construction, payment and physical chains."""
import unittest
from expanded import Game,Action,cards,broxigar
from expanded.decks import Deck,eligible,validate
from expanded.fabled_decks import BUNDLES

class FiniteFabledAdmissionTests(unittest.TestCase):
 def deck(self,hero,root):
  records=cards.registry();target=40 if root=='TIME_005' else 30
  selected=[root];slots=target-len(BUNDLES[root])
  for cid in sorted(cards.COLLECTIBLE_IDS):
   if cid==root or cid in BUNDLES or records[cid]['type']!='MINION' or not eligible(records[cid],hero,(0,0,0)):continue
   selected.append(cid)
   if len(selected)==slots:break
  d=Deck(hero,tuple(selected));self.assertEqual(validate(d),[]);return d
 def game(self,hero,root,both=False):
  other=self.deck(hero,root) if both else self.deck('SHAMAN','TIME_209')
  g=Game([self.deck(hero,root),other],seed=87)
  g.step(Action('mulligan'));g.step(Action('mulligan'));g.current=0
  for p in g.players:p.mana=p.max_mana=10;p.board=[];p.health=30;p.armor=0
  return g
 def play_card(self,g,owner,card):
  g.current=owner;p=g.players[owner];p.mana=10
  if card not in p.hand:p.hand.append(card)
  cost=g._cost(card,owner);g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==card.uid))
  self.assertEqual(p.mana,10-cost);g.assert_invariants()
 def play(self,g,cid):
  c=g._add(0,cid);self.play_card(g,0,c);return c
 def test_rafaam_real_forty_card_bundle_and_paid_win_checklist(self):
  g=self.game('WARLOCK','TIME_005');p=g.players[0]
  self.assertEqual(len(p.starting_deck),40);self.assertTrue(set(BUNDLES['TIME_005'])<=set(p.starting_deck))
  p.hand=[];p.deck=[]
  self.play(g,'TIME_005');self.assertFalse(g.terminal);p.board=[]
  for cid in BUNDLES['TIME_005']:
   self.play(g,cid);p.board=[]
  self.play(g,'TIME_005');self.assertTrue(g.terminal);self.assertEqual(g.winner,0)
 def test_garona_original_king_transfers_and_paid_assassination_halves_health(self):
  g=self.game('ROGUE','TIME_875');p,q=g.players
  king=next(c for c in q.deck+q.hand if c.card_id=='TIME_875t')
  self.assertTrue(g._started_in_deck(king,0));self.assertFalse(any(c.card_id=='TIME_875t' for c in p.deck+p.hand))
  if king in q.deck:q.deck.remove(king);q.hand.append(king)
  self.play(g,'TIME_875');self.assertEqual(q.health,15);self.assertNotIn(king,q.hand)
 def test_muradin_captures_and_returns_same_original_hammer(self):
  g=self.game('SHAMAN','TIME_209');p=g.players[0]
  hammer=next(c for c in p.deck+p.hand if c.card_id=='TIME_209t')
  self.play(g,'TIME_209');m=next(m for m in p.minions if m.card_id=='TIME_209')
  self.assertIs(m._muradin_hammer['card'],hammer);self.assertNotIn(hammer,p.deck+p.hand)
  m.health=0;g._settle();self.assertIn(hammer,p.hand)
 def test_both_players_broxigar_chains_return_their_own_physical_original(self):
  g=self.game('DEMONHUNTER','TIME_020',both=True)
  self.assertEqual(len(g._broxigar_waiting),2)
  originals=list(g._broxigar_waiting)
  first=[next(c for c in p.deck+p.hand if c.card_id==broxigar.PORTALS[0]) for p in g.players]
  for p in g.players:p.hand=[];p.deck=[]
  for owner in (0,1):
   card=first[owner]
   for i,cid in enumerate(broxigar.PORTALS):
    self.assertEqual(card.card_id,cid);self.assertEqual(card._brox_chain,originals[owner].uid)
    self.play_card(g,owner,card)
    demon=next(m for m in g.players[1-owner].minions if m.card_id==broxigar.DEMONS[i])
    self.assertEqual(demon._brox_chain,originals[owner].uid)
    demon.health=0;g._settle()
    if i<3:card=g.players[owner].deck.pop()
   self.assertIn(originals[owner],g.players[owner].hand)
   self.assertNotIn(originals[owner],g._broxigar_waiting)
  self.assertFalse(g._broxigar_waiting)

if __name__=='__main__':unittest.main()
