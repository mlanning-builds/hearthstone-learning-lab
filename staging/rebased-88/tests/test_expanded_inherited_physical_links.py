"""Physical relationship references survive donor departure and bearer changes."""
import unittest
from engine.game import Card
from expanded import death_inheritance
import test_expanded_generation as fixtures

class InheritedPhysicalLinkTests(unittest.TestCase):
 def setUp(self):self.g=fixtures.GenerationTests().game();self.p,self.q=self.g.players
 def run_inherited(self,operations,bearer,owner=0):
  self.g._start_play_effects(operations,dict(owner=owner,source=bearer,target=0,bonus=0,lifesteal=False))
  self.g._settle(allow_event_choices=True)
 def test_brox_chain_returns_the_bound_original_once(self):
  original=Card(self.g._new_id(),'TIME_020');other=Card(self.g._new_id(),'TIME_020')
  self.g._broxigar_waiting=[original,other]
  donor=self.g._summon(0,'CS2_231');donor._brox_chain=original.uid
  operations=death_inheritance.capture(self.g,donor,(('brox_return',),))
  donor._brox_chain=other.uid;self.p.board.remove(donor)
  bearer=self.g._summon(0,'CS2_231')
  self.run_inherited(operations,bearer)
  self.assertEqual(self.q.hand,[original]);self.assertEqual(self.g._broxigar_waiting,[other])
  self.run_inherited(operations,bearer)
  self.assertEqual(self.q.hand,[original]);self.assertEqual(self.g._broxigar_waiting,[other])
 def test_gigafin_disposal_keeps_original_parent_reference(self):
  first=self.g._summon(0,'TSC_962');second=self.g._summon(0,'TSC_962')
  first._devoured_cards=['CS2_231'];second._devoured_cards=['CORE_CS2_029']
  donor=next(m for m in self.p.minions if m.card_id=='TSC_962t')
  donor.rule_state['colossal_parent']=first.uid
  operations=death_inheritance.capture(self.g,donor,(('historic_gigafin_dispose',),))
  donor.rule_state['colossal_parent']=second.uid;self.p.board.remove(donor)
  bearer=self.g._summon(1,'CS2_231')
  self.run_inherited(operations,bearer,owner=1)
  self.assertEqual(first._devoured_cards,[]);self.assertEqual(second._devoured_cards,['CORE_CS2_029'])
 def test_gigafin_reference_does_not_redirect_after_parent_departure(self):
  donor=self.g._summon(0,'CS2_231');donor.rule_state['colossal_parent']=987654321
  operations=death_inheritance.capture(self.g,donor,(('historic_gigafin_dispose',),))
  self.run_inherited(operations,donor)
  self.assertEqual(len(self.p.minions),1)
