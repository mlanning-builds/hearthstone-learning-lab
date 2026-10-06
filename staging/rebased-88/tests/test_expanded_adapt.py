import unittest,gzip,json
from pathlib import Path
import test_expanded_generation as fixtures
from expanded.adapt import ADAPTATIONS,PLANT,apply_adaptation
from engine.cards import UnsupportedCard
class AdaptTests(unittest.TestCase):
 def setUp(self):
  self.g=fixtures.GenerationTests().game();self.m=self.g._summon(0,'CORE_EX1_162')
  with gzip.open(Path(__file__).resolve().parents[1]/'data/standard/all_cards.json.gz','rt') as f:self.g.cards.update({c['id']:c for c in json.load(f) if c['id']==PLANT})
 def test_ten_constructed_options(self):self.assertEqual(len(ADAPTATIONS),10);self.assertTrue(all(k.startswith('UNG_999') for k in ADAPTATIONS))
 def test_stats_stack(self):
  attack=self.m.attack;apply_adaptation(self.g,self.m,'UNG_999t3');apply_adaptation(self.g,self.m,'UNG_999t3');self.assertEqual(self.m.attack,attack+6)
 def test_health_grants_current_and_max(self):
  health=self.m.health;apply_adaptation(self.g,self.m,'UNG_999t4');self.assertEqual(self.m.health,health+3);self.assertEqual(self.m.max_health,health+3)
 def test_shield_can_be_restored_after_consumption(self):
  apply_adaptation(self.g,self.m,'UNG_999t8');self.g._damage(self.m.uid,1);apply_adaptation(self.g,self.m,'UNG_999t8');self.assertIn('DIVINE_SHIELD',self.m.keywords)
 def test_spores_summons_two_plants(self):
  apply_adaptation(self.g,self.m,'UNG_999t2');self.m.health=0;self.g._settle();self.assertEqual([m.card_id for m in self.g.players[0].minions],[PLANT,PLANT])
 def test_silence_removes_spores(self):
  apply_adaptation(self.g,self.m,'UNG_999t2');self.g._silence(self.m);self.m.health=0;self.g._settle();self.assertEqual(self.g.players[0].minions,[])
 def test_missing_plant_rejects_before_attachment(self):
  del self.g.cards[PLANT]
  with self.assertRaises(UnsupportedCard):apply_adaptation(self.g,self.m,'UNG_999t2')
  self.assertEqual(self.m.attached_death_effects,[])
 def test_stealth_expires_next_owner_start(self):
  apply_adaptation(self.g,self.m,'UNG_999t10');self.assertEqual(self.m.temporary_keywords[-1]['turn'],self.g.turn+2)
  self.g.current=1;apply_adaptation(self.g,self.m,'UNG_999t10');self.assertEqual(self.m.temporary_keywords[-1]['turn'],self.g.turn+1)
 def test_invalid_choice_rejected(self):
  with self.assertRaises(UnsupportedCard):apply_adaptation(self.g,self.m,'LETL_271e')
 def test_dead_target_not_modified(self):
  self.m.health=0;before=self.m.attack;self.assertFalse(apply_adaptation(self.g,self.m,'UNG_999t3'));self.assertEqual(self.m.attack,before)
