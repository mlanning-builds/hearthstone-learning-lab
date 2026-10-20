import unittest
import test_expanded_generation as fixtures
from engine.game import Card
from expanded import Action

class CrystalCoreCopyTests(unittest.TestCase):
 def setUp(self):
  self.g=fixtures.GenerationTests().game();self.p,self.q=self.g.players
  self.g.current=1;self.q.mana=10;c=self.g._add(1,'UNG_067t1')
  self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid))
  self.g.current=0
 def copy(self,value):
  c=self.g._copy_card(value,source_owner=1);self.g._enter_hand(0,c);return c
 def test_new_latorvius_deck_cards_copy_their_effective_base_stats(self):
  self.g.current=1;self.q.deck=[];self.q.hand=[];self.q.mana=10;c=self.g._add(1,'TLC_602t')
  self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid))
  source=next(c for c in self.q.deck if self.g.cards[c.card_id]['type']=='MINION')
  expected=(self.g._card_stat(source,'attack',1),self.g._card_stat(source,'health',1))
  self.assertEqual(expected,(5,5));self.g.current=0;copied=self.copy(source)
  self.assertEqual((self.g._card_stat(copied,'attack',0),self.g._card_stat(copied,'health',0)),expected)
 def test_string_deck_entry_copy_preserves_source_base(self):
  self.q.deck.append('CORE_EX1_162');c=self.copy(self.q.deck[-1])
  self.assertEqual((self.g._card_stat(c,'attack',0),self.g._card_stat(c,'health',0)),(5,5))
 def test_new_physical_deck_entry_preserves_bonuses_and_cost(self):
  source=Card(self.g._new_id(),'CORE_EX1_162');source.attack_bonus=2;source.health_bonus=3;source.cost_delta=-1
  self.q.deck.append(source);copied=self.copy(source)
  self.assertEqual((self.g._card_stat(copied,'attack',0),self.g._card_stat(copied,'health',0)),(7,8))
  self.assertEqual(copied.cost_delta,-1);self.assertNotEqual(copied.uid,source.uid)
  self.assertFalse(hasattr(source,'base_stat_override'))
 def test_source_without_crystal_core_retains_printed_base(self):
  self.q.crystal_core=False;c=self.copy('CORE_EX1_162')
  self.assertEqual((self.g._card_stat(c,'attack',0),self.g._card_stat(c,'health',0)),(2,2))
 def test_spell_copy_does_not_receive_minion_base(self):
  c=self.copy('CORE_CS2_029');self.assertFalse(hasattr(c,'base_stat_override'))
 def test_copy_keeps_opponent_ancestry_without_starting_origin(self):
  c=self.copy('CORE_EX1_162')
  self.assertTrue(self.g._copied_from_opponent(c,0));self.assertFalse(self.g._started_in_deck(c,0))
