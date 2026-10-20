"""Historical owner-power triggers execute through actual paid actions."""
import unittest
import test_expanded_generation as fixtures
from expanded import Action,cards
from expanded.historical_power_primitives import RULES,TRIGGERS,DEATH_EFFECTS,TOKEN_RULES,GENERATED_IDS,FIXED_TOKEN_IDS


class HistoricalPowerPrimitiveTests(unittest.TestCase):
 def setUp(self):
  self.fx=fixtures.GenerationTests()

 def game(self):return self.fx.game()

 def play(self,g,cid,target=0):
  g.players[0].mana=10;c=g._add(0,cid)
  g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid and a.target==target))
  return next(m for m in g.players[0].minions if m.card_id==cid)

 def power(self,g):
  g.players[0].mana=10;g.step(Action('power',target=-2))

 def test_all_fourteen_complete_paid_play(self):
  self.assertEqual(len(GENERATED_IDS),14)
  for cid in GENERATED_IDS:
   with self.subTest(cid=cid):
    g=self.game();target=g._summon(0,'CORE_GIL_558').uid if cid=='AT_057' else 0
    self.play(g,cid,target);g.assert_invariants()
    self.assertNotIn(cid,cards.COLLECTIBLE_IDS)

 def test_self_attack_health_and_two_two_buffs(self):
  for cid,delta in (('AT_082',(1,0)),('AT_089',(0,1)),('AT_119',(2,2))):
   with self.subTest(cid=cid):
    g=self.game();m=self.play(g,cid);before=(m.attack,m.max_health);self.power(g)
    self.assertEqual((m.attack,m.max_health),(before[0]+delta[0],before[1]+delta[1]))

 def test_opponent_power_does_not_inspire(self):
  g=self.game();m=self.play(g,'AT_119');before=(m.attack,m.max_health)
  g.step(Action('end'));g.step(Action('power'))
  self.assertEqual((m.attack,m.max_health),before)

 def test_silenced_and_dormant_sources_do_not_inspire(self):
  for dormant in (False,True):
   with self.subTest(dormant=dormant):
    g=self.game();m=self.play(g,'AT_119')
    if dormant:m.dormant=1
    else:g._silence(m)
    before=(m.attack,m.max_health);self.power(g)
    self.assertEqual((m.attack,m.max_health),before)

 def test_spawn_of_shadows_battlecry_then_inspire(self):
  g=self.game();self.play(g,'AT_012')
  self.assertEqual([p.health for p in g.players],[26,26]);self.power(g)
  self.assertEqual([p.health for p in g.players],[22,21])

 def test_savage_combatant_attack_expires(self):
  g=self.game();self.play(g,'AT_039');self.power(g)
  self.assertEqual(g._hero_attack(0),2)
  g.step(Action('end'));self.assertEqual(g._hero_attack(0),0)

 def test_aspirant_buffs_equipped_weapon(self):
  g=self.game();g._equip(0,'CS2_091');self.play(g,'AT_066');before=g.players[0].weapon['attack'];self.power(g)
  self.assertEqual(g.players[0].weapon['attack'],before+1)

 def test_dragonhawk_temporary_windfury_expires(self):
  g=self.game();m=self.play(g,'AT_083');self.power(g)
  self.assertIn('WINDFURY',g._effective_keywords(m));g.step(Action('end'))
  self.assertNotIn('WINDFURY',g._effective_keywords(m))

 def test_mukla_champion_buffs_other_minions(self):
  g=self.game();ally=g._summon(0,'CORE_GIL_558');m=self.play(g,'AT_090')
  before=(ally.attack,ally.max_health);source=(m.attack,m.max_health);self.power(g)
  self.assertEqual((ally.attack,ally.max_health),(before[0]+1,before[1]+1))
  self.assertEqual((m.attack,m.max_health),source)

 def test_tournament_medic_heals_owner(self):
  g=self.game();self.play(g,'AT_091');g.players[0].health=20;self.power(g)
  self.assertEqual(g.players[0].health,22)

 def test_regent_summons_recruit(self):
  g=self.game();self.play(g,'AT_100');self.power(g)
  recruits=[m for m in g.players[0].minions if m.card_id=='CS2_101t']
  self.assertEqual(len(recruits),1);self.assertEqual((recruits[0].attack,recruits[0].max_health),(1,1))

 def test_recruiter_adds_exact_squire(self):
  g=self.game();self.play(g,'AT_113');self.power(g)
  c=g.players[0].hand[-1];self.assertEqual(c.card_id,'CS2_152')
  self.assertEqual((g._card_stat(c,'attack',0),g._card_stat(c,'health',0)),(2,2))

 def test_rhonin_death_adds_three_playable_arcane_missiles(self):
  g=self.game();m=self.play(g,'AT_009');m.health=0;g._settle(allow_event_choices=True)
  self.assertEqual([c.card_id for c in g.players[0].hand],['EX1_277']*3)
  g.players[0].mana=10;c=g.players[0].hand[0]
  g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid))
  self.assertEqual(g.players[1].health,27)

 def test_flame_juggler_hits_only_enemy_when_board_empty(self):
  g=self.game();self.play(g,'AT_094');self.assertEqual(g.players[1].health,29)

 def test_stablemaster_immune_expires_at_end_of_turn(self):
  g=self.game();target=g._summon(0,'CORE_GIL_558');self.play(g,'AT_057',target.uid)
  self.assertIn('IMMUNE',g._effective_keywords(target));g.step(Action('end'))
  self.assertNotIn('IMMUNE',g._effective_keywords(target))

 def test_generated_registrations_and_fixed_outcomes_are_present(self):
  self.assertTrue(GENERATED_IDS<=set(cards.registry()))
  self.assertTrue(GENERATED_IDS<=set(cards.RULES))
  self.assertTrue(set(TRIGGERS)<=set(cards.TRIGGERS))
  self.assertTrue({'CS2_152','CS2_101t','EX1_277'}<=set(cards.registry())&set(cards.RULES))
