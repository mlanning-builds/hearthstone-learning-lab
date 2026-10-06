import unittest,gzip,json
from pathlib import Path
from copy import deepcopy
from unittest.mock import patch
import test_expanded_generation as fixtures
from expanded import cards,rafaam as rules,Action
from engine.game import Card

class RafaamTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with gzip.open(Path(__file__).resolve().parents[1]/'data/standard/all_cards.json.gz','rt') as f:cls.records={c['id']:c for c in json.load(f)}
 def setUp(self):
  self.g=fixtures.GenerationTests().game();self.p,self.q=self.g.players
  self.g.cards.update({cid:deepcopy(self.records[cid]) for cid in rules.FAMILY})
  for table,values in ((cards.RULES,{**rules.RULES,**rules.TOKEN_RULES}),(cards.DEATH_EFFECTS,rules.DEATH_EFFECTS)):
   p=patch.dict(table,values);p.start();self.addCleanup(p.stop)
 def run_ops(self,ops,**kw):
  ctx=dict(owner=0,source=None,target=0,bonus=0,lifesteal=False);ctx.update(kw)
  self.g._start_play_effects(ops,ctx);self.g._settle(allow_event_choices=True)
 def play(self,cid):
  card=self.g._add(0,cid);self.p.mana=10
  self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==card.uid));return card
 def history(self,ids):self.p.played_history=[dict(card_id=cid,cost=0) for cid in ids]
 def test_family_excludes_historical_rafaams_and_includes_sheep(self):
  self.assertEqual(len(rules.FAMILY),11);self.assertIn('TIME_005t9t',rules.FAMILY)
  self.assertFalse({'LOE_092','DAL_422','REV_835'}&rules.FAMILY);self.assertNotIn('TIME_005t9t',rules.REQUIRED)
 def test_tiny_paid_battlecry_and_actual_death_draw_physical_rafaams(self):
  a=Card(self.g._new_id(),'TIME_005t7');a.attack_bonus=3
  b=Card(self.g._new_id(),'TIME_005t4');self.p.deck=[a,b,'CORE_CS2_029']
  self.play('TIME_005t1');self.assertEqual(len(self.p.hand),1)
  m=self.p.minions[0];m.health=0;self.g._settle()
  self.assertEqual({c.uid for c in self.p.hand},{a.uid,b.uid});self.assertEqual(a.attack_bonus,3);self.assertEqual(self.p.deck,['CORE_CS2_029'])
 def test_filtered_draw_empty_deck_does_not_fatigue(self):
  self.p.deck=[];self.run_ops([('rafaam_draw',)]);self.assertEqual(self.p.fatigue,0);self.assertEqual(self.p.health,30)
 def test_filtered_draw_full_hand_burns_matching_card(self):
  for _ in range(10):self.g._add(0,'TOKEN_COIN')
  self.p.deck=['TIME_005t1'];self.run_ops([('rafaam_draw',)]);self.assertFalse(self.p.deck);self.assertEqual(len(self.p.hand),10)
 def test_green_buffs_other_friendly_rafaams_only(self):
  source=self.g._summon(0,'TIME_005t2');a=self.g._summon(0,'TIME_005t1');b=self.g._summon(1,'TIME_005t1');sheep=self.g._add(0,'TIME_005t9t');other=self.g._add(0,'NEW1_034')
  before=(source.attack,a.attack,b.attack);self.run_ops([('rafaam_buff',)],source=source)
  self.assertEqual((source.attack,a.attack,b.attack),(before[0],before[1]+2,before[2]));self.assertEqual(sheep.attack_bonus,2);self.assertEqual(other.attack_bonus,0)
 def test_explorer_offers_only_rafaams_and_preserves_selected_physical_card(self):
  c=Card(self.g._new_id(),'TIME_005t7');c.cost_delta=-2;self.p.deck=['CORE_CS2_029',c,'NEW1_034']
  self.play('TIME_005t3');self.assertEqual([x['card_id'] for x in self.g.pending_choice['options']],['TIME_005t7'])
  self.g.step(next(a for a in self.g.legal_actions() if a.kind=='choose'))
  self.assertIs(self.p.hand[0],c);self.assertEqual(c.cost_delta,-2);self.assertEqual(self.p.discoveries_total,1)
 def test_explorer_empty_family_does_not_open_choice(self):
  self.run_ops([('rafaam_discover',)]);self.assertIsNone(self.g.pending_choice)
 def test_explorer_options_hidden_from_opponent(self):
  self.p.deck=['TIME_005t7'];self.play('TIME_005t3')
  self.assertNotIn('options',self.g.observe(1)['pending_choice'])
 def test_warchief_base_and_holding_sheep(self):
  self.play('TIME_005t4');self.assertEqual(self.p.armor,5)
  self.g._add(0,'TIME_005t9t');self.play('TIME_005t4');self.assertEqual(self.p.armor,15)
 def test_mindflayer_copies_buffs_without_repeating_battlecry(self):
  self.g._add(0,'TIME_005t9t');card=self.g._add(0,'TIME_005t5');card.attack_bonus=2;card.health_bonus=3
  self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==card.uid))
  self.assertEqual(len(self.p.minions),2);self.assertEqual(self.p.minions[0].attack,self.p.minions[1].attack);self.assertEqual(self.p.minions[0].max_health,self.p.minions[1].max_health)
 def test_mindflayer_without_other_rafaam_does_not_copy(self):
  self.play('TIME_005t5');self.assertEqual(len(self.p.minions),1)
 def test_calamitous_spares_family_both_sides_and_heroes(self):
  a=self.g._summon(0,'TIME_005t9t');b=self.g._summon(1,'TIME_005t1');x=self.g._summon(0,'NEW1_034');y=self.g._summon(1,'NEW1_034')
  self.run_ops([('rafaam_damage',)]);self.assertIn(a,self.p.minions);self.assertIn(b,self.q.minions);self.assertNotIn(x,self.p.minions);self.assertNotIn(y,self.q.minions);self.assertEqual((self.p.health,self.q.health),(30,30))
 def test_giant_counts_repeat_paid_plays_and_sheep_but_not_summons(self):
  card=self.g._add(0,'TIME_005t7');base=self.g._cost(card,0);self.g._summon(0,'TIME_005t1');self.assertEqual(self.g._cost(card,0),base)
  self.history(['TIME_005t1','TIME_005t1','TIME_005t9t','NEW1_034']);self.assertEqual(self.g._cost(card,0),max(0,base-3))
 def test_murloc_discount_waits_for_rafaam_then_consumes(self):
  self.play('TIME_005t8');self.play('NEW1_034');self.assertEqual(len(self.p.cost_effects),1)
  card=self.g._add(0,'TIME_005t7');expected=max(0,self.records[card.card_id]['cost']-1-3);self.assertEqual(self.g._cost(card,0),expected)
  self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==card.uid));self.assertFalse(self.p.cost_effects)
 def test_repeated_murloc_discounts_stack_until_next_rafaam(self):
  self.run_ops([('next_discount','RAFAAM',3,'permanent')]*2);card=self.g._add(0,'TIME_005t7')
  self.assertEqual(self.g._cost(card,0),max(0,self.records[card.card_id]['cost']-6))
 def test_archmage_transforms_both_boards_and_spares_existing_sheep(self):
  original=self.g._summon(0,'TIME_005t9t');a=self.g._summon(0,'NEW1_034');b=self.g._summon(1,'NEW1_034');self.run_ops([('rafaam_transform',)])
  self.assertIn(original,self.p.minions);self.assertTrue(all(m.card_id=='TIME_005t9t' for p in self.g.players for m in p.minions));self.assertFalse(self.p.death_history or self.q.death_history)
 def test_win_requires_all_nine_distinct_companions(self):
  self.history(['TIME_005t1']*9+['TIME_005t9t']);self.run_ops([('rafaam_win',)]);self.assertFalse(self.g.terminal)
  self.history(sorted(rules.REQUIRED));self.q.armor=100;self.run_ops([('rafaam_win',)]);self.assertTrue(self.g.terminal);self.assertEqual(self.g.winner,0)
 def test_sheep_does_not_replace_missing_ninth_companion(self):
  self.history(sorted(rules.REQUIRED-{'TIME_005t7'})+['TIME_005t9t']);self.run_ops([('rafaam_win',)]);self.assertFalse(self.g.terminal)
 def test_enemy_history_does_not_satisfy_win(self):
  self.q.played_history=[dict(card_id=cid,cost=0) for cid in rules.REQUIRED];self.run_ops([('rafaam_win',)]);self.assertFalse(self.g.terminal)
 def test_root_paid_play_finishes_game_after_other_nine(self):
  self.history(sorted(rules.REQUIRED));self.play('TIME_005');self.assertTrue(self.g.terminal);self.assertEqual(self.g.winner,0)
 def test_owner_cost_effect_is_policy_visible_and_opponent_private(self):
  from expanded.features import encode_decision
  self.run_ops([('next_discount','RAFAAM',3,'permanent')]);view=self.g.observe(0);self.assertEqual(view['players'][0]['cost_effects'][0]['selector'],'RAFAAM');self.assertNotIn('cost_effects',self.g.observe(1)['players'][0])
  features=encode_decision(dict(observation=view,actor=0,actions=view['legal_actions']))
  self.assertIn('RAFAAM',str(features))

 def test_fabled_root_is_excluded_from_constructed_generation(self):
  from expanded.generation import request_matches
  from expanded.generation_cards import pool
  from expanded.pools import GenerationPool
  from engine.cards import UnsupportedCard
  request=pool(card_type='MINION')
  self.assertFalse(request_matches(request,self.records['TIME_005'],'WARLOCK'))
  self.g._generation_pools={(request,self.p.hero_class):GenerationPool('fixture',('TIME_005',),'deliberately invalid')}
  before=self.g.rng.getstate()
  with self.assertRaisesRegex(UnsupportedCard,'ineligible'):self.g._generation_candidates(request,0)
  self.assertEqual(self.g.rng.getstate(),before)
