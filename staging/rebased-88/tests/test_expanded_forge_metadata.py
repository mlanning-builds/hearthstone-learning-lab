"""Compiled printed stats and costs are physical, not the generic token's."""
from copy import deepcopy
import unittest
import test_expanded_zombeast_text as fixtures
from expanded.generation_cards import pool,board_pool
from expanded.transformations import evolve_pool,cost_pool
from expanded.pools import GenerationPool
from expanded import cards
from expanded.dormant_cards import INITIAL


class ForgeMetadataTests(unittest.TestCase):
 def setUp(self):
  self.fixture=fixtures.ZombeastTextTests();self.fixture.setUp()
  self.addCleanup(self.fixture.doCleanups);self.game=self.fixture.game

 def craft(self):return self.fixture.craft('CORE_EX1_014')

 def play(self):
  card=self.craft();self.cost=card.set_cost
  self.game.step(next(a for a in self.game.legal_actions() if a.kind=='play' and a.source==card.uid))
  return next(m for m in self.game.players[0].minions if m.card_id==card.card_id)

 def install(self,request):
  cid=next(cid for cid,d in self.game.cards.items() if cid in cards.RULES and d.get('type')=='MINION' and d.get('cost')==request.minimum and cid not in INITIAL)
  if not hasattr(self.game,'_generation_pools'):self.game._generation_pools={}
  self.game._generation_pools[(request,self.game.players[0].hero_class)]=GenerationPool('fixture only',(cid,),'Explicit transformation test; not production membership')
  return cid

 def effect(self,operation,source=None,target=0):
  self.game._start_play_effects([operation],dict(owner=0,source=source,target=target,bonus=0,spell=False,lifesteal=False))
  self.game._settle(allow_event_choices=True)

 def test_printed_metadata_ignores_discount_buffs_and_catalog_token(self):
  card=self.craft();cost=card.set_cost;stats=card.base_stat_override;catalog=deepcopy(self.game.cards[card.card_id])
  self.game._set_card_cost(card,0);card.attack_bonus=9;card.health_bonus=8
  shown=self.game._card_data(card)
  self.assertEqual((shown['cost'],shown['attack'],shown['health']),(cost,*stats))
  self.assertEqual(self.game._cost(card,0),0);self.assertEqual(self.game.cards[card.card_id],catalog)

 def test_silenced_board_metadata_retains_compiled_printed_cost(self):
  m=self.play();self.game._buff(m,7,7);self.game._silence(m)
  self.assertEqual(self.game._card_data(m)['cost'],self.cost)

 def test_board_evolve_uses_compiled_cost_plus_one(self):
  m=self.play();cid=self.install(evolve_pool(self.cost,1))
  self.effect(('mutation_board',1,False),m)
  self.assertEqual([v.card_id for v in self.game.players[0].minions],[cid])

 def test_life_cycle_replaces_with_compiled_same_cost(self):
  m=self.play();cid=self.install(board_pool(cost_pool(self.cost)))
  self.effect(('mutation_life_cycle',),m,m.uid)
  self.assertEqual([v.card_id for v in self.game.players[0].minions],[cid])

 def test_imbue_evolve_uses_compiled_cost(self):
  m=self.play();cid=self.install(board_pool(pool(card_type='MINION',minimum=self.cost+1,maximum=self.cost+1)))
  self.effect(('imbue_evolve',1),m,m.uid)
  self.assertEqual([v.card_id for v in self.game.players[0].minions],[cid])

 def test_death_source_generation_uses_compiled_cost(self):
  m=self.play();cid=self.install(board_pool(pool(card_type='MINION',minimum=self.cost,maximum=self.cost)))
  m.health=0;self.game._settle(allow_event_choices=True)
  self.effect(('generation_dynamic_summon','death_source_cost'),m)
  self.assertEqual([v.card_id for v in self.game.players[0].minions],[cid])

 def test_reset_cost_restores_compiled_base_not_zero(self):
  card=self.craft();cost=card.set_cost;self.game._set_card_cost(card,0)
  self.effect(('reset_hand_costs',))
  self.assertEqual(self.game._cost(card,0),cost)

 def test_titan_draw_sets_compiled_card_to_two_two_two(self):
  card=self.craft();self.game.players[0].hand.remove(card);card.attack_bonus=8;card.health_bonus=9
  self.game.players[0].deck=[card]
  self.effect(('osk_draw_twos',))
  self.assertEqual(tuple(self.game._card_stat(card,key,0) for key in ('attack','health','cost')),(2,2,2))

 def test_titan_draw_sets_crystal_core_base_to_two_two(self):
  self.game.players[0].crystal_core=True;card=self.craft();self.game.players[0].hand.remove(card)
  self.game.players[0].deck=[card]
  self.effect(('osk_draw_twos',))
  self.assertEqual(tuple(self.game._card_stat(card,key,0) for key in ('attack','health','cost')),(2,2,2))

 def test_recruit_does_not_treat_undiscounted_composite_as_zero(self):
  card=self.craft();self.game.players[0].hand.remove(card);self.game.players[0].deck=[card]
  self.effect(('recruit',card.set_cost-1))
  self.assertFalse(self.game.players[0].minions)
  self.assertEqual(self.game.players[0].deck,[card])

 def test_recruit_honors_physical_deck_cost_discount(self):
  card=self.craft();self.game.players[0].hand.remove(card);self.game.players[0].deck=[card]
  base=card.set_cost;self.game._set_card_cost(card,2)
  self.effect(('recruit',2))
  m=self.game.players[0].minions[-1]
  self.assertEqual(m.card_id,card.card_id);self.assertEqual(self.game._card_data(m)['cost'],base)
