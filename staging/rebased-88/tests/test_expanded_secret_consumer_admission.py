"""Paid Secret consumers over complete frozen pools, without training or pool overrides."""
import unittest
from copy import deepcopy
from unittest.mock import patch
from expanded import Action,cards
from expanded.automatic_casting import MAGE_SECRETS,SECRETS
from engine.cards import UnsupportedCard
import test_expanded_imbue_azure_admission as fixtures
class SecretConsumerAdmissionTests(unittest.TestCase):
 def game(self,cid):
  self.fx=fixtures.ImbueAzureAdmissionTests();return self.fx.game('MAGE',cid)
 def play(self,g,cid):return self.fx.play(g,cid)
 def test_pools_match_entire_frozen_secret_membership_for_both_owners(self):
  from standard.catalog import load_catalog
  g=self.game('TIME_860');frozen=load_catalog()
  all_ids={c['id'] for c in frozen if c['type']=='SPELL' and 'SECRET' in c.get('mechanics',())}
  mage={c['id'] for c in frozen if c['id'] in all_ids and c['cardClass']=='MAGE'}
  for owner in (0,1):
   self.assertEqual(set(g._autocast_candidates(SECRETS,owner)),all_ids)
   self.assertEqual(set(g._autocast_candidates(MAGE_SECRETS,owner)),mage)
  self.assertTrue(all_ids<=cards.COLLECTIBLE_IDS)
 def test_improviser_no_previous_spell_does_not_cast_or_sample(self):
  g=self.game('JAIL_321');rng=g.rng.getstate();self.play(g,'JAIL_321')
  self.assertFalse(g.players[0].secrets);self.assertEqual(g.rng.getstate(),rng)
 def test_improviser_executes_every_real_mage_outcome_and_duplicate_does_not_stack(self):
  g=self.game('JAIL_321');ids=g._autocast_candidates(MAGE_SECRETS,0)
  for cid in ids:
   with self.subTest(cid=cid):
    g=self.game('JAIL_321');self.play(g,'TOKEN_COIN');p=g.players[0];history=list(p.spells_turn)
    choice=g.rng.choice
    def choose(values):return cid if cid in values else choice(values)
    with patch.object(g.rng,'choice',side_effect=choose):self.play(g,'JAIL_321')
    self.assertEqual([c.card_id for c in p.secrets],[cid]);self.assertEqual(p.spells_turn,history)
    self.assertEqual(p.cards_played,2);g.assert_invariants()
 def test_improviser_prepare_defers_play_until_next_owner_turn(self):
  g=self.game('JAIL_321');c=g._add(0,'JAIL_321');g.step(Action('prepare',source=c.uid))
  self.assertFalse(any(a.kind=='play' and a.source==c.uid for a in g.legal_actions()))
  self.assertFalse(g.players[0].secrets);self.assertEqual(g.players[0].cards_played,0)
  g.step(Action('end'));g.step(Action('end'));self.play(g,'TOKEN_COIN')
  g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid))
  self.assertTrue(g.players[0].secrets);g.assert_invariants()
 def test_enigma_executes_every_secret_for_either_recipient_and_choice_is_not_discover(self):
  base=self.game('TIME_860');ids=base._autocast_candidates(SECRETS,0)
  for cid in ids:
   for selected_index in (0,1):
    with self.subTest(cid=cid,index=selected_index):
     g=self.game('TIME_860');p,q=g.players;other=next(v for v in ids if v!=cid)
     with patch.object(g.rng,'sample',return_value=[cid,other]):self.play(g,'TIME_860')
     self.assertEqual([o['card_id'] for o in g.pending_choice['options']],[cid,other])
     self.assertNotIn(cid,str(g.observe(1).get('pending_choice')))
     p_mana,q_mana=p.mana,q.mana
     g.step(Action('choose',choices=(selected_index,)))
     expected=[cid,other] if selected_index==0 else [other,cid]
     self.assertEqual([c.card_id for c in p.secrets],[expected[0]])
     if expected[1]=='CORE_LOOT_101':
      # The opponent's new Explosive Runes sees Enigma's after-play event.
      self.assertFalse(q.secrets);self.assertFalse(any(m.card_id=='TIME_860' for m in p.minions))
     else:self.assertEqual([c.card_id for c in q.secrets],[expected[1]])
     self.assertEqual((p.mana,q.mana),(p_mana,q_mana));self.assertEqual(p.cards_played,1)
     self.assertFalse(p.spells_turn);self.assertFalse(q.spells_turn)
     self.assertEqual((p.discoveries_total,q.discoveries_total),(0,0));g.assert_invariants()
 def test_opponent_unsupported_outcome_fails_before_sampling_and_rolls_back_paid_play(self):
  g=self.game('TIME_860');c=g._add(0,'TIME_860');before=deepcopy(g.__dict__)
  original=g._supports_internal_spell
  with patch.object(g,'_supports_internal_spell',side_effect=lambda cid,owner=None:False if owner==1 else original(cid,owner)):
   with self.assertRaises(UnsupportedCard):g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid))
  self.assertEqual(g.players,before['players']);self.assertEqual(g.rng.getstate(),before['rng'].getstate())

 def test_generated_enigma_remains_executable_for_all_eleven_native_decks(self):
  from expanded.selectors import HERO_CLASSES
  from standard.catalog import load_catalog
  expected={c['id'] for c in load_catalog() if c['type']=='SPELL' and 'SECRET' in c.get('mechanics',())}
  for hero in sorted(HERO_CLASSES):
   with self.subTest(hero=hero):
    fx=fixtures.ImbueAzureAdmissionTests();g=fx.game(hero,'CORE_EX1_162')
    self.assertEqual(set(g._autocast_candidates(SECRETS,0)),expected)
    self.assertEqual(set(g._autocast_candidates(SECRETS,1)),expected)
    fx.play(g,'TIME_860');self.assertEqual(len(g.pending_choice['options']),2)
    g.step(Action('choose',choices=(0,)));g.assert_invariants()
