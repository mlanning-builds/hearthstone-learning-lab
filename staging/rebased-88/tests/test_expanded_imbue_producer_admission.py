"""Real legal decks and paid actions for finite Imbue producers."""
import unittest
from expanded import Game,Action,cards
from expanded.imbue import IMBUE_POWERS
from expanded.standard_integrations import FINITE_IMBUE_PRODUCERS
import test_expanded_fixed_standard_admission as fixtures
import test_expanded_imbue_azure_admission as rune_fixtures

class ImbueProducerAdmissionTests(unittest.TestCase):
 def game(self,cid):
  records=cards.registry();hero=records[cid].get('cardClass') or records[cid]['classes'][0]
  if hero=='NEUTRAL':hero='MAGE'
  helper=fixtures.FixedStandardAdmissionTests()
  own=rune_fixtures.ImbueAzureAdmissionTests().deck(hero,cid) if hero=='DEATHKNIGHT' else helper.deck(hero,cid,kind='MINION')
  g=Game([own,helper.deck('WARRIOR',kind='MINION')],seed=22)
  g.step(Action('mulligan'));g.step(Action('mulligan'))
  for p in g.players:p.hand=[]
  return g,hero
 def play(self,g,cid,target=0):
  p=g.players[0];p.mana=p.max_mana=10;c=g._add(0,cid);cost=g._cost(c,0)
  g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid and a.target==target))
  self.assertEqual(p.mana,10-cost);g.assert_invariants()
 def test_all_nine_paid_producers_upgrade_the_actual_class_power(self):
  for cid in sorted(FINITE_IMBUE_PRODUCERS):
   with self.subTest(card=cid):
    g,hero=self.game(cid);target=-2 if cid=='END_000' else -1 if cid=='EDR_231' else 0
    g.players[0].health=20;self.play(g,cid,target)
    self.assertEqual(g.players[0].imbue_count,1)
    if hero in IMBUE_POWERS:self.assertEqual(g.players[0].primary_power['card_id'],IMBUE_POWERS[hero])
    if cid=='EDR_231':self.assertEqual(g.players[0].health,24)
    if cid=='END_000':self.assertEqual(g.players[1].health,28)
 def test_hand_discount_is_a_private_physical_choice(self):
  g,_=self.game('EDR_518');chosen=g._add(0,'CORE_EX1_012')
  self.play(g,'EDR_518');self.assertEqual(g.observe(1)['pending_choice'],{'owner':0,'waiting':True})
  g.step(Action('choose',choices=(0,)));self.assertEqual(chosen.cost_delta,-1)
 def test_deathrattle_imbues_again_and_silence_suppresses_it(self):
  for silence,expected in ((False,2),(True,1)):
   g,_=self.game('EDR_451');self.play(g,'EDR_451');m=next(m for m in g.players[0].minions if m.card_id=='EDR_451')
   if silence:g._silence(m)
   m.health=0;g._settle();self.assertEqual(g.players[0].imbue_count,expected)
