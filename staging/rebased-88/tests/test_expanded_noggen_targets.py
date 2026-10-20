import gzip,json,unittest
from unittest.mock import patch
import test_expanded_generation as fixtures
from expanded import Action

class NoggenTargetTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with gzip.open('data/standard/all_cards.json.gz','rt') as f:cls.record=next(r for r in json.load(f) if r['id']=='CORE_CFM_670')
 def setUp(self):
  self.g=fixtures.GenerationTests().game();self.p,self.q=self.g.players
  self.g.cards['CORE_CFM_670']=self.record
  self.mayor=self.g._summon(0,'CORE_CFM_670')
 def chosen(self,callback):
  with patch.object(self.g.rng,'choice',side_effect=lambda values:values[0]) as choose:
   result=callback();self.assertEqual(choose.call_count,1)
   return result,list(choose.call_args.args[0])
 def action(self,cid,target):
  c=self.g._add(0,cid);return Action('play',source=c.uid,target=target)
 def test_attacks_never_include_friendly_characters(self):
  friendly=self.g._summon(0,'CS2_182');enemy=self.g._summon(1,'CS2_182')
  _,targets=self.chosen(lambda:self.g._random_attack_target(friendly.uid,self.g.hero_id(1)))
  self.assertEqual(set(targets),{self.g.hero_id(1),enemy.uid})
  self.assertNotIn(self.mayor.uid,targets);self.assertNotIn(self.g.hero_id(0),targets)
 def test_off_turn_attacker_uses_its_controller(self):
  enemy=self.g._summon(1,'CS2_182')
  _,targets=self.chosen(lambda:self.g._random_attack_target(enemy.uid,self.g.hero_id(0)))
  self.assertEqual(set(targets),{self.g.hero_id(0),self.mayor.uid})
 def test_hero_attacker_uses_its_controller(self):
  _,targets=self.chosen(lambda:self.g._random_attack_target(self.g.hero_id(1),self.g.hero_id(0)))
  self.assertEqual(set(targets),{self.g.hero_id(0),self.mayor.uid})
 def test_enemy_only_spell_stays_on_enemy_minions(self):
  self.g._summon(0,'CS2_182');enemy=self.g._summon(1,'CS2_182')
  _,targets=self.chosen(lambda:self.g._random_action_target(self.action('CORE_CS2_076',enemy.uid)))
  self.assertEqual(targets,[enemy.uid])
 def test_friendly_only_battlecry_stays_on_friendly_minions(self):
  friend=self.g._summon(0,'CS2_182');self.g._summon(1,'CS2_182')
  _,targets=self.chosen(lambda:self.g._random_action_target(self.action('CORE_ULD_191',friend.uid)))
  self.assertEqual(set(targets),{self.mayor.uid,friend.uid})
 def test_enemy_character_spell_excludes_friendly_characters(self):
  friend=self.g._summon(0,'CS2_182');enemy=self.g._summon(1,'CS2_182')
  _,targets=self.chosen(lambda:self.g._random_action_target(self.action('END_014',enemy.uid)))
  self.assertEqual(set(targets),{enemy.uid,self.g.hero_id(1)})
  self.assertNotIn(friend.uid,targets)
 def test_large_minion_restriction_is_preserved(self):
  big=self.g._summon(1,'CS2_182');self.g._buff(big,10,0);self.g._summon(1,'CS2_182')
  _,targets=self.chosen(lambda:self.g._random_action_target(self.action('CORE_EX1_005',big.uid)))
  self.assertEqual(targets,[big.uid])
 def test_damaged_minion_restriction_is_preserved(self):
  damaged=self.g._summon(1,'CS2_182');damaged.health-=1;self.g._summon(1,'CS2_182')
  _,targets=self.chosen(lambda:self.g._random_action_target(self.action('CATA_585',damaged.uid)))
  self.assertEqual(targets,[damaged.uid])
 def test_shaman_replacement_power_remains_friendly(self):
  self.g._imbue(0);self.p.hero_class='SHAMAN';self.g._imbue(0)
  friend=self.g._summon(0,'CS2_182');self.g._summon(1,'CS2_182')
  _,targets=self.chosen(lambda:self.g._random_action_target(Action('power',target=friend.uid)))
  self.assertEqual(set(targets),{self.mayor.uid,friend.uid})
 def test_elusive_minion_remains_illegal_for_a_targeted_spell(self):
  enemy=self.g._summon(1,'CS2_182');hidden=self.g._summon(1,'CS2_182');hidden.keywords.add('ELUSIVE')
  _,targets=self.chosen(lambda:self.g._random_action_target(self.action('CORE_CS2_076',enemy.uid)))
  self.assertEqual(targets,[enemy.uid])
 def test_targetless_action_does_not_consume_randomness(self):
  before=self.g.rng.getstate();action=Action('end')
  self.assertEqual(self.g._random_action_target(action),action);self.assertEqual(self.g.rng.getstate(),before)
 def test_silenced_mayor_does_not_redirect(self):
  self.g._silence(self.mayor);action=self.action('CORE_CS2_029',self.g.hero_id(1));before=self.g.rng.getstate()
  self.assertEqual(self.g._random_action_target(action),action);self.assertEqual(self.g.rng.getstate(),before)
