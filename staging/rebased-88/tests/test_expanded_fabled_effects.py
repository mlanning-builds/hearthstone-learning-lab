import unittest,gzip,json
from pathlib import Path
from copy import deepcopy
from unittest.mock import patch
import test_expanded_generation as fixtures
from expanded import cards, fabled_effects as rules, Action
from engine.game import Card
from engine.cards import UnsupportedCard
from expanded.pools import GenerationPool

class FabledEffectTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with gzip.open(Path(__file__).resolve().parents[1]/'data/standard/all_cards.json.gz','rt') as f:cls.records={c['id']:c for c in json.load(f)}
 def setUp(self):
  self.g=fixtures.GenerationTests().game();self.p,self.q=self.g.players
  self.g.cards.update({cid:deepcopy(self.records[cid]) for cid in (*rules.RULES,*rules.TOKEN_RULES)})
  for table,values in ((cards.RULES,{**rules.RULES,**rules.TOKEN_RULES}),(cards.DEATH_EFFECTS,rules.DEATH_EFFECTS)):
   p=patch.dict(table,values);p.start();self.addCleanup(p.stop)
 def run_ops(self,ops,**kw):
  ctx=dict(owner=0,source=None,target=0,bonus=0,lifesteal=False);ctx.update(kw)
  self.g._start_play_effects(ops,ctx);self.g._settle(allow_event_choices=True)
 def sister(self,cid):self.run_ops([('fabled_sisters',cid)])
 def history(self,*ids):self.p.played_history=[dict(card_id=cid,cost=0) for cid in ids]
 def test_sylvanas_base_hits_enemy_hero_and_minions_only(self):
  own=self.g._summon(0,'NEW1_034');enemy=self.g._summon(1,'NEW1_034');self.sister('TIME_609')
  self.assertEqual(self.q.health,28);self.assertEqual(self.p.health,30);self.assertEqual(own.health,2);self.assertEqual(enemy.health,0)
 def test_distinct_other_sisters_cap_repetitions_at_three(self):
  self.history(*rules.SISTERS,*rules.SISTERS);self.sister('TIME_609');self.assertEqual(self.q.health,24)
 def test_own_replays_and_opponent_history_do_not_count(self):
  self.history('TIME_609','TIME_609');self.q.played_history=[dict(card_id='TIME_609t1',cost=0)]
  self.sister('TIME_609');self.assertEqual(self.q.health,28)
 def test_vereesa_buffs_only_deck_minions_for_each_distinct_sister(self):
  self.history('TIME_609','TIME_609t1');minion=Card(self.g._new_id(),'NEW1_034');spell=Card(self.g._new_id(),'CORE_CS2_029');self.p.deck=[minion,spell];self.g._add(0,'NEW1_034')
  self.sister('TIME_609t2');self.assertEqual((minion.attack_bonus,minion.health_bonus),(3,3));self.assertEqual(spell.attack_bonus,0);self.assertEqual(self.p.hand[0].attack_bonus,0)
 def test_alleria_three_distinct_choices_resume_in_order(self):
  self.history('TIME_609','TIME_609t2');self.g._generation_pools={(rules.SPELLS,self.p.hero_class):GenerationPool('fixture',('CORE_CS2_029',),'controlled')}
  self.sister('TIME_609t1')
  for index in range(3):
   self.assertIsNotNone(self.g.pending_choice);self.assertEqual(len(self.p.hand),index)
   self.g.step(next(a for a in self.g.legal_actions() if a.kind=='choose'))
  self.assertIsNone(self.g.pending_choice);self.assertEqual(len(self.p.hand),3)
 def test_missing_discover_pool_fails_closed(self):
  with self.assertRaises(UnsupportedCard):self.sister('TIME_609t1')
 def test_broll_recruits_real_hand_card_buffs_and_grants_taunt(self):
  c=self.g._add(0,'TIME_850t1');c.attack_bonus=2;c.health_bonus=1;self.run_ops(rules.DEATH_EFFECTS['TIME_850t'])
  m=self.p.minions[0];self.assertEqual(m.card_id,c.card_id);self.assertNotIn(c,self.p.hand);self.assertIn('TAUNT',m.keywords)
  self.assertEqual(m.attack,self.records[c.card_id]['attack']+7);self.assertEqual(m.health,self.records[c.card_id]['health']+6)
 def test_valeera_grants_elusive(self):
  self.g._add(0,'TIME_850');self.run_ops(rules.DEATH_EFFECTS['TIME_850t1']);self.assertIn('ELUSIVE',self.p.minions[0].keywords)
 def test_logosh_forces_attack_after_buff(self):
  self.g._add(0,'TIME_850t');self.run_ops(rules.DEATH_EFFECTS['TIME_850']);self.assertEqual(self.q.health,30-self.records['TIME_850t']['attack']-5)
 def test_empty_hand_and_nonfighter_do_nothing(self):
  self.g._add(0,'NEW1_034');self.run_ops(rules.DEATH_EFFECTS['TIME_850']);self.assertFalse(self.p.board);self.assertEqual(len(self.p.hand),1)
 def test_full_board_does_not_consume_fighter(self):
  for _ in range(7):self.g._summon(0,'NEW1_034')
  c=self.g._add(0,'TIME_850');self.run_ops(rules.DEATH_EFFECTS['TIME_850t']);self.assertIn(c,self.p.hand)
 def test_actual_death_triggers_recruit(self):
  m=self.g._summon(0,'TIME_850t');self.g._add(0,'TIME_850t1');m.health=0;self.g._settle();self.assertEqual([m.card_id for m in self.p.minions],['TIME_850t1']);self.assertIn('TAUNT',self.p.minions[0].keywords)
 def test_silenced_fighter_does_not_recruit(self):
  m=self.g._summon(0,'TIME_850t');self.g._add(0,'TIME_850t1');self.g._silence(m);m.health=0;self.g._settle();self.assertFalse(self.p.minions)
 def test_identity_filter_validates_even_for_empty_zone(self):
  with self.assertRaises(ValueError):self.g._recruit_from_zone(0,'hand',(('id','in','TIME_850'),))
 def test_staging_does_not_admit_root(self):self.assertFalse((set(rules.RULES)-{'TIME_850'})&cards.COLLECTIBLE_IDS)
