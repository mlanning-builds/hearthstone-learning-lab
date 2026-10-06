import json,unittest
import test_expanded_generation as fixtures
from expanded.replay_history import plays_for_turn
from expanded import Action
class ReplayHistoryTests(unittest.TestCase):
 def setUp(self):self.fx=fixtures.GenerationTests();self.g=self.fx.game();self.p=self.g.players[0]
 def play(self,cid):
  c=self.g._add(0,cid);self.p.mana=10;self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid));return c
 def test_records_physical_order_and_duplicates(self):
  a=self.play('TOKEN_COIN');b=self.play('TOKEN_COIN');r=plays_for_turn(self.p,self.g.turn);self.assertEqual([x.card.uid for x in r],[a.uid,b.uid])
 def test_snapshot_does_not_alias_original(self):
  c=self.play('TOKEN_COIN');c.cost_delta=10;self.assertEqual(getattr(plays_for_turn(self.p,self.g.turn)[0].card,'cost_delta',0),0)
 def test_returned_snapshot_cannot_mutate_history(self):
  self.play('TOKEN_COIN');plays_for_turn(self.p,self.g.turn)[0].card.cost_delta=10;self.assertEqual(getattr(self.p.replay_history[0].card,'cost_delta',0),0)
 def test_excludes_physical_source_only(self):
  a=self.play('TOKEN_COIN');b=self.play('TOKEN_COIN');self.assertEqual([x.card.uid for x in plays_for_turn(self.p,self.g.turn,b.uid)],[a.uid])
 def test_turn_filter_ignores_previous_plays(self):
  self.play('TOKEN_COIN');self.g.step(Action('end'));self.assertEqual(plays_for_turn(self.p,self.g.turn),())
 def test_internal_cast_does_not_enter_hand_play_history(self):
  self.fx.run_ops(self.g,[('cast_fixed_spell','TOKEN_COIN','random')]);self.assertEqual(self.p.replay_history,[])
 def test_secret_snapshot_not_exposed_to_opponent(self):
  self.play('CORE_EX1_287');self.assertNotIn('CORE_EX1_287',json.dumps(self.g.observe(1)));self.assertNotIn('replay_history',self.g.observe(0)['players'][0])
