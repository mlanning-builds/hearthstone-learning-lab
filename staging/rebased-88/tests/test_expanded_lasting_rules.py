"""Regression contracts for persistent effects and defensive replacements."""
import json,unittest
import test_expanded_generation as fixtures
from expanded import Action
from expanded.cards import COLLECTIBLE_IDS
from expanded.lasting_rules import RULES
from engine.game import Card

class LastingRulesTests(unittest.TestCase):
 def setUp(self):self.g=fixtures.GenerationTests().game();self.p=self.g.players[0];self.q=self.g.players[1]
 def add(self,cid):
  c=Card(self.g._new_id(),cid);self.g._enter_hand(0,c);return c
 def play(self,cid,choice=0):
  c=self.add(cid);self.p.mana=10
  acts=[a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid and (not a.choices or a.choices==(choice,))]
  self.g.step(max(acts,key=lambda a:a.position));return c
 def op(self,name,*args):self.g._effect((name,*args),dict(owner=0,source=None,target=0,bonus=0,lifesteal=False));self.g._settle()
 def choose(self,index=0):self.g.step(Action('choose',choices=(index,)))
 def cycle(self):self.g.step(Action('end'));self.g.step(Action('end'))
 def test_registry(self):self.assertTrue(set(RULES)|{'MEND_044'}<=COLLECTIBLE_IDS)
 def test_life_sets_health_preserves_armor(self):
  self.p.armor=7;self.play('CATA_307');self.assertEqual((self.p.health,self.p.armor,self.p.life_rewards),(15,7,1))
 def test_life_waits_for_full(self):
  self.play('CATA_307');self.g._heal(-1,14,healer=0);self.g._settle();self.assertEqual(self.q.health,30)
 def test_life_fires_once(self):
  self.play('CATA_307');self.g._heal(-1,15,healer=0);self.g._settle();self.assertEqual(self.q.health,15)
  self.g._damage(-1,1);self.g._heal(-1,1,healer=0);self.g._settle();self.assertEqual(self.q.health,15)
 def test_life_survives_source_silence_and_death(self):
  self.play('CATA_307');m=self.p.minions[0];self.g._silence(m);m.health=0;self.g._settle()
  self.g._heal(-1,30,healer=0);self.g._settle();self.assertEqual(self.q.health,15)
 def test_life_repeated_battlecries_stack(self):
  self.op('lasting_life');self.op('lasting_life');self.q.armor=20
  self.g._heal(-1,30,healer=0);self.g._settle();self.assertEqual((self.q.health,self.q.armor),(20,0))
 def test_life_uses_current_max_health(self):
  self.p.max_health=40;self.op('lasting_life');self.g._heal(-1,15,healer=0);self.g._settle();self.assertEqual(self.q.health,30)
  self.g._heal(-1,10,healer=0);self.g._settle();self.assertEqual(self.q.health,15)
 def test_life_full_by_setting_health(self):
  self.op('lasting_life');self.p.health=self.p.max_health;self.g._settle();self.assertEqual(self.q.health,15)
 def test_life_recruit_has_no_battlecry(self):
  self.g._summon(0,'CATA_307');self.assertEqual(self.p.life_rewards,0)
 def test_geddon_battlecry_only_installs(self):
  self.play('CATA_591');self.assertIsNone(self.g.pending_choice);self.assertTrue(self.p.geddon_draw)
 def test_geddon_turn_choice_and_resume(self):
  self.play('CATA_591');self.cycle();self.assertEqual(self.g.pending_choice['kind'],'lasting_deck');self.choose()
  self.assertIsNone(self.g._turn_frame);self.assertEqual(self.p.hand[-1].cost_delta,-3)
 def test_geddon_normal_draw_unaffected(self):
  self.op('lasting_draw');self.g._draw(0);self.assertEqual(self.p.hand[-1].card_id,'CORE_CS2_029');self.assertIsNone(self.g.pending_choice)
 def test_geddon_removes_only_offered_physical_cards(self):
  self.p.deck=['CORE_CS2_029','CORE_EX1_012','CORE_CS2_188','CORE_EX1_012'];self.op('lasting_draw')
  self.g._turn_card_draw(0);self.choose();self.assertEqual(len(self.p.deck),1);self.assertEqual(len(self.p.hand),1)
 def test_geddon_preserves_selected_enchantments(self):
  c=Card(self.g._new_id(),'CORE_CS2_188',attack_bonus=4);self.p.deck=[c];self.op('lasting_draw')
  self.g._turn_card_draw(0);self.choose();self.assertIs(self.p.hand[0],c);self.assertEqual(c.attack_bonus,4)
 def test_geddon_discovers_not_draws(self):
  self.op('lasting_draw');self.g._turn_card_draw(0);self.choose();self.assertEqual(self.p.discoveries_total,1)
 def test_geddon_burns_selected_with_full_hand(self):
  for _ in range(10):self.add('CORE_CS2_029')
  self.p.deck=['CORE_CS2_188'];self.op('lasting_draw');self.g._turn_card_draw(0);self.choose()
  self.assertEqual(len(self.p.hand),10);self.assertFalse(self.p.deck)
 def test_geddon_empty_deck_fatigues(self):
  self.p.deck=[];self.op('lasting_draw');self.g._turn_card_draw(0);self.assertEqual((self.p.fatigue,self.p.health),(1,29))
 def test_geddon_choice_is_private(self):
  self.op('lasting_draw');self.g._turn_card_draw(0)
  self.assertFalse(self.g.observe(1)['legal_actions']);json.dumps(self.g.observe(0))
 def test_falric_gain_doubles(self):
  self.g._summon(0,'CORE_EDR_003');before=self.p.corpses;self.op('gain_corpses',3);self.assertEqual(self.p.corpses-before,6)
 def test_falric_two_multiply(self):
  self.g._summon(0,'CORE_EDR_003');self.g._summon(0,'CORE_EDR_003');before=self.p.corpses;self.op('gain_corpses',1);self.assertEqual(self.p.corpses-before,4)
 def test_falric_silence_disables(self):
  m=self.g._summon(0,'CORE_EDR_003');self.g._silence(m);before=self.p.corpses;self.op('gain_corpses',1);self.assertEqual(self.p.corpses-before,1)
 def test_falric_dormant_disables(self):
  m=self.g._summon(0,'CORE_EDR_003');self.g._sleep_minion(m,2);before=self.p.corpses;self.op('gain_corpses',1);self.assertEqual(self.p.corpses-before,1)
 def test_falric_doubles_other_death(self):
  self.g._summon(0,'CORE_EDR_003');m=self.g._summon(0,'CORE_CS2_188');before=self.p.corpses;m.health=0;self.g._settle();self.assertEqual(self.p.corpses-before,2)
 def test_falric_does_not_double_own_death(self):
  m=self.g._summon(0,'CORE_EDR_003');before=self.p.corpses;m.health=0;self.g._settle();self.assertEqual(self.p.corpses-before,1)
 def test_falric_simultaneous_death_aura_inactive(self):
  m=self.g._summon(0,'CORE_EDR_003');n=self.g._summon(0,'CORE_CS2_188');before=self.p.corpses;m.health=n.health=0;self.g._settle();self.assertEqual(self.p.corpses-before,2)
 def test_falric_draws_spender_not_gain(self):
  self.p.deck=['RLK_503','CORE_RLK_712'];self.play('CORE_EDR_003');self.assertEqual(self.p.hand[-1].card_id,'CORE_RLK_712');self.assertEqual(self.p.deck,['RLK_503'])
 def test_falric_no_match_does_not_fatigue(self):
  self.p.deck=[];self.play('CORE_EDR_003');self.assertEqual(self.p.fatigue,0)
 def test_toreth_three_hits(self):
  m=self.g._summon(0,'EDR_258');hp=m.health
  for _ in range(2):self.assertEqual(self.g._damage(m.uid,99,True),0);self.assertIn('DIVINE_SHIELD',m.keywords)
  self.g._damage(m.uid,99,True);self.assertNotIn('DIVINE_SHIELD',m.keywords);self.assertEqual(m.health,hp)
 def test_toreth_other_friendly_shields(self):
  self.g._summon(0,'EDR_258');m=self.g._summon(0,'CORE_CS2_188');m.keywords.add('DIVINE_SHIELD');self.g._damage(m.uid,1);self.assertIn('DIVINE_SHIELD',m.keywords)
 def test_toreth_enemy_unaffected(self):
  self.g._summon(0,'EDR_258');m=self.g._summon(1,'CORE_CS2_188');m.keywords.add('DIVINE_SHIELD');self.g._damage(m.uid,1);self.assertNotIn('DIVINE_SHIELD',m.keywords)
 def test_toreth_hero_shield(self):
  self.g._summon(0,'EDR_258');self.p.divine_shield=True
  self.g._damage(-1,1);self.g._damage(-1,1);self.assertTrue(self.p.divine_shield)
  self.g._damage(-1,1);self.assertFalse(self.p.divine_shield);self.assertEqual(self.p.health,30)
 def test_toreth_silence_aura_ends(self):
  t=self.g._summon(0,'EDR_258');m=self.g._summon(0,'CORE_CS2_188');m.keywords.add('DIVINE_SHIELD');self.g._damage(m.uid,1);self.g._silence(t);self.g._damage(m.uid,1);self.assertNotIn('DIVINE_SHIELD',m.keywords)
 def test_toreth_new_shield_new_three_hits(self):
  m=self.g._summon(0,'EDR_258')
  for _ in range(3):self.g._damage(m.uid,1)
  m.keywords.add('DIVINE_SHIELD');self.g._damage(m.uid,1);self.assertIn('DIVINE_SHIELD',m.keywords)
 def test_toreth_zero_damage_not_a_hit(self):
  m=self.g._summon(0,'EDR_258');self.g._damage(m.uid,0);self.assertNotIn('shield_hits',m.rule_state)
 def test_toreth_duplicate_aura_does_not_stack(self):
  m=self.g._summon(0,'EDR_258');self.g._summon(0,'EDR_258')
  for _ in range(3):self.g._damage(m.uid,1)
  self.assertNotIn('DIVINE_SHIELD',m.keywords)
 def test_thorn_poison_kills(self):
  self.play('EDR_525');m=self.g._summon(1,'CORE_CS2_188');self.g._buff(m,0,10)
  self.g.step(Action('attack',-1,m.uid));self.assertNotIn(m,self.q.minions)
 def test_thorn_poison_expires(self):
  self.play('EDR_525');self.cycle();m=self.g._summon(1,'CORE_CS2_188');self.g._buff(m,0,10)
  self.g.step(Action('attack',-1,m.uid));self.assertIn(m,self.q.minions)
 def test_thorn_death_aoe(self):
  self.play('EDR_525',1);m=self.g._summon(1,'CORE_CS2_188');self.g._break_weapon(0);self.g._settle()
  self.assertEqual(self.q.health,28);self.assertNotIn(m,self.q.minions)
 def test_thorn_poison_does_not_attach_death(self):
  self.play('EDR_525');self.g._break_weapon(0);self.assertEqual(self.q.health,30)
 def test_guard_sorry_death(self):
  m=self.g._summon(0,'JAIL_703');m.health=0;self.g._settle();self.assertTrue(self.p.sorry_enabled)
 def test_guard_silenced(self):
  m=self.g._summon(0,'JAIL_703');self.g._silence(m);m.health=0;self.g._settle();self.assertFalse(self.p.sorry_enabled)
 def test_clearing_is_location(self):
  self.play('MEND_044');self.assertEqual(len(self.p.locations),1)
 def sleep_target(self,enemy=False):
  m=self.g._summon(int(enemy),'CORE_CS2_188');self.play('MEND_044');self.g.step(Action('activate',self.p.locations[0].uid,m.uid));return m
 def test_clearing_stats_and_sleep(self):
  m=self.sleep_target();self.assertEqual(m.max_health,3);self.assertIn('TAUNT',m.keywords);self.assertTrue(m.dormant)
 def test_clearing_wakes_end_next_casters_turn(self):
  m=self.sleep_target();self.cycle();self.assertTrue(m.dormant);self.g.step(Action('end'));self.assertFalse(m.dormant)
 def test_clearing_enemy_same_caster_clock(self):
  m=self.sleep_target(True);self.cycle();self.assertTrue(m.dormant);self.g.step(Action('end'));self.assertFalse(m.dormant)
 def test_clearing_survives_location_removal(self):
  m=self.sleep_target();self.g._remove_location(self.p.locations[0]);self.cycle();self.g.step(Action('end'));self.assertFalse(m.dormant)
 def test_player_effects_observable(self):
  self.op('lasting_life');self.op('lasting_draw');v=self.g.observe(1)['players'][0]
  self.assertEqual((v['life_rewards'],v['geddon_draw']),(1,True))

 def test_corpse_gain_log_reports_multiplied_amount(self):
  self.g._summon(0,'CORE_EDR_003');self.op('gain_corpses',3)
  events=self.g.observe(0)['events']
  self.assertTrue(any(e.get('event')=='gain_corpse' and e.get('amount')==6 for e in events))
