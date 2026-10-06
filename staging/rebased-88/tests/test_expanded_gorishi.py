import unittest,gzip,json
from pathlib import Path
from unittest.mock import patch
import test_expanded_generation as fixtures
from expanded import cards,quest_families,Action
class GorishiTests(unittest.TestCase):
 def setUp(self):
  self.g=fixtures.GenerationTests().game();self.p,self.q=self.g.players
  with gzip.open(Path(__file__).resolve().parents[1]/'data/standard/all_cards.json.gz','rt') as f:
   self.g.cards.update({c['id']:c for c in json.load(f) if c['id'] in ('TLC_631','TLC_631t')})
  p=patch.dict(cards.RULES,{**quest_families.RULES,**quest_families.TOKEN_RULES});p.start();self.addCleanup(p.stop)
 def play(self,cid):
  self.p.mana=10;c=self.g._add(0,cid);self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid))
 def hit(self,owner=0,target=-2,amount=2):
  self.g._deal_effect(target,amount,dict(owner=owner,source=None,bonus=0,lifesteal=False));self.g._settle()
 def test_twelve_events_award_reward(self):
  self.play('TLC_631');self.q.health=100
  for _ in range(12):self.hit()
  self.assertIsNone(self.p.quest);self.assertEqual(self.p.hand[-1].card_id,'TLC_631t')
 def test_wrong_amount_does_not_progress(self):
  self.play('TLC_631');self.hit(amount=3);self.assertEqual(self.p.quest['progress'],0)
 def test_friendly_damage_does_not_progress(self):
  self.play('TLC_631');self.hit(target=-1);self.assertEqual(self.p.quest['progress'],0)
 def test_opponent_turn_does_not_progress(self):
  self.play('TLC_631');self.g.current=1;self.hit();self.assertEqual(self.p.quest['progress'],0)
 def test_opponent_source_does_not_progress(self):
  self.play('TLC_631');self.hit(owner=1,target=-1);self.assertEqual(self.p.quest['progress'],0)
 def test_reward_triggers_on_opponent_turn(self):
  self.play('TLC_631t');self.g.current=1;self.hit();self.assertEqual(self.q.health,26)
 def test_reward_does_not_recurse(self):
  self.play('TLC_631t');self.hit();self.assertEqual(self.q.health,26);self.assertFalse(self.g._rule_events)
 def test_two_rewards_stack_linearly(self):
  self.play('TLC_631t');self.play('TLC_631t');self.hit();self.assertEqual(self.q.health,24)
 def test_reward_persists_after_silence(self):
  self.play('TLC_631t');self.g._silence(self.p.minions[0]);self.hit();self.assertEqual(self.q.health,26)
 def test_full_hand_waits(self):
  self.play('TLC_631');self.q.health=100
  for _ in range(10):self.g._add(0,'CORE_CS2_029')
  for _ in range(12):self.hit()
  self.assertEqual(self.p.quest['progress'],12);self.p.hand.pop();self.g._settle();self.assertIsNone(self.p.quest)
 def test_shield_prevents_progress_and_reward(self):
  self.play('TLC_631');self.play('TLC_631t');self.q.divine_shield=True;self.hit();self.assertEqual(self.p.quest['progress'],0);self.assertEqual(self.q.health,30)
 def test_public_reward_count(self):
  self.play('TLC_631t');self.assertEqual(self.g.observe(1)['players'][0]['gorishi_stacks'],1)
