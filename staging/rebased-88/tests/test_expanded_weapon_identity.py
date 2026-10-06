"""Physical weapon retention required for cross-zone weapon mechanics."""
import unittest
from unittest.mock import patch
from copy import deepcopy
import test_expanded_generation as fixtures
from engine.game import Card
from expanded import cards

class WeaponIdentityTests(unittest.TestCase):
 def setUp(self):
  self.g=fixtures.GenerationTests().game();self.p=self.g.players[0]
 def test_paid_weapon_retains_physical_card_and_modifiers(self):
  c=self.g._add(0,'CS2_082');c.attack_bonus=2;c.rule_state={'retained_marker':3}
  with patch.dict(cards.RULES,{'CS2_082':('none',[])}):self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid))
  self.assertIs(self.p.equipped_card,c);self.assertEqual(self.p.weapon['attack'],3);self.assertEqual(c.rule_state,{'retained_marker':3});self.assertNotIn(c,self.p.hand)
 def test_generated_weapon_has_unique_physical_identity(self):
  self.g._equip(0,'CS2_082');first=self.p.equipped_card
  self.g._equip(0,'CS2_082');self.assertIsInstance(first,Card);self.assertNotEqual(first.uid,self.p.equipped_card.uid)
 def test_break_passes_original_card_and_clears_slot_before_effect(self):
  c=Card(self.g._new_id(),'CS2_082');self.g._equip(0,c.card_id,physical_card=c);seen=[]
  def effect(op,ctx):seen.append((ctx['broken_weapon_card'],self.p.equipped_card,self.p.weapon))
  with patch.dict(cards.DEATH_EFFECTS,{'CS2_082':[('fixture',)]}),patch.object(self.g,'_effect',side_effect=effect):self.g._break_weapon(0)
  self.assertEqual(seen,[(c,None,None)])
 def test_replacement_death_effect_receives_old_identity(self):
  self.g._equip(0,'CS2_082');old=self.p.equipped_card;seen=[]
  with patch.dict(cards.DEATH_EFFECTS,{'CS2_082':[('fixture',)]}),patch.object(self.g,'_effect',side_effect=lambda op,ctx:seen.append(ctx['broken_weapon_card'])):self.g._equip(0,'CS2_082')
  self.assertEqual(seen,[old]);self.assertIsNot(self.p.equipped_card,old)
 def test_mismatched_card_rejects_without_breaking_weapon(self):
  self.g._equip(0,'CS2_082');old=self.p.equipped_card
  with self.assertRaises(ValueError):self.g._equip(0,'CS2_082',physical_card=Card(999,'CORE_CS2_029'))
  self.assertIs(self.p.equipped_card,old)
 def test_private_card_is_not_exposed_in_observation(self):
  self.g._equip(0,'CS2_082');before=[deepcopy(self.g.observe(i)) for i in range(2)]
  self.p.equipped_card.rule_state={'private_marker':98765}
  self.assertEqual(before,[self.g.observe(i) for i in range(2)])
