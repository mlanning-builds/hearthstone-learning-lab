"""Paid production Dredge consumers, private choices and successful-draw checkpoints."""
import unittest
from copy import deepcopy
from expanded import Action,cards
import test_expanded_generation as fixtures
class HistoricalDredgeTests(unittest.TestCase):
 def game(self):return fixtures.GenerationTests().game()
 def play(self,g,cid,target=0):
  c=g._add(0,cid);g.players[0].mana=10
  g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid and a.target==target));return c
 def deck(self,g,cid,owner=0):
  p=g.players[owner];p.deck=[];c=g._add(owner,cid);p.hand.remove(c);p.deck=[c];return c
 def choose(self,g):g.step(Action('choose',choices=(0,)))
 def test_all_paid_roots_have_real_private_bottom_choice_and_no_discover(self):
  roots=('TSC_909','TSC_915','TSC_637','TSC_210','TSC_911','TID_714','NX2_018','TID_700','TSC_942','TSC_916','TSC_642')
  for cid in roots:
   with self.subTest(cid=cid):
    g=self.game();owner=1 if cid=='TID_700' else 0;chosen=self.deck(g,'CORE_EX1_162',owner);state=g.rng.getstate()
    self.play(g,cid,-2 if cid=='TSC_637' else 0)
    self.assertEqual(g.pending_choice['owner'],0);self.assertEqual(g.pending_choice['zone_owner'],owner)
    self.assertEqual(g.pending_choice['options'][0]['snapshot'].uid,chosen.uid)
    self.choose(g);self.assertIs(g.players[owner].deck[-1],chosen);self.assertEqual(g.rng.getstate(),state);self.assertEqual(g.players[0].discoveries_total,0)
    self.assertIn(cid,cards.TOKEN_IDS);self.assertNotIn(cid,cards.COLLECTIBLE_IDS);g.assert_invariants()
 def test_cost_changes_preserve_physical_identity_and_apply_only_correct_types(self):
  for root,target,delta in (('TSC_210','CORE_CS2_029',-3),('TSC_210','CORE_EX1_162',0),('TSC_911','CORE_EX1_162',-1)):
   g=self.game();c=self.deck(g,target);c.attack_bonus=2;self.play(g,root);self.choose(g)
   self.assertEqual(getattr(c,"cost_delta",0),delta);self.assertEqual(c.attack_bonus,2)
  g=self.game();c=self.deck(g,'CORE_EX1_162',1);c.cost_delta=-1;self.play(g,'TID_700');self.choose(g)
  self.assertEqual((c.set_cost,c.cost_delta),(6,0));self.assertEqual(g._cost(c,1),6)
 def test_obsidiansmith_minion_weapon_buffs_and_spell_exclusion(self):
  for target,expected in (('CORE_EX1_162',1),('CS2_106',1),('CORE_CS2_029',0)):
   g=self.game();c=self.deck(g,target);self.play(g,'TSC_942');self.choose(g)
   self.assertEqual((c.attack_bonus,c.health_bonus),(expected,expected))
 def test_armor_uses_selected_cost_and_undead_damage_is_conditional(self):
  g=self.game();c=self.deck(g,'CORE_CS2_029');c.cost_delta=-1;self.play(g,'TID_714');self.choose(g);self.assertEqual(g.players[0].armor,3)
  for target,damage in (('DMF_064',0),('NX2_018',5)):
   g=self.game();self.deck(g,target);before=g.players[1].health;self.play(g,'NX2_018');self.choose(g);self.assertEqual(g.players[1].health,before-damage)
 def test_mech_draw_uses_shared_draw_listener_and_preserves_uid(self):
  g=self.game();c=self.deck(g,'GVG_058');listener=g._summon(1,'CORE_SCH_717');self.play(g,'TSC_642');self.choose(g)
  self.assertIn(c,g.players[0].hand);self.assertEqual(len(g.players[0].hand),1);self.assertEqual(len(g.players[1].hand),1);self.assertFalse(g.players[0].deck)
 def test_combo_draw_is_after_dredge_and_does_not_fire_without_combo(self):
  for combo in (False,True):
   g=self.game();c=self.deck(g,'CORE_EX1_162');g.players[0].cards_played=int(combo);self.play(g,'TSC_916')
   self.assertFalse(g.players[0].hand);self.choose(g)
   self.assertEqual(c in g.players[0].hand,combo);self.assertEqual(c in g.players[0].deck,not combo)
 def test_empty_decks_do_not_open_choice_or_apply_bonus(self):
  for root in ('TSC_210','TSC_911','TID_714','NX2_018','TID_700','TSC_642'):
   g=self.game();g.players[0].deck=[];g.players[1].deck=[];before=g.players[1].health;self.play(g,root)
   self.assertIsNone(g.pending_choice);self.assertEqual(g.players[0].armor,0);self.assertEqual(g.players[1].health,before)

 def test_internal_illuminate_automatically_dredges_without_payment_or_play_history(self):
  g=self.game();p=g.players[0];c=self.deck(g,'CORE_CS2_029');before=(p.mana,p.cards_played,list(p.spells_turn),p.discoveries_total);rng=g.rng.getstate()
  self.assertTrue(g._supports_internal_spell('TSC_210',0))
  g._start_play_effects([('cast_fixed_spell','TSC_210','random')],dict(owner=0,source=None,target=0,bonus=0,lifesteal=False))
  g._settle(allow_event_choices=True)
  self.assertIsNone(g.pending_choice);self.assertIs(p.deck[-1],c);self.assertEqual(c.cost_delta,-3)
  self.assertEqual((p.mana,p.cards_played,list(p.spells_turn),p.discoveries_total),before);self.assertEqual(g.rng.getstate(),rng)
 def test_internal_combo_dredge_draw_resumes_after_automatic_choice(self):
  for combo in (False,True):
   g=self.game();p=g.players[0];c=self.deck(g,'CORE_EX1_162');p.cards_played=int(combo)
   self.assertTrue(g._supports_internal_spell('TSC_916',0))
   g._start_play_effects([('cast_fixed_spell','TSC_916','random'),('armor',2)],dict(owner=0,source=None,target=0,bonus=0,lifesteal=False,combo=combo))
   g._settle(allow_event_choices=True);self.assertIsNone(g.pending_choice);self.assertEqual(c in p.hand,combo);self.assertEqual(p.armor,2);self.assertEqual(p.cards_played,int(combo))
