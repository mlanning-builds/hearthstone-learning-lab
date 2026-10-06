"""Physical identity and privacy contracts for entity changes."""
import json,unittest
import test_expanded_generation as fixtures
from expanded import Action
from expanded.cards import COLLECTIBLE_IDS,registry
from expanded.entity_effects import RULES,TOKEN_IDS
from engine.game import Card

class EntityEffectsTests(unittest.TestCase):
 def setUp(self):self.g=fixtures.GenerationTests().game();self.p=self.g.players[0];self.q=self.g.players[1]
 def add(self,cid,owner=0):
  c=Card(self.g._new_id(),cid);self.g._enter_hand(owner,c);return c
 def play(self,cid,target=0):
  c=self.add(cid);self.play_card(c,target);return c
 def play_card(self,c,target=0):
  self.p.mana=10
  self.g.step(max((a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid and a.target==target),key=lambda a:a.position))
 def op(self,op,source=None,target=0):
  self.g._start_play_effects([op],dict(owner=0,source=source,target=target,bonus=0,lifesteal=False));self.g._settle()
 def cycle(self):self.g.step(Action('end'));self.g.step(Action('end'))
 def choose(self,index=0):self.g.step(Action('choose',choices=(index,)))
 def test_registry(self):self.assertTrue(set(RULES)-TOKEN_IDS<=COLLECTIBLE_IDS);self.assertTrue(TOKEN_IDS<=registry().keys())
 def test_tribute_copies_second_selected_stats(self):
  a=self.g._summon(0,'CORE_CS2_188');b=self.g._summon(1,'CORE_EX1_012');self.g._buff(b,3,3);self.g._damage(b.uid,1)
  self.play('DINO_414',a.uid);self.choose()
  m=self.p.minions[0];self.assertEqual((m.card_id,m.attack,m.health,m.max_health),(b.card_id,b.attack,b.health,b.max_health))
 def test_tribute_keeps_target_owner_position(self):
  left=self.g._summon(0,'CORE_CS2_188');a=self.g._summon(0,'CORE_CS2_188');right=self.g._summon(0,'CORE_CS2_188');b=self.g._summon(1,'CORE_EX1_012')
  self.play('DINO_414',a.uid);choice=next(i for i,o in enumerate(self.g.pending_choice['options']) if o['uid']==b.uid);self.choose(choice)
  self.assertEqual([m.uid for m in self.p.minions][::2],[left.uid,right.uid]);self.assertEqual(self.p.minions[1].owner,0)
 def test_tribute_not_summon_or_death(self):
  a=self.g._summon(0,'JAIL_703');b=self.g._summon(1,'CORE_EX1_012');before=len(self.g.events)
  self.play('DINO_414',a.uid);self.choose();self.assertFalse(self.p.sorry_enabled)
  self.assertFalse(any(e['event']=='summon' for e in self.g.events[before:]))
 def test_tribute_excludes_first_target(self):
  a=self.g._summon(0,'CORE_CS2_188');b=self.g._summon(1,'CORE_EX1_012');self.play('DINO_414',a.uid)
  self.assertEqual([o['uid'] for o in self.g.pending_choice['options']],[b.uid])
 def test_tribute_no_second_target_fizzles(self):
  a=self.g._summon(0,'CORE_CS2_188');self.play('DINO_414',a.uid);self.assertIsNone(self.g.pending_choice);self.assertIn(a,self.p.minions)
 def test_tribute_does_not_count_discover(self):
  a=self.g._summon(0,'CORE_CS2_188');self.g._summon(1,'CORE_EX1_012');self.play('DINO_414',a.uid);self.choose();self.assertEqual(self.p.discoveries_total,0)
 def test_tribute_second_target_obeys_elusive(self):
  a=self.g._summon(0,'CORE_CS2_188');self.g._summon(1,'CATA_185');self.play('DINO_414',a.uid);self.assertIsNone(self.g.pending_choice)
 def test_illusion_one_fragile_two_possible(self):
  self.play('EDR_780');self.assertEqual(len(self.p.minions),2);self.assertEqual(sum(getattr(m,'_fragile_illusion',False) for m in self.p.minions),1)
  self.assertTrue(all(m._illusion_possible for m in self.p.minions))
 def test_illusion_hides_which_from_both_players(self):
  self.play('EDR_780')
  for viewer in (0,1):
   view=self.g.observe(viewer);encoded=json.dumps(view);self.assertNotIn('fragile_illusion',encoded)
   self.assertTrue(all(m['illusion_possible'] for m in view['players'][0]['board']))
 def test_illusion_positive_damage_kills(self):
  self.play('EDR_780');m=next(m for m in self.p.minions if getattr(m,'_fragile_illusion',False));self.g._damage(m.uid,1);self.g._settle();self.assertNotIn(m,self.p.minions)
 def test_illusion_real_copy_survives_ping(self):
  self.play('EDR_780');m=next(m for m in self.p.minions if not getattr(m,'_fragile_illusion',False));self.g._damage(m.uid,1);self.g._settle();self.assertIn(m,self.p.minions)
 def test_illusion_shield_prevents_fragile_death(self):
  self.play('EDR_780');m=next(m for m in self.p.minions if getattr(m,'_fragile_illusion',False));m.keywords.add('DIVINE_SHIELD');self.g._damage(m.uid,1);self.g._settle();self.assertIn(m,self.p.minions)
 def test_illusion_silence_removes_fragility(self):
  self.play('EDR_780');m=next(m for m in self.p.minions if getattr(m,'_fragile_illusion',False));self.g._silence(m);self.g._damage(m.uid,1);self.g._settle();self.assertIn(m,self.p.minions)
 def test_illusion_copy_preserves_hidden_enchantment(self):
  self.play('EDR_780');m=next(m for m in self.p.minions if getattr(m,'_fragile_illusion',False));n=self.g._summon(0,m.card_id,copy_from=m);self.assertTrue(n._fragile_illusion)
 def test_illusion_full_board_marks_original(self):
  for _ in range(6):self.g._summon(0,'CORE_CS2_188')
  self.play('EDR_780');self.assertTrue(self.p.minions[-1]._fragile_illusion)
 def test_illusion_copies_hand_buffs(self):
  c=self.add('EDR_780');c.attack_bonus=3;c.health_bonus=2;self.play_card(c);self.assertEqual([(m.attack,m.health) for m in self.p.minions],[(5,6),(5,6)])
 def test_alarm_swaps_actual_card_preserving_hand_buffs(self):
  m=self.g._summon(0,'JAIL_502');c=self.add('CORE_CS2_188',1);c.attack_bonus=4;c.health_bonus=3
  self.op(('entity_swap_hand',),m);self.assertEqual((self.p.minions[0].attack,self.p.minions[0].health),(5,4));self.assertEqual(self.q.hand[0].card_id,'JAIL_502')
 def test_alarm_return_resets_enchantments(self):
  m=self.g._summon(0,'JAIL_502');self.g._buff(m,5,5);self.add('CORE_CS2_188',1);self.op(('entity_swap_hand',),m)
  self.assertEqual(self.q.hand[0].attack_bonus,0)
 def test_alarm_ignores_spells(self):
  m=self.g._summon(0,'JAIL_502');self.add('CORE_CS2_029',1);self.op(('entity_swap_hand',),m);self.assertIn(m,self.p.minions)
 def test_alarm_swap_is_not_discard_or_death(self):
  m=self.g._summon(0,'JAIL_502');self.add('JAIL_703',1);self.op(('entity_swap_hand',),m);self.assertFalse(self.p.death_history);self.assertFalse(self.q.discard_history)
 def test_alarm_does_not_play_incoming_battlecry(self):
  m=self.g._summon(0,'JAIL_502');self.add('CATA_307',1);self.op(('entity_swap_hand',),m);self.assertEqual(self.p.life_rewards,0)
 def test_alarm_works_with_full_board_and_hand(self):
  m=self.g._summon(0,'JAIL_502')
  for _ in range(6):self.g._summon(0,'CORE_CS2_188')
  for _ in range(10):self.add('CORE_CS2_188',1)
  self.op(('entity_swap_hand',),m);self.assertEqual((len(self.p.board),len(self.q.hand)),(7,10))
 def test_alarm_turn_trigger(self):
  self.g._summon(0,'JAIL_502');self.add('CORE_CS2_188',1);self.cycle();self.assertEqual(self.p.minions[0].card_id,'CORE_CS2_188')
 def test_alarm_silenced_no_swap(self):
  m=self.g._summon(0,'JAIL_502');self.g._silence(m);self.add('CORE_CS2_188',1);self.cycle();self.assertIn(m,self.p.minions)
 def test_replicator_attacking_killer(self):
  a=self.g._summon(0,'CORE_CS2_188');self.g._buff(a,4,5);a.summoned_turn=-1;b=self.g._summon(1,'CATA_185')
  self.g.step(Action('attack',a.uid,b.uid));self.assertEqual(self.p.minions[0].card_id,'CATA_185')
 def test_replicator_retaliating_killer(self):
  a=self.g._summon(0,'CATA_185');a.summoned_turn=-1;b=self.g._summon(1,'CORE_CS2_188');self.g._buff(b,4,5)
  self.g.step(Action('attack',a.uid,b.uid));self.assertEqual(self.q.minions[0].card_id,'CATA_185')
 def test_replicator_minion_effect_killer(self):
  a=self.g._summon(0,'CORE_CS2_188');b=self.g._summon(1,'CATA_185');self.op(('damage',3),a,b.uid);self.assertEqual(self.p.minions[0].card_id,'CATA_185')
 def test_replicator_destroy_effect_killer(self):
  a=self.g._summon(0,'CORE_CS2_188');b=self.g._summon(1,'CATA_185');self.op(('destroy',),a,b.uid);self.assertEqual(self.p.minions[0].card_id,'CATA_185')
 def test_replicator_spell_does_not_change_minions(self):
  a=self.g._summon(0,'CORE_CS2_188');b=self.g._summon(1,'CATA_185');self.op(('damage',3),None,b.uid);self.assertIn(a,self.p.minions)
 def test_replicator_dead_killer_no_resurrection(self):
  a=self.g._summon(0,'CORE_CS2_188');self.g._buff(a,2,0);a.summoned_turn=-1;b=self.g._summon(1,'CATA_185')
  self.g.step(Action('attack',a.uid,b.uid));self.assertFalse(self.p.minions+self.q.minions)
 def test_replicator_silence_no_transform(self):
  a=self.g._summon(0,'CORE_CS2_188');b=self.g._summon(1,'CATA_185');self.g._silence(b);self.op(('damage',3),a,b.uid);self.assertIn(a,self.p.minions)
 def test_ido_provides_spell_without_battlecry(self):
  self.g._summon(0,'TLC_241');self.g._settle();self.assertEqual([c.card_id for c in self.p.hand],['TLC_241t'])
 def test_ido_replenishes_after_play(self):
  m=self.g._summon(0,'TLC_241');self.g._settle();c=self.p.hand[0];self.play_card(c,m.uid)
  self.assertEqual((m.attack,m.health),(4,9));self.assertIn('DIVINE_SHIELD',m.keywords);self.assertEqual(len(self.p.hand),1);self.assertNotEqual(self.p.hand[0].uid,c.uid)
 def test_ido_does_not_duplicate_idle_card(self):
  self.g._summon(0,'TLC_241');self.g._settle();self.g._settle();self.assertEqual(len(self.p.hand),1)
 def test_ido_silence_removes_bound_spell(self):
  m=self.g._summon(0,'TLC_241');self.g._settle();self.g._silence(m);self.g._settle();self.assertFalse(self.p.hand)
 def test_ido_death_removes_spell_without_discard(self):
  m=self.g._summon(0,'TLC_241');self.g._settle();m.health=0;self.g._settle();self.assertFalse(self.p.hand);self.assertFalse(self.p.discard_history)
 def test_ido_full_hand_recovers_when_slot_opens(self):
  for _ in range(10):self.add('CORE_CS2_029')
  self.g._summon(0,'TLC_241');self.g._settle();self.assertEqual(len(self.p.hand),10);self.p.hand.pop();self.g._settle();self.assertEqual(self.p.hand[-1].card_id,'TLC_241t')
 def test_ido_independent_sources(self):
  a=self.g._summon(0,'TLC_241');self.g._summon(0,'TLC_241');self.g._settle();self.assertEqual(len(self.p.hand),2)
  a.health=0;self.g._settle();self.assertEqual(len(self.p.hand),1)
 def test_lunar_cycle_delayed_three_owner_starts(self):
  self.play('EDR_895');self.cycle();self.cycle();self.assertFalse(self.p.full_moon);self.cycle();self.assertTrue(self.p.full_moon)
 def test_full_moon_all_card_types(self):
  self.op(('entity_full_moon',))
  for cid in ('CORE_CS2_029','CORE_CS2_188','EDR_525','MEND_044'):
   c=self.add(cid);self.assertEqual(self.g._cost(c,0),1)
 def test_full_moon_opponent_unaffected(self):
  self.op(('entity_full_moon',));c=self.add('CORE_CS2_029',1);self.assertEqual(self.g._cost(c,1),4)
 def test_lunar_survives_source_death(self):
  self.play('EDR_895');self.p.minions[0].health=0;self.g._settle()
  for _ in range(3):self.cycle()
  self.assertTrue(self.p.full_moon)
 def test_lunar_observation_serializable(self):
  self.play('EDR_895');json.dumps(self.g.observe(1));self.assertTrue(self.p.scheduled_effects)

 def test_replicator_explicit_effect_source(self):
  a=self.g._summon(0,'CORE_CS2_188');b=self.g._summon(1,'CATA_185')
  self.g._deal_effect(b.uid,3,dict(owner=0,source=a,bonus=0,lifesteal=False));self.g._settle()
  self.assertEqual(self.p.minions[0].card_id,'CATA_185')

 def test_full_moon_survives_consecutive_paid_plays(self):
  self.op(('entity_full_moon',))
  for _ in range(2):self.play('CORE_EX1_012')
  c=self.add('CORE_CS2_029');self.assertEqual(self.g._cost(c,0),1)
  self.assertTrue(any(e.get('consume_on_play') is False for e in self.p.cost_effects))
