import unittest
import test_expanded_generation as fixtures
from expanded import cards,Action
class DrawEntryTests(unittest.TestCase):
 def setUp(self):
  self.g=fixtures.GenerationTests().game()
 def play(self,cid,target=0):
  g=self.g;c=g._add(0,cid);g.players[0].mana=10;cost=g._cost(c,0);g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid and a.target==target));self.assertEqual(g.players[0].mana,10-cost);g.assert_invariants()
 def test_ancestral_knowledge_draws_two_and_locks_one_next_turn(self):
  g=self.g;n=len(g.players[0].deck);self.play('AT_053');self.assertEqual(len(g.players[0].deck),n-2);self.assertEqual(g.players[0].overload_next,1);g.step(Action('end'));g.step(Action('end'));self.assertEqual(g.players[0].mana,g.players[0].max_mana-1)
 def test_windchill_freezes_enemy_and_draws_one(self):
  g=self.g;m=g._summon(1,'CS2_182');n=len(g.players[0].deck);self.play('AV_266',m.uid);self.assertGreaterEqual(m.frozen_until,0);self.assertEqual(m.health,5);self.assertEqual(len(g.players[0].deck),n-1)
 def test_beakered_lightning_hits_both_boards_with_spell_damage_and_overload(self):
  g=self.g;g._summon(0,'TID_708t');a=g._summon(0,'CS2_182');b=g._summon(1,'CS2_182');self.play('BOT_246');self.assertEqual((a.health,b.health),(2,2));self.assertEqual(g.players[0].overload_next,2);self.assertEqual((g.players[0].health,g.players[1].health),(30,30))
 def test_backfire_draws_before_self_damage_and_uses_spell_damage(self):
  g=self.g;g.players[0].deck=[];g._summon(0,'TID_708t');self.play('YOP_033');self.assertEqual(g.players[0].health,19);self.assertEqual(g.players[0].fatigue,3);self.assertEqual(g.players[1].health,30)
 def test_lay_on_hands_heals_selected_enemy_before_fatigue_draws(self):
  g=self.g;g.players[1].health=10;g.players[0].deck=[];self.play('WON_048',g.hero_id(1));self.assertEqual(g.players[1].health,18);self.assertEqual(g.players[0].health,24)
 def test_triple_sevens_resolves_death_then_draws_even_if_target_dies(self):
  g=self.g;m=g._summon(1,'EX1_556');n=len(g.players[0].deck);self.play('WW_410',m.uid);self.assertEqual([x.card_id for x in g.players[1].minions],['skele21']);self.assertEqual(len(g.players[0].deck),n-7)
 def test_imployee_grants_lifesteal_to_friendly_target(self):
  g=self.g;m=g._summon(0,'CS2_182');self.play('WORK_009',m.uid);self.assertIn('LIFESTEAL',g._effective_keywords(m));source=next(x for x in g.players[0].minions if x.card_id=='WORK_009');self.assertNotIn('LIFESTEAL',g._effective_keywords(source))
 def test_sparring_partner_can_give_enemy_taunt_and_keeps_own_taunt(self):
  g=self.g;m=g._summon(1,'CS2_182');self.play('AT_069',m.uid);self.assertIn('TAUNT',g._effective_keywords(m));self.assertIn('TAUNT',g._effective_keywords(g.players[0].minions[0]))
 def test_lance_carrier_only_targets_friendly_minions(self):
  g=self.g;m=g._summon(0,'CS2_182');enemy=g._summon(1,'CS2_182');c=g._add(0,'AT_084');g.players[0].mana=10;targets={a.target for a in g.legal_actions() if a.kind=='play' and a.source==c.uid};self.assertIn(m.uid,targets);self.assertNotIn(enemy.uid,targets);g.players[0].hand.remove(c);self.play('AT_084',m.uid);self.assertEqual((m.attack,m.health),(6,5))
 def test_earth_revenant_battlecry_does_not_use_spell_damage(self):
  g=self.g;g._summon(0,'TID_708t');a=g._summon(0,'CS2_182');b=g._summon(1,'CS2_182');self.play('BAR_750');self.assertEqual((a.health,b.health),(5,4));source=next(x for x in g.players[0].minions if x.card_id=='BAR_750');self.assertIn('TAUNT',g._effective_keywords(source));self.assertEqual(source.health,g.cards[source.card_id]['health'])


 def test_reviewed_bodies_are_registered_only_as_generated_dependencies(self):
  from expanded.historical_generation import validate_past_candidates
  ids=('AT_053', 'AT_069', 'AT_084', 'AV_266', 'BAR_750', 'BOT_246', 'WON_048', 'WORK_009', 'WW_410', 'YOP_033')
  metadata=cards.registry();validate_past_candidates(ids,metadata)
  for cid in ids:
   self.assertIn(cid,cards.TOKEN_IDS);self.assertIn(cid,cards.PLAYABLE_TOKENS);self.assertIn(cid,cards.RULES);self.assertNotIn(cid,cards.COLLECTIBLE_IDS)

if __name__=="__main__":unittest.main()
