"""Compiled zone growth, Gift requests and paid-play Rewind."""
from copy import deepcopy
import json,unittest
import test_expanded_zombeast_text as fixtures
from expanded import Action
from expanded.dark_gift_generators import request,GiftRequest
from expanded.rewind_generators import BEAST_GIFT
from expanded.generation_cards import pool
from expanded.pools import GenerationPool
from expanded.effect_schema import validate_operations,EffectSchemaError
from expanded.features import encode_decision
from expanded.exceptional_finish import MINIONS
from engine.cards import UnsupportedCard


class RemainingZombeastTests(unittest.TestCase):
 def setUp(self):
  self.fixture=fixtures.ZombeastTextTests();self.fixture.setUp()
  self.addCleanup(self.fixture.doCleanups);self.game=self.fixture.game

 def gift_pool(self,req):
  self.game._dark_generation_pools={(req,self.game.players[0].hero_class):GenerationPool('fixture only',('CORE_GIL_558',),'Controlled recipe execution; not production membership')}

 def choose(self,index=0):self.game.step(Action('choose',choices=(index,)))

 def test_grazing_growth_on_board_hand_and_deck_once_per_owner_turn(self):
  held=self.fixture.craft('TLC_827');decked=self.fixture.craft('TLC_827')
  self.game.players[0].hand.remove(decked);self.game.players[0].deck=[decked]
  m=self.fixture.play('TLC_827');attack=m.attack
  self.game.step(Action('end'))
  self.assertEqual((held.attack_bonus,decked.attack_bonus,m.attack),(1,1,attack+1))
  self.game.step(Action('end'))
  self.assertEqual((held.attack_bonus,decked.attack_bonus,m.attack),(1,1,attack+1))

 def test_grazing_board_silence_removes_future_growth(self):
  m=self.fixture.play('TLC_827');self.game._silence(m);attack=m.attack
  self.game.step(Action('end'))
  self.assertEqual(m.attack,attack)

 def test_grazing_hand_copy_grows_independently(self):
  original=self.fixture.craft('TLC_827');copy=self.game._copy_card(original)
  self.game.players[0].deck=[copy]
  self.game._b60_turn_end(0)
  self.assertEqual((original.attack_bonus,copy.attack_bonus),(1,1))
  original.attack_bonus=17
  self.assertEqual(copy.attack_bonus,1)

 def test_brutish_endmaw_discovers_a_gifted_one_cost_minion(self):
  self.gift_pool(request(minimum=1,maximum=1));self.game.players[0].hand=[]
  self.fixture.play('END_013');self.assertEqual(self.game.pending_choice['kind'],'dark_global')
  self.choose();card=self.game.players[0].hand[-1]
  self.assertEqual(card.card_id,'CORE_GIL_558');self.assertTrue(self.game._dark_list(card))

 def test_raptor_rewind_restores_discovery_and_pays_only_once(self):
  self.gift_pool(BEAST_GIFT);self.game.players[0].hand=[]
  card=self.fixture.craft('CORE_EDR_004_2026');paid=self.game._cost(card,0)
  self.game.step(next(a for a in self.game.legal_actions() if a.kind=='play' and a.source==card.uid))
  self.game.pending_choice['options'][0]['dark_gift']='EDR_100t1'
  self.choose();self.assertEqual(self.game.pending_choice['kind'],'rewind')
  self.choose(1);self.assertEqual(self.game.pending_choice['kind'],'dark_global')
  self.game.pending_choice['options'][0]['dark_gift']='EDR_100t1'
  self.choose()
  p=self.game.players[0]
  self.assertIsNone(self.game.pending_choice);self.assertEqual(p.mana,10-paid)
  self.assertEqual(p.cards_played,1);self.assertEqual(p.discoveries_total,1)
  self.assertEqual([m.card_id for m in p.minions],['ICC_828t'])
  self.assertEqual([c.card_id for c in p.hand],['CORE_GIL_558'])

 def test_recruited_rewind_composite_does_not_offer_rewind(self):
  card=self.fixture.craft('CORE_EDR_004_2026')
  self.game._summon(0,card.card_id,entry_source=card)
  self.assertIsNone(self.game.pending_choice)

 def test_gift_request_observation_is_detached_plain_data(self):
  card=self.fixture.craft('END_013');view=self.game.observe(0);json.dumps(view)
  self.assertTrue(encode_decision(dict(observation=view,actor=0,actions=view['legal_actions'])))
  shown=next(c for c in view['players'][0]['hand'] if c['uid']==card.uid)
  shown['rule_state']['crafted_ops'][0][1]['alternatives'][0]['maximum']=999
  self.assertEqual(card.rule_state['crafted_ops'][0][1].alternatives[0].maximum,1)

 def test_missing_gift_outcome_rolls_back_paid_composite_play(self):
  self.game._dark_generation_pools={(BEAST_GIFT,self.game.players[0].hero_class):GenerationPool('fixture only',('MISSING',),'Invalid fixture outcome')}
  card=self.fixture.craft('CORE_EDR_004_2026');before=deepcopy(self.game.observe(0));rng=self.game.rng.getstate()
  with self.assertRaises(UnsupportedCard):self.game.step(next(a for a in self.game.legal_actions() if a.kind=='play' and a.source==card.uid))
  self.assertEqual(self.game.observe(0),before);self.assertEqual(self.game.rng.getstate(),rng)

 def test_watfin_correct_choice_buffs_composite_source(self):
  hero=self.game.players[0].hero_class
  self.game._generation_pools={(MINIONS,hero):GenerationPool('fixture only',('CORE_GIL_558',),'Controlled mutation fixture')}
  self.game.suspicious_mutation_contract=dict(source='Explicit test distribution',mutations=[dict(field='attack',delta=1)])
  m=self.fixture.play('JAIL_EVENT_100');before=(m.attack,m.max_health)
  self.choose(self.game.pending_choice['suspect'])
  self.assertEqual((m.attack,m.max_health),(before[0]+1,before[1]+1))

 def test_new_rule_contracts_reject_invalid_gift_requests_and_modifiers(self):
  malformed=(('dark_global_discover',GiftRequest((),False),()),
   ('dark_global_discover',GiftRequest((pool(),),1),()),
   ('dark_global_discover',request(),(('cost_delta',True),)),
   ('dark_global_discover',request(),(('copy_selected',1),)),
   ('dark_global_discover',request(),(('unknown',1),)),('rewindgen_gift',1),('suspicious_discover',1))
  for op in malformed:
   with self.assertRaises(EffectSchemaError):validate_operations((op,),strict_unknown=True)

 def test_raptor_kindred_discounts_the_gifted_card(self):
  self.gift_pool(BEAST_GIFT);self.game.players[0].hand=[]
  self.game.players[0].previous_tribes={'BEAST'}
  self.fixture.play('CORE_EDR_004_2026')
  self.game.pending_choice['options'][0]['dark_gift']='EDR_100t1';self.choose()
  self.assertEqual(self.game.pending_choice['kind'],'rewind');self.choose(0)
  self.assertEqual(self.game.players[0].hand[-1].cost_delta,-1)

 def test_watfin_wrong_choice_does_not_buff_composite(self):
  hero=self.game.players[0].hero_class
  self.game._generation_pools={(MINIONS,hero):GenerationPool('fixture only',('CORE_GIL_558','CORE_CS2_188'),'Controlled mutation fixture')}
  self.game.suspicious_mutation_contract=dict(source='Explicit test distribution',mutations=[dict(field='attack',delta=1)])
  m=self.fixture.play('JAIL_EVENT_100');before=(m.attack,m.max_health)
  self.choose(1-self.game.pending_choice['suspect'])
  self.assertEqual((m.attack,m.max_health),before)

 def test_every_explicit_text_keyword_pair_preserves_base_stats_and_cost(self):
  from expanded.zombeast_text_parts import PARTS as TEXT
  from expanded.zombeast_keyword_parts import PARTS as KEYWORDS
  checked=0
  for first in TEXT.values():
   for second in KEYWORDS.values():
    self.game.players[0].hand=[]
    self.game._forge_choice(dict(kind='forge_part',forge_kind='zombeast',owner=0,discount=3,first=first,parts=[second]),dict(card_id=second.card_id))
    card=self.game.players[0].hand[-1];a=self.game.cards[first.card_id];b=self.game.cards[second.card_id]
    self.assertEqual(card.base_stat_override,(a['attack']+b['attack'],a['health']+b['health']))
    self.assertEqual(card.set_cost,a['cost']+b['cost']);self.assertEqual(card.cost_delta,-3)
    self.assertEqual(card.rule_state['forge_parts'],(first.card_id,second.card_id));checked+=1
  self.assertEqual(checked,2006)

 def test_crafted_card_mutation_does_not_change_contract_or_other_card(self):
  from expanded.zombeast_text_parts import PARTS
  original=deepcopy(PARTS['DINO_435'].operations)
  first=self.fixture.craft('DINO_435');second=self.fixture.craft('DINO_435')
  first.rule_state['crafted_ops'][0][1].append(('draw',1))
  self.assertEqual(PARTS['DINO_435'].operations,original)
  self.assertEqual(second.rule_state['crafted_ops'],original)
