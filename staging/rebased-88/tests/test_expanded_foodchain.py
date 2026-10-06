import unittest,json,gzip
from pathlib import Path
from unittest.mock import patch
import test_expanded_generation as fixtures
from expanded import cards,quest_families,Action
from engine.cards import UnsupportedCard
class FoodChainTests(unittest.TestCase):
 def setUp(self):
  self.fx=fixtures.GenerationTests();self.g=self.fx.game();self.p,self.q=self.g.players
  with gzip.open(Path(__file__).resolve().parents[1]/'data/standard/all_cards.json.gz','rt') as f:self.g.cards.update({c['id']:c for c in json.load(f) if c['id'] in ('TLC_830','TLC_830t')})
  rules={**quest_families.RULES,**quest_families.TOKEN_RULES}
  for n in range(1,9):
   cid='TEST_BEAST_'+str(n);self.g.cards[cid]=dict(id=cid,name=cid,type='MINION',cost=0,attack=n,health=5,races=['BEAST'],cardClass='NEUTRAL',dbfId=990000+n);rules[cid]=('none',[])
  p=patch.dict(cards.RULES,rules);p.start();self.addCleanup(p.stop)
  for r in quest_families.SHOKK_POOLS:self.fx.install(self.g,r,['TEST_BEAST_'+str(r.attack_minimum)])
 def play(self,cid,bonus=0):
  self.p.mana=10;c=self.g._add(0,cid);c.attack_bonus=bonus;self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid))
 def test_distinct_attacks_any_order(self):
  self.play('TLC_830')
  for n in (7,1,5,3):self.play('TEST_BEAST_'+str(n))
  self.assertIsNone(self.p.quest);self.assertEqual(self.p.hand[0].card_id,'TLC_830t')
 def test_duplicate_does_not_advance_twice(self):
  self.play('TLC_830');self.play('TEST_BEAST_1');self.play('TEST_BEAST_1');self.assertEqual(self.p.quest['progress'],1)
 def test_summon_does_not_count_as_play(self):
  self.play('TLC_830');self.g._summon(0,'TEST_BEAST_1');self.assertEqual(self.p.quest['progress'],0)
 def test_even_attack_ignored(self):
  self.play('TLC_830');self.play('TEST_BEAST_2');self.assertEqual(self.p.quest['progress'],0)
 def test_hand_buff_counts_modified_attack(self):
  self.play('TLC_830');self.play('TEST_BEAST_2',1);self.assertEqual(self.p.quest['seen'],[3])
 def test_non_beast_ignored(self):
  self.play('TLC_830');self.g.cards['TEST_BEAST_1']['races']=[];self.play('TEST_BEAST_1');self.assertEqual(self.p.quest['progress'],0)
 def test_reward_sequential_choices_and_cost(self):
  self.play('TLC_830t')
  for n in (8,6,4):
   self.assertEqual(self.g.pending_choice['options'][0]['card_id'],'TEST_BEAST_'+str(n));self.g.step(Action('choose',choices=(0,)))
  self.assertIsNone(self.g.pending_choice);self.assertEqual([c.card_id for c in self.p.hand],['TEST_BEAST_8','TEST_BEAST_6','TEST_BEAST_4']);self.assertTrue(all(c.cost_delta==2 for c in self.p.hand))
 def test_missing_later_pool_rejects_before_first_choice(self):
  del self.g._generation_pools[(quest_families.SHOKK_POOLS[-1],self.p.hero_class)]
  with self.assertRaises(UnsupportedCard):self.play('TLC_830t')
  self.assertIsNone(self.g.pending_choice)
 def test_root_still_staged(self):
  self.assertNotIn('TLC_830',cards.COLLECTIBLE_IDS)
