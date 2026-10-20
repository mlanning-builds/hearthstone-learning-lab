"""Finite older Paladin Mechs remain generated-only; broad pools stay gated."""
import unittest
from expanded import Action,cards
from expanded.historical_generation import validate_past_candidates
import test_expanded_generation as fixtures
IDS={'ULD_217','NX2_022','JAM_010','WORK_002','TSC_059','GVG_062','DRG_225','TSC_644','TSC_083'}
class HistoricalPaladinMechTests(unittest.TestCase):
 def game(self):return fixtures.GenerationTests().game()
 def play(self,g,cid):
  c=g._add(0,cid);g.players[0].mana=10
  g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid))
  g.assert_invariants();return next(m for m in g.players[0].minions if m.card_id==cid)
 def test_frozen_generated_identities_and_normal_paid_bodies(self):
  self.assertTrue(IDS<=cards.TOKEN_IDS&cards.PLAYABLE_TOKENS);self.assertFalse(IDS&cards.COLLECTIBLE_IDS)
  validate_past_candidates(IDS,cards.registry())
  for cid in sorted(IDS):
   with self.subTest(card=cid):self.play(self.game(),cid)
 def test_goldwing_requires_a_held_mech_not_one_in_play(self):
  g=self.game();g._summon(0,'BOT_537');m=self.play(g,'NX2_022');self.assertNotIn('WINDFURY',m.keywords)
  g=self.game();g._add(0,'BOT_537');m=self.play(g,'NX2_022');self.assertIn('WINDFURY',m.keywords)
  self.assertIn('RUSH',m.keywords)
 def test_busy_bot_snapshots_friendly_one_attack_minions(self):
  g=self.game();own=g._summon(0,'CORE_CS2_188');enemy=g._summon(1,'CORE_CS2_188')
  dormant=g._summon(0,'CORE_CS2_188',dormant_turns=2)
  before={m.uid:(m.attack,m.health) for m in (own,enemy,dormant)};source=self.play(g,'WORK_002')
  self.assertEqual((own.attack,own.health),(before[own.uid][0]+1,before[own.uid][1]+1))
  self.assertEqual((enemy.attack,enemy.health),before[enemy.uid])
  self.assertEqual((dormant.attack,dormant.health),before[dormant.uid]);self.assertEqual((source.attack,source.health),(3,2))
 def test_bubblebot_only_gives_other_friendly_mechs_keywords(self):
  g=self.game();mech=g._summon(0,'BOT_537');other=g._summon(0,'CORE_CS2_188');enemy=g._summon(1,'BOT_537')
  source=self.play(g,'TSC_059')
  self.assertTrue({'DIVINE_SHIELD','TAUNT'}<=mech.keywords)
  for m in (other,enemy,source):self.assertNotIn('DIVINE_SHIELD',m.keywords)
 def test_micro_mummy_end_buff_and_reborn_new_physical_entity(self):
  g=self.game();target=g._summon(0,'CORE_CS2_188');source=self.play(g,'ULD_217')
  g.step(Action('end'));self.assertEqual(target.attack,2);self.assertEqual(source.attack,1)
  source.health=0;g._settle();reborn=next(m for m in g.players[0].minions if m.card_id=='ULD_217')
  self.assertNotEqual(reborn.uid,source.uid);self.assertEqual(reborn.health,1);self.assertNotIn('REBORN',reborn.keywords)
 def test_micro_mummy_alone_consumes_no_end_buff_rng(self):
  g=self.game();source=self.play(g,'ULD_217');state=g.rng.getstate()
  g._start_play_effects([('buff_random_other',1,0)],dict(owner=0,source=source,target=0,bonus=0,lifesteal=False))
  self.assertEqual(g.rng.getstate(),state);self.assertEqual(source.attack,1)
 def test_jukebox_summons_real_recruit_and_silence_cancels_later_tick(self):
  g=self.game();source=self.play(g,'JAM_010');g.step(Action('end'))
  recruit=next(m for m in g.players[0].minions if m.card_id=='CS2_101t');self.assertEqual((recruit.attack,recruit.health),(1,1))
  g._silence(source);g.step(Action('end'));g.step(Action('end'))
  self.assertEqual(sum(m.card_id=='CS2_101t' for m in g.players[0].minions),1);g.assert_invariants()

 def test_cobalt_guardian_only_friendly_non_dormant_mech_summons_grant_shield(self):
  g=self.game();source=self.play(g,'GVG_062');self.assertNotIn('DIVINE_SHIELD',source.keywords)
  g._summon(1,'BOT_537');g._settle();self.assertNotIn('DIVINE_SHIELD',source.keywords)
  g._summon(0,'CORE_CS2_188');g._settle();self.assertNotIn('DIVINE_SHIELD',source.keywords)
  g._summon(0,'BOT_537',dormant_turns=2);g._settle();self.assertNotIn('DIVINE_SHIELD',source.keywords)
  g._summon(0,'BOT_537');g._settle();self.assertIn('DIVINE_SHIELD',source.keywords)
 def test_cobalt_guardian_silence_prevents_next_mech_trigger(self):
  g=self.game();source=self.play(g,'GVG_062');g._silence(source)
  g._summon(0,'BOT_537');g._settle();self.assertNotIn('DIVINE_SHIELD',source.keywords)
 def test_sky_claw_literal_microcopters_and_silenceable_mech_aura(self):
  g=self.game();ally=g._summon(0,'BOT_537');enemy=g._summon(1,'BOT_537');source=self.play(g,'DRG_225')
  children=[m for m in g.players[0].minions if m.card_id=='DRG_225t']
  self.assertEqual(len(children),2);self.assertEqual(len({m.uid for m in children}),2)
  self.assertEqual([(m.attack,m.health) for m in children],[(2,1),(2,1)])
  self.assertEqual((ally.attack,enemy.attack,source.attack),(1,0,1))
  g._silence(source);self.assertEqual(ally.attack,0);self.assertEqual([m.attack for m in children],[1,1])

 def test_azsharan_mooncatcher_inserts_plain_sunken_copy_at_bottom(self):
  g=self.game();old=g._add(0,'CORE_CS2_029');g.players[0].hand=[];g.players[0].deck=[old]
  self.play(g,'TSC_644');p=g.players[0]
  self.assertEqual(p.deck[0].card_id,'TSC_644t');self.assertIs(p.deck[-1],old)
  self.assertFalse(g._started_in_deck(p.deck[0],0))
 def test_sunken_mooncatcher_copies_body_enchantments_with_new_uid(self):
  g=self.game();c=g._add(0,'TSC_644t');c.attack_bonus=2;c.health_bonus=3;g.players[0].mana=10
  g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid))
  bodies=[m for m in g.players[0].minions if m.card_id=='TSC_644t']
  self.assertEqual(len(bodies),2);self.assertEqual(len({m.uid for m in bodies}),2)
  self.assertEqual([(m.attack,m.health) for m in bodies],[(6,5),(6,5)])
  self.assertTrue(all('DIVINE_SHIELD' in m.keywords for m in bodies))
 def test_dredge_offers_physical_bottom_three_without_rng_or_discover(self):
  g=self.game();p=g.players[0]
  values=[g._add(0,cid) for cid in ('CORE_CS2_188','CORE_CS2_188','CORE_CS2_029','CORE_EX1_162')]
  values[1].attack_bonus=3;chosen=values[1];p.deck=values;p.hand=[];rng=g.rng.getstate()
  source=self.play(g,'TSC_083');self.assertEqual(g.rng.getstate(),rng)
  self.assertEqual([o['index'] for o in g.pending_choice['options']],[0,1,2])
  self.assertEqual([o['card_id'] for o in g.pending_choice['options']],[c.card_id for c in values[:3]])
  self.assertEqual(g.observe(1)['pending_choice'],{'owner':0,'waiting':True})
  g.step(Action('choose',choices=(1,)));self.assertIs(p.deck[-1],chosen)
  self.assertEqual((chosen.attack_bonus,chosen.health_bonus),(3+source.attack,source.health))
  self.assertEqual(p.discoveries_total,0);g.assert_invariants()
 def test_dredged_spell_is_not_buffed_and_empty_deck_opens_no_choice(self):
  g=self.game();p=g.players[0];c=g._add(0,'CORE_CS2_029');p.hand=[];p.deck=[c]
  self.play(g,'TSC_083');g.step(Action('choose',choices=(0,)))
  self.assertEqual((c.attack_bonus,c.health_bonus),(0,0));self.assertIs(p.deck[-1],c)
  g=self.game();g.players[0].deck=[];self.play(g,'TSC_083');self.assertIsNone(g.pending_choice)
