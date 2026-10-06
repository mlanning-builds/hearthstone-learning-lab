import unittest
import test_expanded_latorvius_rewards as rewards
from expanded import Action
class CrystalCoreTests(unittest.TestCase):
 setUp=rewards.LatorviusRewardTests.setUp
 play=rewards.LatorviusRewardTests.play
 def test_existing_minion_reset_clears_damage_and_old_buff(self):
  m=self.g._summon(0,'CORE_EX1_162');self.g._buff(m,3,3);m.health-=2;self.play('UNG_067t1');self.assertEqual((m.attack,m.health,m.max_health),(5,5,5))
 def test_future_minion_and_silence_remain_five(self):
  self.play('UNG_067t1');m=self.g._summon(0,'CORE_EX1_162');self.g._buff(m,2,2);self.g._silence(m);self.assertEqual((m.attack,m.max_health),(5,5))
 def test_later_stat_setting_overrides_until_silence(self):
  self.play('UNG_067t1');m=self.g._summon(0,'CORE_EX1_162');self.g._set_entity_stats(m,1,1);self.g._refresh_auras();self.assertEqual((m.attack,m.health),(1,1));self.g._silence(m);self.assertEqual((m.attack,m.health),(5,5))
 def test_future_buff_applies_above_new_base(self):
  self.play('UNG_067t1');m=self.g._summon(0,'CORE_EX1_162',attack_bonus=2,health_bonus=3);self.assertEqual((m.attack,m.health),(7,8))
 def test_opponent_minions_unchanged(self):
  m=self.g._summon(1,'CORE_EX1_162');before=(m.attack,m.health);self.play('UNG_067t1');self.assertEqual((m.attack,m.health),before)
 def test_copy_keeps_base_after_changing_owner(self):
  self.play('UNG_067t1');m=self.g._summon(0,'CORE_EX1_162');n=self.g._summon(1,m.card_id,copy_from=m);self.g._buff(n,2,2);self.g._silence(n);self.assertEqual((n.attack,n.max_health),(5,5))
 def test_hand_observation_and_play_agree(self):
  c=self.g._add(0,'CORE_EX1_162');self.play('UNG_067t1');self.assertEqual(self.g._card_stat(c,'attack',0),5);self.p.mana=10;self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid));self.assertEqual(self.p.minions[0].attack,5)
 def test_recast_resets_later_enchantments(self):
  self.play('UNG_067t1');m=self.g._summon(0,'CORE_EX1_162');self.g._buff(m,4,4);self.play('UNG_067t1');self.assertEqual((m.attack,m.health),(5,5))
