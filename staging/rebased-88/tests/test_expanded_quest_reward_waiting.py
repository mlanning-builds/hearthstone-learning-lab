import unittest
import test_expanded_quests as fixtures
from expanded import Action

class WaitingQuestRewardTests(unittest.TestCase):
 def setUp(self):
  self.fx=fixtures.QuestTests();self.g=self.fx.game();self.p=self.g.players[0]
  self.fx.start(self.g)
  for _ in range(10):self.g._add(0,'CORE_CS2_029')
  self.p.corpses=30;self.g._spend_corpses(0,15)
 def test_full_hand_waits_across_checkpoints(self):
  for _ in range(4):self.g._settle();self.g._refresh_auras()
  self.assertEqual(len(self.p.hand),10);self.assertEqual(self.p.quest['progress'],15)
 def test_additional_progress_does_not_duplicate_reward(self):
  self.g._spend_corpses(0,15);self.p.hand.pop();self.g._settle();self.g._settle();self.assertEqual(sum(c.card_id=='TLC_433t' for c in self.p.hand),1);self.assertIsNone(self.p.quest)
 def test_play_opens_slot_and_delivers_reward(self):
  c=self.p.hand[0];self.g.step(Action('play',source=c.uid,target=-2));self.assertEqual(len(self.p.hand),10);self.assertEqual(self.p.hand[-1].card_id,'TLC_433t');self.assertIsNone(self.p.quest)
 def test_discard_opens_slot_without_discarding_new_reward(self):
  before=list(self.p.hand);self.g._discard_cards(0,before);self.g._settle();self.assertEqual([c.card_id for c in self.p.hand],['TLC_433t']);self.assertEqual(len(self.p.discard_history),10)
 def test_draw_does_not_falsely_report_receiving_card_when_reward_fills_slot(self):
  self.p.hand.pop();result=self.g._draw(0);self.assertIsNone(result);self.assertEqual(len(self.p.hand),10);self.assertEqual(self.p.hand[-1].card_id,'TLC_433t')
 def test_generation_respects_waiting_reward_capacity(self):
  self.p.hand.pop();result=self.g._add(0,'CORE_CS2_029');self.assertIsNone(result);self.assertEqual(self.p.hand[-1].card_id,'TLC_433t');self.assertEqual(len(self.p.hand),10)
 def test_other_players_space_does_not_release_owners_reward(self):
  self.g._add(1,'CORE_CS2_029');self.g._settle();self.assertIsNotNone(self.p.quest);self.assertFalse(any(c.card_id=='TLC_433t' for c in self.g.players[1].hand))
 def test_reward_survives_turn_boundary(self):
  self.g.step(Action('end'));self.assertIsNotNone(self.p.quest);self.p.hand.pop();self.g._settle();self.assertIsNone(self.p.quest);self.assertEqual(self.p.hand[-1].card_id,'TLC_433t')
 def test_completed_waiting_state_is_public(self):
  view=self.g.observe(1);self.assertEqual(view['players'][0]['quest']['progress'],15);self.assertNotIn('hand',view['players'][0])
 def test_illegal_action_does_not_release_or_destroy_reward(self):
  with self.assertRaises(ValueError):self.g.step(Action('play',source=999999))
  self.assertEqual(self.p.quest['progress'],15);self.assertEqual(len(self.p.hand),10)

 def test_direct_hand_entry_cannot_overwrite_waiting_reward(self):
  self.p.hand.pop();result=self.g._enter_hand(0,'CORE_CS2_029');self.assertIsNone(result);self.assertEqual(self.p.hand[-1].card_id,'TLC_433t');self.assertEqual(len(self.p.hand),10)
 def test_reward_works_with_event_recording_disabled(self):
  self.g.record=False;self.p.hand.pop();self.g._settle();self.assertIsNone(self.p.quest);self.assertEqual(self.p.hand[-1].card_id,'TLC_433t')
