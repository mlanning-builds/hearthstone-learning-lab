"""Complete Dark Gift operation family using explicitly limited fixture pools.

These pools validate runtime behavior, not production pool membership or closure.
"""
import copy,json,unittest
import test_expanded_generation as fixtures
from expanded import Action
from expanded.cards import COLLECTIBLE_IDS
from expanded.dark_gift_generators import RULES,request,requests_for,discover
from expanded.generation import request_matches
from expanded.pools import GenerationPool
from engine.game import Card
from engine.cards import UnsupportedCard

class DarkGiftGeneratorTests(unittest.TestCase):
 def setUp(self):self.g=fixtures.GenerationTests().game();self.p=self.g.players[0];self.g._dark_generation_pools={}
 def install(self,req,ids=None):
  if ids is None:
   ids=[cid for cid,d in self.g.cards.items() if d.get('collectible') and any(request_matches(r,d,self.p.hero_class) for r in req.alternatives)][:3]
  self.g._dark_generation_pools[(req,self.p.hero_class)]=GenerationPool('fixture only',tuple(ids),'Controlled runtime test; not reviewed production membership')
  return ids
 def prepare(self,cid):
  for req in requests_for(cid):self.install(req)
 def run_card(self,cid,target=0):
  self.g._dark_global_preflight(cid,0)
  self.g._start_play_effects(RULES[cid][1],dict(owner=0,card_id=cid,source=None,target=target,bonus=0,lifesteal=False))
  self.g._settle()
 def run_request(self,req,**mods):
  self.g._effect(discover(req,**mods),dict(owner=0,source=None,target=0,bonus=0,lifesteal=False))
 def choose(self,index=0,gift=None):
  if gift is not None:self.g.pending_choice['options'][index]['dark_gift']=gift
  self.g.step(Action('choose',choices=(index,)))
 def add(self,cid):
  c=Card(self.g._new_id(),cid);self.g._enter_hand(0,c);return c
 def test_all_twelve_declared_and_still_fail_closed(self):
  from expanded.pending_definitions import DEFINITIONS
  expected={cid for cid,d in DEFINITIONS.items() if d['family']=='dark_gift'}
  self.assertEqual(set(RULES),expected);self.assertEqual(len(RULES),12);self.assertFalse(set(RULES)&COLLECTIBLE_IDS)
 def test_every_card_has_explicit_request(self):self.assertTrue(all(requests_for(cid) for cid in RULES))
 def test_all_standard_declarations_reach_choice(self):
  for cid in sorted(set(RULES)-{'END_027'}):
   with self.subTest(card=cid):
    self.setUp();self.p.corpses=2;self.prepare(cid);self.add('EDR_851t') if cid=='EDR_456' else None
    if cid=='EDR_456':
     dragon=next(k for k,d in self.g.cards.items() if 'DRAGON' in d.get('races',[]));self.add(dragon)
    self.run_card(cid,-2 if cid=='FIR_939' else 0)
    self.assertEqual(self.g.pending_choice['kind'],'dark_global');self.choose(gift='EDR_100t');self.assertIsNone(self.g.pending_choice)
 def test_missing_contract_rejects_without_rng_or_hand_mutation(self):
  before=self.g.rng.getstate()
  with self.assertRaisesRegex(UnsupportedCard,'reviewed'):self.run_request(request())
  self.assertEqual(before,self.g.rng.getstate());self.assertFalse(self.p.hand)
 def test_preflight_catches_later_pool_before_damage(self):
  before=self.g.players[1].health
  with self.assertRaises(UnsupportedCard):self.run_card('FIR_939',-2)
  self.assertEqual(self.g.players[1].health,before)
 def test_no_supported_only_fallback(self):
  req=request();self.install(req,['CORE_CS2_188','missing'])
  with self.assertRaises(UnsupportedCard):self.run_request(req)
 def test_invalid_selector_rejects_before_rng(self):
  req=request(tribe='DRAGON');self.install(req,['CORE_CS2_188']);before=self.g.rng.getstate()
  with self.assertRaisesRegex(UnsupportedCard,'Ineligible'):self.run_request(req)
  self.assertEqual(before,self.g.rng.getstate())
 def test_duplicate_canonical_contract_rejected(self):
  req=request();self.g.cards['FIXTURE_ALIAS']=dict(self.g.cards['CORE_CS2_188'],id='FIXTURE_ALIAS');self.install(req,['CORE_CS2_188','FIXTURE_ALIAS'])
  with self.assertRaisesRegex(UnsupportedCard,'Duplicate'):self.run_request(req)
 def test_empty_reviewed_pool_is_noop(self):
  req=request();self.install(req,[]);self.run_request(req);self.assertIsNone(self.g.pending_choice)
 def test_offers_have_distinct_gifts(self):
  req=request();self.install(req);self.run_request(req);options=self.g.pending_choice['options'];self.assertEqual(len({o['dark_gift'] for o in options}),len(options))
 def test_gifts_visible_to_decision_owner(self):
  req=request();self.install(req);self.run_request(req)
  self.assertTrue(all('dark_gift' in o for o in self.g.observe(0)['pending_choice']['options']))
  self.assertNotIn('options',self.g.observe(1)['pending_choice']);json.dumps(self.g.observe(0))
 def test_choices_consume_no_physical_entity_ids(self):
  req=request();self.install(req);before=self.g._new_id();self.run_request(req);after=self.g._new_id();self.assertEqual(after,before+1)
 def test_selection_counts_one_discover(self):
  req=request();self.install(req);self.run_request(req);self.choose(gift='EDR_100t');self.assertEqual(self.p.discoveries_total,1)
 def test_selected_gift_attaches(self):
  req=request();self.install(req,['CORE_CS2_188']);self.run_request(req);self.choose(gift='EDR_100t')
  self.assertEqual(self.g._dark_list(self.p.hand[-1]),['EDR_100t']);self.assertEqual(self.p.hand[-1].attack_bonus,3)
 def test_cremate_cost_reduction(self):
  self.prepare('FIR_900');self.run_card('FIR_900');self.choose(gift='EDR_100t');self.assertEqual(self.p.hand[-1].cost_delta,-2)
 def test_cremate_discount_applies_to_sweet_dreams_result(self):
  self.prepare('FIR_900');self.run_card('FIR_900');self.choose(gift='EDR_100t8');self.assertEqual(self.p.deck[-1].cost_delta,-2);self.assertFalse(self.p.hand)
 def test_rite_without_corpses_still_discovers(self):
  self.p.corpses=0;self.prepare('EDR_811');self.run_card('EDR_811');self.assertTrue(all(o['dark_gift'] is None for o in self.g.pending_choice['options']));self.choose();self.assertFalse(self.g._dark_list(self.p.hand[-1]))
 def test_rite_spends_exactly_two_on_selection(self):
  self.p.corpses=5;self.prepare('EDR_811');self.run_card('EDR_811');self.assertEqual(self.p.corpses,5);self.choose(gift='EDR_100t');self.assertEqual(self.p.corpses,3)
 def test_rite_insufficient_payment_rejects(self):
  self.p.corpses=2;self.prepare('EDR_811');self.run_card('EDR_811');self.p.corpses=0
  with self.assertRaisesRegex(UnsupportedCard,'payment'):self.choose()
  self.assertIsNotNone(self.g.pending_choice)
 def test_darkrider_without_held_dragon_no_choice(self):
  self.prepare('EDR_456');self.run_card('EDR_456');self.assertIsNone(self.g.pending_choice)
 def test_stalker_copy_has_identical_gift_and_new_identity(self):
  self.prepare('FIR_924');self.run_card('FIR_924');self.choose(gift='EDR_100t1');a,b=self.p.hand
  self.assertNotEqual(a.uid,b.uid);self.assertEqual(a.card_id,b.card_id);self.assertEqual(self.g._dark_list(a),self.g._dark_list(b));self.assertEqual(a.attack_bonus,b.attack_bonus)
 def test_stalker_sweet_dreams_copies_deck_result_to_hand(self):
  self.prepare('FIR_924');self.run_card('FIR_924');self.choose(gift='EDR_100t8');self.assertEqual(len(self.p.hand),1);self.assertEqual(self.p.hand[0].card_id,self.p.deck[-1].card_id)
 def test_stalker_with_one_free_slot_burns_copy(self):
  for _ in range(9):self.add('CORE_CS2_029')
  self.prepare('FIR_924');self.run_card('FIR_924');self.choose(gift='EDR_100t');self.assertEqual(len(self.p.hand),10)
 def test_jumpscare_unchosen_keep_assigned_gifts(self):
  self.p.deck=[];self.prepare('EDR_882');self.run_card('EDR_882')
  for option in self.g.pending_choice['options']:option['dark_gift']='EDR_100t1'
  self.choose();self.assertEqual(len(self.p.deck),2);self.assertTrue(all(self.g._dark_list(c)==['EDR_100t1'] for c in self.p.deck));self.assertEqual(len(self.p.hand),1)
 def test_jumpscare_records_shuffle_not_discard(self):
  self.prepare('EDR_882');self.run_card('EDR_882');self.choose(gift='EDR_100t');self.assertFalse(self.p.discard_history);self.assertEqual(self.p.shuffle_history[-1]['count'],2)
 def test_jumpscare_selected_sweet_dreams_placed_after_shuffle(self):
  self.p.deck=[];self.prepare('EDR_882');self.run_card('EDR_882');cid=self.g.pending_choice['options'][0]['card_id'];self.choose(gift='EDR_100t8');self.assertEqual(self.p.deck[-1].card_id,cid)
 def test_suffusion_damages_before_choice(self):
  self.prepare('FIR_939');self.run_card('FIR_939',-2);self.assertEqual(self.g.players[1].health,28);self.assertIsNotNone(self.g.pending_choice)
 def test_smoke_bomb_union_matches_each_alternative(self):
  req=next(iter(requests_for('FIR_920')));self.assertEqual({r.mechanic for r in req.alternatives},{'COMBO','BATTLECRY','STEALTH'})
  ids=self.install(req);self.run_request(req);self.assertTrue(set(o['card_id'] for o in self.g.pending_choice['options'])<=set(ids))
 def test_historical_request_never_falls_back_to_standard(self):
  req=next(iter(requests_for('END_027')))
  for r in req.alternatives:self.g._generation_pools={(r,self.p.hero_class):GenerationPool('fixture',(),'not historical')}
  with self.assertRaisesRegex(UnsupportedCard,'Historical'):self.run_request(req)
 def test_historical_contract_rejects_standard_outcomes(self):
  req=next(iter(requests_for('END_027')));self.install(req)
  with self.assertRaisesRegex(UnsupportedCard,'Standard'):self.run_request(req)
 def test_historical_contract_rejects_tokens(self):
  req=next(iter(requests_for('END_027')))
  token=next(cid for cid,d in self.g.cards.items() if not d.get('collectible') and 'DRAGON' in d.get('races',[]) and any(request_matches(r,d,self.p.hero_class) for r in req.alternatives))
  self.install(req,[token])
  with self.assertRaisesRegex(UnsupportedCard,'tokens'):self.run_request(req)
 def test_historical_reviewed_fixture_path(self):
  req=next(iter(requests_for('END_027')));cid='FIXTURE_PAST_DRAGON'
  self.g.cards[cid]=dict(id=cid,dbfId=-999,type='MINION',set='GILNEAS',collectible=True,cardClass='NEUTRAL',races=['DRAGON'],cost=4,attack=4,health=4,mechanics=[])
  self.install(req,[cid]);self.run_card('END_027');self.choose(gift='EDR_100t');self.assertEqual(self.p.hand[-1].card_id,cid)
 def test_copy_does_not_double_wallow_notification(self):
  wallow=self.add('EDR_487');self.prepare('FIR_924');self.run_card('FIR_924');self.choose(gift='EDR_100t1');self.assertEqual(self.g._dark_list(wallow),['EDR_100t1'])
 def test_unknown_modifier_is_not_silently_ignored(self):
  req=request();self.install(req)
  with self.assertRaisesRegex(UnsupportedCard,'modifiers'):self.run_request(req,invented=True)

 def test_discover_excludes_source_canonical_identity(self):
  req=request();self.install(req,['CORE_CS2_188','CORE_EX1_012'])
  ids=self.g._dark_global_candidates(req,0,'CORE_CS2_188');self.assertEqual(ids,('CORE_EX1_012',))
