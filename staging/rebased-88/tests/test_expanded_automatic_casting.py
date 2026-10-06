"""Controlled-pool automatic casting checks; not full pool certification."""
import unittest
from copy import deepcopy
from unittest.mock import patch
import test_expanded_generation as fixtures
from expanded import Action,cards,locations
from expanded.automatic_casting import RULES,TRIGGERS,END_EFFECTS,UNRESOLVED,MAGE_SECRETS,SECRETS,LOCATION_RULES
from expanded.generation_cards import pool
from expanded.pools import GenerationPool
from engine.game import Card
from engine.cards import UnsupportedCard
from standard.catalog import load_catalog
class AutomaticCastingTests(unittest.TestCase):
 def setUp(self):
  self.g=fixtures.GenerationTests().game();self.g._generation_pools={}
  self.g.cards.update({c['id']:c for c in load_catalog() if c['id'] in RULES})
  for table,values in ((locations.LOCATION_RULES,LOCATION_RULES),(cards.RULES,RULES),(cards.TRIGGERS,TRIGGERS),(cards.END_EFFECTS,END_EFFECTS)):
   context=patch.dict(table,values);context.start();self.addCleanup(context.stop)
 @property
 def p(self):return self.g.players[0]
 @property
 def q(self):return self.g.players[1]
 def install(self,request,ids):self.g._generation_pools[(request,self.p.hero_class)]=GenerationPool('fixture',tuple(ids),'Controlled fixture only')
 def op(self,operation,**kwargs):
  context=dict(owner=0,source=None,target=0,bonus=0,lifesteal=False);context.update(kwargs)
  self.g._start_play_effects([operation],context);self.g._settle(allow_event_choices=True)
 def play(self,cid):
  c=Card(self.g._new_id(),cid);self.g._enter_hand(0,c)
  self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid));return c
 def test_family_accounted_for(self):
  from expanded.pending_definitions import DEFINITIONS
  from expanded.gelbin import RULES as PLACEMENT_RULES
  self.assertEqual((set(RULES)|set(UNRESOLVED)|set(PLACEMENT_RULES))-cards.COLLECTIBLE_IDS,{cid for cid,d in DEFINITIONS.items() if d['family']=='automatic_casting'}|{'EDR_031','JAIL_500'})
  self.assertEqual(DEFINITIONS['EDR_031']['family'],'automatic_play')
  self.assertTrue(all(self.g.cards[cid]['type']=='LOCATION' for cid in LOCATION_RULES))
  self.assertEqual(set(RULES)&cards.COLLECTIBLE_IDS,{'TLC_430'})
 def test_shrine_spends_available_mana_and_casts_exact_cost(self):
  self.play('EDR_520');self.p.mana=4;self.install(pool(card_type='SPELL',minimum=4,maximum=4),['CORE_CS2_029'])
  before=self.p.health+self.q.health;self.g.step(Action('activate',self.p.locations[0].uid))
  self.assertEqual(self.p.mana,0);self.assertEqual(self.p.health+self.q.health,before-6)
  self.assertEqual(self.p.spells_turn,[]);self.assertEqual(self.p.cards_played,1)
 def test_shrine_uses_available_not_maximum_mana(self):
  self.play('EDR_520');self.p.mana=0;self.p.max_mana=10;self.install(pool(card_type='SPELL',minimum=0,maximum=0),[])
  self.g.step(Action('activate',self.p.locations[0].uid));self.assertEqual(self.p.mana,0)
 def test_missing_shrine_pool_rolls_back(self):
  self.play('EDR_520');self.p.mana=4;location=self.p.locations[0];rng=self.g.rng.getstate()
  with self.assertRaises(UnsupportedCard):self.g.step(Action('activate',location.uid))
  self.assertEqual(self.g.players[0].mana,4);self.assertEqual(self.g.rng.getstate(),rng);self.assertEqual(self.g.players[0].locations[0].durability,3)
 def test_unsupported_internal_outcome_not_filtered(self):
  request=pool(card_type='SPELL',minimum=4,maximum=4);self.install(request,['CORE_CS2_029','FIX_UNSUPPORTED'])
  self.g.cards['FIX_UNSUPPORTED']=dict(id='FIX_UNSUPPORTED',name='x',type='SPELL',cardClass='MAGE',cost=4)
  self.p.mana=4
  with self.assertRaises(UnsupportedCard):self.op(('autocast_spend_mana',))
  self.assertEqual(self.p.mana,4)
 def test_chaos_matches_paid_cost_and_other_class(self):
  self.install(pool(card_type='SPELL',minimum=1,maximum=1,classes='other'),['CORE_CS2_004'])
  self.g._summon(0,'CATA_786');self.g._queue_event('spell_cast',owner=0,card_id='CORE_CS2_029',cost=1)
  size=len(self.p.hand);self.g._settle(allow_event_choices=True);self.assertEqual(len(self.p.hand),size+1)
 def test_chaos_does_not_retrigger_on_internal_cast(self):
  self.g._summon(0,'CATA_786');self.op(('cast_fixed_spell','CORE_CS2_004','random'));self.assertEqual(self.p.spells_turn,[])
 def test_silenced_chaos_does_not_cast(self):
  m=self.g._summon(0,'CATA_786');self.g._silence(m);self.g._queue_event('spell_cast',owner=0,card_id='CORE_CS2_029',cost=4);self.g._settle();self.assertFalse(self.p.hand)
 def test_manastorm_survives_source_removal(self):
  self.play('JAIL_122');m=self.p.minions[0];m.health=0;self.g._settle()
  self.install(pool(card_type='MINION',minimum=2,maximum=2),['CORE_EX1_012'])
  self.g._queue_event('spell_cast',owner=0,card_id='TOKEN_COIN',cost=2);self.g._settle(allow_event_choices=True)
  self.assertEqual([m.card_id for m in self.p.minions],['CORE_EX1_012'])
 def test_multiple_manastorm_effects_stack(self):
  self.op(('autocast_install_manastorm',));self.op(('autocast_install_manastorm',));self.install(pool(card_type='MINION',minimum=2,maximum=2),['CORE_EX1_012'])
  self.g._queue_event('spell_cast',owner=0,card_id='TOKEN_COIN',cost=2);self.g._settle(allow_event_choices=True);self.assertEqual(len(self.p.minions),2)
 def test_manastorm_ignores_opponent_and_internal_casts(self):
  self.op(('autocast_install_manastorm',));self.g._queue_event('spell_cast',owner=1,card_id='TOKEN_COIN',cost=0);self.g._settle();self.op(('cast_fixed_spell','TOKEN_COIN','random'));self.assertFalse(self.p.minions)
 def test_manastorm_state_public_and_cloned(self):
  self.op(('autocast_install_manastorm',));self.assertEqual(self.g.observe(1)['players'][0]['manastorm_effects'],1);self.assertEqual(deepcopy(self.g).players[0].manastorm_effects,1)
 def test_tricksy_no_prior_spell_no_pool_needed(self):self.play('JAIL_321');self.assertFalse(self.p.secrets)
 def test_tricksy_two_casts_duplicate_secret_does_not_stack(self):
  self.p.spells_turn=['TOKEN_COIN'];self.install(MAGE_SECRETS,['CORE_EX1_287']);self.play('JAIL_321');self.assertEqual(len(self.p.secrets),1)
 def test_tricksy_prepare_available(self):
  c=Card(self.g._new_id(),'JAIL_321');self.p.hand.append(c);self.assertTrue(any(a.kind=='prepare' and a.source==c.uid for a in self.g.legal_actions()))
 def test_secret_pair_choice_private_and_not_discover(self):
  self.install(SECRETS,['CORE_EX1_287','CORE_EX1_289']);self.play('TIME_860')
  self.assertEqual(self.g.observe(1)['pending_choice'],{'owner':0,'waiting':True});self.assertEqual(len(self.g.pending_choice['options']),2)
  self.g.step(Action('choose',choices=(0,)));self.assertEqual(len(self.p.secrets),1);self.assertEqual(len(self.q.secrets),1);self.assertEqual(self.p.discoveries_total,0)
 def test_secret_pair_empty_pool_no_choice(self):
  self.install(SECRETS,[]);self.play('TIME_860');self.assertIsNone(self.g.pending_choice)
 def test_holy_history_prefers_source_and_ignores_other_schools(self):
  m=self.g._summon(0,'TLC_430');m.health-=1;self.p.spells_turn=['CORE_CS2_029','CORE_CS2_004'];before=len(self.p.hand)
  self.op(('autocast_holy_history',),source=m);self.assertEqual((m.health,m.max_health),(6,7));self.assertEqual(len(self.p.hand),before+1)
 def test_holy_empty_history_no_effect(self):
  self.op(('autocast_holy_history',));self.assertFalse(self.p.hand)
 def test_holy_end_trigger_runs(self):
  m=self.g._summon(0,'TLC_430');m.health-=1;self.p.spells_turn=['CORE_CS2_004'];self.g.step(Action('end'));self.assertEqual((m.health,m.max_health),(6,7))

 def test_shrine_play_does_not_activate_or_require_pool(self):
  self.play('EDR_520');self.assertEqual(self.p.mana,9);self.assertEqual(len(self.p.locations),1);self.assertEqual(self.p.locations[0].durability,3)
 def test_shrine_last_charge_removed_and_cooldown(self):
  self.play('EDR_520');self.install(pool(card_type='SPELL',minimum=0,maximum=0),[]);self.p.mana=0;l=self.p.locations[0]
  self.g.step(Action('activate',l.uid));self.assertEqual(l.durability,2);self.assertFalse(any(a.kind=='activate' for a in self.g.legal_actions()))
  l.ready_turn=self.g.turn;l.durability=1;self.g.step(Action('activate',l.uid));self.assertFalse(self.p.locations)

 def test_all_live_holy_spells_have_internal_cast_support(self):
  from expanded.selectors import has_school
  self.assertEqual([cid for cid,d in cards.registry().items() if d['type']=='SPELL' and has_school(d,'HOLY') and not self.g._supports_internal_spell(cid)],[])
