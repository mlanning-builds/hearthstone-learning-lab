"""Rewind generation bodies and repeated timelines, using controlled pools only."""
import copy,json,unittest
from unittest.mock import patch
import test_expanded_generation as fixtures
from expanded import Action
from expanded import cards
from expanded.rewind_generators import RULES,DEATH_EFFECTS,REWINDS,UNRESOLVED,requests_for,BUDGET_POOL,HOLY,NATURE,WEAPON,ANY_SPELL,OWN_SPELL,BEAST_GIFT
from expanded.generation_cards import pool
from expanded.pools import GenerationPool
from engine.game import Card
from engine.cards import UnsupportedCard
from standard.catalog import load_catalog

class RewindGeneratorTests(unittest.TestCase):
 def setUp(self):
  self.g=fixtures.GenerationTests().game();self.g._generation_pools={};self.g._dark_generation_pools={}
  self.g.cards.update({c['id']:c for c in load_catalog() if c['id'] in RULES})
  for table,values in ((cards.RULES,RULES),(cards.DEATH_EFFECTS,DEATH_EFFECTS)):
   context=patch.dict(table,values);context.start();self.addCleanup(context.stop)
 @property
 def p(self):return self.g.players[0]
 @property
 def q(self):return self.g.players[1]
 def install(self,request,ids,owner=0):
  self.g._generation_pools[(request,self.g.players[owner].hero_class)]=GenerationPool('fixture only',tuple(ids),'Controlled fixture; not reviewed Standard membership')
 def fake(self,cid,cost=3,attack=2,health=3,**extra):
  self.g.cards[cid]=dict(id=cid,name=cid,type='MINION',cardClass='NEUTRAL',cost=cost,attack=attack,health=health,mechanics=[],**extra);return cid
 def add(self,cid):
  c=Card(self.g._new_id(),cid);self.g._enter_hand(0,c);return c
 def play(self,cid):
  c=self.add(cid);self.p.mana=10;self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid));return c
 def choose(self,index=0):self.g.step(Action('choose',choices=(index,)))
 def keep(self):self.assertEqual(self.g.pending_choice['kind'],'rewind');self.choose(0)
 def reroll(self):self.assertEqual(self.g.pending_choice['kind'],'rewind');self.choose(1)
 def op(self,op,**context):
  ctx=dict(owner=0,source=None,target=0,bonus=0,lifesteal=False);ctx.update(context);self.g._start_play_effects([op],ctx);self.g._settle(allow_event_choices=True)
 def test_remaining_family_accounted_for(self):
  from expanded.pending_definitions import DEFINITIONS
  from expanded.morchie import RULES as SHARED_RULES
  self.assertEqual(set(RULES)|set(UNRESOLVED)|set(SHARED_RULES),{cid for cid,d in DEFINITIONS.items() if d['family']=='rewind'})
  self.assertFalse(set(SHARED_RULES)&cards.COLLECTIBLE_IDS)
  self.assertFalse(set(RULES)&cards.COLLECTIBLE_IDS);self.assertEqual(REWINDS['TIME_038'],3);self.assertNotIn('TIME_035',REWINDS)
 def test_portal_discount_and_reroll_no_extra_card(self):
  self.install(pool(card_type='MINION'),['CORE_EX1_012']);self.play('TIME_000');mana=self.p.mana;self.reroll()
  self.assertEqual(len(self.p.hand),1);self.assertEqual(self.p.hand[0].cost_delta,-3);self.assertEqual(self.p.mana,mana);self.assertEqual(self.p.cards_played,1)
 def test_missing_pool_rejected_before_payment(self):
  c=self.add('TIME_000');before=(self.p.mana,self.g.rng.getstate())
  with self.assertRaises(UnsupportedCard):self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid))
  self.assertEqual((self.p.mana,self.g.rng.getstate()),before);self.assertIn(c.uid,[c.uid for c in self.p.hand])
 def test_unsupported_outcomes_never_filtered(self):
  self.install(pool(card_type='MINION'),['CORE_EX1_012','missing'])
  with self.assertRaises(UnsupportedCard):self.play('TIME_000')
  self.assertEqual(self.p.mana,10)
 def test_wizard_two_own_class_spells_per_final_timeline(self):
  self.install(OWN_SPELL,['CORE_CS2_029']);self.play('TIME_002');self.reroll();self.assertEqual([c.card_id for c in self.p.hand],['CORE_CS2_029']*2);self.assertEqual(len(self.p.minions),1)
 def test_own_class_contract_rejects_wrong_class(self):
  self.install(OWN_SPELL,['CORE_CS2_004'])
  with self.assertRaises(UnsupportedCard):self.play('TIME_002')
 def test_clocksworth_three_rerolls_keep_only_two_summons(self):
  cid=self.fake('FIX_LEGEND',rarity='LEGENDARY');self.install(pool(card_type='MINION',rarity='LEGENDARY'),[cid]);self.play('TIME_038')
  for remaining in (3,2,1):
   self.assertEqual(self.g.pending_choice['remaining'],remaining);self.assertEqual(self.g.observe(0)['pending_choice']['remaining'],remaining);self.reroll()
  self.assertIsNone(self.g.pending_choice);self.assertEqual([m.card_id for m in self.p.minions],['TIME_038',cid,cid]);self.assertEqual(self.p.cards_played,1)
 def test_clocksworth_keep_ends_choice_early(self):
  self.install(pool(card_type='MINION',rarity='LEGENDARY'),['CORE_EX1_012']);self.play('TIME_038');self.reroll();self.keep();self.assertIsNone(self.g.pending_choice);self.assertEqual(len(self.p.minions),3)
 def test_multiple_rewind_budget_private_to_chooser(self):
  self.install(pool(card_type='MINION',rarity='LEGENDARY'),['CORE_EX1_012']);self.play('TIME_038');self.assertEqual(self.g.observe(1)['pending_choice'],{'owner':0,'waiting':True});self.assertNotIn('snapshot',json.dumps(self.g.observe(0)))
 def test_clocksworth_bounce_preserves_two_remaining(self):
  self.install(pool(card_type='MINION',rarity='LEGENDARY'),['CORE_EX1_012']);self.play('TIME_038');self.reroll();self.keep();m=next(m for m in self.p.minions if m.card_id=='TIME_038');self.g._bounce(m);c=self.p.hand[0];self.p.mana=10;self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid));self.assertEqual(self.g.pending_choice['remaining'],2)
 def test_budget_spends_printed_cost_until_twelve(self):
  cid=self.fake('FIX_THREE');self.install(BUDGET_POOL,[cid]);self.play('TIME_014');self.assertEqual(len(self.p.minions),4);self.keep()
 def test_budget_reroll_restores_board_and_overload(self):
  cid=self.fake('FIX_THREE');self.install(BUDGET_POOL,[cid]);self.play('TIME_014');overload=self.p.overload_next;self.reroll();self.assertEqual(len(self.p.minions),4);self.assertEqual(self.p.overload_next,overload)
 def test_budget_zero_cost_outcomes_stop_at_full_board(self):
  cid=self.fake('FIX_ZERO',0);self.install(BUDGET_POOL,[cid]);self.play('TIME_014');self.assertEqual(len(self.p.minions),7)
 def test_budget_stops_if_remaining_cannot_fit(self):
  cid=self.fake('FIX_SEVEN',7);self.install(BUDGET_POOL,[cid]);self.play('TIME_014');self.assertEqual(len(self.p.minions),1)
 def test_budget_no_overspend_or_supported_subset(self):
  cid=self.fake('FIX_THIRTEEN',13);self.install(BUDGET_POOL,[cid])
  with self.assertRaises(UnsupportedCard):self.play('TIME_014')
  self.assertFalse(self.p.minions)
 def test_budget_empty_contract_terminates_with_rewind(self):
  self.install(BUDGET_POOL,[]);self.play('TIME_014');self.assertEqual(self.g.pending_choice['kind'],'rewind');self.assertFalse(self.p.minions)
 def test_holy_heals_combined_cost_once(self):
  self.install(HOLY,['CORE_CS2_004']);self.p.health=10
  with patch.object(self.g,'_heal',wraps=self.g._heal) as heal:
   self.play('TIME_018');amount=self.g.cards['CORE_CS2_004']['cost']*2;self.assertEqual(self.p.health,10+amount);self.assertEqual(heal.call_count,1)
  self.assertEqual(len(self.p.hand),2)
 def test_holy_reroll_does_not_stack_heal_or_cards(self):
  self.install(HOLY,['CORE_CS2_004']);self.p.health=10;self.play('TIME_018');health=self.p.health;self.reroll();self.assertEqual(self.p.health,health);self.assertEqual(len(self.p.hand),2)
 def test_holy_heals_even_if_hand_full(self):
  for _ in range(9):self.add('TOKEN_COIN')
  self.install(HOLY,['CORE_CS2_004']);self.p.health=10;self.play('TIME_018');self.assertEqual(len(self.p.hand),10);self.assertEqual(self.p.health,10+2*self.g.cards['CORE_CS2_004']['cost'])
 def test_weapon_equip_both_buff_only_own(self):
  weapon=next(cid for cid,d in self.g.cards.items() if d['type']=='WEAPON')
  for owner in (0,1):self.install(WEAPON,[weapon],owner)
  self.play('TIME_034');self.assertEqual(self.p.weapon['attack'],self.q.weapon['attack']+1);self.assertEqual(self.p.weapon['durability'],self.q.weapon['durability']+1)
 def test_weapon_reroll_preserves_single_buff(self):
  weapon=next(cid for cid,d in self.g.cards.items() if d['type']=='WEAPON')
  for owner in (0,1):self.install(WEAPON,[weapon],owner)
  self.play('TIME_034');before=copy.deepcopy(self.p.weapon);self.reroll();self.assertEqual(self.p.weapon,before)
 def test_opponent_weapon_contract_required_before_payment(self):
  self.install(WEAPON,[])
  with self.assertRaises(UnsupportedCard):self.play('TIME_034')
  self.assertEqual(self.p.mana,10);self.assertFalse(self.p.minions)
 def test_wormhole_attacks_and_reroll_keeps_one_result(self):
  cid=self.fake('FIX_BEAST',3,4,5,races=['BEAST']);self.install(pool(card_type='MINION',tribe='BEAST',minimum=3,maximum=3),[cid]);self.play('TIME_602');self.assertEqual(self.q.health,26);self.reroll();self.assertEqual(self.q.health,26);self.assertEqual(len(self.p.minions),1)
 def test_time_machine_death_generates_without_rewind_choice(self):
  self.install(pool(mechanic='REWIND'),['TIME_001']);m=self.g._summon(0,'TIME_035');m.health=0;self.g._settle();self.assertEqual([c.card_id for c in self.p.hand],['TIME_001']);self.assertIsNone(self.g.pending_choice)
 def test_time_machine_silence_removes_generation(self):
  m=self.g._summon(0,'TIME_035');self.g._silence(m);m.health=0;self.g._settle();self.assertFalse(self.p.hand)
 def test_sands_changes_pool_after_rewind(self):
  self.install(ANY_SPELL,['CORE_CS2_004']);self.install(OWN_SPELL,['CORE_CS2_029']);self.play('TIME_EVENT_999');self.assertEqual(self.g.pending_choice['options'][0]['card_id'],'CORE_CS2_004');self.choose();self.reroll();self.assertEqual(self.g.pending_choice['options'][0]['card_id'],'CORE_CS2_029');self.choose();self.assertEqual([c.card_id for c in self.p.hand],['CORE_CS2_029']);self.assertEqual(self.p.discoveries_total,1)
 def test_sands_validates_both_timeline_pools_before_play(self):
  self.install(ANY_SPELL,['CORE_CS2_004'])
  with self.assertRaises(UnsupportedCard):self.play('TIME_EVENT_999')
  self.assertEqual(self.p.mana,10)
 def test_raptor_dark_gift_choice_then_rewind(self):
  cid=self.fake('FIX_BEAST',3,4,5,races=['BEAST']);self.g._dark_generation_pools[(BEAST_GIFT,self.p.hero_class)]=GenerationPool('fixture',(cid,),'controlled')
  self.play('CORE_EDR_004_2026');self.assertEqual(self.g.pending_choice['kind'],'dark_global');self.g.pending_choice['options'][0]['dark_gift']='EDR_100t';self.choose();self.reroll();self.assertEqual(self.g.pending_choice['kind'],'dark_global');self.g.pending_choice['options'][0]['dark_gift']='EDR_100t';self.choose();self.assertEqual(len(self.p.hand),1);self.assertEqual(self.p.discoveries_total,1)
 def test_raptor_kindred_discount(self):
  cid=self.fake('FIX_BEAST',3,4,5,races=['BEAST']);self.g._dark_generation_pools[(BEAST_GIFT,self.p.hero_class)]=GenerationPool('fixture',(cid,),'controlled');self.op(('rewindgen_gift',),kindred=True);self.g.pending_choice['options'][0]['dark_gift']='EDR_100t';self.choose();self.assertEqual(self.p.hand[0].cost_delta,-1)
 def test_nature_casts_twice_without_counting_as_paid_spells(self):
  self.install(NATURE,['CORE_EX1_154']);self.play('TIME_033');self.assertEqual(self.p.cards_played,1);self.assertEqual(self.g.pending_choice['kind'],'rewind');self.reroll();self.assertEqual(self.p.cards_played,1)
 def test_nature_unsupported_internal_outcome_rejected_before_rng(self):
  cid=self.fake('FIX_NATURE');self.g.cards[cid].update(type='SPELL',spellSchool='NATURE');self.install(NATURE,[cid]);before=self.g.rng.getstate()
  with self.assertRaisesRegex(UnsupportedCard,'internal support'):self.play('TIME_033')
  self.assertEqual(before,self.g.rng.getstate());self.assertEqual(self.p.mana,10)
 def test_empty_nature_pool_is_noop(self):
  self.install(NATURE,[]);self.play('TIME_033');self.assertEqual(len(self.p.minions),1);self.keep()
 def test_recruit_wizard_has_no_battlecry_or_rewind(self):
  self.g._summon(0,'TIME_002');self.g._settle();self.assertFalse(self.p.hand);self.assertIsNone(self.g.pending_choice)
 def test_full_board_clocksworth_still_allows_rewind(self):
  for _ in range(6):self.g._summon(0,'CORE_CS2_188')
  self.install(pool(card_type='MINION',rarity='LEGENDARY'),['CORE_EX1_012']);self.play('TIME_038');self.assertEqual(len(self.p.minions),7);self.reroll();self.assertEqual(len(self.p.minions),7)

 def test_rewind_keyword_membership_is_explicit_not_text_mention(self):
  from expanded.generation import request_matches
  from expanded.rewind_generators import REWIND_CARD_IDS
  catalog={c['id']:c for c in load_catalog()};request=pool(mechanic='REWIND')
  self.assertEqual(len(REWIND_CARD_IDS),17)
  self.assertTrue(all(request_matches(request,catalog[cid],'MAGE') for cid in REWIND_CARD_IDS))
  self.assertFalse(request_matches(request,catalog['END_036'],'MAGE'));self.assertFalse(request_matches(request,catalog['TIME_035'],'MAGE'))
 def test_remaining_budget_changes_choice_conditioned_features(self):
  from expanded.features import encode_decision
  self.install(pool(card_type='MINION',rarity='LEGENDARY'),['CORE_EX1_012']);self.play('TIME_038')
  view=self.g.observe(0);decision=dict(actor=0,observation=view,actions=view['legal_actions']);before=encode_decision(decision)
  view['pending_choice']['remaining']=1;after=encode_decision(decision);self.assertNotEqual(before,after)
  key_keep=json.dumps(['rewind_budget',0]);key_rewind=json.dumps(['rewind_budget',1])
  self.assertIn(key_keep,after[0]);self.assertNotIn(key_keep,after[1]);self.assertIn(key_rewind,after[1])
 def test_invalid_visible_rewind_budget_rejected(self):
  from expanded.features import encode_decision
  self.install(pool(card_type='MINION',rarity='LEGENDARY'),['CORE_EX1_012']);self.play('TIME_038');view=self.g.observe(0);view['pending_choice']['remaining']=-1
  with self.assertRaises(ValueError):encode_decision(dict(actor=0,observation=view,actions=view['legal_actions']))

 def test_internal_portal_cast_does_not_offer_rewind(self):
  self.install(pool(card_type='MINION'),['CORE_EX1_012']);self.op(('cast_fixed_spell','TIME_000','random'));self.assertEqual(len(self.p.hand),1);self.assertIsNone(self.g.pending_choice);self.assertEqual(self.p.cards_played,0)
 def test_internal_budget_cast_applies_overload_without_rewind(self):
  self.install(BUDGET_POOL,[self.fake('FIX_THREE')]);self.op(('cast_fixed_spell','TIME_014','random'));self.assertEqual(len(self.p.minions),4);self.assertEqual(self.p.overload_next,3);self.assertIsNone(self.g.pending_choice)
 def test_internal_sands_automatically_resolves_discover(self):
  self.install(ANY_SPELL,['CORE_CS2_004']);self.op(('cast_fixed_spell','TIME_EVENT_999','random'));self.assertIsNone(self.g.pending_choice);self.assertEqual([c.card_id for c in self.p.hand],['CORE_CS2_004']);self.assertEqual(self.p.cards_played,0)
 def test_two_nature_casts_survive_reroll_as_two_events(self):
  self.install(NATURE,['CORE_EX1_169']);self.play('TIME_033');mana=self.p.mana
  self.assertEqual(sum(e['event']=='internal_spell_cast' for e in self.g.events),2);self.reroll()
  self.assertEqual(sum(e['event']=='internal_spell_cast' for e in self.g.events),2);self.assertEqual(self.p.mana,mana)
