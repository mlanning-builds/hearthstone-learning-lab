import unittest
from unittest.mock import patch
import test_expanded_zone_triggers as fixtures
from expanded import Action,cards
from engine.game import Card

class DeckDestructionTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):fixtures.ZoneTriggerTests.setUpClass();cls.records=fixtures.ZoneTriggerTests.records
 setUp=fixtures.ZoneTriggerTests.setUp
 def op(self,op):
  self.g._start_play_effects([op],dict(owner=0,source=None,target=0,bonus=0,lifesteal=False))
  self.g._settle(allow_event_choices=True)
 def play(self,cid):
  self.p.mana=10;c=self.g._add(0,cid)
  self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid))
  return c
 def test_watcher_paid_death_destroys_three_and_triggers_impfernal(self):
  self.p.deck=['CORE_CS2_029','JAIL_398','CORE_CS2_029','CORE_CS2_029'];self.play('TLC_621')
  m=next(m for m in self.p.minions if m.card_id=='TLC_621');m.health=0;self.g._settle()
  self.assertEqual(self.p.deck,['CORE_CS2_029']);self.assertEqual((self.p.health,self.q.health),(27,27))
  self.assertEqual(self.p.corpses,1);self.assertNotIn('JAIL_398',self.p.death_history)
 def test_top_destruction_triggers_each_physical_copy_once(self):
  self.p.deck=[Card(self.g._new_id(),'JAIL_398') for _ in range(2)];self.op(('remove_own_top',3))
  self.assertFalse(self.p.deck);self.assertEqual((self.p.health,self.q.health),(24,24))
  self.assertEqual(self.p.corpses,0);self.assertFalse(self.p.death_history)
 def test_geddon_destroys_unchosen_offer_but_not_selected_impfernal(self):
  self.p.deck=[Card(self.g._new_id(),'JAIL_398'),Card(self.g._new_id(),'CORE_CS2_029'),Card(self.g._new_id(),'CORE_EX1_012')]
  selected=self.p.deck[0];self.g._effect(('lasting_draw',),dict(owner=0));self.g._turn_card_draw(0)
  index=next(i for i,o in enumerate(self.g.pending_choice['options']) if o['card_id']=='JAIL_398')
  self.g.step(Action('choose',choices=(index,)))
  self.assertIs(self.p.hand[0],selected);self.assertEqual(selected.cost_delta,-3)
  self.assertEqual((self.p.health,self.q.health),(30,30));self.assertFalse(self.p.deck)
 def test_geddon_unchosen_impfernal_runs_after_offer_removal(self):
  self.p.deck=['JAIL_398','CORE_CS2_029','CORE_EX1_012'];self.g._effect(('lasting_draw',),dict(owner=0));self.g._turn_card_draw(0)
  index=next(i for i,o in enumerate(self.g.pending_choice['options']) if o['card_id']=='CORE_CS2_029')
  self.g.step(Action('choose',choices=(index,)))
  self.assertEqual(self.p.hand[0].card_id,'CORE_CS2_029');self.assertFalse(self.p.deck)
  self.assertEqual((self.p.health,self.q.health),(27,27));self.g.assert_invariants()
 def test_mass_destroy_dispatches_original_deck_owner(self):
  self.p.deck=['JAIL_398'];self.q.deck=['JAIL_398'];seen=[]
  with patch.object(self.g,'_zone_card_removed',side_effect=lambda owner,value,zone,cause:seen.append((owner,value,zone,cause))):
   self.op(('remove_cheap_decks',6))
  self.assertEqual(seen,[(0,'JAIL_398','deck','destroy'),(1,'JAIL_398','deck','destroy')])
  self.assertFalse(self.p.deck);self.assertFalse(self.q.deck)
 def test_printed_mass_threshold_keeps_expensive_cards(self):
  self.p.deck=['JAIL_398','CORE_EX1_012'];self.q.deck=['CORE_CS2_029']
  self.play('CATA_720');self.assertEqual(self.p.deck,['JAIL_398']);self.assertEqual(self.q.deck,['CORE_CS2_029'])
  self.assertEqual((self.p.health,self.q.health),(30,30))
 def test_gnomeferatu_remove_is_not_destroy(self):
  self.q.deck=['JAIL_398'];self.play('CORE_ICC_407');self.assertFalse(self.q.deck)
  self.assertEqual((self.p.health,self.q.health),(30,30))
 def test_void_storage_does_not_destroy_impfernal(self):
  self.p.deck=['JAIL_398','CORE_CS2_029'];self.play('JAIL_719')
  self.assertEqual(len(self.p.deck),1);self.assertEqual((self.p.health,self.q.health),(30,30))
 def test_empty_top_destruction_never_fatigues(self):
  self.p.deck=[];self.op(('remove_own_top',3));self.assertEqual((self.p.fatigue,self.p.health),(0,30))
