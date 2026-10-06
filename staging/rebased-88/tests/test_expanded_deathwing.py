"""Staged Herald payoff integration; controlled pools are not admission evidence."""
import unittest
from copy import deepcopy
from unittest.mock import patch
import test_expanded_herald as fixtures
from expanded import cards,Action
from expanded.herald import CATACLYSMS,LEGENDARY_DRAGONS,DEATHWINGS
from expanded.features import encode_decision
from engine.game import Card
from engine.cards import UnsupportedCard

class DeathwingTests(unittest.TestCase):
 setUpClass=classmethod(fixtures.HeraldTests.setUpClass.__func__)
 p=fixtures.HeraldTests.p;q=fixtures.HeraldTests.q
 op=fixtures.HeraldTests.op;play=fixtures.HeraldTests.play;contract=fixtures.HeraldTests.contract;prep=fixtures.HeraldTests.prep
 def setUp(self):
  fixtures.HeraldTests.setUp(self)
  ids=set(CATACLYSMS)|{'CATA_190p','CATA_190t14'}|set(DEATHWINGS)
  self.g.cards.update({cid:deepcopy(self.records[cid]) for cid in ids})
  self.contract(LEGENDARY_DRAGONS,['CS3_036'])
 def choose(self,index):self.g.step(Action('choose',choices=(index,)))
 def test_hero_replacement_preserves_health_class_and_adds_armor(self):
  self.p.health=17;self.p.armor=3;self.play('CATA_190h')
  self.assertEqual((self.p.health,self.p.armor,self.p.hero_class),(17,15,'WARRIOR'))
  self.assertEqual(self.p.primary_power['card_id'],'CATA_190p');self.choose(0)
 def test_zero_herald_one_choice_summons_dragon(self):
  self.play('CATA_190h');self.choose(0)
  self.assertEqual([m.card_id for m in self.p.minions],['CATA_190t14']);self.assertIsNone(self.g.pending_choice)
 def test_two_heralds_allow_two_repeated_choices(self):
  self.p.herald_count=2;self.play('CATA_190h');self.choose(0);self.choose(0)
  self.assertEqual(len(self.p.minions),2)
 def test_four_heralds_allow_four_repeated_choices(self):
  self.p.herald_count=4;self.play('CATA_190h')
  for _ in range(4):self.choose(0)
  self.assertEqual(len(self.p.minions),4);self.assertEqual(self.p.herald_count,4)
 def test_count_is_snapshotted_when_offer_opens(self):
  self.p.herald_count=2;self.play('CATA_190h');self.p.herald_count=4;self.choose(0);self.choose(0)
  self.assertIsNone(self.g.pending_choice);self.assertEqual(len(self.p.minions),2)
 def test_full_board_summon_choice_does_not_overflow(self):
  for _ in range(7):self.g._summon(0,'NEW1_034')
  self.play('CATA_190h');self.choose(0);self.assertEqual(len(self.p.board),7)
 def test_topple_uses_current_health_not_maximum(self):
  a=self.g._summon(1,'CATA_190t14');b=self.g._summon(1,'CATA_190t14');a.health=2;b.health=8
  self.play('CATA_190h');self.choose(1);self.assertIn(a,self.q.board);self.assertNotIn(b,self.q.board)
 def test_topple_empty_board_is_safe(self):self.play('CATA_190h');self.choose(1);self.assertFalse(self.q.board)
 def test_raze_hits_enemy_minions_only(self):
  ally=self.g._summon(0,'CATA_190t14');enemy=self.g._summon(1,'CATA_190t14')
  self.play('CATA_190h');self.choose(2);self.assertEqual((ally.health,enemy.health,self.q.health),(12,8,30))
 def test_enthrall_generates_five_cost_one_dragons(self):
  before=len(self.p.deck);self.play('CATA_190h');self.choose(3)
  generated=[c for c in self.p.deck if isinstance(c,Card) and c.card_id=='CS3_036']
  self.assertEqual(len(self.p.deck),before+5);self.assertEqual(len(generated),5);self.assertTrue(all(self.g._cost(c,0)==1 for c in generated))
 def test_cataclysms_are_not_cast_spells_or_discoveries(self):
  self.play('CATA_190h');self.choose(2);self.assertFalse(self.p.spells_turn);self.assertEqual(self.p.discoveries_total,0)
 def test_missing_pool_rolls_back_hero_play(self):
  self.g._generation_pools.clear();self.p.mana=10;c=self.g._enter_hand(0,Card(self.g._new_id(),'CATA_190h'))
  with self.assertRaises(UnsupportedCard):self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid))
  self.assertIsNone(self.p.hero_card_id);self.assertEqual(self.p.armor,0);self.assertEqual(self.p.mana,10)
 def test_replacement_power_grants_five_attack_once_per_turn(self):
  self.play('CATA_190h');self.choose(1);self.p.mana=2;self.g.step(Action('power'))
  self.assertEqual(self.g._hero_attack(0),5);self.assertTrue(self.p.power_used)
 def test_choice_clone_keeps_pending_selections(self):
  self.p.herald_count=2;self.play('CATA_190h');self.choose(0);clone=deepcopy(self.g)
  self.choose(0);clone.step(Action('choose',choices=(0,)));self.assertEqual(self.g.observe(0),clone.observe(0))
 def test_ultraxion_base_discount_and_one_herald(self):
  self.play('CATA_497');self.assertEqual((self.p.herald_count,self.p.deathwing_discount),(1,1))
  self.assertEqual(self.g._cost(Card(0,'CATA_190h'),0),9)
 def test_ultraxion_discount_scales_with_prior_heralds(self):
  self.p.herald_count=5;self.play('CATA_497');self.assertEqual((self.p.herald_count,self.p.deathwing_discount),(6,6))
 def test_ultraxion_repeated_battlecry_snapshots_each_time(self):
  self.op(('herald_ultraxion',),('herald_ultraxion',));self.assertEqual(self.p.deathwing_discount,3)
 def test_discount_applies_to_later_copies_and_is_owner_only(self):
  self.play('CATA_497')
  for cid in DEATHWINGS:
   self.assertEqual(self.g._cost(Card(0,cid),0),self.g.cards[cid]['cost']-1)
   self.assertEqual(self.g._cost(Card(0,cid),1),self.g.cards[cid]['cost'])
 def test_discount_does_not_apply_to_similar_name(self):
  self.g.cards['ONY_035']=deepcopy(self.records['ONY_035']);self.play('CATA_497')
  self.assertEqual(self.g._cost(Card(0,'ONY_035'),0),self.records['ONY_035']['cost'])
 def test_ultraxion_full_board_still_heralds_and_discounts(self):
  for _ in range(7):self.g._summon(0,'NEW1_034')
  self.op(('herald_ultraxion',));self.assertEqual((self.p.herald_count,self.p.deathwing_discount),(1,1))
 def test_discount_clamps_at_zero(self):
  self.p.deathwing_discount=20;self.assertEqual(self.g._cost(Card(0,'CATA_190h'),0),0)
 def test_discount_state_is_public_and_encoded(self):
  self.play('CATA_497');view=self.g.observe(0);self.assertEqual(self.g.observe(1)['players'][0]['deathwing_discount'],1)
  rows=encode_decision(dict(actor=0,observation=view,actions=view['legal_actions']));self.assertIn('deathwing_discount',str(rows))
 def test_choice_progress_visible_to_actor_only_and_encoded(self):
  self.p.herald_count=2;self.play('CATA_190h');self.choose(0);view=self.g.observe(0)
  self.assertEqual(view['pending_choice']['remaining'],1);self.assertEqual(view['pending_choice']['picks'],['CATA_190t10'])
  self.assertEqual(self.g.observe(1)['pending_choice'],{'owner':0,'waiting':True})
  rows=encode_decision(dict(actor=0,observation=view,actions=view['legal_actions']));self.assertIn('cataclysm_context',str(rows))
 def test_two_topples_resolve_against_updated_board(self):
  self.p.herald_count=2;self.g._summon(1,'CATA_190t14');self.g._summon(1,'CATA_190t14')
  self.play('CATA_190h');self.choose(1);self.choose(1);self.assertFalse(self.q.board)
 def test_cataclysm_selection_order_controls_results(self):
  self.p.herald_count=2;enemy=self.g._summon(1,'CATA_190t14');enemy.health=4
  self.play('CATA_190h');self.choose(2);self.choose(1);self.assertFalse(self.q.board)
 def test_ultraxion_missing_soldier_rolls_back_play(self):
  del self.g.cards['CATA_580t'];self.p.mana=10;c=self.g._enter_hand(0,Card(self.g._new_id(),'CATA_497'))
  with self.assertRaises(UnsupportedCard):self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid))
  self.assertEqual((self.p.herald_count,self.p.deathwing_discount,self.p.mana),(0,0,10));self.assertFalse(self.p.board)
