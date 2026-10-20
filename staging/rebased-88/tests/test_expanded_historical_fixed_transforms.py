import unittest
import test_expanded_generation as fixtures
from expanded import cards,Action

class FixedTransformTests(unittest.TestCase):
 def game(self):
  return fixtures.GenerationTests().game()
 def play(self,g,cid,target=0):
  c=g._add(0,cid);g.players[0].mana=10;cost=g._cost(c,0);g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid and a.target==target));self.assertEqual(g.players[0].mana,10-cost);g.assert_invariants()
 def test_literal_children_are_generated_only(self):
  ids={'AT_005t','TID_708t'}
  self.assertTrue(ids<=cards.PLAYABLE_TOKENS)
  self.assertFalse(ids&cards.COLLECTIBLE_IDS)
  self.assertTrue(ids<=cards.registry().keys())
 def test_fixed_transforms_replace_state_and_keep_controller_position(self):
  for cid,child in [('AT_005','AT_005t'),('CS2_022','CS2_tk1'),('TID_708','TID_708t')]:
   for owner in (0,1):
    g=self.game();left=g._summon(owner,'CS2_182');m=g._summon(owner,'CORE_LOOT_413');right=g._summon(owner,'CS2_182');g._buff(m,3,4);m.health-=1;m.keywords.add('TAUNT');self.play(g,cid,m.uid);new=g.players[owner].minions[1]
    self.assertEqual([x.uid for x in g.players[owner].minions if x is not new],[left.uid,right.uid]);self.assertEqual(new.card_id,child);self.assertNotEqual(new.uid,m.uid);self.assertEqual((new.attack,new.health,new.max_health),(g.cards[child]['attack'],g.cards[child]['health'],g.cards[child]['health']));self.assertNotIn('TAUNT',new.keywords);self.assertEqual(g.players[owner].armor,0);self.assertFalse(g.players[owner].death_history)
 def test_jellyfish_spell_damage_uses_generated_record(self):
  g=self.game();m=g._summon(0,'CS2_182');self.play(g,'TID_708',m.uid);self.assertEqual(g._spell_damage(0),2)
 def test_jellyfish_silence_removes_its_spell_damage(self):
  g=self.game();m=g._summon(0,'CS2_182');self.play(g,'TID_708',m.uid);g._silence(g.players[0].minions[0]);self.assertEqual(g._spell_damage(0),0)
 def test_boar_charge_can_attack_hero_immediately(self):
  g=self.game();m=g._summon(0,'CS2_182');self.play(g,'AT_005',m.uid);new=g.players[0].minions[0];self.assertTrue(any(a.kind=='attack' and a.source==new.uid and a.target==g.hero_id(1) for a in g.legal_actions()))
 def test_pocket_galaxy_sets_only_current_deck_minions_to_one(self):
  g=self.game();hand=g._add(0,'CS2_182');g.players[0].deck=['CS2_182','CORE_EX1_012','CS2_008'];self.play(g,'BOT_257');self.assertEqual([g._card_stat(c,'cost') for c in g.players[0].deck],[1,1,g.cards['CS2_008']['cost']]);self.assertEqual(g._cost(hand,0),g.cards['CS2_182']['cost']);g.players[0].deck.append('CS2_182');self.assertEqual(g._card_stat(g.players[0].deck[-1],'cost'),g.cards['CS2_182']['cost'])

if __name__=="__main__":unittest.main()
