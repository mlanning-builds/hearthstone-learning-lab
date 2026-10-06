import unittest,gzip,json
from pathlib import Path
import test_expanded_generation as fixtures
class MugZeeTests(unittest.TestCase):
 def setUp(self):
  self.fx=fixtures.GenerationTests();self.g=self.fx.game();self.p=self.g.players[0]
  with gzip.open(Path(__file__).resolve().parents[1]/'data/standard/all_cards.json.gz','rt') as f:self.g.cards.update({c['id']:c for c in json.load(f) if c['id'].startswith('JAIL_800')})
 def setup_deck(self,ids):self.p.starting_deck=ids;self.g._mug_start()
 def test_both_conditions_grant_two_passives(self):
  self.setup_deck(['JAIL_800','CS2_082']);self.assertEqual(self.p.primary_power['card_id'],'JAIL_800hp1');self.assertEqual(self.p.secondary_power['card_id'],'JAIL_800hp2');self.assertFalse(any(a.kind=='power' for a in self.g.legal_actions()))
 def test_spells_only_grant_mug(self):
  self.setup_deck(['JAIL_800','CORE_CS2_029']);self.assertEqual(self.p.primary_power['card_id'],'JAIL_800hp1');self.assertIsNone(self.p.secondary_power)
 def test_minions_only_grant_zee(self):
  self.setup_deck(['JAIL_800','CORE_EX1_162']);self.assertEqual(self.p.primary_power['card_id'],'JAIL_800hp2')
 def test_neither_condition_leaves_base_power(self):
  self.setup_deck(['JAIL_800','CORE_EX1_162','CORE_CS2_029']);self.assertIsNone(self.p.primary_power)
 def test_discount_unlock_and_first_minion_only(self):
  self.setup_deck(['JAIL_800']);self.p.turns_taken=2;self.assertEqual(self.g._mug_discount(0,'JAIL_800'),0);self.p.turns_taken=3;self.assertEqual(self.g._mug_discount(0,'JAIL_800'),2);self.p.minion_played_this_turn=True;self.assertEqual(self.g._mug_discount(0,'JAIL_800'),0)
 def test_fifth_minion_repeats_battlecry(self):
  self.setup_deck(['JAIL_800','CORE_EX1_162']);ops=[('draw',1)]
  for _ in range(4):self.g._mug_play_operations(0,'CORE_EX1_162',[])
  self.assertEqual(self.g._mug_play_operations(0,'UNG_920t2',ops),ops*2)
 def test_primary_replacement_keeps_secondary(self):
  self.setup_deck(['JAIL_800']);self.g._replace_primary_power(0,dict(card_id='TLC_632t'));self.assertIsNone(self.g._mug_power(0,'JAIL_800hp1'));self.assertIsNotNone(self.g._mug_power(0,'JAIL_800hp2'))

 def test_paid_fifth_minion_runs_battlecry_twice(self):
  from unittest.mock import patch
  from expanded import cards
  self.setup_deck(['JAIL_800','CORE_EX1_162']);self.p.primary_power['played']=4
  # Controlled Battlecry metadata makes the replay boundary explicit.
  data=dict(self.g.cards['CORE_EX1_162'],mechanics=['BATTLECRY'])
  with patch.dict(self.g.cards,{'CORE_EX1_162':data}),patch.dict(cards.RULES,{'CORE_EX1_162':('none',[('draw',1)])}):
   c=self.g._add(0,'CORE_EX1_162');before=len(self.p.deck);self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid));self.assertEqual(len(self.p.deck),before-2);self.assertEqual(self.p.primary_power['played'],0)
