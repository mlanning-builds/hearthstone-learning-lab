"""Paid shared-system paths use the production registry and full contracts."""
import unittest
from unittest.mock import patch
import test_expanded_generation as fixtures
from expanded import Action
from expanded.game import Card
from expanded import reviewed_system_bindings as bindings

class SystemProductionBatchTests(unittest.TestCase):
 def setUp(self):self.g=fixtures.GenerationTests().game();self.p,self.q=self.g.players
 def play(self,cid,target=0):
  c=self.g._enter_hand(0,Card(self.g._new_id(),cid))
  self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid and a.target==target))
  return c
 def test_all_shared_roots_and_exact_dependencies_in_real_registry(self):
  self.assertTrue(bindings.COLLECTIBLE_IDS<=self.g.cards.keys())
  self.assertTrue(bindings.TOKEN_IDS<=self.g.cards.keys())
 def test_ley_walker_paid_discount_then_death_full_three_outcomes(self):
  self.play('MEND_501');self.assertEqual(self.p.leyline_discount,1)
  m=next(m for m in self.p.minions if m.card_id=='MEND_501');m.health=0;self.g._settle()
  self.assertIn(self.p.hand[-1].card_id,('MEND_500','MEND_502','MEND_504'))
 def test_arcanomicon_paid_adds_three_and_resumes_upgrade(self):
  self.play('MEND_505');self.assertEqual({c.card_id for c in self.p.hand},{'MEND_500','MEND_502','MEND_504'})
  self.assertEqual(self.g.pending_choice['kind'],'leyline_upgrade')
  self.g.step(Action('choose',choices=(0,)));self.assertEqual(self.p.leyline_repeats,1)
 def test_sylvanas_paid_has_printed_damage(self):
  self.play('TIME_609');self.assertEqual(self.q.health,28)
 def test_bwonsamdi_all_boones_present_before_every_repeated_entry(self):
  self.g._summon(0,'CORE_DAL_575');self.p.bwonsamdi_boons=['TIME_619t3','TIME_619t4','TIME_619t5']
  seen=[];original=self.g._summon_one
  def capture(*args,**kwargs):
   m=original(*args,**kwargs)
   if m is not None:seen.append(set(m.keywords))
   return m
  with patch.object(self.g,'_summon_one',side_effect=capture):
   self.g._start_play_effects([('bwonsamdi_summon',)],dict(owner=0,source=None,target=0,bonus=0,lifesteal=False));self.g._settle(allow_event_choices=True)
  self.assertEqual(len(seen),2)
  for keywords in seen:self.assertTrue({'TAUNT','LIFESTEAL','RUSH'}<=keywords)
