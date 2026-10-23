"""Scripted paid/internal cast fixtures; no policy rollouts or training."""
from copy import deepcopy
import unittest
from unittest.mock import patch
from engine.game import Card
from engine.cards import UnsupportedCard
from expanded import Action
from test_expanded_generation import GenerationTests

class ResumeRepairs(unittest.TestCase):
 def setUp(self):
  self.g=GenerationTests().game();self.p=self.g.players[self.g.current]
  self.p.hand=[];self.p.mana=10
  self.ctx=dict(owner=self.g.current,source=None,target=0,bonus=0,lifesteal=False)
 def test_duplicate_sidequest_is_not_playable_and_internal_cast_preserves_progress(self):
  g=self.g;p=self.p
  g._forge_effect(('forge_sidequest',),self.ctx);p.forge_sidequests[0]['progress']=2
  card=g._add(g.current,'TLC_EVENT_400')
  self.assertFalse(any(a.kind=='play' and a.source==card.uid for a in g.legal_actions()))
  g._forge_effect(('forge_sidequest',),self.ctx)
  self.assertEqual(p.forge_sidequests,[dict(card_id='TLC_EVENT_400',progress=2,total=3)])
  self.assertEqual(g._quest_slots(g.current),1)
  p.forge_sidequests=[]
  self.assertTrue(any(a.kind=='play' and a.source==card.uid for a in g.legal_actions()))
 def test_full_secret_zone_blocks_sidequest_without_overflow(self):
  self.p.secrets=[object()]*5
  self.g._forge_effect(('forge_sidequest',),self.ctx)
  self.assertFalse(getattr(self.p,'forge_sidequests',()))
 def trial(self):
  c=Card(self.g._new_id(),'CAP_405tb1')
  c.rule_state=dict(crafted_ops=(('armor',7),),crafted_target='none')
  self.g._enter_hand(self.g.current,c)
  return c
 def test_intrinsic_payload_survives_missing_mutable_rule_state(self):
  c=self.trial();c.rule_state={'temporary':True}
  a=next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid)
  self.g.step(a);self.assertEqual(self.p.armor,7)
 def test_spell_play_trigger_cannot_erase_captured_crafted_program(self):
  c=self.trial();original=self.g._drain_events
  def drain(*args,**kwargs):
   c.rule_state={};return original(*args,**kwargs)
  with patch.object(self.g,'_drain_events',side_effect=drain):
   self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid))
  self.assertEqual(self.p.armor,7)
 def test_payloadless_custom_spell_still_fails_explicitly(self):
  c=Card(self.g._new_id(),'CAP_405tb1');self.p.hand=[c]
  with self.assertRaisesRegex(UnsupportedCard,'physical crafted payload'):
   self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid))
