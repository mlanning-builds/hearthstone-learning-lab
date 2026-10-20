"""Exercise historical triggers with physical damage/casts/attacks, no training."""
import gzip,json,unittest
from pathlib import Path
from unittest.mock import patch
import test_expanded_generation as fixtures
from expanded import Action,cards
from expanded.historical_triggers import RULES,TRIGGERS,TOKEN_RULES

class HistoricalTriggerTests(unittest.TestCase):
 def setUp(self):
  self.g=fixtures.GenerationTests().game();self.p,self.q=self.g.players
  records={c['id']:c for c in json.load(gzip.open(Path('data/standard/all_cards.json.gz'),'rt'))}
  self.g.cards.update({cid:records[cid] for cid in set(RULES)|set(TOKEN_RULES)})
  for table,values in ((cards.RULES,RULES|TOKEN_RULES),(cards.TRIGGERS,TRIGGERS)):
   manager=patch.dict(table,values);manager.start();self.addCleanup(manager.stop)
 def summon(self,cid,owner=0):return self.g._summon(owner,cid)
 def damage(self,m,n=1):self.g._damage(m.uid,n);self.g._settle()
 def cast(self,owner=0,cost=1):
  self.g._queue_event('spell_cast',owner=owner,card_id='CORE_CS2_029',cost=cost,targeted_minion=False);self.g._settle()
 def test_damage_draws_once_even_lethal(self):
  for cid in ('EX1_007','WON_357'):
   with self.subTest(cid=cid):
    m=self.summon(cid);before=len(self.p.hand);self.damage(m,30);self.assertEqual(len(self.p.hand),before+1)
 def test_zero_damage_and_shield_do_not_trigger(self):
  m=self.summon('BOT_059');m.keywords.add('DIVINE_SHIELD');self.damage(m);self.assertEqual(self.p.armor,0)
  self.damage(m,0);self.assertEqual(self.p.armor,0);self.damage(m);self.assertEqual(self.p.armor,2)
 def test_damage_buffs_and_cross_owner_frothing(self):
  a=self.summon('EX1_399');f=self.summon('EX1_604');base=f.attack;self.damage(a)
  self.assertEqual(a.attack,5);self.assertEqual(f.attack,base+1)
  enemy=self.summon('CORE_CS2_188',1);self.damage(enemy);self.assertEqual(f.attack,base+2)
 def test_enemy_spell_does_not_buff_and_silence_stops_listener(self):
  m=self.summon('CFM_060');base=m.attack;self.cast(1);self.assertEqual(m.attack,base)
  self.cast();self.assertEqual(m.attack,base+2);self.g._silence(m);base=m.attack;self.cast();self.assertEqual(m.attack,base)
 def test_health_buff_and_full_growth(self):
  a=self.summon('KAR_036');b=self.summon('EX1_187');ah=a.health;ba,bh=b.attack,b.health
  self.cast();self.assertEqual(a.health,ah+1);self.assertEqual((b.attack,b.health),(ba+2,bh+2))
 def test_friendly_spell_heal_draw_refresh_and_fireball(self):
  for cid in ('EX1_095','KAR_035','CFM_807','EX1_559'):self.summon(cid)
  self.p.health=20;self.p.power_used=True;before=len(self.p.hand);self.cast()
  self.assertEqual(self.p.health,23);self.assertFalse(self.p.power_used);self.assertEqual(len(self.p.hand),before+2)
  self.assertIn('CS2_029',[c.card_id for c in self.p.hand])
 def test_damage_spawns_intrinsic_body_tokens(self):
  for cid,token in (('BRM_006','BRM_006t'),('BRM_022','BRM_022t')):
   m=self.summon(cid);self.damage(m);self.assertIn(token,[x.card_id for x in self.p.minions])
 def test_spell_summon_tokens_have_intrinsic_keywords(self):
  for cid in ('NEW1_026','TRL_131','BAR_035'):self.summon(cid)
  self.cast();bodies={m.card_id:m for m in self.p.minions}
  self.assertIn('NEW1_026t',bodies);self.assertIn('TAUNT',bodies['TRL_131t'].keywords);self.assertIn('RUSH',bodies['BAR_035t'].keywords)
 def test_hero_damage_and_board_attack_buff(self):
  a=self.summon('BRM_016');b=self.summon('UNG_087');self.damage(a);self.assertEqual(self.q.health,28)
  self.damage(b);self.assertEqual(self.p.health,27)
  c=self.summon('AV_129');before=a.attack;self.damage(c);self.assertEqual(a.attack,before+1)
 def test_pyromancer_damage_both_boards_and_trainee_enemy_only(self):
  a=self.summon('NEW1_020');b=self.summon('NX2_002');e=self.summon('CORE_EX1_012',1);ah,bh,eh=a.health,b.health,e.health
  self.cast();self.assertEqual((a.health,b.health),(ah-1,bh-1));self.assertNotIn(e,self.q.minions)
 def test_random_missiles_keep_minion_spell_damage_out(self):
  self.summon('BRM_002');self.summon('CORE_EX1_012');before=self.q.health;self.cast();self.assertEqual(self.q.health,before-2)
 def test_after_attack_destroy_and_freeze(self):
  for cid in ('UNG_079','RLK_117'):
   m=self.summon(cid);m.summoned_turn=0;self.g.turn=3
   self.g._queue_event('minion_attack',owner=0,source=m.uid,target=-2);self.g._settle()
   if cid=='UNG_079':self.assertGreaterEqual(m.frozen_until,3)
   else:self.assertNotIn(m,self.p.minions)
 def test_missing_trigger_visual_does_not_remove_explicit_rule(self):
  m=self.summon('NEW1_012');self.g.cards['NEW1_012']=dict(self.g.cards['NEW1_012'],mechanics=[])
  before=m.attack;self.cast();self.assertEqual(m.attack,before+1)

 def test_haleh_four_missiles_do_not_inherit_spell_damage(self):
  self.summon('ONY_007');self.summon('CORE_EX1_012');before=self.q.health;self.cast();self.assertEqual(self.q.health,before-4)
 def test_dart_frog_only_damages_enemy_minions(self):
  self.summon('DAL_182');enemy=self.summon('CORE_CS2_188',1);before=enemy.health;hero=self.q.health
  self.cast();self.assertEqual(enemy.health,before-1);self.assertEqual(self.q.health,hero)
 def test_quartermaster_buffs_one_physical_minion_not_spells(self):
  self.summon('AV_401');a=self.g._add(0,'CORE_CS2_188');spell=self.g._add(0,'CORE_CS2_029')
  self.cast();self.assertEqual((a.attack_bonus,a.health_bonus),(1,1));self.assertEqual((spell.attack_bonus,spell.health_bonus),(0,0))
 def test_piper_buffs_beasts_only_on_own_attack(self):
  m=self.summon('SW_459');beast=self.summon('CORE_EX1_162');other=self.summon('CORE_CS2_188')
  before=(beast.attack,beast.health,other.attack,other.health)
  self.g._queue_event('minion_attack',owner=0,source=other.uid,target=-2);self.g._settle()
  self.assertEqual((beast.attack,beast.health,other.attack,other.health),before)
  self.g._queue_event('minion_attack',owner=0,source=m.uid,target=-2);self.g._settle()
  self.assertEqual((beast.attack,beast.health),(before[0]+1,before[1]+1));self.assertEqual((other.attack,other.health),before[2:])
