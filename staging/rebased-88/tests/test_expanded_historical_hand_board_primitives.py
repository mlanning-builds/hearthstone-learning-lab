import unittest
import test_expanded_generation as fixtures
from expanded import cards,Action

class NextNumericTests(unittest.TestCase):
 def game(self):
  return fixtures.GenerationTests().game()
 def play(self,g,cid,target=0):
  c=g._add(0,cid);g.players[0].mana=10;cost=g._cost(c,0);g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid and a.target==target));self.assertEqual(g.players[0].mana,10-cost);g.assert_invariants();return c
 def test_health_buffs_preserve_existing_damage(self):
  for cid in ('CFM_626','EX1_623'):
   g=self.game();m=g._summon(0,'CS2_182');m.health-=2;before=m.health,m.max_health,m.attack;self.play(g,cid,m.uid);self.assertEqual((m.health,m.max_health,m.attack),(before[0]+3,before[1]+3,before[2]))
 def test_hero_attack_expires_armor_persists(self):
  for cid,n in [('CS2_005',2),('ICC_079',3)]:
   g=self.game();self.play(g,cid);self.assertEqual((g._hero_attack(0),g.players[0].armor),(n,n));g.step(Action('end'));self.assertEqual((g._hero_attack(0),g.players[0].armor),(0,n))
 def test_hand_buff_only_existing_minions(self):
  g=self.game();m=g._add(0,'CS2_182');spell=g._add(0,'CS2_008');self.play(g,'BOT_910');self.assertEqual((m.attack_bonus,m.health_bonus),(2,2));self.assertEqual((spell.attack_bonus,spell.health_bonus),(0,0));later=g._add(0,'CS2_182');self.assertEqual((later.attack_bonus,later.health_bonus),(0,0))
 def test_stormstrike_minion_damage_and_temporary_hero_attack(self):
  for owner in (0,1):
   g=self.game();m=g._summon(owner,'CS2_182');h=m.health;self.play(g,'DMF_702',m.uid);self.assertEqual(m.health,h-3);self.assertEqual(g._hero_attack(0),3);g.step(Action('end'));self.assertEqual(g._hero_attack(0),0)
 def test_street_sweeper_hits_other_minions_both_sides(self):
  g=self.game();a=g._summon(0,'CS2_182');b=g._summon(1,'CS2_182');self.play(g,'RLK_104');source=next(m for m in g.players[0].minions if m.card_id=='RLK_104');self.assertEqual((a.health,b.health),(3,3));self.assertEqual(source.health,g.cards['RLK_104']['health']);self.assertEqual((g.players[0].health,g.players[1].health),(30,30))

if __name__=="__main__":unittest.main()
