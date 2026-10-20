"""Paid Herald bodies, literal Soldiers and full production Fel Discover."""
import unittest
from expanded import Game,Action,cards
from expanded.herald import SOLDIERS
from expanded.standard_integrations import FINITE_HERALDS
import test_expanded_fixed_standard_admission as fixtures

class FiniteHeraldAdmissionTests(unittest.TestCase):
 def game(self,hero,cid):
  helper=fixtures.FixedStandardAdmissionTests();g=Game([helper.deck(hero,cid,kind='MINION'),helper.deck('WARRIOR',kind='MINION')],seed=40)
  g.step(Action('mulligan'));g.step(Action('mulligan'))
  for p in g.players:p.hand=[]
  return g
 def play(self,g,cid):
  p=g.players[0];p.mana=p.max_mana=10;c=g._add(0,cid);cost=g._cost(c,0)
  g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid))
  self.assertEqual(p.mana,10-cost);g.assert_invariants()
 def test_all_seven_paid_sources_summon_the_class_soldier(self):
  for cid in sorted(FINITE_HERALDS):
   with self.subTest(card=cid):
    hero=cards.registry()[cid]['cardClass'];g=self.game(hero,cid);self.play(g,cid)
    self.assertEqual(g.players[0].herald_count,1)
    self.assertIn(SOLDIERS[hero],[m.card_id for m in g.players[0].minions])
    if cid=='CATA_561':self.assertEqual([c.card_id for c in g.players[0].hand],['CATA_561t']*2)
 def test_warrior_soldier_death_deals_two_without_spellpower(self):
  g=self.game('WARRIOR','CATA_580');self.play(g,'CATA_580');m=next(m for m in g.players[0].minions if m.card_id=='CATA_580t')
  m.health=0;g._settle();self.assertEqual(g.players[1].health,28)
 def test_production_fel_discover_has_no_fixture_contract(self):
  g=self.game('DEMONHUNTER','FIR_952');self.play(g,'FIR_952')
  self.assertIsNotNone(g.pending_choice);g.step(Action('choose',choices=(0,)))
  c=g.players[0].hand[-1];self.assertEqual(g.cards[c.card_id]['spellSchool'],'FEL');self.assertEqual(c.cost_delta,-1)
