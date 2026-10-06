import unittest,gzip,json
from pathlib import Path
from copy import deepcopy
from unittest.mock import patch
import test_expanded_generation as fixtures
from expanded import cards,fabled_effects as rules,Action
from expanded.generation_cards import pool
from expanded.features import SCHEMA
from engine.cards import UnsupportedCard
from engine.game import Card

class TalanjiTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  root=Path(__file__).resolve().parents[1]
  with gzip.open(root/'data/standard/all_cards.json.gz','rt') as f:cls.records={c['id']:c for c in json.load(f)}
 def setUp(self):
  self.fx=fixtures.GenerationTests();self.g=self.fx.game();self.p,self.q=self.g.players
  self.g.cards.update({cid:deepcopy(c) for cid,c in self.records.items() if cid.startswith('TIME_619')})
  for table,values in ((cards.RULES,{**rules.RULES,**rules.TOKEN_RULES}),(cards.DEATH_EFFECTS,rules.DEATH_EFFECTS)):
   p=patch.dict(table,values);p.start();self.addCleanup(p.stop)
  for cost in (4,6,8,10):
   cid='TEST_BOON_'+str(cost);self.g.cards[cid]=dict(self.g.cards['NEW1_034'],id=cid,cost=cost,attack=cost,health=cost)
   self.fx.install(self.g,pool(card_type='MINION',minimum=cost,maximum=cost),[cid])
 def run_ops(self,ops,**kw):self.fx.run_ops(self.g,ops,**kw)
 def choose(self,cid):
  self.g.step(Action('choose',choices=(next(i for i,o in enumerate(self.g.pending_choice['options']) if o['card_id']==cid),)))
 def boon(self,cid):self.run_ops([('choose_boon',)]);self.choose(cid)
 def play(self,cid):
  self.p.mana=10;c=self.g._add(0,cid);self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid));return c
 def test_draw_precedes_resurrection_and_preserves_physical_card(self):
  c=Card(self.g._new_id(),'TIME_619t',attack_bonus=3);self.p.deck=[c];self.p.death_history=['TIME_619t'];self.play('TIME_619')
  self.assertIs(self.p.hand[0],c);self.assertEqual(c.attack_bonus,3);self.assertEqual([m.card_id for m in self.p.minions],['TIME_619']);self.assertIsNotNone(self.g.pending_choice)
 def test_dead_and_not_in_deck_resurrects_before_choice(self):
  self.p.death_history=['TIME_619t'];self.play('TIME_619');self.assertEqual([m.card_id for m in self.p.minions],['TIME_619','TIME_619t']);self.assertIsNotNone(self.g.pending_choice)
 def test_absent_bwonsamdi_still_grants_future_boon_without_draw(self):
  self.p.deck=[];self.play('TIME_619');self.assertEqual(self.p.fatigue,0);self.choose('TIME_619t3');m=self.g._summon(0,'TIME_619t');self.assertIn('TAUNT',self.g._effective_keywords(m))
 def test_three_unique_choices_then_no_more(self):
  for cid in rules.BOONS:
   self.run_ops([('choose_boon',)]);self.assertNotIn(cid,self.p.bwonsamdi_boons);self.assertEqual(len(self.g.pending_choice['options']),3-len(self.p.bwonsamdi_boons));self.choose(cid)
  self.run_ops([('choose_boon',)]);self.assertIsNone(self.g.pending_choice);self.assertEqual(len(self.p.bwonsamdi_boons),3)
 def test_boons_apply_to_all_current_and_future_friendly_copies(self):
  a=self.g._summon(0,'TIME_619t');b=self.g._summon(0,'TIME_619t');enemy=self.g._summon(1,'TIME_619t');self.boon('TIME_619t4');c=self.g._summon(0,'TIME_619t')
  for m in (a,b,c):self.assertIn('LIFESTEAL',self.g._effective_keywords(m))
  self.assertNotIn('LIFESTEAL',self.g._effective_keywords(enemy))
 def test_external_boon_survives_silence_but_deathrattle_does_not(self):
  self.boon('TIME_619t3');m=self.g._summon(0,'TIME_619t');self.g._silence(m);self.assertIn('TAUNT',self.g._effective_keywords(m));m.health=0;self.g._settle();self.assertFalse(self.p.minions)
 def test_deathrattle_costs_four_six_eight_ten(self):
  for count in range(4):
   self.p.bwonsamdi_boons=list(rules.BOONS)[:count];self.p.board=[];self.run_ops([('bwonsamdi_summon',)]);m=self.p.minions[0];self.assertEqual(m.card_id,'TEST_BOON_'+str(4+2*count));self.assertTrue({rules.BOONS[c] for c in self.p.bwonsamdi_boons}<=self.g._effective_keywords(m))
 def test_inherited_keywords_are_silenceable(self):
  self.p.bwonsamdi_boons=list(rules.BOONS);self.run_ops([('bwonsamdi_summon',)]);m=self.p.minions[0];self.g._silence(m);self.assertFalse(set(rules.BOONS.values())&self.g._effective_keywords(m));self.assertEqual(len(self.p.bwonsamdi_boons),3)
 def test_actual_death_uses_current_boons(self):
  self.boon('TIME_619t5');m=self.g._summon(0,'TIME_619t');m.health=0;self.g._settle();self.assertEqual(self.p.minions[0].card_id,'TEST_BOON_6');self.assertIn('RUSH',self.g._effective_keywords(self.p.minions[0]))
 def test_missing_pool_is_not_silently_filtered(self):
  self.g._generation_pools.clear();before=self.g.rng.getstate()
  with self.assertRaises(UnsupportedCard):self.run_ops([('bwonsamdi_summon',)])
  self.assertEqual(before,self.g.rng.getstate());self.assertFalse(self.p.board)
 def test_full_board_resurrection_still_offers_boon(self):
  for _ in range(6):self.g._summon(0,'NEW1_034')
  self.p.death_history=['TIME_619t'];self.play('TIME_619');self.assertEqual(len(self.p.board),7);self.assertIsNotNone(self.g.pending_choice)
 def test_full_board_deathrattle_does_not_consume_rng(self):
  for _ in range(7):self.g._summon(0,'NEW1_034')
  before=self.g.rng.getstate();self.run_ops([('bwonsamdi_summon',)]);self.assertEqual(before,self.g.rng.getstate());self.assertEqual(len(self.p.board),7)
 def test_zandalar_damage_finishes_before_choice(self):
  enemy=self.g._summon(1,'NEW1_034');self.play('TIME_619t2');self.assertEqual(self.q.health,28);self.assertFalse(self.q.minions);self.assertIsNotNone(self.g.pending_choice)
 def test_boons_are_not_discover_events(self):
  before=self.p.discoveries_total;self.boon('TIME_619t3');self.assertEqual(self.p.discoveries_total,before)
 def test_choice_clone_resumes_identically(self):
  self.run_ops([('choose_boon',)]);clone=deepcopy(self.g);self.choose('TIME_619t4');clone.step(Action('choose',choices=(1,)));self.assertEqual(self.g.observe(0),clone.observe(0))
 def test_public_boons_are_visible_to_both_players(self):
  self.boon('TIME_619t3')
  for viewer in (0,1):self.assertEqual(self.g.observe(viewer)['players'][0]['bwonsamdi_boons'],['TIME_619t3'])
  self.assertEqual(SCHEMA,'visible-action-features-v58')
 def test_controller_changes_boon_aura_without_changing_owner_state(self):
  self.boon('TIME_619t3');m=self.g._summon(0,'TIME_619t');self.p.board.remove(m);m.owner=1;self.q.board.append(m)
  self.assertNotIn('TAUNT',self.g._effective_keywords(m));self.assertEqual(self.p.bwonsamdi_boons,['TIME_619t3'])
 def test_root_stays_staged_and_all_cost_pools_are_declared(self):
  self.assertNotIn('TIME_619',cards.COLLECTIBLE_IDS);self.assertEqual(len(rules.requests_for('TIME_619')),4)

 def test_internal_zandalar_resolves_random_boon_without_paid_history(self):
  self.run_ops([('cast_fixed_spell','TIME_619t2','random')]);self.assertEqual(self.q.health,28);self.assertEqual(len(self.p.bwonsamdi_boons),1);self.assertIsNone(self.g.pending_choice);self.assertFalse(self.p.played_history)
 def test_feature_encoding_contains_public_boon(self):
  from expanded.features import encode_decision
  self.boon('TIME_619t4');view=self.g.observe(0);rows=encode_decision(dict(actor=0,observation=view,actions=view['legal_actions']));self.assertIn('bwonsamdi_boons',str(rows));self.assertIn('TIME_619t4',str(rows))
 def test_full_hand_burns_draw_instead_of_resurrecting(self):
  self.p.deck=['TIME_619t'];self.p.death_history=['TIME_619t']
  for _ in range(10):self.g._add(0,'NEW1_034')
  self.run_ops([('talanji_find',),('choose_boon',)]);self.assertFalse(self.p.deck);self.assertEqual(len(self.p.hand),10);self.assertFalse(self.p.minions);self.assertIsNotNone(self.g.pending_choice)
