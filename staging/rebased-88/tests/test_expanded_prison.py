import unittest,json,gzip
from unittest.mock import patch
from copy import deepcopy
import test_expanded_generation as fixtures
from expanded import cards,locations,Action,evolving_locations as rules
class PrisonTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with gzip.open('data/standard/all_cards.json.gz','rt') as f:cls.data={c['id']:c for c in json.load(f) if c['id'].startswith('JAIL_887')}
 def setUp(self):
  self.fx=fixtures.GenerationTests();self.g=self.fx.game();self.p,self.q=self.g.players;self.g.cards.update(deepcopy(self.data))
  for table,items in ((cards.RULES,dict(rules.RULES,**rules.TOKEN_RULES)),(locations.LOCATION_RULES,rules.LOCATION_RULES),(cards.END_EFFECTS,rules.END_EFFECTS)):
   ctx=patch.dict(table,items);ctx.start();self.addCleanup(ctx.stop)
 def activate(self,loc,cid='CORE_EX1_162'):
  c=self.g._add(0,cid);loc.ready_turn=self.g.turn;self.g.step(Action('activate',loc.uid,c.uid));return c
 def release(self,cid='CORE_EX1_162'):
  loc=self.g._place_location(0,'JAIL_887');loc.durability=1;self.activate(loc,cid);return next(m for m in self.p.minions if m.card_id=='JAIL_887t2')
 def test_empty_hand_cannot_activate(self):
  loc=self.g._place_location(0,'JAIL_887');self.assertFalse(any(a.kind=='activate' and a.source==loc.uid for a in self.g.legal_actions()))
 def test_discard_stores_card_and_summons_five_five(self):
  loc=self.g._place_location(0,'JAIL_887');c=self.activate(loc)
  self.assertNotIn(c,self.p.hand);self.assertEqual(len(loc.rule_state['prison_cards']),1);m=self.p.minions[0];self.assertEqual((m.card_id,m.attack,m.health),('JAIL_887t3',5,5));self.assertIn('TAUNT',m.keywords)
 def test_final_discard_is_in_freed_pool(self):
  m=self.release();self.assertEqual(len(m.rule_state['prison_cards']),1);self.assertFalse(self.p.locations)
 def test_destroyed_location_releases_prior_pool(self):
  loc=self.g._place_location(0,'JAIL_887');self.activate(loc);self.g._remove_location(loc);self.g._settle();m=next(m for m in self.p.minions if m.card_id=='JAIL_887t2');self.assertEqual(len(m.rule_state['prison_cards']),1)
 def test_end_turn_plays_once_then_exhausts(self):
  m=self.release();self.g.step(Action('end'));self.assertEqual(sum(x.card_id=='CORE_EX1_162' for x in self.p.minions),1);self.assertFalse(m.rule_state['prison_cards'])
  self.g.step(Action('end'));self.g.step(Action('end'));self.assertEqual(sum(x.card_id=='CORE_EX1_162' for x in self.p.minions),1)
 def test_silence_prevents_replay(self):
  m=self.release();self.g._silence(m);self.g.step(Action('end'));self.assertFalse(any(x.card_id=='CORE_EX1_162' for x in self.p.minions))
 def test_copy_inherits_independent_remaining_pool(self):
  m=self.release();copy=self.g._summon(0,m.card_id,copy_from=m);self.assertIsNot(m.rule_state['prison_cards'],copy.rule_state['prison_cards']);self.g.step(Action('end'));self.assertFalse(m.rule_state['prison_cards']);self.assertFalse(copy.rule_state['prison_cards']);self.assertEqual(sum(x.card_id=='CORE_EX1_162' for x in self.p.minions),2)
 def test_plain_summon_has_no_pool(self):
  self.g._summon(0,'JAIL_887t2');self.g.step(Action('end'));self.assertEqual(len(self.p.minions),1)
 def test_two_prisons_have_independent_pools(self):
  a=self.g._place_location(0,'JAIL_887');b=self.g._place_location(0,'JAIL_887');self.activate(a);self.activate(b,'CORE_CS2_029');self.assertEqual(a.rule_state['prison_cards'][0].card_id,'CORE_EX1_162');self.assertEqual(b.rule_state['prison_cards'][0].card_id,'CORE_CS2_029')
 def test_spell_replay_uses_automatic_casting(self):
  m=self.release('CORE_CS2_029');before=self.p.health+self.q.health+sum(x.health for p in self.g.players for x in p.minions);self.g.step(Action('end'));after=self.p.health+self.q.health+sum(x.health for p in self.g.players for x in p.minions);self.assertLess(after,before);self.assertFalse(m.rule_state['prison_cards'])
 def test_stored_cards_serialize_without_private_source_uid_in_activation(self):
  loc=self.g._place_location(0,'JAIL_887');c=self.activate(loc);json.dumps(self.g.observe(1));events=[e for e in self.g.events if e.get('kind')=='location_activated'];self.assertTrue(all(e.get('target')!=c.uid for e in events))
 def test_enemy_end_does_not_consume_pool(self):
  m=self.release();self.g.current=1;self.g.step(Action('end'));self.assertEqual(len(m.rule_state['prison_cards']),1)
 def test_replay_validates_before_consuming_pool(self):
  from engine.cards import UnsupportedCard
  from engine.game import Card
  m=self.release();m.rule_state['prison_cards'].append(Card(self.g._new_id(),'MISSING_PRISON_CARD'))
  with self.assertRaises(UnsupportedCard):self.g.step(Action('end'))
  restored=next(x for x in self.g.players[0].minions if x.uid==m.uid);self.assertEqual(len(restored.rule_state['prison_cards']),2)
 def test_partial_pool_copy_never_regains_consumed_card(self):
  m=self.release();self.g.step(Action('end'));copy=self.g._summon(0,m.card_id,copy_from=m);self.assertEqual(copy.rule_state['prison_cards'],[])
