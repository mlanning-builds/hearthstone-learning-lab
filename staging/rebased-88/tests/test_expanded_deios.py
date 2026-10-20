import unittest,gzip,json
from copy import deepcopy
from unittest.mock import patch
import test_expanded_generation as fixtures
from expanded import Action,cards

class DeiosTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with gzip.open('data/standard/all_cards.json.gz','rt') as f:cls.records={d['id']:d for d in json.load(f)}
 def setUp(self):
  self.g=fixtures.GenerationTests().game();self.p,self.q=self.g.players
  self.g.cards['TIME_064']=deepcopy(self.records['TIME_064'])
  change=patch.dict(cards.RULES,{'TIME_064':('none',[])});change.start();self.addCleanup(change.stop)
 def deios(self,owner=0):return self.g._summon(owner,'TIME_064')
 def test_baseline_weapon_deathrattle_draws_once(self):
  self.g._equip(0,'JAIL_503');self.g._break_weapon(0);self.assertEqual(len(self.p.hand),1)
 def test_weapon_deathrattle_draws_twice(self):
  self.deios();self.g._equip(0,'JAIL_503');self.g._break_weapon(0)
  self.assertEqual(len(self.p.hand),2);self.assertIsNone(self.p.weapon);self.assertIsNone(self.p.equipped_card)
 def test_weapon_attached_effect_repeats(self):
  self.deios();self.g._equip(0,'JAIL_503');self.p.weapon['attached_death_effects']=[('armor',1)]
  self.g._break_weapon(0);self.assertEqual(self.p.armor,2);self.assertEqual(len(self.p.hand),2)
 def test_silenced_deios_does_not_repeat_weapon(self):
  self.g._silence(self.deios());self.g._equip(0,'JAIL_503');self.g._break_weapon(0);self.assertEqual(len(self.p.hand),1)
 def test_enemy_deios_does_not_repeat_weapon(self):
  self.deios(1);self.g._equip(0,'JAIL_503');self.g._break_weapon(0);self.assertEqual(len(self.p.hand),1)
 def test_two_deios_are_twice_not_four_times(self):
  self.deios();self.deios();self.g._equip(0,'JAIL_503');self.g._break_weapon(0);self.assertEqual(len(self.p.hand),2)
 def test_dormant_deios_does_not_repeat(self):
  self.g._summon(0,'TIME_064',dormant_turns=2);self.g._equip(0,'JAIL_503');self.g._break_weapon(0);self.assertEqual(len(self.p.hand),1)
 def test_weapon_summons_two_printed_tokens(self):
  self.deios();self.g._equip(0,'CORE_OG_031');self.g._break_weapon(0);self.g._settle()
  self.assertEqual([m.card_id for m in self.p.minions].count('OG_031a'),2)
 def test_frostmourne_repeats_captured_identity_list(self):
  self.deios();self.g._equip(0,'CORE_RLK_086');self.p.weapon['stored_kills']=['CORE_EX1_162']
  self.g._break_weapon(0);self.g._settle();self.assertEqual([m.card_id for m in self.p.minions].count('CORE_EX1_162'),2)
 def test_weapon_end_replay_and_end_trigger_each_double(self):
  m=self.deios();self.g._summon(0,'CS2_058');self.g._equip(0,'CATA_472');self.g._break_weapon(0);self.g._settle()
  self.assertEqual(m.attack,8)
 def test_repeated_break_of_removed_weapon_is_noop(self):
  self.deios();self.g._equip(0,'JAIL_503');self.g._break_weapon(0);self.g._break_weapon(0);self.assertEqual(len(self.p.hand),2)
 def test_activated_power_pays_and_counts_once(self):
  self.deios();before=self.p.hero_power_uses;self.g.step(Action('power',target=-2))
  self.assertEqual(self.q.health,28);self.assertEqual(self.p.mana,8);self.assertEqual(self.p.hero_power_uses,before+1)
 def test_minion_deathrattle_doubles(self):
  self.deios();m=self.g._summon(0,'CORE_LOOT_413');m.health=0;self.g._settle();self.assertEqual(self.p.armor,6)
 def test_end_effect_doubles(self):
  m=self.deios();self.g._summon(0,'CS2_058');self.g.step(Action('end'));self.assertEqual(m.attack,6)
 def test_passive_deathknight_power_remains_single(self):
  self.deios();self.p.primary_power=dict(card_id='END_003p',imbue_level=1)
  c=self.g._add(0,'CORE_EX1_012');self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid))
  m=next(m for m in self.p.minions if m.card_id=='CORE_EX1_012');attack=self.g.cards[m.card_id]['attack']
  from expanded.imbue import PINNED_VALUES
  self.assertEqual(m.attack,attack+int(PINNED_VALUES['END_003p']['TAG_SCRIPT_DATA_NUM_1']))
 def test_passive_power_affects_only_first_undead_even_with_deios(self):
  self.deios();self.p.primary_power=dict(card_id='END_003p',imbue_level=1)
  for _ in range(2):
   c=self.g._add(0,'CORE_EX1_012');self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid))
  latest=max((m for m in self.p.minions if m.card_id=='CORE_EX1_012'),key=lambda m:m.uid)
  self.assertEqual(latest.attack,self.g.cards['CORE_EX1_012']['attack'])

 def test_free_active_power_repetition_preserves_usage_payment_and_cost_modifiers(self):
  self.deios();self.p.primary_power=dict(card_id='EDR_851p',imbue_level=1);self.p.power_used=True
  self.p.next_power_cost_effects=[dict(kind='increase',amount=3)];before=(self.p.mana,self.p.hero_power_uses,self.p.power_used,deepcopy(self.p.next_power_cost_effects))
  self.g._start_play_effects([('imbue_trigger_power',)],dict(owner=0,source=None,target=0,bonus=0,lifesteal=False));self.g._settle(allow_event_choices=True)
  self.assertEqual(self.q.health,28);self.assertEqual((self.p.mana,self.p.hero_power_uses,self.p.power_used,self.p.next_power_cost_effects),before)
 def test_paid_wisprider_with_deios_imbues_then_triggers_twice(self):
  self.deios();c=self.g._add(0,'EDR_519');before=self.p.hero_power_uses
  self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid))
  self.assertEqual(self.q.health,24);self.assertEqual(self.p.imbue_count,2);self.assertEqual(self.p.hero_power_uses,before);self.assertFalse(self.p.power_used)
 def test_free_passive_power_is_noop_even_with_deios(self):
  self.deios();self.p.primary_power=dict(card_id='END_003p',imbue_level=1)
  self.assertEqual(self.g._imbue_consumer_split(('imbue_trigger_power',),dict(owner=0)),(('batch30_noop',),()))
