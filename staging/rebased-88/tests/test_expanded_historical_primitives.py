import unittest
import test_expanded_generation as fixtures
from expanded import cards,Action
from expanded.historical_generation import validate_past_candidates
BATCH_IDS=frozenset('AT_001 BAR_745 BT_235 CFM_021 CFM_065 CS2_025 CS2_057 CS2_117 DRG_226 EX1_019 EX1_195 EX1_313 ICC_058 ICC_094 ICC_802 LOOT_291 OG_083 SCH_535 TRL_526 TRL_546 ULD_714 UNG_817 WON_341'.split())
class HistoricalPrimitiveBatchTests(unittest.TestCase):
 def game(self):
  g=fixtures.GenerationTests().game()
  for p in g.players:p.mana_capacity=p.mana=p.max_mana=10;p.overload_next=p.locked_mana=0
  g._summon(0,'CS2_182');g._summon(1,'CS2_182');return g
 def play(self,g,cid,target=0):
  c=g._add(0,cid);cost=g._cost(c,0)
  g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid and a.target==target))
  self.assertEqual(g.players[0].last_paid_cost,cost)
 def test_all_reviewed_bodies_have_paid_play_paths(self):
  for cid in sorted(BATCH_IDS):
   with self.subTest(cid=cid):
    g=self.game();c=g._add(0,cid);g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid));g.assert_invariants()
 def test_historical_canonical_identities_stay_outside_standard(self):
  self.assertTrue(BATCH_IDS<=cards.TOKEN_IDS&cards.PLAYABLE_TOKENS)
  self.assertFalse(BATCH_IDS&cards.COLLECTIBLE_IDS)
  validate_past_candidates(BATCH_IDS,cards.registry())
 def test_self_damage_respects_printed_amount(self):
  for cid,damage in [('BAR_745',3),('EX1_313',5),('TRL_546',5)]:
   g=self.game();self.play(g,cid);self.assertEqual(g.players[0].health,30-damage)
 def test_targeted_healing_uses_printed_amount(self):
  for cid,amount in [('CS2_117',3),('DRG_226',8),('LOOT_291',4)]:
   g=self.game();g.players[0].health=10;self.play(g,cid,-1);self.assertEqual(g.players[0].health,10+amount)
 def test_minion_buffs_use_printed_amount(self):
  for cid,delta in [('EX1_019',(1,1)),('EX1_195',(0,2)),('ICC_094',(1,1))]:
   g=self.game();m=g.players[0].minions[0];a,h=m.attack,m.max_health;self.play(g,cid,m.uid)
   self.assertEqual((m.attack-a,m.max_health-h),delta)
 def test_enemy_freeze_does_not_damage(self):
  for cid in ('CFM_021','ICC_058'):
   g=self.game();m=g.players[1].minions[0];h=m.health;self.play(g,cid,m.uid)
   self.assertEqual(m.health,h);self.assertGreaterEqual(m.frozen_until,g.turn)
 def test_spells_gain_spell_damage_but_battlecry_does_not(self):
  g=self.game();g._summon(0,'CORE_EX1_012');m=g.players[1].minions[0];self.play(g,'CS2_057',m.uid)
  self.assertNotIn(m,g.players[1].board)
  g=self.game();g._summon(0,'CORE_EX1_012');m=g.players[1].minions[0];self.play(g,'OG_083');self.assertEqual(m.health,4)
 def test_flame_lance_printed_twenty_five_kills_large_target(self):
  for cid in ('AT_001','WON_341'):
   g=self.game();m=g.players[1].minions[0];g._buff(m,0,19);self.play(g,cid,m.uid);self.assertNotIn(m,g.players[1].board)
 def test_area_damage_and_lifesteal_cross_both_boards(self):
  for cid,amount,heal in [('BT_235',4,0),('CFM_065',2,0),('ICC_802',1,2),('SCH_535',3,6)]:
   g=self.game();g.players[0].health=10;self.play(g,cid)
   self.assertEqual([p.minions[0].health for p in g.players],[5-amount]*2)
   self.assertEqual(g.players[0].health,10+heal)
 def test_lifesteal_targeted_damage_uses_school_and_modifiers(self):
  for cid,amount in [('ULD_714',3),('UNG_817',5)]:
   g=self.game();g.players[0].health=10;m=g.players[1].minions[0];g._buff(m,0,3);g._summon(0,'CORE_EX1_012');self.play(g,cid,m.uid)
   self.assertEqual(m.health,8-amount-1);self.assertEqual(g.players[0].health,11+amount)
 def test_scorcher_excludes_own_body_but_hits_existing_friends(self):
  g=self.game();friend=g.players[0].minions[0];self.play(g,'TRL_526');self.assertEqual(friend.health,4)
  self.assertEqual(g.players[1].minions[0].health,4);self.assertEqual(next(m for m in g.players[0].minions if m.card_id=='TRL_526').health,6)
 def test_enemy_area_leaves_friendly_board_untouched(self):
  g=self.game();self.play(g,'CS2_025');self.assertEqual(g.players[0].minions[0].health,5);self.assertEqual(g.players[1].minions[0].health,4)
if __name__=='__main__':unittest.main()
