"""Weapon outcomes: lifecycle effects retain the physical equipped instance."""
from copy import deepcopy
import unittest
from expanded import Game,Action,random_deck
from engine.game import Card
from expanded.generation_cards import pool
from expanded.historical_generation_catalog import load_universe,historical_contract
from standard.catalog import CLASSES

class HistoricalPoolWeaponTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  g=Game([random_deck('PALADIN',31),random_deck('MAGE',53)],seed=71,record=True)
  g.step(Action('mulligan'));g.step(Action('mulligan'))
  for p in g.players:
   p.hand=[];p.board=[];p.deck=[];p.mana=p.max_mana=10;p.health=30;p.armor=0
  cls.prototype=g
 def game(self):return deepcopy(self.prototype)
 def play(self,g,cid):
  c=g._add(0,cid);g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid));return c
 def test_whack_full_twenty_seven_weapon_pool_all_classes(self):
  u=load_universe();r=pool(era='past',card_type='WEAPON',classes='PALADIN')
  for cls in CLASSES:
   g=self.game();g.players[0].hero_class=cls
   ids=g._generation_candidates(r,0)
   self.assertEqual(len(ids),27);self.assertEqual(set(ids),set(historical_contract(r,cls,u).card_ids))
 def test_sword_of_justice_buffs_summon_and_consumes_durability(self):
  g=self.game();g._equip(0,'EX1_366');before=g.players[0].weapon['durability'];m=g._summon(0,'CS2_182')
  self.assertEqual((m.attack,m.health),(5,6));self.assertEqual(g.players[0].weapon['durability'],before-1)
 def test_silver_sword_last_swing_still_buffs(self):
  g=self.game();m=g._summon(0,'CS2_182');g._equip(0,'GIL_596');g.players[0].weapon['durability']=1
  g.step(next(a for a in g.legal_actions() if a.kind=='attack' and a.source==g.hero_id(0) and a.target==g.hero_id(1)))
  self.assertIsNone(g.players[0].weapon);self.assertEqual((m.attack,m.health),(5,6))
 def test_libram_discount_battlecry_and_deathrattle(self):
  g=self.game();self.play(g,'GDB_726');self.assertEqual(g.players[0].historical_libram_discount,1)
  g._break_weapon(0);g._settle();self.assertEqual(g.players[0].historical_libram_discount,2)
 def test_maul_identifies_in_hand_and_preserves_bonus(self):
  g=self.game();c=Card(g._new_id(),'LOOT_286',attack_bonus=1,health_bonus=1);g._enter_hand(0,c)
  self.assertIn(c.card_id,tuple('LOOT_286t'+str(i) for i in range(1,5)))
  self.assertEqual((c.attack_bonus,c.health_bonus),(1,1))
 def test_valanyr_buff_then_death_reequips(self):
  g=self.game();c=g._add(0,'CS2_182');g._equip(0,'LOOT_500');g._break_weapon(0);g._settle()
  self.assertEqual((c.attack_bonus,c.health_bonus),(4,2))
  g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid))
  m=g.players[0].minions[0];self.assertEqual((m.attack,m.health),(8,7));m.health=0;g._settle()
  self.assertEqual(g.players[0].weapon['card_id'],'LOOT_500')
 def test_cavalry_horn_uses_lowest_cost_and_removes_physical_card(self):
  g=self.game();a=g._add(0,'CS2_182');b=g._add(0,'CS2_231');g._equip(0,'AV_341');g._break_weapon(0);g._settle()
  self.assertIn(a,g.players[0].hand);self.assertNotIn(b,g.players[0].hand);self.assertEqual(g.players[0].minions[0].card_id,'CS2_231')
 def test_lightbringers_hammer_cannot_attack_heroes(self):
  g=self.game();g._equip(0,'SW_314');g._summon(1,'CS2_182')
  targets={a.target for a in g.legal_actions() if a.kind=='attack' and a.source==g.hero_id(0)}
  self.assertTrue(targets);self.assertTrue(all(uid>0 for uid in targets))
 def test_prismatic_kit_hand_buff_and_wear(self):
  g=self.game();c=g._add(0,'CS2_182');m=g._summon(0,'CS2_182');m.keywords.add('DIVINE_SHIELD');g._equip(0,'SW_048')
  before=g.players[0].weapon['durability'];g._damage(m.uid,1);g._settle()
  self.assertEqual((c.attack_bonus,c.health_bonus),(1,1));self.assertEqual(g.players[0].weapon['durability'],before-1)
 def test_lights_sorrow_grows_without_wear(self):
  g=self.game();m=g._summon(0,'CS2_182');m.keywords.add('DIVINE_SHIELD');g._equip(0,'ICC_071')
  before=dict(g.players[0].weapon);g._damage(m.uid,1);g._settle()
  self.assertEqual(g.players[0].weapon['attack'],before['attack']+1);self.assertEqual(g.players[0].weapon['durability'],before['durability'])
 def test_ceremonial_maul_triggers_once_after_spell(self):
  g=self.game();g._equip(0,'SCH_523');self.play(g,'CS2_023');ms=[m for m in g.players[0].minions if m.card_id=='SCH_523t']
  self.assertEqual([(m.attack,m.health) for m in ms],[(3,3)])
  self.play(g,'CS2_023');self.assertEqual(sum(m.card_id=='SCH_523t' for m in g.players[0].minions),1)
 def test_seedcloud_buckler_death_grants_shields(self):
  g=self.game();m=g._summon(0,'CS2_182');g._equip(0,'WC_032');g._break_weapon(0);g._settle()
  self.assertIn('DIVINE_SHIELD',g._effective_keywords(m))
 def test_bloodclaw_battlecry_self_damage(self):
  g=self.game();self.play(g,'TRL_543');self.assertEqual(g.players[0].health,25)
 def test_argent_lance_joust_wins_extra_durability(self):
  g=self.game();g.players[0].deck=[Card(g._new_id(),'CS2_182')];g.players[1].deck=[Card(g._new_id(),'CS2_231')]
  self.play(g,'AT_077');self.assertEqual(g.players[0].weapon['durability'],3)
 def test_whack_generates_modified_weapon_with_full_membership(self):
  g=self.game();self.play(g,'MIS_700');self.assertIsNotNone(g.pending_choice)
  g.step(next(a for a in g.legal_actions() if a.kind=='choose'));c=g.players[0].hand[0]
  self.assertEqual((c.attack_bonus,c.health_bonus),(1,1))

 def test_student_physical_base_stats_and_cost_survive_bounce(self):
  g=self.game();g._equip(0,'SCH_523');self.play(g,'CS2_023');m=next(m for m in g.players[0].minions if m.card_id=='SCH_523t')
  self.assertEqual(g._card_stat(m,'cost',0),3);g._bounce(m)
  c=next(c for c in g.players[0].hand if c.card_id=='SCH_523t')
  self.assertEqual((g._card_stat(c,'attack',0),g._card_stat(c,'health',0),g._cost(c,0)),(3,3,3))
 def test_volley_maul_generates_executable_sunscreen(self):
  g=self.game();g._equip(0,'VAC_921');g.step(next(a for a in g.legal_actions() if a.kind=='attack' and a.source==g.hero_id(0) and a.target==g.hero_id(1)))
  c=g.players[0].hand[0];self.assertEqual((c.card_id,g._cost(c,0)),('VAC_917t',1))
  m=g._summon(0,'CS2_182');g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid and a.target==m.uid))
  self.assertEqual((m.attack,m.health),(5,7))
