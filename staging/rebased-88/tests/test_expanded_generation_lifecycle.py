"""Closed Fel Beasts and staged event/choice/turn generation contracts."""
import json,unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch
import test_expanded_generation as fixtures
from expanded import Action,cards
from expanded.game import Card
from expanded import event_generation as eg,exceptional_generation as ex
from expanded.on_draw import CAST_EFFECTS
from expanded.permanents import FEL_BEASTS
from engine.cards import UnsupportedCard
from standard.catalog import load_all_records

class GenerationLifecycleTests(unittest.TestCase):
 def setUp(self):
  self.h=fixtures.GenerationTests();self.g=self.h.game();self.p,self.q=self.g.players
  archive={d['id']:d for d in load_all_records()}
  self.g.cards.update({cid:archive[cid] for cid in eg.RULES.keys()|ex.RULES.keys()|eg.TOKEN_RULES.keys()})
  for table,values in ((cards.RULES,{**eg.RULES,**ex.RULES,**eg.TOKEN_RULES}),(cards.TRIGGERS,eg.TRIGGERS),(CAST_EFFECTS,eg.CAST_EFFECTS)):
   p=patch.dict(table,values);p.start();self.addCleanup(p.stop)
 def put(self,cid):
  c=Card(self.g._new_id(),cid);self.p.hand.append(c);return c
 def play(self,cid,target=0):
  self.p.mana=10;c=self.put(cid)
  a=next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid and a.target==target)
  self.g.step(a);return c
 def outcome(self,request):
  cid='GEN_FIX_'+str(len(self.g.cards));d=deepcopy(self.g.cards['CS3_025'])
  d.update(id=cid,dbfId=-len(self.g.cards),cost=request.minimum,mechanics=[request.mechanic] if request.mechanic else [],races=[request.tribe] if request.tribe else [])
  self.g.cards[cid]=d;self.h.install(self.g,request,[cid]);return cid
 def kill(self,m):self.g._damage(m.uid,99);self.g._settle(allow_event_choices=True)
 def test_maw_registered_with_complete_existing_outcomes(self):
  self.assertIn('TLC_479',cards.COLLECTIBLE_IDS)
  self.assertTrue(set(FEL_BEASTS)<=self.g.cards.keys())
 def test_maw_every_outcome_retains_keywords(self):
  for cid in FEL_BEASTS:
   self.p.board=[];m=self.g._summon(0,'TLC_479')
   with patch.object(self.g.rng,'choice',return_value=cid):self.kill(m)
   self.assertEqual([x.card_id for x in self.p.minions],[cid])
   self.assertTrue(set(self.g.cards[cid]['mechanics'])<=self.p.minions[0].keywords)
 def test_silenced_maw_does_not_generate(self):
  m=self.g._summon(0,'TLC_479');self.g._silence(m);self.kill(m);self.assertFalse(self.p.board)
 def test_maw_death_frees_own_slot(self):
  m=self.g._summon(0,'TLC_479')
  for _ in range(6):self.g._summon(0,'CS3_025')
  self.kill(m);self.assertEqual(len(self.p.board),7)
 def test_vanessa_does_not_trigger_from_own_play(self):
  self.play('JAIL_407');self.assertFalse(self.p.hand)
 def test_vanessa_after_spell_reduces_generated_cost(self):
  cid=self.outcome(eg.BATTLECRY);self.play('JAIL_407');self.play('CORE_CS2_029',-2)
  self.assertEqual([c.card_id for c in self.p.hand],[cid]);self.assertEqual(self.p.hand[0].cost_delta,-2)
 def test_vanessa_after_minion_once(self):
  self.outcome(eg.BATTLECRY);self.play('JAIL_407');self.play('CS3_025');self.assertEqual(len(self.p.hand),1)
 def test_vanessa_after_weapon_and_location(self):
  self.outcome(eg.BATTLECRY);self.play('JAIL_407');self.play('CORE_BT_781');self.play('CATA_584');self.assertEqual(len(self.p.hand),2)
 def test_vanessa_enemy_event_and_silence(self):
  self.outcome(eg.BATTLECRY);self.play('JAIL_407')
  self.g._queue_event('spell_cast',owner=1,card_id='CORE_CS2_029');self.g._settle(allow_event_choices=True);self.assertFalse(self.p.hand)
  self.g._silence(self.p.minions[0]);self.play('CORE_CS2_029',-2);self.assertFalse(self.p.hand)
 def test_vanessa_has_prepare_without_play_event(self):
  c=self.put('JAIL_407');self.assertIn(Action('prepare',source=c.uid),self.g.legal_actions())
  self.g.step(Action('prepare',source=c.uid));self.assertFalse(self.p.board);self.assertFalse(self.p.played_history)
 def test_location_can_target_either_owner_and_reopen(self):
  self.outcome(eg.THREE);loc=self.g._place_location(1,'CATA_584');loc.ready_turn=self.g.turn+4
  # Pool contract belongs to the location's controller.
  self.g._generation_pools[(eg.THREE,self.q.hero_class)]=self.g._generation_pools[(eg.THREE,self.p.hero_class)]
  self.play('TIME_EVENT_997',loc.uid);self.assertEqual(loc.ready_turn,self.g.turn);self.assertEqual(len(loc.attached_death_effects),1)
 def test_location_death_uses_freed_slot_and_stacks(self):
  cid=self.outcome(eg.THREE);loc=self.g._place_location(0,'CATA_584')
  self.play('TIME_EVENT_997',loc.uid);self.play('TIME_EVENT_997',loc.uid)
  self.g._remove_location(loc);self.g._settle(allow_event_choices=True)
  self.assertEqual([m.card_id for m in self.p.minions],[cid,cid])
 def test_location_missing_contract_rolls_back(self):
  loc=self.g._place_location(0,'CATA_584');loc.ready_turn=20;c=self.put('TIME_EVENT_997')
  a=next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid)
  with self.assertRaises(UnsupportedCard):self.g.step(a)
  loc=self.g.players[0].locations[0];self.assertEqual(loc.ready_turn,20);self.assertFalse(loc.attached_death_effects)
 def test_location_view_serializes_attached_effect(self):
  self.outcome(eg.THREE);loc=self.g._place_location(0,'CATA_584');self.play('TIME_EVENT_997',loc.uid)
  json.dumps(self.g.observe(0));other=deepcopy(self.g);self.assertEqual(other.observe(0),self.g.observe(0))
 def test_tripwire_shuffles_two_physical_tokens(self):
  self.outcome(eg.BEAST_FIVE);self.play('JAIL_879');self.assertEqual(len(self.p.minions),1)
  self.assertEqual(sum(self.g._card_data(c)['id']==eg.TRIPWIRE for c in self.p.deck),2)
 def test_tripwire_draw_summons_and_replaces_draw(self):
  cid=self.outcome(eg.BEAST_FIVE);self.p.deck=['CORE_CS2_029',eg.TRIPWIRE]
  self.g._draw(0);self.g._settle(allow_event_choices=True)
  self.assertEqual([m.card_id for m in self.p.minions],[cid]);self.assertEqual([c.card_id for c in self.p.hand],['CORE_CS2_029'])
 def test_tripwire_overdraw_burns_without_cast(self):
  self.outcome(eg.BEAST_FIVE);self.p.deck=[eg.TRIPWIRE]
  for _ in range(10):self.put('CORE_CS2_029')
  self.g._draw(0);self.g._settle(allow_event_choices=True);self.assertFalse(self.p.board)
 def test_murozond_fills_heals_and_schedules_skip(self):
  self.outcome(ex.DRAGON);self.p.health=4;self.play('END_037')
  self.assertEqual(len(self.p.board),7);self.assertEqual(self.p.health,self.p.max_health);self.assertEqual(self.p.skipped_turns_pending,1)
 def test_skipped_turn_has_no_draw_mana_or_owner_turn(self):
  self.p.skipped_turns_pending=1;self.g.step(Action('end'));before=(len(self.p.deck),self.p.max_mana,self.p.turns_taken)
  self.g.step(Action('end'));self.assertEqual(self.g.current,1);self.assertEqual((len(self.p.deck),self.p.max_mana,self.p.turns_taken),before)
  self.assertEqual(self.p.skipped_turns_pending,0)
 def test_skips_stack_and_are_owner_specific(self):
  self.p.skipped_turns_pending=2;self.g.step(Action('end'));self.g.step(Action('end'));self.assertEqual(self.p.skipped_turns_pending,1)
  self.g.step(Action('end'));self.assertEqual(self.p.skipped_turns_pending,0);self.assertEqual(self.g.current,1)
 def test_both_players_skips_terminate_at_turn_limit(self):
  self.p.skipped_turns_pending=100;self.q.skipped_turns_pending=100;self.g.step(Action('end'));self.assertTrue(self.g.terminal)
 def spell_pool(self):self.h.install(self.g,ex.SPELL,['CORE_CS2_029'])
 def test_skeleton_choice_refresh_is_private(self):
  self.spell_pool();self.play('JAIL_319');self.assertEqual(len(self.g.pending_choice['options']),2)
  self.assertNotIn('options',self.g.observe(1).get('pending_choice') or {})
 def choose(self,i=0):self.g.step(Action('choose',choices=(i,)))
 def test_refresh_does_not_count_discover_or_finish_spell(self):
  self.spell_pool();self.play('JAIL_319')
  with patch.object(self.g.rng,'randrange',return_value=1):self.choose(1)
  self.assertEqual(self.p.discoveries_total,0);self.assertEqual(self.g.phase,'choice');self.assertFalse(self.p.hand)
  self.choose();self.assertEqual(self.p.discoveries_total,1);self.assertEqual(len(self.p.hand),1);self.assertEqual(self.g.phase,'play')
 def test_refresh_can_damage_hero_without_spell_bonus(self):
  self.spell_pool();self.play('JAIL_319');self.p.armor=2
  with patch.object(self.g.rng,'randrange',return_value=0):self.choose(1)
  self.assertEqual(self.p.health,27);self.assertEqual(self.p.armor,0);self.assertEqual(self.p.spell_damage_turn,0)
 def test_refresh_lethal_ends_game(self):
  self.spell_pool();self.play('JAIL_319');self.p.health=4
  with patch.object(self.g.rng,'randrange',return_value=0):self.choose(1)
  self.assertTrue(self.g.terminal);self.assertFalse(self.p.hand)
 def test_refresh_clone_replays(self):
  self.spell_pool();self.play('JAIL_319');other=deepcopy(self.g);a=Action('choose',choices=(1,))
  self.g.step(a);other.step(a);self.assertEqual(self.g.observe(0),other.observe(0))
 def test_missing_skeleton_contract_rolls_back_paid_play(self):
  c=self.put('JAIL_319');a=next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid)
  with self.assertRaises(UnsupportedCard):self.g.step(a)
  self.assertEqual(self.g.players[0].mana,10);self.assertEqual(len(self.g.players[0].hand),1)
