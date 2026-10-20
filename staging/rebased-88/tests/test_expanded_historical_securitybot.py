"""Securitybot's physical draw, modifier replacement, Silence and overdraw."""
import unittest
from expanded import Action,cards
from engine.game import Card
import test_expanded_generation as fixtures
class HistoricalSecuritybotTests(unittest.TestCase):
 def game(self):return fixtures.GenerationTests().game()
 def play(self,g):
  c=g._add(0,'YOG_510');g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid))
  return next(m for m in g.players[0].minions if m.card_id=='YOG_510')
 def kill(self,g,m):m.health=0;g._settle(allow_event_choices=True)
 def test_draw_retains_uid_and_keywords_replaces_stats_cost_and_later_paid_body(self):
  g=self.game();m=self.play(g);p=g.players[0];c=Card(g._new_id(),'CORE_EX1_162');c.attack_bonus=9;c.health_bonus=8;c.cost_delta=-1
  c.rule_state={'extra_keywords':['TAUNT']};p.deck=[c,'CORE_CS2_029'];self.kill(g,m)
  self.assertEqual(p.hand,[c]);self.assertEqual(p.deck,['CORE_CS2_029'])
  self.assertEqual((g._card_stat(c,'attack',0),g._card_stat(c,'health',0),g._cost(c,0)),(5,5,5))
  self.assertEqual(c.rule_state,{'extra_keywords':['TAUNT']})
  p.mana=10;g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid));self.assertEqual((p.minions[0].attack,p.minions[0].health),(5,5));g.assert_invariants()
 def test_silence_blocks_draw_and_missing_minion_is_noop_without_fatigue_or_rng(self):
  for silence in (True,False):
   g=self.game();m=self.play(g);p=g.players[0];p.deck=['CORE_CS2_029'];rng=g.rng.getstate()
   if silence:g._silence(m)
   self.kill(g,m);self.assertFalse(p.hand);self.assertEqual(p.fatigue,0);self.assertEqual(p.deck,['CORE_CS2_029']);self.assertEqual(g.rng.getstate(),rng)
 def test_full_hand_burn_is_not_a_successful_draw_or_buff(self):
  g=self.game();m=self.play(g);p=g.players[0];c=Card(g._new_id(),'CORE_EX1_162');c.attack_bonus=3;p.deck=[c]
  for _ in range(10):g._add(0,'CORE_CS2_029')
  self.kill(g,m);self.assertFalse(p.deck);self.assertEqual(c.attack_bonus,3);self.assertFalse(hasattr(c,'set_cost'));self.assertEqual(len(p.hand),10)
 def test_draw_can_select_another_physical_securitybot(self):
  g=self.game();m=self.play(g);p=g.players[0];c=Card(g._new_id(),'YOG_510');p.deck=[c];self.kill(g,m)
  self.assertEqual(p.hand,[c]);self.assertEqual((g._card_stat(c,'attack',0),g._card_stat(c,'health',0)),(5,5))
 def test_generated_only_excluded_from_standard_decks(self):
  self.assertIn('YOG_510',cards.TOKEN_IDS&cards.PLAYABLE_TOKENS);self.assertNotIn('YOG_510',cards.COLLECTIBLE_IDS)

 def test_draw_listener_copies_original_snapshot_before_stat_replacement(self):
  g=self.game();m=self.play(g);p=g.players[0];q=g.players[1];g._summon(1,'CORE_SCH_717')
  c=Card(g._new_id(),'CORE_EX1_162');c.attack_bonus=3;c.health_bonus=4;p.deck=[c];self.kill(g,m)
  self.assertEqual(len(q.hand),1);copy=q.hand[0]
  self.assertEqual((copy.attack_bonus,copy.health_bonus),(3,4));self.assertEqual(g._cost(copy,1),1)
  self.assertEqual((g._card_stat(c,'attack',0),g._card_stat(c,'health',0),g._cost(c,0)),(5,5,5))

 def test_stat_replacement_removes_negative_modifiers_and_keeps_intrinsic_base(self):
  for stats in ((-20,-20),(20,20)):
   g=self.game();m=self.play(g);p=g.players[0];c=Card(g._new_id(),'CORE_EX1_162')
   c.attack_bonus,c.health_bonus=stats;c.base_stat_override=(8,9);p.deck=[c];self.kill(g,m)
   self.assertEqual((g._card_stat(c,'attack',0),g._card_stat(c,'health',0)),(5,5))
   self.assertEqual(c.base_stat_override,(8,9))
