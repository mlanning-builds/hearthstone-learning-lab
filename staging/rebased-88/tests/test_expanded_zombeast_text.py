"""Compiled Beast effects execute on the physical composite bearer."""
import unittest
from unittest.mock import patch
import gzip,json
import test_expanded_forge_intrinsics as fixtures
from expanded.minion_forge import ForgePart
from expanded import cards
from expanded.game import Card
from expanded.effect_schema import validate_operations,EffectSchemaError
from expanded.forge_intrinsics import validate_intrinsics
from expanded.zombeast_text_parts import PARTS


class ZombeastTextTests(unittest.TestCase):
 def setUp(self):
  self.fixture=fixtures.ForgeIntrinsicTests();self.fixture.setUp()
  self.addCleanup(self.fixture.doCleanups);self.game=self.fixture.game
  with gzip.open('data/standard/all_cards.json.gz','rt') as stream:
   records={c['id']:c for c in json.load(stream)}
   self.game.cards.update({cid:records[cid] for cid in set(PARTS)|{'ICC_828t'}})
  change=patch.dict(cards.RULES,{'ICC_828t':('none',[])})
  change.start();self.addCleanup(change.stop)

 def craft(self,cid):
  second=ForgePart('CORE_GIL_558',keywords=('LIFESTEAL',),source='explicit fixture')
  self.game._forge_choice(dict(kind='forge_part',forge_kind='zombeast',owner=0,discount=0,first=PARTS[cid],parts=[second]),dict(card_id=second.card_id))
  return self.game.players[0].hand[-1]

 def play(self,cid,target=None):
  c=self.craft(cid)
  actions=[a for a in self.game.legal_actions() if a.kind=='play' and a.source==c.uid and (target is None or a.target==target)]
  self.assertTrue(actions);self.game.step(actions[0])
  return next(m for m in self.game.players[0].minions if m.card_id=='ICC_828t')

 def test_explicit_recipes_validate_without_installing_pool(self):
  self.assertEqual(len(PARTS),59)
  for cid,part in PARTS.items():
   validate_operations(part.operations,cid,strict_unknown=True)
   validate_operations(part.death_operations,cid,strict_unknown=True)
   validate_intrinsics(part.intrinsics,cid)
  self.assertTrue(self.game.forge_contracts)

 def test_mukla_gives_two_real_bananas_to_opponent(self):
  self.game.players[1].hand=[];self.play('CORE_EX1_014')
  self.assertEqual([c.card_id for c in self.game.players[1].hand],['EX1_014t']*2)

 def test_lifedrinker_damages_enemy_and_heals_owner(self):
  self.game.players[0].health=20;self.game.players[1].health=30
  self.play('CORE_GIL_622')
  self.assertEqual((self.game.players[0].health,self.game.players[1].health),(23,27))

 def test_phoenix_uses_selected_target(self):
  self.game.players[1].health=30;self.play('CORE_UNG_084',self.game.hero_id(1))
  self.assertEqual(self.game.players[1].health,27)

 def test_mother_duck_summons_three_rush_ducklings(self):
  self.play('EDR_492');ducks=[m for m in self.game.players[0].minions if m.card_id=='EDR_492t']
  self.assertEqual(len(ducks),3)
  self.assertTrue(all('RUSH' in self.game._effective_keywords(m) for m in ducks))

 def test_plated_beetle_deathrattle_belongs_to_composite(self):
  m=self.play('CORE_LOOT_413');before=self.game.players[0].armor
  m.health=0;self.game._settle(allow_event_choices=True)
  self.assertEqual(self.game.players[0].armor,before+3)

 def test_marshland_spell_trigger_and_silence(self):
  m=self.play('TLC_256')
  self.game._queue_event('spell_cast',owner=0,card_id='CORE_CS2_029',cost=4)
  self.game._settle(allow_event_choices=True)
  self.assertIn('DIVINE_SHIELD',self.game._effective_keywords(m))
  self.game._silence(m)
  self.game._queue_event('spell_cast',owner=0,card_id='CORE_CS2_029',cost=4)
  self.game._settle(allow_event_choices=True)
  self.assertNotIn('DIVINE_SHIELD',self.game._effective_keywords(m))

 def test_maluk_discards_other_cards_then_gives_infinite_banana(self):
  self.game.players[0].hand=[Card(self.game._new_id(),'CORE_CS2_029')]
  self.play('TIME_042')
  self.assertEqual([c.card_id for c in self.game.players[0].hand],['TIME_042t'])

 def test_generation_condition_validates_nested_operation(self):
  valid=PARTS['CORE_LOE_039'].operations[0]
  for invalid in ((valid[0],'BAD_TRIBE',valid[2]),(valid[0],valid[1],('missing_handler',))):
   with self.assertRaises(EffectSchemaError):validate_operations((invalid,),strict_unknown=True)

 def test_ravasaur_kindred_uses_combined_attack(self):
  enemy=self.game._summon(1,'EDR_851t');self.game._buff(enemy,0,40)
  before=enemy.health;self.game.players[0].previous_tribes={'BEAST'}
  m=self.play('TLC_825',enemy.uid)
  self.assertEqual(enemy.health,before-m.attack)

 def test_crater_gator_healing_block_expires_on_owner_turn(self):
  from expanded import Action
  self.game.players[1].health=20;self.play('TLC_250')
  self.game._heal(self.game.hero_id(1),3,healer=1)
  self.assertEqual(self.game.players[1].health,20)
  self.game.step(Action('end'));self.game.step(Action('end'))
  self.game._heal(self.game.hero_id(1),3,healer=1)
  self.assertEqual(self.game.players[1].health,23)

 def test_new_operand_contracts_reject_malformed_rules(self):
  malformed=(('add_opponent','EX1_014t',True),('damage_enemy_heal_own',3),
   ('discard_entire_hand',1),('prevent_enemy_hero_healing_until_next_turn',True),
   ('source_attack_damage',1))
  for operation in malformed:
   with self.subTest(operation=operation):
    with self.assertRaises(EffectSchemaError):validate_operations((operation,),strict_unknown=True)
