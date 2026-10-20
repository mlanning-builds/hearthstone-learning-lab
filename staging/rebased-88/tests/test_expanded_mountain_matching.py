import unittest,itertools,copy
from expanded.quest_families import maximum_tribe_matching
from test_expanded_ashalon import AshalonTests
from expanded import Action
from expanded.adapt import ADAPTATIONS,PLANT

class MountainMatchingTests(unittest.TestCase):
 setUp=AshalonTests.setUp
 play=AshalonTests.play
 tribe=AshalonTests.tribe
 def test_prior_dual_type_reassigns_to_missing_type(self):
  self.play('TLC_229');self.tribe('BEAST','DRAGON');self.tribe('BEAST');self.assertEqual(self.p.quest['progress'],2)
 def test_prior_assignments_reassign_through_chain(self):
  self.play('TLC_229');self.tribe('BEAST','DRAGON');self.tribe('DRAGON','MURLOC');self.tribe('BEAST')
  self.assertEqual(self.p.quest['progress'],3);self.assertEqual(set(self.p.quest['seen']),{'BEAST','DRAGON','MURLOC'})
 def test_same_type_cannot_count_for_two_cards(self):
  self.play('TLC_229');self.tribe('BEAST','DRAGON');self.tribe('BEAST');self.tribe('DRAGON');self.assertEqual(self.p.quest['progress'],2)
 def test_assignment_does_not_consume_rng(self):
  self.play('TLC_229');rng=self.g.rng.getstate();self.tribe('BEAST','DRAGON');self.tribe('BEAST');self.assertEqual(self.g.rng.getstate(),rng)
 def test_all_can_fill_later_missing_type(self):
  self.play('TLC_229');self.tribe('ALL')
  for t in ('BEAST','DEMON','DRAGON','MURLOC','PIRATE'):self.tribe(t)
  self.assertIsNone(self.p.quest)
 def test_deferred_reward_progress_stays_complete(self):
  self.play('TLC_229')
  for _ in range(10):self.g._add(0,'TOKEN_COIN')
  for t in ('BEAST','DEMON','DRAGON','MURLOC','PIRATE','TOTEM','UNDEAD'):self.tribe(t)
  self.assertEqual(self.p.quest['progress'],6)
  self.p.hand.pop();self.g._quest_deliver_ready(0)
  self.assertIsNone(self.p.quest);self.assertEqual(self.p.hand[-1].card_id,'TLC_229t14')
 def test_snapshot_does_not_follow_later_metadata_mutation(self):
  self.play('TLC_229');self.tribe('BEAST','DRAGON');self.g.cards['TEST_TRIBES']['races']=['MURLOC'];self.tribe('BEAST')
  self.assertEqual(set(self.p.quest['seen']),{'BEAST','DRAGON'})
 def test_cloned_progress_is_independent(self):
  self.play('TLC_229');self.tribe('BEAST','DRAGON');clone=copy.deepcopy(self.g)
  clone.players[0].quest['played_types'].append(('DEMON',))
  self.assertEqual(len(self.p.quest['played_types']),1)
 def test_matching_agrees_with_exhaustive_assignment_oracle(self):
  types=('BEAST','DRAGON','MURLOC')
  subsets=[tuple(t for i,t in enumerate(types) if mask&(1<<i)) for mask in range(1,8)]
  for plays in itertools.product(subsets,repeat=3):
   expected=max(len(set(x)-{None}) for x in itertools.product(*(p+(None,) for p in plays)) if len([t for t in x if t is not None])==len(set(x)-{None}))
   self.assertEqual(len(maximum_tribe_matching(plays)),expected,plays)
 def test_two_stat_grants_stack_on_played_minion(self):
  self.p.ashalon_adaptations=['UNG_999t3','UNG_999t3'];self.play('CORE_EX1_162')
  self.assertEqual(self.p.minions[0].attack,self.g.cards['CORE_EX1_162']['attack']+6)
 def test_spores_grants_stack_independent_deathrattles(self):
  self.p.ashalon_adaptations=['UNG_999t2','UNG_999t2'];self.play('CORE_EX1_162');self.p.minions[0].health=0;self.g._settle()
  self.assertEqual([m.card_id for m in self.p.minions],[PLANT]*4)
 def test_granted_stealth_expires_on_next_owner_start(self):
  self.p.ashalon_adaptations=['UNG_999t10'];self.play('CORE_EX1_162');m=self.p.minions[0]
  self.assertIn('STEALTH',self.g._effective_keywords(m))
  self.g.step(Action('end'));self.assertIn('STEALTH',self.g._effective_keywords(m))
  self.g.step(Action('end'));self.assertNotIn('STEALTH',self.g._effective_keywords(m))
 def test_dormant_entry_grants_survive_awakening(self):
  self.p.ashalon_adaptations=['UNG_999t3','UNG_999t4','UNG_999t8','UNG_999t2']
  m=self.g._summon(0,'CORE_EX1_162',dormant_turns=2,entry_origin='play')
  self.assertEqual((m.attack,m.max_health),(self.g.cards[m.card_id]['attack']+3,self.g.cards[m.card_id]['health']+3))
  self.assertIn('DIVINE_SHIELD',m.keywords);self.assertEqual(len(m.attached_death_effects),1)
  self.g._awaken(m);self.assertIn('DIVINE_SHIELD',self.g._effective_keywords(m))
 def test_regular_adapt_cannot_target_dormant_board_minion(self):
  from expanded.adapt import apply_adaptation
  m=self.g._summon(0,'CORE_EX1_162',dormant_turns=2);before=(m.attack,m.max_health)
  self.assertFalse(apply_adaptation(self.g,m,'UNG_999t3'));self.assertEqual((m.attack,m.max_health),before)
