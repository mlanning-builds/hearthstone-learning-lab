import unittest,gzip,json
from pathlib import Path
from unittest.mock import patch
import test_expanded_generation as fixtures
from expanded import cards,automatic_casting,Action
from engine.game import Card
from engine.cards import UnsupportedCard
class OhnahraTests(unittest.TestCase):
 def setUp(self):
  self.fx=fixtures.GenerationTests();self.g=self.fx.game();self.p,self.q=self.g.players
  with gzip.open(Path(__file__).resolve().parents[1]/'data/standard/all_cards.json.gz','rt') as f:self.g.cards.update({c['id']:c for c in json.load(f) if c['id']=='EDR_031'})
  for table,values in ((cards.RULES,automatic_casting.RULES),(cards.END_EFFECTS,automatic_casting.END_EFFECTS)):
   p=patch.dict(table,values);p.start();self.addCleanup(p.stop)
 def test_end_turn_consumes_three(self):
  self.g._summon(0,'EDR_031');self.p.deck=['CORE_EX1_162']*4;self.g.step(Action('end'));self.assertEqual(len(self.p.deck),1);self.assertEqual(len(self.p.minions),4)
 def test_silence_disables_trigger(self):
  m=self.g._summon(0,'EDR_031');self.g._silence(m);self.p.deck=['CORE_EX1_162']*4;self.g.step(Action('end'));self.assertEqual(len(self.p.deck),4)
 def test_empty_deck_no_fatigue(self):
  self.p.deck=[];self.fx.run_ops(self.g,[('automatic_top',3)]);self.assertEqual(self.p.fatigue,0)
 def test_short_deck_no_fatigue(self):
  self.p.deck=['CORE_EX1_162'];self.fx.run_ops(self.g,[('automatic_top',3)]);self.assertEqual(len(self.p.minions),1);self.assertEqual(self.p.fatigue,0)
 def test_physical_weapon_preserved(self):
  c=Card(self.g._new_id(),'CS2_082');c.attack_bonus=2;self.p.deck=[c];self.fx.run_ops(self.g,[('automatic_top',1)]);self.assertIs(self.p.equipped_card,c)
 def test_no_draw_or_discard_events(self):
  self.p.deck=['CORE_EX1_162'];self.g.events.clear();self.fx.run_ops(self.g,[('automatic_top',1)]);self.assertFalse(any(e['event'] in ('draw','discard','play') for e in self.g.events))
 def test_unsupported_top_not_consumed(self):
  self.p.deck=['UNKNOWN']
  with self.assertRaises(UnsupportedCard):self.fx.run_ops(self.g,[('automatic_top',1)])
  self.assertEqual(self.p.deck,['UNKNOWN'])
 def test_full_hand_does_not_burn_top(self):
  for _ in range(10):self.g._add(0,'TOKEN_COIN')
  self.p.deck=['CORE_EX1_162'];self.fx.run_ops(self.g,[('automatic_top',1)]);self.assertEqual(len(self.p.hand),10);self.assertEqual(len(self.p.minions),1)
