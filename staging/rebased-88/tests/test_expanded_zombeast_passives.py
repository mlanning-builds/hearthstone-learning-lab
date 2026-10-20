"""Composite aura, cleave and remembered Deathrattle behavior."""
from copy import deepcopy
import unittest
import test_expanded_zombeast_text as fixtures
from expanded.forge_intrinsics import validate_intrinsics
from engine.cards import UnsupportedCard


class ZombeastPassiveTests(unittest.TestCase):
 def setUp(self):
  self.fixture=fixtures.ZombeastTextTests();self.fixture.setUp()
  self.addCleanup(self.fixture.doCleanups);self.game=self.fixture.game

 def test_dire_wolf_buffs_physical_neighbors_and_silence_removes_aura(self):
  left=self.game._summon(0,'EDR_851t');right=self.game._summon(0,'EDR_851t')
  base=(left.attack,right.attack)
  card=self.fixture.craft('CORE_EX1_162');wolf=self.game._summon(0,card.card_id,position=1,entry_source=card)
  self.game._refresh_auras()
  self.assertEqual((left.attack,right.attack),(base[0]+1,base[1]+1))
  self.assertEqual(wolf.aura_attack,0)
  self.game._silence(wolf)
  self.assertEqual((left.attack,right.attack),base)

 def test_aura_is_cloned_and_stacks_without_changing_catalog(self):
  card=self.fixture.craft('CORE_EX1_162');wolf=self.game._summon(0,card.card_id,entry_source=card)
  middle=self.game._summon(0,'EDR_851t');base=middle.attack
  self.game._summon(0,wolf.card_id,copy_from=wolf);self.game._refresh_auras()
  self.assertEqual(middle.attack,base+1)
  clone=deepcopy(self.game);self.game._silence(wolf)
  self.assertEqual(clone._find(middle.uid).attack,base+1)
  self.assertNotIn('adjacent_attack',self.game.cards['ICC_828t'])

 def thresher_attack(self,silenced=False):
  m=self.fixture.play('CORE_SCH_605');m.exhausted=False
  if silenced:self.game._silence(m)
  targets=[self.game._summon(1,'EDR_851t') for _ in range(3)]
  for t in targets:self.game._buff(t,0,30)
  before=[t.health for t in targets];attack=m.attack
  self.game._attack(m.uid,targets[1].uid)
  return before,[t.health for t in targets],attack

 def test_cleave_hits_both_adjacent_targets_with_combined_attack(self):
  before,after,attack=self.thresher_attack()
  self.assertEqual(after,[health-attack for health in before])

 def test_silence_removes_composite_cleave(self):
  before,after,attack=self.thresher_attack(True)
  self.assertEqual(after,[before[0],before[1]-attack,before[2]])

 def test_porcupine_death_uses_combined_attack_and_lifesteal(self):
  m=self.fixture.play('CORE_BT_201');self.game.players[0].health=10
  self.game.players[1].health=30;attack=m.attack
  m.health=0;self.game._settle(allow_event_choices=True)
  self.assertEqual(self.game.players[1].health,30-attack)
  self.assertEqual(self.game.players[0].health,10+attack)

 def test_platysaur_discards_the_physical_drawn_card(self):
  self.game.players[0].hand=[];self.game.players[0].deck=['CORE_CS2_029']
  m=self.fixture.play('TLC_603');drawn=self.game.players[0].hand[-1]
  self.assertEqual(drawn.card_id,'CORE_CS2_029')
  m.health=0;self.game._settle(allow_event_choices=True)
  self.assertNotIn(drawn,self.game.players[0].hand)

 def test_cleave_and_adjacent_attack_reject_wrong_operand_types(self):
  for properties in ((('cleave',1),),(('adjacent_attack',True),),(('adjacent_attack',-1),)):
   with self.assertRaises(UnsupportedCard):validate_intrinsics(properties,'fixture')

 def test_stegodon_choice_changes_composite(self):
  m=self.fixture.play('TLC_242');self.game._resolve_choice(0)
  self.assertIn('TAUNT',self.game._effective_keywords(m))

 def test_raptor_choice_grants_plant_deathrattle_to_composite(self):
  m=self.fixture.play('TLC_245');self.game._resolve_choice(2)
  m.health=0;self.game._settle(allow_event_choices=True)
  self.assertEqual([x.card_id for x in self.game.players[0].minions],['UNG_999t2t1']*2)

 def test_pterrordax_choice_stealth_expires_at_next_owner_turn(self):
  from expanded import Action
  m=self.fixture.play('TLC_246');self.game._resolve_choice(0)
  self.assertIn('STEALTH',self.game._effective_keywords(m))
  self.game.step(Action('end'));self.game.step(Action('end'))
  self.assertNotIn('STEALTH',self.game._effective_keywords(m))

 def test_dreambound_raptor_grants_bonus_to_other_played_minion(self):
  from expanded.game import Card
  self.fixture.play('EDR_849');card=Card(self.game._new_id(),'CORE_GIL_558')
  self.game.players[0].hand.append(card)
  self.game.step(next(a for a in self.game.legal_actions() if a.kind=='play' and a.source==card.uid))
  target=next(m for m in self.game.players[0].minions if m.card_id==card.card_id)
  self.assertTrue(self.game._effective_keywords(target)-{'LIFESTEAL'})

 def test_grizzly_health_loss_and_taunt_apply_to_combined_body(self):
  from expanded.game import Card
  self.game.players[1].hand=[Card(self.game._new_id(),'CORE_CS2_029') for _ in range(3)]
  card=self.fixture.craft('CORE_GIL_623');health=card.base_stat_override[1]
  self.game.step(next(a for a in self.game.legal_actions() if a.kind=='play' and a.source==card.uid))
  m=next(m for m in self.game.players[0].minions if m.card_id==card.card_id)
  self.assertEqual(m.max_health,health-3);self.assertIn('TAUNT',self.game._effective_keywords(m))

 def test_halazzi_fills_hand_and_gives_composite_rush(self):
  self.game.players[0].hand=[];m=self.fixture.play('CORE_TRL_900')
  self.assertEqual([c.card_id for c in self.game.players[0].hand],['TRL_348t']*10)
  self.assertIn('RUSH',self.game._effective_keywords(m))

 def test_discounted_dreamsaber_composite_attacks_two_enemies(self):
  enemies=[self.game._summon(1,'EDR_851t') for _ in range(2)]
  for m in enemies:self.game._buff(m,0,30)
  before=[m.health for m in enemies]
  card=self.fixture.craft('EDR_014');card.cost_delta=-20
  self.game.step(next(a for a in self.game.legal_actions() if a.kind=='play' and a.source==card.uid))
  m=next(m for m in self.game.players[0].minions if m.card_id==card.card_id)
  self.assertEqual([e.health for e in enemies],[h-m.attack for h in before])

 def test_torga_draws_kindred_and_matching_partner(self):
  self.game.players[0].deck=['DINO_435','CORE_GIL_558'];before={c.uid for c in self.game.players[0].hand}
  self.fixture.play('TLC_102')
  drawn={c.card_id for c in self.game.players[0].hand if c.uid not in before}
  self.assertEqual(drawn,{'DINO_435','CORE_GIL_558'})

 def test_choice_schema_rejects_invalid_nested_death_and_expiry(self):
  from expanded.effect_schema import validate_operations,EffectSchemaError
  malformed=(('choose_self_effect',(('label',('missing_handler',)),)),
   ('grant_death_self',(('draw',True),)),('temporary_keyword_self','STEALTH','never'),
   ('choose_self_effect',(('label',),)))
  for op in malformed:
   with self.assertRaises(EffectSchemaError):validate_operations((op,),strict_unknown=True)

 def test_all_component_recipes_cross_visible_feature_boundary(self):
  import json
  from expanded.zombeast_text_parts import PARTS
  from expanded.features import encode_decision
  for cid in PARTS:
   with self.subTest(cid=cid):
    self.game.players[0].hand=[];self.fixture.craft(cid)
    view=self.game.observe(0);json.dumps(view)
    self.assertTrue(encode_decision(dict(observation=view,actor=0,actions=view['legal_actions'])))

 def test_attacking_kill_memory_includes_cleave_victims(self):
  m=self.fixture.play('CORE_SCH_605');m.exhausted=False
  victims=[self.game._summon(1,'EDR_851t') for _ in range(3)]
  self.game._attack(m.uid,victims[1].uid)
  self.assertEqual({v.uid for v in self.game._combat_kill_history[m.uid]},{v.uid for v in victims})

 def test_triennium_rex_generates_discounted_minions_on_kindred_and_death(self):
  self.game.players[0].previous_tribes={'BEAST'}
  before={c.uid for c in self.game.players[0].hand}
  m=self.fixture.play('END_015')
  given=[c for c in self.game.players[0].hand if c.uid not in before]
  self.assertEqual(len(given),1);self.assertEqual(given[0].cost_delta,-2)
  before={c.uid for c in self.game.players[0].hand}
  m.health=0;self.game._settle(allow_event_choices=True)
  given=[c for c in self.game.players[0].hand if c.uid not in before]
  self.assertEqual(len(given),1);self.assertEqual(given[0].cost_delta,-2)

 def test_all_text_recipes_pass_strict_admission(self):
  from expanded.zombeast_text_parts import PARTS
  self.assertEqual(len(PARTS),59)
  self.game.forge_contracts={('zombeast',1):tuple(PARTS.values())}
  self.assertEqual(len(self.game._forge_pool('zombeast',1,0)),59)
