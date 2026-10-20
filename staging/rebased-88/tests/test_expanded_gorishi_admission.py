"""Normal paid Standard quest and persistent reward paths."""
import unittest
from expanded import Game,Action,cards
import test_expanded_fixed_standard_admission as fixtures

class GorishiAdmissionTests(unittest.TestCase):
 def game(self):
  helper=fixtures.FixedStandardAdmissionTests()
  g=Game([helper.deck('DEMONHUNTER','TLC_631',kind='MINION'),helper.deck('WARRIOR',kind='MINION')],seed=14)
  g.step(Action('mulligan'));g.step(Action('mulligan'))
  for p in g.players:p.hand=[]
  return g
 def play(self,g,cid):
  p=g.players[0];p.mana=p.max_mana=10;c=g._add(0,cid);before=g._cost(c,0)
  g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid))
  self.assertEqual(p.mana,10-before);g.assert_invariants()
 def test_paid_drake_waves_complete_quest_and_reward_persists(self):
  g=self.game();p,q=g.players;self.play(g,'TLC_631')
  for _ in range(7):g._summon(1,'CORE_EX1_012')
  self.play(g,'CORE_UNG_848');self.assertEqual(p.quest['progress'],7)
  for _ in range(5):g._summon(1,'CORE_EX1_012')
  self.play(g,'CORE_UNG_848');self.assertIsNone(p.quest)
  self.assertEqual([c.card_id for c in p.hand],['TLC_631t'])
  self.play(g,'TLC_631t');g._silence(next(m for m in p.minions if m.card_id=='TLC_631t'))
  g._deal_effect(-2,2,dict(owner=0,source=None,bonus=0,lifesteal=False));g._settle()
  self.assertEqual(q.health,26);self.assertEqual(p.gorishi_stacks,1)
 def test_unknown_target_ownership_does_not_progress(self):
  g=self.game();self.play(g,'TLC_631')
  g._quest_family_event('damage',dict(damage_owner=0,target_owner=None,amount=2,target=9999))
  self.assertEqual(g.players[0].quest['progress'],0)
