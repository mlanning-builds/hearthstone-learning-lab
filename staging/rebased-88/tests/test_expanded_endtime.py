import unittest,gzip,json
from pathlib import Path
from unittest.mock import patch
import test_expanded_generation as fixtures
from expanded import cards,quest_families
class EndTimeTests(unittest.TestCase):
 def setUp(self):
  self.g=fixtures.GenerationTests().game();self.p,self.q=self.g.players
  with gzip.open(Path(__file__).resolve().parents[1]/'data/standard/all_cards.json.gz','rt') as f:
   self.g.cards.update({c['id']:c for c in json.load(f) if c['id'] in ('END_017','END_017t')})
  for table,values in ((cards.RULES,{**quest_families.RULES,**quest_families.TOKEN_RULES}),(cards.DEATH_EFFECTS,quest_families.DEATH_EFFECTS)):
   p=patch.dict(table,values);p.start();self.addCleanup(p.stop)
 def play(self,cid):
  self.p.mana=10;c=self.g._add(0,cid);self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid))
 def start_full(self):
  self.play('END_017')
  for _ in range(10):self.g._add(0,'CORE_CS2_029')
 def test_full_advances_first_stage(self):
  self.start_full();self.assertEqual(self.p.quest['progress'],1)
 def test_empty_without_prior_full_does_not_complete(self):
  self.play('END_017');self.g._settle();self.assertEqual(self.p.quest['progress'],0)
 def test_discard_batch_awards_once(self):
  self.start_full();self.g._discard_cards(0,list(self.p.hand));self.g._settle()
  self.assertIsNone(self.p.quest);self.assertEqual([c.card_id for c in self.p.hand],['END_017t'])
 def test_empty_and_refill_captures_transient_state(self):
  self.start_full();self.p._starting_hand=[]
  from engine.game import Card
  self.p._starting_hand=[Card(self.g._new_id(),'CORE_CS2_029')]
  self.g._effect(('stored_starting_hand',),dict(owner=0,source=None,target=0,bonus=0,lifesteal=False))
  self.assertIsNone(self.p.quest);self.assertIn('END_017t',[c.card_id for c in self.p.hand])
 def test_shuffle_final_card_completes(self):
  self.start_full()
  while self.p.hand:self.g._shuffle_hand_card(0,self.p.hand[-1]);break
  self.assertEqual(self.p.quest['progress'],1)
  for c in list(self.p.hand):self.g._shuffle_hand_card(0,c)
  self.assertIsNone(self.p.quest);self.assertEqual(self.p.hand[0].card_id,'END_017t')
 def test_reward_draws_to_full(self):
  self.play('END_017t');self.assertEqual(len(self.p.hand),10)
 def test_deathrattle_empties_opponent_only(self):
  self.play('END_017t');self.g._add(1,'CORE_CS2_029');self.p.minions[0].health=0;self.g._settle()
  self.assertEqual(self.q.hand,[]);self.assertEqual(len(self.p.hand),10)
 def test_silence_removes_deathrattle(self):
  self.play('END_017t');self.g._add(1,'CORE_CS2_029');self.g._silence(self.p.minions[0]);self.p.minions[0].health=0;self.g._settle();self.assertEqual(len(self.q.hand),1)
 def test_opponent_empty_does_not_advance_owner(self):
  self.start_full();self.g._settle();self.assertEqual(self.p.quest['progress'],1)
 def test_public_progress_no_private_hand(self):
  self.start_full();v=self.g.observe(1)['players'][0];self.assertEqual(v['quest']['progress'],1);self.assertNotIn('hand',v)
