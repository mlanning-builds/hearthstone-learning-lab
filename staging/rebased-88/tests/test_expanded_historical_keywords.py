"""Paid historical primitives with keyword and zone interactions."""
import unittest
import test_expanded_generation as fixtures
from expanded import Action

class HistoricalKeywordTests(unittest.TestCase):
 def game(self):
  g=fixtures.GenerationTests().game()
  for p in g.players:p.health=30;p.armor=0;p.mana=p.max_mana=10
  g._summon(0,'CS2_182');g._summon(1,'CS2_182');return g
 def play(self,g,cid,target=0):
  g.players[0].mana=10;c=g._add(0,cid)
  g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid and a.target==target))
 def test_stat_and_keyword_buffs_apply_to_selected_enemy_too(self):
  for cid,a,h,keywords in [('AT_074',3,0,{'DIVINE_SHIELD'}),('BT_257',2,3,{'LIFESTEAL'}),('CS2_087',3,0,set()),('ULD_143',4,4,{'DIVINE_SHIELD','TAUNT'})]:
   g=self.game();m=g.players[1].minions[0];before=(m.attack,m.max_health);self.play(g,cid,m.uid)
   self.assertEqual((m.attack,m.max_health),(before[0]+a,before[1]+h));self.assertTrue(keywords<=g._effective_keywords(m))
 def test_board_buffs_affect_friends_only(self):
  for cid,a,h in [('BAR_534',1,3),('CFM_614',1,1)]:
   g=self.game();m=g.players[0].minions[0];before=(m.attack,m.max_health);enemy=g.players[1].minions[0];self.play(g,cid)
   self.assertEqual((m.attack,m.max_health),(before[0]+a,before[1]+h));self.assertEqual((enemy.attack,enemy.max_health),(4,5))
 def test_hand_buff_does_not_buff_spells_or_deck(self):
  g=self.game();m=g._add(0,'CS2_182');spell=g._add(0,'TOKEN_COIN');self.play(g,'CFM_305')
  self.assertEqual((m.attack_bonus,m.health_bonus),(1,1));self.assertEqual((spell.attack_bonus,spell.health_bonus),(0,0))
  self.assertEqual(g.players[0].minions[0].max_health,5)
 def test_hero_attack_expires_at_end_of_owner_turn(self):
  for cid,amount in [('BT_512',8),('CS2_105',4),('TRL_243',2)]:
   g=self.game();self.play(g,cid);self.assertEqual(g.players[0].temporary_attack,amount)
   g.step(Action('end'));self.assertEqual(g.players[0].temporary_attack,0)
 def test_enemy_hero_damage_and_own_healing(self):
  for cid,amount in [('CS2_075',3),('DS1_233',5)]:
   g=self.game();self.play(g,cid);self.assertEqual(g.players[1].health,30-amount);self.assertEqual(g.players[0].health,30)
  for cid,amount in [('CS2_089',8),('EX1_192',5)]:
   g=self.game();g.players[0].health=10;self.play(g,cid);self.assertEqual(g.players[0].health,10+amount)
 def test_all_character_damage_includes_both_heroes_and_boards(self):
  for cid,amount in [('CFM_094',5),('DRG_206',1)]:
   g=self.game();self.play(g,cid);self.assertEqual([p.health for p in g.players],[30-amount]*2)
   self.assertEqual([len(p.minions) for p in g.players],[0,0] if amount==5 else [1,1])
 def test_board_divine_shield_blocks_one_hit_and_silence_clears_grant(self):
  g=self.game();m=g.players[0].minions[0];enemy=g.players[1].minions[0];self.play(g,'EX1_184')
  self.assertNotIn('DIVINE_SHIELD',g._effective_keywords(enemy));g._damage(m.uid,2);self.assertEqual(m.health,5)
  self.play(g,'EX1_184');g._silence(m);self.assertNotIn('DIVINE_SHIELD',g._effective_keywords(m))
 def test_windfury_allows_second_attack(self):
  g=self.game();m=g.players[0].minions[0];m.summoned_turn=-1;self.play(g,'CS2_039',m.uid)
  for _ in range(2):g.step(next(a for a in g.legal_actions() if a.kind=='attack' and a.source==m.uid and a.target==g.hero_id(1)))
  self.assertFalse(any(a.kind=='attack' and a.source==m.uid for a in g.legal_actions()));self.assertEqual(g.players[1].health,22)
 def test_reborn_grant_resummons_at_one_health_once(self):
  g=self.game();m=g.players[0].minions[0];self.play(g,'ULD_265',m.uid);m.health=0;g._settle()
  m=g.players[0].minions[0];self.assertEqual(m.health,1);self.assertNotIn('REBORN',g._effective_keywords(m))
  m.health=0;g._settle();self.assertFalse(g.players[0].minions)
 def test_cryostasis_buffs_before_freezing(self):
  g=self.game();m=g.players[1].minions[0];self.play(g,'ICC_056',m.uid)
  self.assertEqual((m.attack,m.max_health),(7,8));self.assertGreaterEqual(m.frozen_until,g.turn)
 def test_shipment_requires_weapon_and_changes_both_dimensions(self):
  g=self.game();c=g._add(0,'WORK_005');self.assertFalse(any(a.kind=='play' and a.source==c.uid for a in g.legal_actions()))
  g._equip(0,'CS2_082');before=dict(g.players[0].weapon)
  g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid))
  self.assertEqual(g.players[0].weapon['attack'],before['attack']+2);self.assertEqual(g.players[0].weapon['durability'],before['durability']+2)
  self.assertEqual((g.players[0].equipped_card.attack_bonus,g.players[0].equipped_card.health_bonus),(2,2))

if __name__=='__main__':unittest.main()
