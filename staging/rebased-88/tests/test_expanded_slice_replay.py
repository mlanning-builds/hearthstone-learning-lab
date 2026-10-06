import unittest
from unittest.mock import patch
import test_expanded_generation as fixtures
from expanded import Action,cards,automatic_casting
from standard.catalog import load_catalog
class SliceReplayTests(unittest.TestCase):
 def setUp(self):
  self.fx=fixtures.GenerationTests();self.g=self.fx.game();self.p,self.q=self.g.players
  self.g.cards.update({c['id']:c for c in load_catalog() if c['id']=='JAIL_500'})
  ctx=patch.dict(cards.RULES,{'JAIL_500':automatic_casting.RULES['JAIL_500']});ctx.start();self.addCleanup(ctx.stop)
 def play(self,cid,target=None):
  c=self.g._add(0,cid);self.p.mana=10;self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid and (target is None or a.target==target)));return c
 def test_empty_replay_ends_turn(self):
  self.play('JAIL_500');self.assertEqual(self.g.current,1)
 def test_replays_spell_at_enemy_and_then_ends(self):
  self.play('CORE_CS2_029',self.g.hero_id(1));self.play('JAIL_500');self.assertEqual(self.q.health,18);self.assertEqual(self.g.current,1)
 def test_duplicate_cards_both_replay(self):
  self.play('CORE_EX1_162');self.play('CORE_EX1_162');self.play('JAIL_500');self.assertEqual(len(self.p.minions),4)
 def test_replayed_minion_does_not_repeat_battlecry(self):
  with patch.dict(cards.RULES,{'CORE_EX1_162':('none',[('draw',1)])}):
   self.play('CORE_EX1_162');hand=len(self.p.hand);self.play('JAIL_500');self.assertEqual(len(self.p.hand),hand)
 def test_prior_turn_does_not_replay(self):
  self.play('CORE_EX1_162');self.g.step(Action('end'));self.g.step(Action('end'));self.play('JAIL_500');self.assertEqual(len(self.p.minions),1)
 def test_replay_does_not_add_paid_history_entries(self):
  self.play('TOKEN_COIN');self.play('JAIL_500');self.assertEqual(len(self.p.played_history),2)
 def test_end_request_during_end_phase_is_ignored(self):
  self.g._turn_frame={'kind':'end'};self.fx.run_ops(self.g,[('request_end_turn',)]);self.assertIsNone(getattr(self.g,'_requested_turn_end',None));self.g._turn_frame=None
 def test_opponent_end_request_does_not_end_active_turn(self):
  self.fx.run_ops(self.g,[('request_end_turn',)],owner=1);self.assertIsNone(getattr(self.g,'_requested_turn_end',None))
