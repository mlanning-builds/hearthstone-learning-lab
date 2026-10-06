import unittest,gzip,json
from pathlib import Path
from copy import deepcopy
from unittest.mock import patch
import test_expanded_generation as fixtures
from expanded import cards,azshara as rules,Action
from expanded.locations import LOCATION_RULES
from engine.game import Card
from engine.cards import UnsupportedCard

class AzsharaTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with gzip.open(Path(__file__).resolve().parents[1]/'data/standard/all_cards.json.gz','rt') as f:cls.records={c['id']:c for c in json.load(f)}
 def setUp(self):
  self.fx=fixtures.GenerationTests();self.g=self.fx.game();self.p,self.q=self.g.players
  self.g.cards.update({cid:deepcopy(c) for cid,c in self.records.items() if cid.startswith('TIME_211')})
  self.g.cards['TEST_AZ_MINION']=dict(self.g.cards['NEW1_034'],id='TEST_AZ_MINION',attack=3,health=5,mechanics=[])
  for table,values in ((cards.RULES,rules.RULES),(cards.CHOICES,rules.CHOICES),(LOCATION_RULES,rules.LOCATION_RULES)):
   p=patch.dict(table,values);p.start();self.addCleanup(p.stop)
  self.fx.install(self.g,rules.SPELLS,['CORE_CS2_029'])
 def play(self,branch):
  self.p.mana=10;c=self.g._add(0,'TIME_211');self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid and a.choices==(branch,)))
 def run_ops(self,ops,**kw):self.fx.run_ops(self.g,ops,**kw)
 def activate(self,cid,target=0):
  location=self.g._place_location(0,cid);self.g.step(Action('activate',source=location.uid,target=target));return location
 def test_upgrades_all_physical_copies_in_hand_deck_and_board(self):
  hand=self.g._add(0,rules.ZIN[0]);hand.cost_delta=-2;deck=Card(self.g._new_id(),rules.ZIN[0]);self.p.deck=[deck];board=self.g._place_location(0,rules.ZIN[0]);board.durability=1;board.ready_turn=self.g.turn+4;board.rule_state={'example':7};self.play(0)
  self.assertIs(self.p.hand[0],hand);self.assertEqual(hand.card_id,rules.ZIN[1]);self.assertEqual(hand.cost_delta,-2);self.assertIs(self.p.deck[0],deck);self.assertEqual(deck.card_id,rules.ZIN[1]);self.assertEqual(board.card_id,rules.ZIN[1]);self.assertEqual((board.durability,board.ready_turn),(1,self.g.turn+4));self.assertEqual(board.rule_state,{'example':7})
 def test_destroys_other_family_in_all_zones_including_upgraded(self):
  self.g._add(0,rules.WELL[1]);self.p.deck=[rules.WELL[0],rules.WELL[1]];location=self.g._place_location(0,rules.WELL[1]);self.play(0)
  self.assertFalse(self.p.hand);self.assertFalse(self.p.deck);self.assertNotIn(location,self.p.board);self.assertFalse(self.p.discard_history)
 def test_opponent_copies_are_unchanged(self):
  c=self.g._add(1,rules.WELL[0]);location=self.g._place_location(1,rules.ZIN[0]);self.play(0);self.assertEqual(c.card_id,rules.WELL[0]);self.assertEqual(location.card_id,rules.ZIN[0])
 def test_choose_both_destroys_both_families(self):
  self.g._summon(0,'CORE_OG_044');self.p.deck=[*rules.WELL,*rules.ZIN];self.g._place_location(0,rules.WELL[0]);self.g._place_location(0,rules.ZIN[0]);self.play(-1);self.assertFalse(self.p.deck);self.assertFalse(self.p.locations)
 def test_reverse_choice_empowers_well(self):
  self.p.deck=[rules.WELL[0],rules.ZIN[0]];self.play(1);self.assertEqual(self.p.deck,[rules.WELL[1]])
 def test_repeated_same_choice_does_not_reset_durability(self):
  location=self.g._place_location(0,rules.ZIN[1]);location.durability=1;self.play(0);self.assertEqual(location.durability,1);self.assertEqual(location.card_id,rules.ZIN[1])
 def test_missing_location_metadata_rejects_before_mutation(self):
  self.p.deck=[rules.ZIN[0],rules.WELL[0]];del self.g.cards[rules.ZIN[1]]
  with self.assertRaises(UnsupportedCard):self.run_ops(rules.CHOICES['TIME_211'][0][2])
  self.assertEqual(self.p.deck,[rules.ZIN[0],rules.WELL[0]])
 def test_destroyed_board_location_uses_removal_effects(self):
  location=self.g._place_location(0,rules.WELL[0]);location.attached_death_effects=[('summon','TEST_AZ_MINION',1)];self.play(0)
  self.assertEqual(sum(m.card_id=='TEST_AZ_MINION' for m in self.p.minions),1)
 def test_normal_well_fills_hand_with_temporary_spells(self):
  self.g._add(0,'NEW1_034');location=self.activate(rules.WELL[0]);self.assertEqual(len(self.p.hand),10);self.assertEqual(location.durability,2)
  generated=self.p.hand[1:];self.assertTrue(all(c.card_id=='CORE_CS2_029' and self.g._is_temporary(c) for c in generated));self.assertTrue(all(not c.rule_state.get('repeat_spell') for c in generated))
 def test_upgraded_well_retains_repeat_flag_on_generated_cards(self):
  self.activate(rules.WELL[1]);self.assertEqual(len(self.p.hand),10);self.assertTrue(all(c.rule_state.get('repeat_spell') for c in self.p.hand))
 def test_temporary_spells_expire_at_owner_end(self):
  self.activate(rules.WELL[1]);self.g.step(Action('end'));self.assertFalse(self.p.hand);self.assertEqual(len(self.p.discard_history),10)
 def test_full_hand_well_does_not_overfill_or_consume_rng(self):
  for _ in range(10):self.g._add(0,'NEW1_034')
  rng=self.g.rng.getstate();self.activate(rules.WELL[1]);self.assertEqual(len(self.p.hand),10);self.assertEqual(self.g.rng.getstate(),rng)
 def test_missing_pool_rolls_back_location_charge(self):
  location=self.g._place_location(0,rules.WELL[0]);self.g._generation_pools.clear();before=deepcopy(self.g.observe(0))
  with self.assertRaises(UnsupportedCard):self.g.step(Action('activate',source=location.uid))
  self.assertEqual(self.g.observe(0),before)
 def test_well_spell_repeats_on_paid_play(self):
  self.activate(rules.WELL[1]);c=self.p.hand[0];self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid and a.target==-2));self.assertEqual(self.q.health,18);self.assertEqual(len(self.p.played_history),1)
 def test_well_spell_repeats_when_cast_from_hand_internally(self):
  self.activate(rules.WELL[1]);c=self.p.hand[0];self.run_ops([('cast_zone_spell','hand',c.uid,'selected')],target=-2);self.assertEqual(self.q.health,18);self.assertFalse(self.p.played_history);self.assertEqual(len(self.p.hand),9)
 def test_normal_zin_copies_buffs_damage_keywords_without_battlecry(self):
  m=self.g._summon(0,'TEST_AZ_MINION');self.g._buff(m,2,2);m.health=4;m.keywords.add('TAUNT');self.activate(rules.ZIN[0],m.uid);copy=self.p.minions[-1]
  self.assertEqual((copy.attack,copy.max_health,copy.health),(5,7,4));self.assertIn('TAUNT',copy.keywords);self.assertNotEqual(copy.uid,m.uid)
 def test_upgraded_zin_doubles_current_stats_preserving_damage(self):
  m=self.g._summon(0,'TEST_AZ_MINION');self.g._buff(m,2,2);m.health=4;self.activate(rules.ZIN[1],m.uid);copy=self.p.minions[-1];self.assertEqual((copy.attack,copy.max_health,copy.health),(10,11,8));self.assertEqual((m.attack,m.max_health,m.health),(5,7,4))
 def test_external_attack_aura_not_doubled_as_enchantment(self):
  self.g._summon(0,'NEW1_033');m=self.g._summon(0,'TEST_AZ_MINION');self.assertEqual(m.attack,4);self.activate(rules.ZIN[1],m.uid);self.assertEqual(self.p.minions[-1].attack,7)
 def test_final_charge_frees_space_for_copy(self):
  for _ in range(6):self.g._summon(0,'TEST_AZ_MINION')
  location=self.g._place_location(0,rules.ZIN[0]);location.durability=1;self.g.step(Action('activate',source=location.uid,target=self.p.minions[0].uid));self.assertEqual(len(self.p.minions),7);self.assertFalse(self.p.locations)
 def test_full_board_nonfinal_use_does_not_create_copy(self):
  for _ in range(6):self.g._summon(0,'TEST_AZ_MINION')
  location=self.g._place_location(0,rules.ZIN[0]);self.g.step(Action('activate',source=location.uid,target=self.p.minions[0].uid));self.assertEqual(len(self.p.minions),6);self.assertEqual(location.durability,2)
 def test_staging_and_any_class_spell_contract(self):
  self.assertNotIn('TIME_211',cards.COLLECTIBLE_IDS);self.assertEqual(rules.requests_for('TIME_211'),{rules.SPELLS})

 def test_doubled_stats_exist_before_summon_notification(self):
  m=self.g._summon(0,'TEST_AZ_MINION');seen=[];capture=self.g._capture_summon_event
  def record(entity,origin):
   if entity.card_id=='TEST_AZ_MINION':seen.append((entity.attack,entity.health))
   return capture(entity,origin)
  with patch.object(self.g,'_capture_summon_event',side_effect=record):self.activate(rules.ZIN[1],m.uid)
  self.assertEqual(seen,[(6,10)])
 def test_upgraded_location_destruction_does_not_remove_generated_spells(self):
  self.activate(rules.WELL[1]);self.p.hand.pop();self.play(0);self.assertEqual(len(self.p.hand),9);self.assertTrue(all(c.card_id=='CORE_CS2_029' for c in self.p.hand));self.assertTrue(all(c.rule_state.get('repeat_spell') for c in self.p.hand))
