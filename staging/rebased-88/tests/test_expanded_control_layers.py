"""Focused ownership checks for independent temporary control expiries."""
import unittest
from expanded.permanents import Permanent,RIFT
from expanded.historical_copy_batches import rotate_silas
import test_expanded_generation as fixtures

class ControlLayerTests(unittest.TestCase):
 def setUp(self):
  self.g=fixtures.GenerationTests().game();self.p,self.q=self.g.players
 def take(self,m,owner):
  self.g._temporary_control_effect(('temporary_control',),dict(owner=owner,target=m.uid))
 def expire(self,owner):
  self.g.players[owner].turns_taken+=1;self.g._return_temporary_control(owner)
 def test_earlier_layer_expires_without_overriding_later_controller(self):
  m=self.g._summon(1,'CS2_231');self.take(m,0);self.take(m,1)
  self.expire(1);self.assertEqual(m.owner,1);self.assertEqual(len(m._control_return['layers']),1)
  self.expire(0);self.assertEqual(m.owner,1);self.assertFalse(hasattr(m,'_control_return'))
 def test_later_layer_expires_revealing_still_active_earlier_layer(self):
  m=self.g._summon(1,'CS2_231');self.take(m,0);self.take(m,1)
  self.expire(0);self.assertEqual(m.owner,0)
  self.expire(1);self.assertEqual(m.owner,1)
 def test_permanent_control_supersedes_old_temporary_deadline(self):
  m=self.g._summon(1,'CS2_231');self.take(m,0)
  self.p.board.remove(m);m.owner=1;self.q.board.append(m);self.g._refresh_auras()
  self.assertFalse(hasattr(m,'_control_return'))
  self.expire(1);self.assertEqual(m.owner,1)
 def test_end_turn_control_layer_restores_the_remaining_layer(self):
  m=self.g._summon(1,'CS2_231');self.take(m,0)
  token=self.g._add_control_layer(m,1,deadline_owner=0,due=self.p.turns_taken+1,ready=True,end_timer=True)
  self.g._expire_control_layers(lambda layer:layer['token']==token)
  self.assertEqual(m.owner,0);self.assertEqual(len(m._control_return['layers']),1)
  self.expire(1);self.assertEqual(m.owner,1)
 def test_layer_deadlines_are_public_without_private_cards(self):
  m=self.g._summon(1,'CS2_231');self.take(m,0);self.take(m,1)
  view=self.g.observe(0)['players'][1]['board'][0]['control_return']
  self.assertEqual(len(view['layers']),2)
  self.assertEqual([e['controller'] for e in view['layers']],['self','opponent'])
 def test_silas_overflow_dies_on_original_side_with_its_deathrattle(self):
  self.p.board=[Permanent(self.g._new_id(),RIFT,0) for _ in range(7)]
  m=self.g._summon(1,'CS2_231');m.attached_death_effects.append(('armor',3))
  rotate_silas(self.g,0,'left');self.g._settle(allow_event_choices=True)
  self.assertEqual(len(self.p.board),7);self.assertFalse(self.q.board)
  self.assertEqual(m.owner,1);self.assertEqual(self.q.armor,3)
  self.assertEqual(self.q.death_history,['CS2_231'])
