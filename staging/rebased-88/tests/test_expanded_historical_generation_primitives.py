"""Explicit historical generation bodies, tested with bounded fixture pools.

Fixture pools demonstrate execution only and are not production membership.
"""
from copy import deepcopy
import json,unittest
import test_expanded_generation as fixtures
from expanded import Action,cards
from expanded.generation import request_matches
from expanded.pools import GenerationPool
from expanded.effect_schema import validate_namespace
from engine.cards import UnsupportedCard
from standard.catalog import load_catalog
from expanded import historical_generation_primitives as family


class HistoricalGenerationPrimitiveTests(unittest.TestCase):
 def setUp(self):
  self.fx=fixtures.GenerationTests()

 def game(self,hero='MAGE'):
  g=self.fx.game();g.players[0].hero_class=hero;g._generation_pools={};return g

 def install(self,g,cid):
  selected={};hero=g.players[0].hero_class
  for req in family.requests_for(cid):
   if req.era=='past':outcome=g._generation_candidates(req,0)[0]
   else:outcome=next(d['id'] for d in load_catalog() if d['id'] in g.cards and request_matches(req,d,hero))
   self.assertTrue(request_matches(req,g.cards[outcome],hero))
   g._generation_pools[(req,hero)]=GenerationPool('explicit single-outcome fixture',(outcome,),'Controlled body test; not production membership')
   selected[req]=outcome
  return selected

 def choose(self,g):
  while g.pending_choice:g.step(Action('choose',choices=(0,)))

 def play(self,g,cid):
  c=g._add(0,cid);g.players[0].mana=10
  g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid));self.choose(g)
  return next(m for m in g.players[0].all_minions if m.card_id==cid)

 def test_generation_family_recipes_are_structurally_strict(self):
  self.assertGreaterEqual(len(family.GENERATED_IDS),43)
  validate_namespace(vars(family),strict_unknown=True)
  self.assertTrue(any(family.requests_for(cid) for cid in family.GENERATED_IDS))

 def test_every_battlecry_generates_correct_count_and_destination(self):
  for cid,(_,operations) in family.RULES.items():
   operations=cards.RULES[cid][1]
   if len(operations)!=1 or operations[0][0] not in ('generate_random','generate_discover'):continue
   with self.subTest(cid=cid):
    g=self.game();self.install(g,cid);source=self.play(g,cid);op=operations[0]
    amount=op[2] if op[0]=='generate_random' else 1;destination=op[3] if op[0]=='generate_random' else op[2]
    self.assertEqual(len(g.players[0].hand),amount if destination=='hand' else 0)
    self.assertEqual(len(g.players[0].all_minions),1+(amount if destination=='board' else 0))
    g.assert_invariants()

 def test_every_deathrattle_generates_after_its_bearer_dies(self):
  for cid in family.DEATH_EFFECTS:
   operations=cards.DEATH_EFFECTS[cid]
   if len(operations)!=1 or operations[0][0]!='generate_random':continue
   with self.subTest(cid=cid):
    g=self.game();self.install(g,cid);m=self.play(g,cid)
    self.assertFalse(g.players[0].hand);m.health=0;g._settle(allow_event_choices=True)
    op=operations[0];destination=op[3]
    self.assertEqual(len(g.players[0].hand),op[2] if destination=='hand' else 0)
    self.assertEqual(len(g.players[0].all_minions),op[2] if destination=='board' else 0)
    g.assert_invariants()

 def test_every_owner_end_effect_generates(self):
  for cid in family.END_EFFECTS:
   operations=cards.END_EFFECTS[cid]
   if len(operations)!=1 or operations[0][0]!='generate_random':continue
   with self.subTest(cid=cid):
    g=self.game();self.install(g,cid);self.play(g,cid)
    g.step(Action('end'));op=operations[0];destination=op[3]
    self.assertEqual(len(g.players[0].hand),1 if destination=='hand' else 0)
    self.assertEqual(len(g.players[0].all_minions),2 if destination=='board' else 1)

 def test_silence_removes_death_generation(self):
  g=self.game();self.install(g,'BOT_401');m=self.play(g,'BOT_401');g._silence(m)
  m.health=0;g._settle(allow_event_choices=True);self.assertFalse(g.players[0].hand)

 def test_silence_removes_owner_end_generation(self):
  g=self.game();self.install(g,'CFM_663');m=self.play(g,'CFM_663');g._silence(m)
  g.step(Action('end'));self.assertFalse(g.players[0].hand)

 def test_discover_discount_attaches_to_physical_chosen_card(self):
  for cid in ('LOE_006','WON_056','SW_059','RLK_547'):
   with self.subTest(cid=cid):
    g=self.game();self.install(g,cid);self.play(g,cid)
    self.assertEqual(g.players[0].hand[-1].cost_delta,-1)

 def test_explicit_mage_selector_survives_cross_class_play(self):
  g=self.game('HUNTER');selected=self.install(g,'DAL_163');self.play(g,'DAL_163')
  self.assertEqual(g.players[0].hand[-1].card_id,next(iter(selected.values())))
  self.assertEqual(next(iter(selected)).classes,'MAGE')

 def test_opponent_class_exclusion_is_not_own_spell_pool(self):
  req=next(iter(family.requests_for('DAL_416')));g=self.game()
  self.assertFalse(request_matches(req,g.cards['CORE_CS2_029'],'MAGE'))
  self.assertEqual(req.classes,'other')

 def test_neptulon_generates_four_and_retains_overload(self):
  g=self.game();self.install(g,'GVG_042');self.play(g,'GVG_042')
  self.assertEqual(len(g.players[0].hand),4);self.assertEqual(g.players[0].overload_next,3)

 def test_missing_outcome_rejects_without_sampling_or_paying(self):
  g=self.game();req=next(iter(family.requests_for('BOT_533')))
  g._generation_pools[(req,'MAGE')]=GenerationPool('invalid fixture',('MISSING_OUTCOME',),'Must fail, never filter')
  c=g._add(0,'BOT_533');before=deepcopy(g.observe(0));rng=g.rng.getstate()
  with self.assertRaises(UnsupportedCard):g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid))
  self.assertEqual(g.observe(0),before);self.assertEqual(g.rng.getstate(),rng)

 def test_default_legendary_pool_keeps_deliberately_removed_avatar_outcome(self):
  g=self.game();del g.cards['CORE_WON_145'];c=g._add(0,'ETC_326');before=deepcopy(g.observe(0));rng=g.rng.getstate()
  with self.assertRaisesRegex(UnsupportedCard,'CORE_WON_145'):
   g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid))
  self.assertEqual(g.observe(0),before);self.assertEqual(g.rng.getstate(),rng)

 def test_registered_bodies_remain_generated_only(self):
  self.assertTrue(family.GENERATED_IDS<=set(cards.registry())&set(cards.RULES))
  self.assertFalse(family.GENERATED_IDS&cards.COLLECTIBLE_IDS)

 def test_written_inventory_includes_every_new_registration(self):
  from pathlib import Path
  index=json.loads(Path('expanded/implementation_index.json').read_text())
  self.assertTrue(family.GENERATED_IDS<=set(index['generated_historical_card_ids']))
