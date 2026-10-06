"""Crafted definitions survive zone resets; temporary enchantments do not."""
import unittest
from engine.game import Card
from expanded import custom_builders
from expanded.automatic_cards import place_automatic_card
import test_expanded_final_card_paths as final_fixtures

class CraftedIdentityTests(unittest.TestCase):
 setUpClass=classmethod(final_fixtures.FinalCardPathsTests.setUpClass.__func__)
 setUp=final_fixtures.FinalCardPathsTests.setUp
 def custom(self,cid='CATA_470t1'):
  c=Card(self.g._new_id(),cid);c.set_cost=7;c.cost_delta=-3;c.base_stat_override=(6,8)
  c.rule_state=dict(crafted_ops=(('draw',1),),crafted_target='none',forge_parts=('a','b'),forge_keywords=('TAUNT',),forge_death=(('draw',1),))
  self.g._enter_hand(0,c);return c
 def test_silence_then_bounce_restores_crafted_definition(self):
  c=self.custom();self.p.hand.remove(c)
  m=self.g._summon(0,c.card_id,entry_origin='recruit',entry_zone='deck',entry_source=c)
  self.g._buff(m,3,3);self.g._silence(m);self.g._bounce(m,-1)
  bounced=self.p.hand[-1]
  self.assertEqual(bounced.rule_state,c.rule_state);self.assertEqual(bounced.set_cost,7)
  self.assertEqual(bounced.cost_delta,-1);self.assertEqual(bounced.base_stat_override,(6,8))
  self.assertEqual((bounced.attack_bonus,bounced.health_bonus),(0,0))
 def test_copies_do_not_share_definition(self):
  c=self.custom();copy=self.g._copy_card(c);copy._crafted_definition['state']['forge_parts']=('changed',)
  self.assertEqual(c._crafted_definition['state']['forge_parts'],('a','b'))
 def test_fresh_custom_replay_drops_discounts_and_buffs(self):
  c=self.custom();c.attack_bonus=9;c.rule_state['temporary']=True
  replay=self.g._fresh_replay_card(c)
  self.assertEqual(replay.set_cost,7);self.assertEqual(getattr(replay,'cost_delta',0),0)
  self.assertEqual(replay.attack_bonus,0);self.assertNotIn('temporary',replay.rule_state)
  self.assertEqual(replay.rule_state['crafted_ops'],(('draw',1),))
 def test_ordinary_replay_drops_enchantments(self):
  c=self.g._add(0,'CORE_EX1_162');c.attack_bonus=5;c.set_cost=0;c.base_stat_override=(10,10)
  replay=self.g._fresh_replay_card(c)
  self.assertEqual(replay.attack_bonus,0);self.assertIsNone(getattr(replay,'set_cost',None))
  self.assertIsNone(getattr(replay,'base_stat_override',None))
 def test_transform_discards_crafted_identity(self):
  c=self.custom();self.p.hand.remove(c)
  m=self.g._summon(0,c.card_id,entry_origin='recruit',entry_zone='deck',entry_source=c)
  self.g._transform(m,'CORE_EX1_162');m=self.p.minions[0];self.g._bounce(m)
  self.assertFalse(hasattr(self.p.hand[-1],'_crafted_definition'))
 def test_automatic_location_preserves_activation_and_death(self):
  cid=next(iter(custom_builders.LOCATION_RULES));c=Card(self.g._new_id(),cid)
  c.rule_state=dict(crafted_location_ops=(('draw',1),),crafted_location_death=(('draw',2),))
  place_automatic_card(self.g,('automatic_place',c),{'owner':0})
  loc=self.p.board[-1];self.assertEqual(loc.rule_state,c.rule_state)
  self.assertIn(('draw',2),loc.attached_death_effects)
 def test_slice_replay_executes_custom_spell_payload(self):
  c=Card(self.g._new_id(),'TOKEN_COIN')
  c.rule_state=dict(crafted_ops=(('draw',1),),crafted_target='none')
  self.g._enter_hand(0,c)
  self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid))
  replay=self.g._fresh_replay_card(c)
  self.assertFalse(hasattr(replay,'set_cost'))
  before=len(self.p.deck)
  self.fx.run_ops(self.g,[('slice_replay',)])
  self.assertEqual(len(self.p.deck),before-1)
