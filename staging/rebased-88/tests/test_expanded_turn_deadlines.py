import unittest,gzip,json
from unittest.mock import patch
import test_expanded_generation as fixtures
from expanded import cards,turn_deadlines,Action
class TurnDeadlineTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with gzip.open('data/standard/all_cards.json.gz','rt') as f:cls.records={c['id']:c for c in json.load(f) if c['id'] in ('JAIL_860','TLC_602','TLC_602t')}
 def setUp(self):
  self.fx=fixtures.GenerationTests();self.g=self.fx.game();self.p,self.q=self.g.players;self.g.cards.update(self.records)
  c=patch.dict(cards.RULES,dict(turn_deadlines.RULES,**{'TLC_602t':('none',[])}));c.start();self.addCleanup(c.stop)
 def quest(self):self.fx.run_ops(self.g,[('lost_city_start',)])
 def test_lost_city_is_a_quest_but_chef_is_not(self):
  self.assertTrue(self.g._is_quest('TLC_602'));self.assertFalse(self.g._is_quest('JAIL_860'))
 def test_lost_city_starts_in_each_players_opening_hand(self):
  from engine.game import Card
  for owner,p in enumerate(self.g.players):
   p.hand=[];quest=Card(self.g._new_id(),'TLC_602')
   p.deck=[Card(self.g._new_id(),'CORE_CS2_029') for _ in range(5)]+[quest]
   self.g._quest_opening_hand(owner)
   self.assertIn(quest,p.hand);self.assertNotIn(quest,p.deck)
   self.assertEqual(len(p.hand),3 if owner==self.g.first_player else 4)
 def test_paid_lost_city_counts_as_quest_played(self):
  c=self.g._add(0,'TLC_602');before=self.p.quests_played
  self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid))
  self.assertEqual(self.p.quests_played,before+1);self.assertEqual(self.p.quest['card_id'],'TLC_602')
 def test_lost_city_cannot_replace_an_active_quest(self):
  self.quest();c=self.g._add(0,'TLC_602');uid=self.p.quest['uid']
  self.assertFalse(any(a.kind=='play' and a.source==c.uid for a in self.g.legal_actions()))
  self.assertEqual(self.p.quest['uid'],uid)
 def test_lost_city_cannot_use_a_sixth_secret_slot(self):
  self.p.secrets=['CORE_EX1_287']*5;c=self.g._add(0,'TLC_602')
  self.assertFalse(any(a.kind=='play' and a.source==c.uid for a in self.g.legal_actions()))
 def test_quest_progresses_on_own_end_only(self):
  self.quest();self.g.step(Action('end'));self.assertEqual(self.p.quest['progress'],1);self.g.step(Action('end'));self.assertEqual(self.p.quest['progress'],1)
 def test_quest_ignores_end_trigger_doubling(self):
  self.quest();self.p.end_repeat_expiries=[100];self.g.step(Action('end'));self.assertEqual(self.p.quest['progress'],1)
 def test_tenth_end_delivers_one_reward(self):
  self.quest()
  for _ in range(19):
   self.p.hand.clear();self.q.hand.clear();self.g.step(Action('end'))
  self.assertIsNone(self.p.quest);self.assertEqual(sum(c.card_id=='TLC_602t' for c in self.p.hand),1)
 def test_full_hand_completed_quest_waits(self):
  self.quest();self.p.quest['progress']=9
  for _ in range(10):self.g._add(0,'TOKEN_COIN')
  self.g.step(Action('end'));self.assertEqual(self.p.quest['progress'],10);self.p.hand.pop();self.g._quest_deliver_ready();self.assertIsNone(self.p.quest);self.assertEqual(self.p.hand[-1].card_id,'TLC_602t')
 def test_stale_tick_cannot_advance_replacement_quest(self):
  self.quest();old=self.p.quest['uid'];self.p.quest=None;self.quest();self.fx.run_ops(self.g,[('lost_city_tick',old,self.g.turn)]);self.assertEqual(self.p.quest['progress'],0)
 def test_same_turn_tick_cannot_repeat(self):
  self.quest();op=('lost_city_tick',self.p.quest['uid'],self.g.turn);self.fx.run_ops(self.g,[op,op]);self.assertEqual(self.p.quest['progress'],1)
 def test_chef_original_cost_condition(self):
  self.p.starting_deck=['JAIL_860','CORE_CS2_029'];self.g._deadline_start_game();self.assertFalse(self.p.scheduled_effects)
 def test_chef_schedules_fifth_owner_end(self):
  self.p.turns_taken=0;self.p.starting_deck=['JAIL_860','TOKEN_COIN'];self.g._deadline_start_game();entry=self.p.scheduled_effects[0];self.assertEqual((entry['due'],entry['phase'],entry['remaining']),(5,'end',1))
 def test_chef_runs_once_and_respects_locked_mana(self):
  self.p.locked_mana=2;self.fx.run_ops(self.g,[('chef_set_mana',)]);self.assertEqual((self.p.max_mana,self.p.mana),(10,8))
 def test_chef_end_five_gives_ten_on_turn_six(self):
  self.p.turns_taken=0;self.p.starting_deck=['JAIL_860'];self.g._deadline_start_game();self.p.turns_taken=5;self.p.max_mana=5
  self.g.step(Action('end'));self.assertEqual(self.p.max_mana,10);self.assertFalse(self.p.scheduled_effects);self.g.step(Action('end'));self.assertEqual(self.p.mana,10)
