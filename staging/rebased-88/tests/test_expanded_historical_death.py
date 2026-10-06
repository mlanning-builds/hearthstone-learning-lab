import unittest
import test_expanded_generation as fixtures
from expanded import Action,cards
from expanded.historical_death import GENERATED_IDS
from expanded.historical_generation import validate_past_candidates

class HistoricalDeathTests(unittest.TestCase):
 def game(self):
  g=fixtures.GenerationTests().game()
  for p in g.players:
   p.mana_capacity=p.mana=p.max_mana=10;p.overload_next=p.locked_mana=0;p.hand=[];p.deck=['CS2_182']*20
  return g
 def paid(self,g,cid):
  c=g._add(0,cid);cost=g._cost(c,0)
  g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid))
  self.assertEqual(g.players[0].last_paid_cost,cost)
  return next(m for m in g.players[0].minions if m.card_id==cid)
 def kill(self,g,m):
  g._damage(m.uid,100);g._settle()
 def test_all_sixteen_paid_plays_and_deaths(self):
  self.assertEqual(len(GENERATED_IDS),16)
  for cid in sorted(GENERATED_IDS):
   with self.subTest(cid=cid):
    g=self.game();m=self.paid(g,cid);self.kill(g,m);g.assert_invariants()
 def test_registry_remains_generated_only(self):
  self.assertFalse(GENERATED_IDS&cards.COLLECTIBLE_IDS)
  self.assertTrue(GENERATED_IDS<=cards.TOKEN_IDS)
  validate_past_candidates(GENERATED_IDS,cards.registry())
 def test_enemy_hero_damage_and_silence(self):
  for cid,damage in [('BOT_031',2),('LEG_CS3_013',3),('TSC_001',4)]:
   for silence in (False,True):
    with self.subTest(cid=cid,silence=silence):
     g=self.game();m=self.paid(g,cid)
     if silence:g._silence(m)
     self.kill(g,m);self.assertEqual(g.players[1].health,30-(0 if silence else damage))
 def test_draw_count_and_empty_deck_fatigue(self):
  for cid,count in [('EX1_096',1),('TRL_525',2),('ULD_177',8)]:
   g=self.game();m=self.paid(g,cid);self.kill(g,m)
   self.assertEqual(len(g.players[0].hand),count);self.assertEqual(len(g.players[0].deck),20-count)
  g=self.game();m=self.paid(g,'TRL_525');g.players[0].deck=[];self.kill(g,m)
  self.assertEqual(g.players[0].health,27)
 def test_beetle_armor_and_spawn_surviving_board_buff(self):
  g=self.game();m=self.paid(g,'LOOT_413');self.kill(g,m);self.assertEqual(g.players[0].armor,3)
  g=self.game();other=g._summon(0,'CS2_182');a,h=other.attack,other.max_health;m=self.paid(g,'OG_256');self.kill(g,m)
  self.assertEqual((other.attack,other.max_health),(a+1,h+1))
 def test_area_deathrattle_damages_both_sides_without_spell_damage(self):
  for cid,amount in [('GVG_076',2),('OG_151',1),('OG_120',8)]:
   g=self.game();m=self.paid(g,cid);a=g._summon(0,'CS2_182');b=g._summon(1,'CS2_182')
   for target in (a,b):g._buff(target,0,20)
   before=a.health,b.health;self.kill(g,m)
   self.assertEqual((a.health,b.health),(before[0]-amount,before[1]-amount))
