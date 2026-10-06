import unittest,gzip,json
from pathlib import Path
from copy import deepcopy
from unittest.mock import patch
import test_expanded_generation as fixtures
from expanded import cards,fabled_effects as rules,Action
from expanded.locations import LOCATION_RULES
from engine.cards import UnsupportedCard
from engine.game import Card

class MedivhTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with gzip.open(Path(__file__).resolve().parents[1]/'data/standard/all_cards.json.gz','rt') as f:cls.records={c['id']:c for c in json.load(f)}
 def setUp(self):
  self.fx=fixtures.GenerationTests();self.g=self.fx.game();self.p,self.q=self.g.players
  self.g.cards.update({cid:deepcopy(c) for cid,c in self.records.items() if cid.startswith('TIME_890')})
  for table,values in ((cards.RULES,{**rules.RULES,**rules.TOKEN_RULES}),(LOCATION_RULES,rules.LOCATION_RULES)):
   p=patch.dict(table,values);p.start();self.addCleanup(p.stop)
  self.g.cards['TEST_EIGHT']=dict(self.g.cards['NEW1_034'],id='TEST_EIGHT',cost=8,attack=8,health=8)
  self.fx.install(self.g,rules.KARAZHAN_POOL,['TEST_EIGHT'])
 def run_ops(self,ops,**kw):self.fx.run_ops(self.g,ops,**kw)
 def play(self,cid,target=0):
  self.p.mana=10;c=self.g._add(0,cid);self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid and a.target==target));return c
 def cost(self,cid):return self.g._cost(Card(self.g._new_id(),cid),0)
 def staff(self):self.g._equip(0,'TIME_890t')
 def test_medivh_free_with_friendly_location_not_enemy(self):
  self.g._place_location(1,'TIME_890t2');self.assertEqual(self.cost('TIME_890'),10);self.g._place_location(0,'TIME_890t2');self.assertEqual(self.cost('TIME_890'),0)
 def test_staff_free_with_silenced_medivh(self):
  m=self.g._summon(0,'TIME_890');self.g._silence(m);self.assertEqual(self.cost('TIME_890t'),0);m.health=0;self.g._settle();self.assertEqual(self.cost('TIME_890t'),10)
 def test_location_free_while_staff_equipped(self):
  self.assertEqual(self.cost('TIME_890t2'),10);self.staff();self.assertEqual(self.cost('TIME_890t2'),0);self.g._break_weapon(0);self.assertEqual(self.cost('TIME_890t2'),10)
 def test_clear_silences_deathrattles_reborn_and_preserves_self_location(self):
  location=self.g._place_location(0,'TIME_890t2');a=self.g._summon(0,'NEW1_034');b=self.g._summon(1,'NEW1_034')
  for m in (a,b):m.attached_death_effects=[('summon','NEW1_034',1)];m.keywords.add('REBORN')
  self.play('TIME_890');self.assertEqual([m.card_id for m in self.p.minions],['TIME_890']);self.assertFalse(self.q.minions);self.assertIn(location,self.p.board);self.assertEqual(self.p.mana,10)
 def test_clear_ignores_dormant_minions(self):
  m=self.g._summon(1,'NEW1_034');m.dormant=2;self.play('TIME_890');self.assertIn(m,self.q.board);self.assertEqual(m.dormant,2)
 def test_spell_damage_includes_bonus_before_doubling(self):
  self.staff();self.run_ops([('damage',6)],target=-2,spell=True,bonus=1);self.assertEqual(self.q.health,16)
 def test_paid_fireball_uses_multiplier_once(self):
  self.staff();self.play('CORE_CS2_029',-2);self.assertEqual(self.q.health,18);self.assertEqual(self.p.mana,6)
 def test_internal_fireball_uses_multiplier(self):
  self.staff();self.run_ops([('cast_fixed_spell','CORE_CS2_029','selected')],target=-2);self.assertEqual(self.q.health,18);self.assertFalse(self.p.played_history)
 def test_opponent_and_nonspell_damage_not_doubled(self):
  self.staff();self.run_ops([('damage',3)],target=-2);self.run_ops([('damage',3)],owner=1,target=-1,spell=True);self.assertEqual(self.q.health,27);self.assertEqual(self.p.health,27)
 def test_weapon_break_removes_multiplier(self):
  self.staff();self.g._break_weapon(0);self.run_ops([('damage',3)],target=-2,spell=True);self.assertEqual(self.q.health,27)
 def test_spell_healing_doubles_after_permanent_bonus_not_spell_damage(self):
  self.staff();self.p.health=1;self.p.permanent_healing_bonus=1;self.run_ops([('heal',3)],target=-1,spell=True,bonus=7);self.assertEqual(self.p.health,9)
 def test_nonspell_healing_not_doubled(self):
  self.staff();self.p.health=1;self.run_ops([('heal',3)],target=-1);self.assertEqual(self.p.health,4)
 def test_area_heal_doubles_each_target(self):
  self.staff();self.p.health=1;m=self.g._summon(0,'TIME_890');m.health=1;self.run_ops([('area_heal',2)],spell=True);self.assertEqual(self.p.health,5);self.assertEqual(m.health,5)
 def test_unreviewed_spell_lifesteal_rejects_before_damage(self):
  self.staff();before=self.q.health
  with self.assertRaisesRegex(UnsupportedCard,'Atiesh spell Lifesteal'):self.run_ops([('damage',3)],target=-2,spell=True,lifesteal=True)
  self.assertEqual(self.q.health,before)
 def test_karazhan_summons_two_with_replacement(self):
  location=self.g._place_location(0,'TIME_890t2');self.g.step(Action('activate',source=location.uid));self.assertEqual([m.card_id for m in self.p.minions],['TEST_EIGHT']*2);self.assertEqual(location.durability,1)
 def test_karazhan_final_charge_frees_its_slot(self):
  location=self.g._place_location(0,'TIME_890t2');location.durability=1
  for _ in range(6):self.g._summon(0,'NEW1_034')
  self.g.step(Action('activate',source=location.uid));self.assertNotIn(location,self.p.board);self.assertEqual(len(self.p.board),7);self.assertEqual(sum(m.card_id=='TEST_EIGHT' for m in self.p.minions),1)
 def test_missing_pool_rolls_back_location_payment(self):
  location=self.g._place_location(0,'TIME_890t2');self.g._generation_pools.clear();before=deepcopy(self.g.observe(0))
  with self.assertRaises(UnsupportedCard):self.g.step(Action('activate',source=location.uid))
  self.assertEqual(self.g.observe(0),before)
 def test_source_remains_staged_and_pool_declared(self):
  self.assertNotIn('TIME_890',cards.COLLECTIBLE_IDS);self.assertEqual(rules.requests_for('TIME_890'),{rules.KARAZHAN_POOL})

 def test_split_damage_doubles_hit_count_not_each_hit(self):
  self.staff();self.g.events=[];self.run_ops([('missiles','enemies',3)],spell=True,bonus=1)
  hits=[e['amount'] for e in self.g.events if e['event']=='damage'];self.assertEqual(hits,[1]*8);self.assertEqual(self.q.health,22)
 def test_immediate_split_damage_uses_same_multiplier_rule(self):
  self.staff();self.g.events=[];self.g._effect(('missiles','enemies',3),dict(owner=0,source=None,target=0,spell=True,bonus=1,lifesteal=False))
  hits=[e['amount'] for e in self.g.events if e['event']=='damage'];self.assertEqual(hits,[1]*8)
 def test_nonspell_missiles_are_not_multiplied(self):
  self.staff();self.run_ops([('missiles','enemies',3)]);self.assertEqual(self.q.health,27)
