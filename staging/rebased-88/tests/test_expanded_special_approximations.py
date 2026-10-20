"""Execution regressions for owner-authorized approximate special policies."""
import unittest
from unittest.mock import patch
from engine.game import Card
from expanded import Game
from expanded.decks import Deck
from expanded.cards import RULES
from expanded.generation_cards import pool
from expanded.generation import request_matches
from expanded.automatic_cards import validate_automatic_card

class SpecialApproximationTests(unittest.TestCase):
 def game(self):
  from test_expanded_generation import GenerationTests
  return GenerationTests().game()
 def physical_decks(self,g):
  for p in g.players:p.deck=[Card(g._new_id(),c) if isinstance(c,str) else c for c in p.deck]
 def ops(self,g,ops,cid,source=None):
  g._start_play_effects(ops,dict(owner=0,source=source,target=0,bonus=0,lifesteal=False,card_id=cid))
  g._settle(allow_event_choices=True)
 def test_shared_refresh_accepts_string_deck_entries(self):
  g=self.game();g._summon(0,'CORE_EX1_162');g._refresh_auras()
  self.assertEqual(g.players[0].deck,['CORE_CS2_029']*12)
 def test_string_treasure_halves_forge_as_physical_weapon(self):
  g=self.game();p=g.players[0];p.hand=[];p.deck=['ONY_005tc5','ONY_005tc6']
  g._refresh_auras()
  self.assertEqual(len(p.deck),1);self.assertIsInstance(p.deck[0],Card)
  self.assertEqual(p.deck[0].card_id,'ONY_005tc7')
 def test_neutral_class_selector_for_morphing_mirage(self):
  g=self.game();request=pool(classes='NEUTRAL')
  self.assertTrue(request_matches(request,g.cards['CORE_EX1_162'],'MAGE'))
  self.assertFalse(request_matches(request,g.cards['CORE_CS2_029'],'MAGE'))
 def test_avatar_entire_pool_preflights_for_every_class(self):
  from expanded.selectors import HERO_CLASSES
  g=self.game()
  ids={cid for slot in g.standard_pack_contract['slots'] for _,cid in slot}
  for hero in HERO_CLASSES:
   g.players[0].hero_class=hero
   for cid in ids:
    with self.subTest(hero=hero,cid=cid):validate_automatic_card(g,Card(-1,cid),0)
 def test_avatar_casts_full_default_pack_without_hand_capacity(self):
  g=self.game();self.physical_decks(g)
  for _ in range(10):g._add(0,'CORE_CS2_029')
  source=g._summon(0,'CORE_WON_145')
  self.ops(g,RULES['CORE_WON_145'][1],'CORE_WON_145',source)
  self.assertIsNone(g.pending_choice)
  self.assertIsNone(g.pending_frame)
 def test_off_class_single_class_herald_spell_executes(self):
  g=self.game();self.physical_decks(g)
  self.ops(g,[('cast_fixed_spell','CATA_156','random')],'CATA_156')
  self.assertEqual(g.players[0].herald_count,1)
  self.assertTrue(any(m.card_id=='CATA_780t' for m in g.players[0].minions))
 def test_all_experimental_openings_construct_with_setup(self):
  from expanded.special_approximations import experimental_contract
  from expanded.cards import registry
  from test_expanded_passive_admission import PassiveAdmissionTests
  from expanded.historical_experimental_decks import select
  records=registry();contract=experimental_contract(records)
  opponent=PassiveAdmissionTests().deck('MAGE','CORE_CS2_029')
  original=select
  for recipe in contract.recipes:
   class FixedDeckRandom:
    def __init__(self,rng):self.rng=rng
    def choices(self,values,weights,k):
     return [recipe] if values==contract.recipes else self.rng.choices(values,weights=weights,k=k)
   def selected(c,cards,rng):return original(c,cards,FixedDeckRandom(rng))
   with self.subTest(hero=recipe.hero_class),patch('expanded.historical_experimental_decks.select',side_effect=selected):
    g=Game([Deck('MAGE',('TOY_700',)),opponent],seed=97)
    self.assertEqual(g.players[0].hero_class,recipe.hero_class)
    self.assertEqual(g.players[0].max_health,recipe.health)
    self.assertEqual(g.players[0].historical_experimental_zero_lackeys,recipe.zero_lackeys)
 def test_bloodpetal_biome_generates_on_activation_only(self):
  g=self.game();self.physical_decks(g)
  card=g._add(0,'TLC_449')
  g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==card.uid))
  location=next(loc for loc in g.players[0].locations if loc.card_id=='TLC_449')
  self.assertIsNone(g.pending_choice)
  action=next(a for a in g.legal_actions() if a.kind=='activate' and a.source==location.uid)
  g.step(action)
  self.assertEqual(g.pending_choice['kind'],'generation_discover')
 def test_observation_profile_is_detached_and_explicit(self):
  g=self.game();view=g.observe(0)
  self.assertFalse(view['approximation_profile']['validated'])
  view['approximation_profile']['policies'].clear()
  self.assertTrue(g.approximation_profile['policies'])
