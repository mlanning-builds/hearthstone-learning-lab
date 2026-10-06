import unittest,gzip,json
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch
import test_expanded_generation as fixtures
from expanded import cards,quest_families as rules,Action
from expanded.features import SCHEMA
from engine.game import Card

class EquilibriumTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with gzip.open(Path(__file__).resolve().parents[1]/'data/standard/all_cards.json.gz','rt') as f:cls.records={c['id']:c for c in json.load(f)}
 def setUp(self):
  self.fx=fixtures.GenerationTests();self.g=self.fx.game();self.p,self.q=self.g.players
  self.g.cards.update({cid:deepcopy(c) for cid,c in self.records.items() if cid.startswith('TLC_817')})
  extra={}
  for school in ('HOLY','SHADOW','FIRE'):
   cid='TEST_QUEST_'+school;self.g.cards[cid]=dict(self.g.cards['CORE_CS2_029'],id=cid,cost=0,spellSchool=school,text='Gain 1 Armor.',mechanics=[]);extra[cid]=('none',[('armor',1)])
  for table,values in ((cards.RULES,{**rules.RULES,**rules.TOKEN_RULES,**extra}),(cards.DEATH_EFFECTS,rules.DEATH_EFFECTS)):
   p=patch.dict(table,values);p.start();self.addCleanup(p.stop)
 def play(self,cid):
  self.p.mana=10;c=self.g._add(0,cid);self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid));return c
 def school(self,school,count=1):
  for _ in range(count):self.play('TEST_QUEST_'+school)
 def start(self):self.play(rules.ROOT)
 def test_root_starts_independent_objectives(self):
  self.start();self.assertEqual(self.p.quest['total'],8);self.assertEqual(self.g._quest_slots(0),2);self.assertEqual(self.p.quests_played,1)
 def test_holy_reward_arrives_before_shadow_completion(self):
  self.start();self.school('HOLY',4);self.assertEqual([c.card_id for c in self.p.hand],[rules.HALVES[0]]);self.assertEqual(self.p.quest['progress'],4);self.assertEqual(self.g._quest_slots(0),1)
 def test_shadow_can_complete_first(self):
  self.start();self.school('SHADOW',4);self.assertEqual([c.card_id for c in self.p.hand],[rules.HALVES[1]]);self.assertEqual(self.p.quest['objective']['children'][0]['progress'],0)
 def test_both_rewards_combine_and_release_quest(self):
  self.start();self.school('HOLY',4);self.school('SHADOW',4);self.assertIsNone(self.p.quest);self.assertEqual([c.card_id for c in self.p.hand],[rules.COMBINED])
 def test_more_same_school_does_not_repeat_reward(self):
  self.start();self.school('HOLY',6);self.assertEqual([c.card_id for c in self.p.hand],[rules.HALVES[0]]);self.assertEqual(self.p.quest['progress'],4)
 def test_wrong_school_has_no_progress(self):
  self.start();self.school('FIRE',3);self.assertEqual(self.p.quest['progress'],0)
 def test_opponent_spells_do_not_progress(self):
  self.start();self.g._queue_event('spell_cast',owner=1,card_id='TEST_QUEST_HOLY');self.g._settle();self.assertEqual(self.p.quest['progress'],0)
 def test_no_retroactive_progress(self):
  self.school('HOLY',4);self.start();self.assertEqual(self.p.quest['progress'],0)
 def test_first_completed_branch_does_not_allow_new_quest(self):
  self.start();self.school('HOLY',4);c=self.g._add(0,'TLC_433');self.assertFalse(any(a.kind=='play' and a.source==c.uid for a in self.g.legal_actions()))
 def test_two_subquests_consume_two_shared_secret_slots(self):
  self.start()
  for cid in ('CORE_EX1_287','CORE_EX1_289','CORE_EX1_610'):self.g._place_secret(0,cid)
  self.assertIsNone(self.g._place_secret(0,'CORE_EX1_611')); self.assertEqual(len(self.p.secrets),3)
 def test_completing_one_branch_releases_one_secret_slot(self):
  self.start()
  for cid in ('CORE_EX1_287','CORE_EX1_289','CORE_EX1_610'):self.g._place_secret(0,cid)
  self.school('HOLY',4);self.assertIsNotNone(self.g._place_secret(0,'CORE_EX1_611'))
 def test_four_secrets_only_leave_space_for_first_subquest(self):
  for cid in ('CORE_EX1_287','CORE_EX1_289','CORE_EX1_610','CORE_EX1_611'):self.g._place_secret(0,cid)
  self.start();self.assertEqual(self.p.quest['equilibrium_branches'],[0]);self.assertEqual(self.g._quest_slots(0),1)
 def test_full_secret_zone_disallows_root(self):
  for cid in ('CORE_EX1_287','CORE_EX1_289','CORE_EX1_610','CORE_EX1_611','CORE_GIL_577'):self.g._place_secret(0,cid)
  c=self.g._add(0,rules.ROOT);self.assertFalse(any(a.kind=='play' and a.source==c.uid for a in self.g.legal_actions()))
 def test_subquest_token_starts_only_its_own_school(self):
  self.play(rules.SUBQUESTS[1]);self.school('HOLY',4);self.assertEqual(self.p.quest['progress'],0);self.school('SHADOW',4);self.assertIsNone(self.p.quest);self.assertEqual(self.p.hand[0].card_id,rules.HALVES[1])
 def test_full_hand_reward_waits_without_burning(self):
  self.start();self.school('HOLY',3)
  for _ in range(10):self.g._add(0,'CORE_CS2_029')
  self.g._queue_event('spell_cast',owner=0,card_id='TEST_QUEST_HOLY');self.g._settle();self.assertEqual(self.p.quest['rewards_delivered'],[])
  self.p.hand.pop();self.g._settle();self.assertEqual(self.p.hand[-1].card_id,rules.HALVES[0]);self.assertEqual(self.p.quest['rewards_delivered'],[0])
 def test_lifes_breath_battlecry_copies_buffed_source(self):
  c=self.g._add(0,rules.HALVES[0]);c.attack_bonus=2;c.health_bonus=3;self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid));self.assertEqual([(m.attack,m.health) for m in self.p.minions],[(6,7),(6,7)])
 def test_combined_battlecry_copies(self):
  self.play(rules.COMBINED);self.assertEqual(len(self.p.minions),2);self.assertTrue(all(m.attack==8 and 'REBORN' in m.keywords for m in self.p.minions))
 def test_deaths_touch_deathrattle_and_reborn(self):
  m=self.g._summon(0,rules.HALVES[1]);m.health=0;self.g._settle();self.assertEqual(self.q.health,25);self.assertEqual(len(self.p.minions),1);self.assertEqual(self.p.minions[0].health,1)
 def test_silence_removes_deathrattle_and_reborn(self):
  m=self.g._summon(0,rules.HALVES[1]);self.g._silence(m);m.health=0;self.g._settle();self.assertEqual(self.q.health,30);self.assertFalse(self.p.minions)
 def test_combination_creates_fresh_printed_card(self):
  c=self.g._add(0,rules.HALVES[0]);c.attack_bonus=8;c.cost_delta=-2;self.g._add(0,rules.HALVES[1]);self.g._settle();combined=self.p.hand[0];self.assertEqual(combined.card_id,rules.COMBINED);self.assertEqual(combined.attack_bonus,0);self.assertEqual(getattr(combined,'cost_delta',0),0)
 def test_duplicate_halves_combine_one_pair_at_a_time(self):
  for cid in (rules.HALVES[0],rules.HALVES[0],rules.HALVES[1]):self.g._add(0,cid)
  self.g._settle();self.assertEqual([c.card_id for c in self.p.hand],[rules.COMBINED,rules.HALVES[0]])
 def test_opposing_halves_do_not_combine(self):
  self.g._add(0,rules.HALVES[0]);self.g._add(1,rules.HALVES[1]);self.g._settle();self.assertEqual(self.p.hand[0].card_id,rules.HALVES[0]);self.assertEqual(self.q.hand[0].card_id,rules.HALVES[1])
 def test_objectives_public_but_opponent_hand_private(self):
  self.start();self.school('HOLY',2);view=self.g.observe(1);self.assertEqual(view['players'][0]['quest']['objective']['children'][0]['progress'],2);self.assertNotIn('hand',view['players'][0]);self.assertEqual(SCHEMA,'visible-action-features-v58')
 def test_root_remains_staged(self):self.assertNotIn(rules.ROOT,cards.COLLECTIBLE_IDS)
 def test_repeated_spell_effect_counts_as_one_player_cast(self):
  self.start();self.p.spell_repeat_charges=1;self.school('HOLY');self.assertEqual(self.p.quest['progress'],1);self.assertEqual(self.p.armor,2)
 def test_internal_cast_does_not_count_as_player_cast(self):
  self.start();self.fx.run_ops(self.g,[('cast_fixed_spell','TEST_QUEST_HOLY','random')]);self.assertEqual(self.p.armor,1);self.assertEqual(self.p.quest['progress'],0)
 def test_countered_spell_does_not_progress(self):
  self.start();self.g._place_secret(1,'CORE_EX1_287');self.school('HOLY');self.assertEqual(self.p.quest['progress'],0)
 def test_full_board_keeps_played_reward_without_copy(self):
  for _ in range(6):self.g._summon(0,'NEW1_034')
  self.play(rules.HALVES[0]);self.assertEqual(len(self.p.board),7);self.assertEqual(sum(m.card_id==rules.HALVES[0] for m in self.p.minions),1)
 def test_both_pending_rewards_deliver_once_as_space_appears(self):
  self.start()
  for _ in range(10):self.g._add(0,'CORE_CS2_029')
  for school in ('HOLY','SHADOW'):
   for _ in range(4):self.g._queue_event('spell_cast',owner=0,card_id='TEST_QUEST_'+school)
  self.g._settle();self.assertEqual(self.p.quest['progress'],8)
  self.p.hand.pop(0);self.g._settle();self.assertEqual(self.p.quest['rewards_delivered'],[0]);self.assertEqual(len(self.p.hand),10)
  self.p.hand.pop(0);self.g._settle();self.assertIsNone(self.p.quest);self.assertEqual(sum(c.card_id==rules.COMBINED for c in self.p.hand),1);self.assertEqual(len(self.p.hand),9)
 def test_combined_deathrattle_does_not_replay_battlecry_on_reborn(self):
  m=self.g._summon(0,rules.COMBINED);m.health=0;self.g._settle();self.assertEqual(self.q.health,25);self.assertEqual(len(self.p.minions),1);self.assertEqual(self.p.minions[0].health,1)
 def test_starting_root_gets_opening_hand_priority(self):
  c=Card(self.g._new_id(),rules.ROOT);self.p.deck=[Card(self.g._new_id(),'CORE_CS2_029') for _ in range(10)]+[c];self.g._quest_opening_hand(0);self.assertIn(c,self.p.hand)
