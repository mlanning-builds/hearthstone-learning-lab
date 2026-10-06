import gzip,json,unittest
from pathlib import Path
from unittest.mock import patch
import test_expanded_generation as fixtures
from expanded import Action,cards,quest_families
from expanded.features import encode_decision,SCHEMA

class ExtraTurnTests(unittest.TestCase):
 def setUp(self):
  self.fx=fixtures.GenerationTests();self.g=self.fx.game();self.p,self.q=self.g.players
  with gzip.open(Path(__file__).resolve().parents[1]/'data/standard/all_cards.json.gz','rt') as f:self.g.cards.update({c['id']:c for c in json.load(f) if c['id']=='UNG_028t'})
  p=patch.dict(cards.RULES,{'UNG_028t':quest_families.TOKEN_RULES['UNG_028t']});p.start();self.addCleanup(p.stop)
 def cast(self,owner=0):self.fx.run_ops(self.g,[('time_warp',)],owner=owner)
 def end(self):self.g.step(Action('end'))
 def test_paid_spell_reserves_without_immediate_transition(self):
  c=self.g._add(0,'UNG_028t');turn=self.g.turn
  self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid))
  self.assertEqual(self.p.mana,5);self.assertEqual(self.g.turn,turn);self.assertEqual(self.p.extra_turns_pending,1)
 def test_extra_turn_draws_refreshes_and_returns_to_opponent(self):
  self.cast();deck=len(self.p.deck);taken=self.p.turns_taken;self.p.mana=0;self.p.power_used=True;self.p.hero_attacks=1
  self.end();self.assertEqual(self.g.current,0);self.assertEqual(self.p.turns_taken,taken+1);self.assertEqual(len(self.p.deck),deck-1)
  self.assertEqual(self.p.mana,10);self.assertFalse(self.p.power_used);self.assertEqual(self.p.hero_attacks,0);self.assertEqual(self.p.extra_turns_pending,0)
  self.end();self.assertEqual(self.g.current,1)
 def test_repeated_cast_does_not_stack(self):
  self.cast();self.cast();self.assertEqual(self.p.extra_turns_pending,1)
 def test_once_per_game_survives_consumption(self):
  self.cast();self.end();self.cast();self.assertEqual(self.p.extra_turns_pending,0);self.end();self.assertEqual(self.g.current,1)
 def test_players_have_independent_once_per_game_state(self):
  self.cast();self.end();self.end();self.cast(1);self.end();self.assertEqual(self.g.current,1);self.assertTrue(self.q.time_warp_used)
 def test_temporary_attack_expires_before_extra_turn(self):
  self.p.temporary_attack=4;self.cast();self.end();self.assertEqual(self.p.temporary_attack,0)
 def test_end_turn_triggers_run_on_each_actual_turn(self):
  self.p.permanent_end_damage=[2];health=self.q.health;self.cast();self.end();self.assertEqual(self.q.health,health-2);self.end();self.assertEqual(self.q.health,health-4)
 def test_turn_limit_still_ends_game(self):
  self.cast();self.g.max_turns=self.g.turn;self.end();self.assertTrue(self.g.terminal)
 def test_skipped_extra_turn_does_not_draw(self):
  self.cast();self.p.skipped_turns_pending=1;deck=len(self.p.deck);taken=self.p.turns_taken;self.end()
  self.assertEqual(self.g.current,1);self.assertEqual(len(self.p.deck),deck);self.assertEqual(self.p.turns_taken,taken)
 def test_internal_cast_uses_same_once_per_game_state(self):
  self.fx.run_ops(self.g,[('cast_fixed_spell','UNG_028t','random')]);self.assertEqual(self.p.extra_turns_pending,1);self.assertTrue(self.p.time_warp_used)
 def test_public_state_and_feature_schema(self):
  self.cast();view=self.g.observe(0);self.assertEqual(view['players'][0]['extra_turns_pending'],1);self.assertTrue(view['players'][0]['time_warp_used'])
  rows=encode_decision(dict(observation=view,actor=0,actions=view['legal_actions']));self.assertIn('extra_turns_pending',str(rows));self.assertEqual(SCHEMA,'visible-action-features-v58')
