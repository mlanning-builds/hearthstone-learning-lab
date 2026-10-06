"""Frozen primitive historical bodies, paid without registry or pool patches."""
import json
from pathlib import Path
import unittest
import test_expanded_generation as fixtures
from expanded import Action
from expanded import cards
from expanded.historical_simple import GENERATED_IDS,RULES
from expanded.historical_generation import validate_past_candidates

class HistoricalSimpleTests(unittest.TestCase):
 def game(self):
  g=fixtures.GenerationTests().game()
  for p in g.players:p.mana_capacity=10;p.overload_next=p.locked_mana=0
  g._summon(0,'CS2_182');g._summon(1,'CS2_182')
  return g
 def test_explicit_declarations_match_reviewed_source_behavior(self):
  audit=json.loads((Path(__file__).resolve().parents[1]/'../../docs/engine-audit/historical-simple-admission-2026-10-06.json').read_text())
  self.assertEqual(set(audit['card_ids']),GENERATED_IDS);self.assertEqual(len(GENERATED_IDS),40)
  for row in audit['records']:
   cid=row['card_id'];mode,ops=cards.RULES[row['source_card_id']]
   self.assertEqual(RULES[cid],(mode,ops))
 def test_all_forty_bodies_complete_actual_paid_play(self):
  for cid in sorted(GENERATED_IDS):
   with self.subTest(cid=cid):
    g=self.game();c=g._add(0,cid);cost=g._cost(c,0)
    g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid))
    self.assertEqual(g.players[0].last_paid_cost,cost);self.assertEqual(g.players[0].cards_played,1)
    self.assertNotIn(c,g.players[0].hand);g.assert_invariants()
 def test_generated_only_ids_do_not_enter_standard_decks(self):
  self.assertTrue(GENERATED_IDS<=cards.TOKEN_IDS);self.assertFalse(GENERATED_IDS&cards.COLLECTIBLE_IDS)
  validate_past_candidates(GENERATED_IDS,cards.registry())
 def test_old_eye_beam_uses_printed_outcast_cost_and_lifesteal(self):
  g=self.game();p=g.players[0];p.hand=[];p.health=20;c=g._add(0,'BT_801');enemy=g.players[1].minions[0]
  self.assertEqual(g._cost(c,0),1)
  g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid and a.target==enemy.uid))
  self.assertEqual(p.mana,9);self.assertEqual(p.health,23)
  g=self.game();p=g.players[0];p.hand=[];g._add(0,'TOKEN_COIN');c=g._add(0,'BT_801');g._add(0,'TOKEN_COIN')
  self.assertEqual(g._cost(c,0),3)
 def test_old_overload_is_locked_on_next_owner_turn(self):
  g=self.game();p=g.players[0];c=g._add(0,'EX1_238');enemy=g.players[1].minions[0]
  g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid and a.target==enemy.uid))
  self.assertEqual(p.overload_next,1);g.step(Action('end'));g.step(Action('end'))
  self.assertEqual((p.locked_mana,p.mana),(1,9))
 def test_old_tradeable_card_preserves_physical_cards_and_is_not_a_play(self):
  g=self.game();p=g.players[0];p.hand=[];p.deck=[]
  original=g._add(0,'CS2_182');p.hand.remove(original);p.deck=[original]
  c=g._add(0,'SW_066');uids={c.uid,original.uid}
  g.step(next(a for a in g.legal_actions() if a.kind=='trade' and a.source==c.uid))
  self.assertEqual(p.mana,9);self.assertEqual(p.cards_played,0)
  self.assertEqual({c.uid for c in p.hand+p.deck},uids)
