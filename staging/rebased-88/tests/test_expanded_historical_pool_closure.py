"""Outcome membership and literal behavior for historical generation closure."""
from copy import deepcopy
import unittest
from expanded import Game,Action,random_deck
from engine.game import Card
from expanded.cards import registry,CHOICES
from expanded.generation_cards import pool
from expanded.historical_generation_catalog import load_universe,historical_contract
from standard.catalog import CLASSES

class HistoricalPoolClosureTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  g=Game([random_deck('DRUID',31),random_deck('MAGE',53)],seed=71,record=True)
  g.step(Action('mulligan'));g.step(Action('mulligan'))
  for p in g.players:
   p.hand=[];p.board=[];p.deck=[];p.mana=p.max_mana=10;p.health=30;p.armor=0
  cls.prototype=g
 def game(self):return deepcopy(self.prototype)
 def play(self,g,cid,branch=None,target=0):
  c=g._add(0,cid)
  matches=[a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid and a.target==target and (branch is None or a.choices==(branch,))]
  self.assertTrue(matches,(cid,branch,target));g.step(matches[0]);return c
 def test_alternate_reality_full_pool_all_eleven_classes(self):
  u=load_universe();r=pool(era='past',mechanic='CHOOSE_ONE');implemented=registry()
  for hero_class in CLASSES:
   contract=historical_contract(r,hero_class,u)
   self.assertEqual(len(contract.card_ids),54)
   self.assertEqual(set(contract.card_ids)-implemented.keys(),set())
   g=self.game();g.players[0].hero_class=hero_class
   self.assertEqual(set(g._generation_candidates(r,0)),set(contract.card_ids))
 def test_capture_extreme_cost_uses_live_cost(self):
  for branch,wanted in ((0,'CORE_CS2_029'),(1,'CORE_CS2_023')):
   g=self.game();a=Card(g._new_id(),'CORE_CS2_029');g._set_card_cost(a,0)
   b=Card(g._new_id(),'CORE_CS2_023');g._set_card_cost(b,9);g.players[0].deck=[a,b]
   self.play(g,'AV_295',branch);self.assertEqual(g.players[0].hand[0].card_id,wanted)
 def test_jade_shuffle_has_three_physical_copies(self):
  g=self.game();self.play(g,'CFM_602',1)
  self.assertEqual([c.card_id for c in g.players[0].deck],['CFM_602']*3)
  self.assertEqual(len({c.uid for c in g.players[0].deck}),3)
 def test_jade_grows_across_casts(self):
  g=self.game();self.play(g,'CFM_602',0);self.play(g,'CFM_602',0)
  self.assertEqual([(m.attack,m.health) for m in g.players[0].minions],[(1,1),(2,2)])
 def test_rising_winds_twinspell_and_copy(self):
  g=self.game();self.play(g,'YOD_001',1)
  self.assertEqual([c.card_id for c in g.players[0].hand],['YOD_001ts'])
  self.play_existing(g,'YOD_001ts',1)
  self.assertEqual(g.players[0].hand,[]);self.assertEqual(len(g.players[0].minions),2)
 def play_existing(self,g,cid,branch):
  c=next(c for c in g.players[0].hand if c.card_id==cid)
  g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid and a.choices==(branch,)))
 def test_combined_twinspell_only_one_copy_paid_and_internal(self):
  for internal in (False,True):
   g=self.game();g._summon(0,'OG_044')
   if internal:g._start_play_effects([('cast_fixed_spell','YOD_001','random')],dict(owner=0,source=None,target=0,bonus=0,lifesteal=False))
   else:self.play(g,'YOD_001',-1)
   self.assertEqual([c.card_id for c in g.players[0].hand],['YOD_001ts'])
   self.assertEqual(sum(m.card_id=='YOD_001t' for m in g.players[0].minions),1)
 def test_phaser_selects_distinct_enemy_targets(self):
  g=self.game();a=g._summon(1,'CS2_182');b=g._summon(1,'CS2_182')
  self.play(g,'GDB_851',0);self.assertEqual((a.health,b.health),(3,3))
 def test_phaser_dormancy(self):
  g=self.game();m=g._summon(1,'CS2_182');self.play(g,'GDB_851',1,m.uid)
  self.assertEqual(m.dormant,2)
 def test_hidden_oasis_correct_token(self):
  g=self.game();self.play(g,'ULD_135',0);m=g.players[0].minions[0]
  self.assertEqual((m.card_id,m.attack,m.health),('ULD_135at',6,6));self.assertIn('TAUNT',g._effective_keywords(m))
 def test_flamecannon_cannot_hit_hero(self):
  g=self.game();m=g._summon(1,'CS2_182');self.play(g,'GVG_001')
  self.assertEqual(m.health,1);self.assertEqual(g.players[1].health,30)
 def test_shatter_only_frozen_targets_legal(self):
  g=self.game();a=g._summon(0,'CS2_182');b=g._summon(1,'CS2_182');g._freeze(b.uid);c=g._add(0,'OG_081')
  targets={action.target for action in g.legal_actions() if action.kind=='play' and action.source==c.uid}
  self.assertEqual(targets,{b.uid})
 def test_mass_polymorph_resets_all_bodies(self):
  g=self.game();g._summon(0,'CS2_182');g._summon(1,'CS2_182');self.play(g,'AV_218')
  self.assertEqual([(m.card_id,m.attack,m.health) for p in g.players for m in p.minions],[('CS2_tk1',1,1)]*2)
 def test_biscuit_refresh_is_capped(self):
  g=self.game();g.players[0].mana=6;self.play(g,'YOP_019t');self.assertEqual(g.players[0].mana,8)
 def test_spell_and_tribe_discounts_match_selectors(self):
  for cid,selector in (('SW_462','FIRE'),('TRL_310','ELEMENTAL')):
   g=self.game();self.play(g,cid);self.assertEqual(g.players[0].cost_effects[-1]['selector'],selector)
 def test_echo_board_to_hand_resets_enchantments_and_identity(self):
  g=self.game();m=g._summon(0,'CS2_182');g._buff(m,2,3);self.play(g,'GVG_005')
  card=g.players[0].hand[0]
  self.assertEqual(card.card_id,'CS2_182');self.assertNotEqual(card.uid,m.uid)
  g._summon(0,card.card_id,entry_source=card)
  self.assertEqual((g.players[0].minions[-1].attack,g.players[0].minions[-1].health),(4,5))
 def test_arcane_blast_doubles_spell_damage_bonus(self):
  g=self.game();g._summon(0,'CORE_EX1_012');m=g._summon(1,'CS2_182')
  self.play(g,'AT_004',target=m.uid);self.assertEqual(m.health,1)
 def test_spring_water_refreshes_only_spell_draws(self):
  g=self.game();g.players[0].deck=[Card(g._new_id(),'CS2_182'),Card(g._new_id(),'CS2_029')]
  self.play(g,'BAR_542');self.assertEqual(g.players[0].mana,7)
 def test_book_discards_only_drawn_spells(self):
  g=self.game();old=g._add(0,'CS2_029');g.players[0].deck=[Card(g._new_id(),'CS2_182'),Card(g._new_id(),'CS2_029'),Card(g._new_id(),'CS2_023')]
  self.play(g,'GIL_548');self.assertIn(old,g.players[0].hand)
  self.assertEqual(sorted(c.card_id for c in g.players[0].hand),['CS2_029','CS2_182'])
 def test_flow_materializes_deck_and_reduces_spells_only(self):
  g=self.game();g.players[0].deck=['CS2_182','CS2_029'];self.play(g,'BT_002')
  self.assertEqual(g.players[0].deck[0],'CS2_182');self.assertEqual(g._cost(g.players[0].deck[1],0),3)
 def test_evocation_generated_cards_are_temporary(self):
  g=self.game();self.play(g,'BT_006');self.assertEqual(len(g.players[0].hand),10)
  self.assertTrue(all(g._is_temporary(c) for c in g.players[0].hand))
 def test_icicle_checks_frozen_before_damage(self):
  g=self.game();g.players[0].deck=[Card(g._new_id(),'CS2_029')];m=g._summon(1,'CS2_182');g._freeze(m.uid)
  self.play(g,'EX1_179',target=m.uid);self.assertEqual(m.health,3);self.assertEqual(len(g.players[0].hand),1)
 def test_shooting_star_hits_only_target_and_neighbors(self):
  g=self.game();ms=[g._summon(1,'CS2_182') for _ in range(4)]
  self.play(g,'BOT_453',target=ms[1].uid);self.assertEqual([m.health for m in ms],[4,4,4,5])
 def test_convoke_admits_complete_choose_one_dependencies(self):
  g=self.game();g._generation_preflight('REV_365',0)
  from expanded.spell_casting import INTERNAL_OPERATIONS
  self.assertIn('historical_ritual_jade',INTERNAL_OPERATIONS)
 def test_all_new_rules_have_strict_operand_schemas(self):
  from expanded.historical_pool_closure import TOKEN_RULES
  from expanded.effect_schema import validate_operations
  for cid,(_,ops) in TOKEN_RULES.items():
   with self.subTest(card=cid):validate_operations(ops,strict_unknown=True)

 def test_specters_draws_all_before_discarding_so_full_hand_burns(self):
  g=self.game()
  for _ in range(8):g._add(0,'CS2_182')
  g.players[0].deck=[Card(g._new_id(),'CS2_182'),Card(g._new_id(),'CS2_023'),Card(g._new_id(),'CS2_029')]
  self.play(g,'GIL_548')
  # Eight held cards, then two spells drawn; the third card burns before
  # those spells are discarded. It cannot occupy their later free slots.
  self.assertEqual(len(g.players[0].hand),8)
  self.assertEqual(g.players[0].deck,[])
 def test_missing_alternate_dependency_rejects_before_rng(self):
  g=self.game();del g.cards['CFM_602'];rng=g.rng.getstate()
  from engine.cards import UnsupportedCard
  with self.assertRaisesRegex(UnsupportedCard,'eligible effects not implemented'):
   g._generation_candidates(pool(era='past',mechanic='CHOOSE_ONE'),0)
  self.assertEqual(g.rng.getstate(),rng)
 def test_alternate_reality_transforms_both_zones_with_discount(self):
  g=self.game();g._add(0,'CS2_182');g.players[0].deck=[Card(g._new_id(),'CS2_029')]
  self.play(g,'TIME_707')
  universe=load_universe();ids=set(historical_contract(pool(era='past',mechanic='CHOOSE_ONE'),'DRUID',universe).card_ids)
  for c in g.players[0].hand+g.players[0].deck:
   self.assertIn(c.card_id,ids);self.assertEqual(getattr(c,'cost_delta',0),-1)

 def test_greater_arcane_missiles_has_three_three_damage_hits(self):
  for bonus in (0,1):
   g=self.game()
   if bonus:g._summon(0,'CORE_EX1_012')
   self.play(g,'CFM_623')
   self.assertEqual(g.players[1].health,30-3*(3+bonus))

 def test_astral_communion_discards_entire_hand(self):
  g=self.game();g.players[0].max_mana=g.players[0].mana=5;g._add(0,'CS2_182');self.play(g,'AT_043')
  self.assertEqual((g.players[0].max_mana,g.players[0].mana),(10,5));self.assertEqual(g.players[0].hand,[])
 def test_alignment_applies_to_both_own_zones_only(self):
  g=self.game();own=g._add(0,'CS2_182');other=g._add(1,'CS2_182');g.players[0].deck=['CS2_029'];self.play(g,'BAR_539')
  self.assertEqual((g.players[0].max_mana,g.players[0].mana),(0,0))
  self.assertEqual(g._cost(own,0),1);self.assertEqual(g._cost(g.players[0].deck[0],0),1);self.assertEqual(g._cost(other,1),4)
 def test_cosmic_phenomenon_checks_board_after_summons(self):
  g=self.game()
  for _ in range(4):g._summon(0,'CS2_182')
  self.play(g,'GDB_882');self.assertEqual(len(g.players[0].minions),7)
  self.assertEqual([(m.attack,m.health) for m in g.players[0].minions[-3:]],[(3,4)]*3)
 def test_choose_thrice_preserves_order_and_does_not_consume_choose_both(self):
  g=self.game();g.players[0].historical_eonar_pending=True
  from expanded.cards import CHOICES
  i=next(i for i,(label,_,_) in enumerate(CHOICES['VAC_907']) if label=='Armor / Refresh / Armor')
  self.play(g,'VAC_907',i)
  self.assertEqual(g.players[0].armor,10);self.assertTrue(g.players[0].historical_eonar_pending)
 def test_ancient_mysteries_draws_secret_at_zero(self):
  g=self.game();g.players[0].deck=[Card(g._new_id(),'CS2_029'),Card(g._new_id(),'EX1_287')];self.play(g,'ULD_726')
  self.assertEqual([c.card_id for c in g.players[0].hand],['EX1_287']);self.assertEqual(g._cost(g.players[0].hand[0],0),0)
