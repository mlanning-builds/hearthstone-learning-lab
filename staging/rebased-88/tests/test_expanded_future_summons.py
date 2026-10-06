"""Persistent summon families with controlled, explicitly incomplete pools."""
import json,unittest
from copy import deepcopy
from unittest.mock import patch
import test_expanded_generation as fixtures
from expanded import Action,cards
from expanded.future_summons import RULES,DEATH_EFFECTS,WEAPON_TRIGGERS,COMPANIONS
from expanded.generation_cards import pool
from expanded.pools import GenerationPool
from engine.game import Card
from engine.cards import UnsupportedCard
from standard.catalog import load_catalog

class FutureSummonTests(unittest.TestCase):
 def setUp(self):
  self.g=fixtures.GenerationTests().game();self.g._generation_pools={}
  self.g.cards.update({c['id']:c for c in load_catalog() if c['id'] in RULES})
  for table,values in ((cards.RULES,RULES),(cards.DEATH_EFFECTS,DEATH_EFFECTS),(cards.WEAPON_TRIGGERS,WEAPON_TRIGGERS)):
   context=patch.dict(table,values);context.start();self.addCleanup(context.stop)
 @property
 def p(self):return self.g.players[0]
 @property
 def q(self):return self.g.players[1]
 def op(self,operation,**kwargs):
  context=dict(owner=0,source=None,target=0,bonus=0,lifesteal=False);context.update(kwargs)
  self.g._start_play_effects([operation],context);self.g._settle(allow_event_choices=True)
 def add(self,cid):
  c=Card(self.g._new_id(),cid);self.g._enter_hand(0,c);return c
 def play(self,cid,target=0):
  self.p.mana=10;c=self.add(cid)
  self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid and a.target==target));return c
 def install(self,tribe,cost,ids,owner=0):
  request=pool(card_type='MINION',tribe=tribe,minimum=cost,maximum=cost)
  self.g._generation_pools[(request,self.g.players[owner].hero_class)]=GenerationPool('fixture',tuple(ids),'Controlled membership only')
 def fake(self,cid,cost,tribe='BEAST'):
  self.g.cards[cid]=dict(id=cid,name=cid,cardClass='NEUTRAL',type='MINION',cost=cost,attack=2,health=3,races=[tribe],mechanics=[]);return cid
 def choose(self,i=0):self.g.step(Action('choose',choices=(i,)))
 def test_eight_definitions_one_admitted(self):
  from expanded.pending_definitions import DEFINITIONS
  self.assertEqual(set(RULES)-cards.COLLECTIBLE_IDS,{c for c,d in DEFINITIONS.items() if d['family'] in ('animal_companion','void_soul')})
  self.assertEqual(set(RULES)&cards.COLLECTIBLE_IDS,{'MEND_304'})
 def test_companions_default_choices_match_original_order(self):
  self.play('MEND_301');self.assertEqual([o['card_id'] for o in self.g.pending_choice['options']],list(reversed(COMPANIONS)));self.choose(0);self.assertEqual(self.p.minions[-1].card_id,'NEW1_034')
 def test_replacement_rolls_three_stable_slots(self):
  ids=[self.fake('PET_A',4),self.fake('PET_B',4)];self.install('BEAST',4,ids);self.play('MEND_300');state=list(self.p.companion_ids)
  self.assertEqual(len(state),3);self.assertTrue(set(state)<=set(ids));self.assertEqual(len(self.p.hand),1)
  for _ in range(3):self.op(('companions_random',))
  self.assertEqual(self.p.companion_ids,state);self.assertTrue(all(m.card_id in state for m in self.p.minions))
 def test_replacement_does_not_transform_existing_board(self):
  m=self.g._summon(0,'NEW1_034');self.install('BEAST',4,[self.fake('PET_A',4)]);self.play('MEND_300');self.assertEqual(m.card_id,'NEW1_034')
 def test_successive_replacements_use_current_printed_cost(self):
  self.install('BEAST',4,[self.fake('PET_A',4)]);self.install('BEAST',5,[self.fake('PET_B',5)])
  self.play('MEND_300');self.play('MEND_303');self.assertEqual(self.p.companion_ids,['PET_B']*3);self.assertEqual(self.p.companion_upgrades,2)
 def test_each_replacement_slot_has_its_own_cost(self):
  self.p.companion_ids=[self.fake('OLD3',3),self.fake('OLD5',5),self.fake('OLD8',8)]
  for cost in (4,6,9):self.install('BEAST',cost,[self.fake('PET'+str(cost),cost)])
  self.op(('companions_replace',1));self.assertEqual(self.p.companion_ids,['PET4','PET6','PET9'])
 def test_missing_pool_rolls_back_payment_and_replacements(self):
  c=self.add('MEND_300');before=(self.p.mana,self.g.rng.getstate(),list(self.p.companion_ids))
  with self.assertRaises(UnsupportedCard):self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid))
  self.assertEqual((self.p.mana,self.g.rng.getstate(),self.p.companion_ids),before)
 def test_empty_successor_does_not_invent_cap_or_keep_rule(self):
  self.install('BEAST',4,[]);before=self.g.rng.getstate()
  with self.assertRaises(UnsupportedCard):self.op(('companions_replace',1))
  self.assertEqual(self.p.companion_ids,list(COMPANIONS));self.assertEqual(self.g.rng.getstate(),before)
 def test_replacement_ids_private_but_upgrade_counters_public(self):
  self.install('BEAST',4,[self.fake('SECRET_PET',4)]);self.play('MEND_300')
  own=self.g.observe(0);other=self.g.observe(1)
  self.assertEqual(own['players'][0]['companion_ids'],['SECRET_PET']*3);self.assertNotIn('companion_ids',other['players'][0]);self.assertNotIn('SECRET_PET',json.dumps(other));self.assertEqual(other['players'][0]['companion_upgrades'],1)
 def test_talya_one_bonus_per_call_of_wild(self):
  self.play('MEND_304');self.play('CORE_OG_211');self.assertEqual(len(self.p.minions),5)
  self.assertEqual([m.card_id for m in self.p.minions[1:4]],list(reversed(COMPANIONS)))
 def test_talya_stacks_and_survives_source_silence(self):
  self.play('MEND_304');self.op(('companions_extra',1));self.g._silence(self.p.minions[0]);self.play('CORE_NEW1_031');self.assertEqual(len(self.p.minions),4)
 def test_selected_companion_bonus_is_random_not_repeated_selection(self):
  self.p.companion_extra=1;self.play('MEND_301')
  with patch.object(self.g.rng,'choice',return_value='NEW1_032'):self.choose(0)
  self.assertEqual([m.card_id for m in self.p.minions[-2:]],['NEW1_034','NEW1_032']);self.assertEqual(self.p.discoveries_total,0)
 def test_extra_counter_is_not_truncated_to_seven(self):
  self.p.companion_extra=9
  # Remove each summon immediately to keep a slot available through the chain.
  original=self.g._summon;seen=[]
  def summon(*args,**kwargs):
   m=original(*args,**kwargs)
   if m is not None:seen.append(m);self.p.board.remove(m)
   return m
  with patch.object(self.g,'_summon',side_effect=summon):self.op(('companions_random',))
  self.assertEqual(len(seen),10)
 def test_roam_free_upgrades_then_chooses(self):
  self.install('BEAST',5,[self.fake('PET5',5)]);self.play('MEND_307');self.assertEqual([o['card_id'] for o in self.g.pending_choice['options']],['PET5']*3)
  self.choose();self.assertEqual(self.p.minions[0].card_id,'PET5');self.assertEqual(self.p.discoveries_total,0)
 def test_replacements_and_bonus_belong_to_one_owner(self):
  self.p.companion_extra=1;self.install('BEAST',4,[self.fake('PET4',4)]);self.play('MEND_300');self.op(('companions_random',),owner=1)
  self.assertEqual(len(self.q.minions),1);self.assertIn(self.q.minions[0].card_id,COMPANIONS)
 def test_live_spell_trigger_uses_upgraded_companions(self):
  self.p.companion_ids=[self.fake('PET4',4)]*3;self.p.companion_extra=1;self.g._summon(0,'EDR_853');self.play('TOKEN_COIN');self.assertEqual([m.card_id for m in self.p.minions[1:]],['PET4','PET4'])
 def test_elekk_intrinsic_taunt_is_not_a_battlecry(self):
  m=self.g._summon(0,'MEND_303');self.assertIn('TAUNT',self.g._effective_keywords(m));self.assertEqual(self.p.companion_ids,list(COMPANIONS));self.g._silence(m);self.assertNotIn('TAUNT',self.g._effective_keywords(m))
 def test_internal_companion_choice_is_automatic(self):
  self.install('BEAST',5,[self.fake('PET5',5)]);self.op(('cast_fixed_spell','MEND_307','random'));self.assertIsNone(self.g.pending_choice);self.assertEqual(self.p.minions[0].card_id,'PET5')
 def test_void_soul_uses_then_improves_owner_level(self):
  for cost in (1,2):self.install('DEMON',cost,[self.fake('DEMON'+str(cost),cost,'DEMON')])
  self.play('JAIL_732');self.play('JAIL_732');self.assertEqual([m.card_id for m in self.p.minions],['DEMON1','DEMON2']);self.assertEqual(self.p.void_soul_level,3);self.assertEqual(self.q.void_soul_level,1)
 def test_generated_and_existing_souls_use_same_future_level(self):
  for cost in (1,2):self.install('DEMON',cost,[self.fake('DEMON'+str(cost),cost,'DEMON')])
  held=self.add('JAIL_732');self.play('JAIL_732');self.p.mana=10
  self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==held.uid));self.assertEqual(self.p.minions[-1].card_id,'DEMON2')
 def test_void_soul_full_board_still_improves(self):
  self.install('DEMON',1,[self.fake('DEMON1',1,'DEMON')])
  for _ in range(7):self.g._summon(0,'CORE_CS2_188')
  self.play('JAIL_732');self.assertEqual(self.p.void_soul_level,2);self.assertEqual(len(self.p.minions),7)
 def test_void_soul_missing_pool_does_not_upgrade(self):
  with self.assertRaises(UnsupportedCard):self.play('JAIL_732')
  self.assertEqual(self.p.void_soul_level,1);self.assertEqual(self.p.mana,10)
 def test_void_soul_level_ten_remains_at_candidate_cap(self):
  self.p.void_soul_level=10;self.install('DEMON',10,[self.fake('DEMON10',10,'DEMON')]);self.play('JAIL_732');self.assertEqual(self.p.void_soul_level,10)
 def test_voidscale_death_adds_soul_but_silence_suppresses(self):
  self.g._summon(0,'JAIL_733').health=0;self.g._settle();self.assertEqual([c.card_id for c in self.p.hand],['JAIL_732'])
  m=self.g._summon(0,'JAIL_733');self.g._silence(m);m.health=0;self.g._settle();self.assertEqual(len(self.p.hand),1)
 def test_scythe_last_swing_still_adds_soul(self):
  self.g._equip(0,'JAIL_730');self.p.weapon['durability']=1;self.g.step(Action('attack',self.g.hero_id(0),self.g.hero_id(1)));self.assertIsNone(self.p.weapon);self.assertEqual([c.card_id for c in self.p.hand],['JAIL_732'])
 def test_void_blast_kill_awards_soul(self):
  m=self.g._summon(1,'CORE_CS2_188');self.play('JAIL_891',m.uid);self.assertEqual([c.card_id for c in self.p.hand],['JAIL_732'])
 def test_void_blast_shield_and_survival_no_soul(self):
  m=self.g._summon(1,'CORE_CS2_188');m.keywords.add('DIVINE_SHIELD');self.play('JAIL_891',m.uid);self.assertFalse(self.p.hand)
 def test_future_state_clones_and_encodes(self):
  self.p.void_soul_level=4;self.p.companion_extra=2;g=deepcopy(self.g)
  self.assertEqual(g.players[0].void_soul_level,4);self.assertEqual(g.observe(1)['players'][0]['companion_extra'],2)
  from expanded.features import encode_decision
  view=g.observe(0);rows=encode_decision(dict(actor=0,observation=view,actions=view['legal_actions']));self.assertTrue(rows)

 def test_void_blast_spell_damage_changes_kill_outcome(self):
  self.g._summon(0,'CORE_EX1_012');m=self.g._summon(1,'JAIL_733');self.play('JAIL_891',m.uid)
  self.assertEqual([c.card_id for c in self.p.hand],['JAIL_732']);self.assertEqual([c.card_id for c in self.q.hand],['JAIL_732'])
 def test_void_blast_reborn_is_not_an_extra_reward(self):
  m=self.g._summon(1,'CORE_CS2_188');m.keywords.add('REBORN');self.play('JAIL_891',m.uid)
  self.assertEqual([c.card_id for c in self.p.hand],['JAIL_732']);self.assertEqual(len(self.q.minions),1)
 def test_companion_full_board_preserves_slots_and_rng(self):
  for _ in range(7):self.g._summon(0,'CORE_CS2_188')
  self.p.companion_extra=9;before=self.g.rng.getstate();self.op(('companions_random',))
  self.assertEqual(len(self.p.minions),7);self.assertEqual(self.g.rng.getstate(),before)
