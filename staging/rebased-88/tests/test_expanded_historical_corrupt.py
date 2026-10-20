"""One-shot Corrupt at the shared completed paid-play boundary; no pool admission."""
import unittest
from expanded import Action,cards
import test_expanded_generation as fixtures
class HistoricalCorruptTests(unittest.TestCase):
 def game(self):return fixtures.GenerationTests().game()
 def play(self,g,cid):
  c=g._add(0,cid);g.players[0].mana=10
  g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid));return c
 def test_higher_paid_minion_upgrades_same_uid_modifiers_and_later_body(self):
  g=self.game();p=g.players[0];c=g._add(0,'DMF_064');c.attack_bonus=2;c.health_bonus=1;c.cost_delta=-1
  uid=c.uid;state=g.rng.getstate();self.play(g,'CS2_200')
  self.assertEqual((c.card_id,c.uid,c.cost_delta),('DMF_064t',uid,-1));self.assertEqual((g._card_stat(c,'attack',0),g._card_stat(c,'health',0)),(10,9))
  self.assertEqual(g.rng.getstate(),state);p.mana=10
  g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==uid));m=next(m for m in p.minions if m.card_id=='DMF_064t')
  self.assertEqual((m.attack,m.health),(10,9));self.assertTrue({'DIVINE_SHIELD','TAUNT'}<=m.keywords);g.assert_invariants()
 def test_strict_current_cost_comparison_on_both_cards(self):
  for target_delta,source_delta,expected in ((0,0,True),(2,0,False),(0,-2,False),(-2,-2,True)):
   with self.subTest(target=target_delta,source=source_delta):
    g=self.game();c=g._add(0,'DMF_064');c.cost_delta=target_delta;s=g._add(0,'CS2_200');s.cost_delta=source_delta
    g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==s.uid));self.assertEqual(c.card_id,'DMF_064t' if expected else 'DMF_064')
 def test_equal_cost_and_opponent_cards_are_not_upgraded(self):
  g=self.game();own=g._add(0,'DMF_064');other=g._add(1,'DMF_064');self.play(g,'DMF_064')
  self.assertEqual(own.card_id,'DMF_064');self.assertEqual(other.card_id,'DMF_064')
  self.play(g,'CS2_200');self.assertEqual(own.card_id,'DMF_064t');self.assertEqual(other.card_id,'DMF_064')
 def test_internal_spell_and_forge_are_not_paid_play_corrupt_triggers(self):
  g=self.game();c=g._add(0,'DMF_064');c.cost_delta=-5
  context=dict(owner=0,source=None,target=0,bonus=0,lifesteal=False)
  g._start_play_effects([('cast_fixed_spell','EX1_279','random')],context);g._settle(allow_event_choices=True)
  self.assertEqual(c.card_id,'DMF_064');forge=g._add(0,'YOG_525');g.step(Action('forge',source=forge.uid));self.assertEqual(c.card_id,'DMF_064')
 def test_base_override_and_crystal_core_do_not_erase_corrupt_stat_gain(self):
  for core in (False,True):
   g=self.game();p=g.players[0];c=g._add(0,'DMF_064');c.base_stat_override=(2,3);p.crystal_core=core
   before=(g._card_stat(c,'attack',0),g._card_stat(c,'health',0));self.play(g,'CS2_200')
   self.assertEqual((g._card_stat(c,'attack',0),g._card_stat(c,'health',0)),tuple(v+3 for v in before))
 def test_hidden_upgrade_event_has_no_card_identity_or_uid(self):
  g=self.game();c=g._add(0,'DMF_064');self.play(g,'CS2_200');view=g.observe(1)
  self.assertNotIn('DMF_064',str(view));self.assertNotIn('DMF_064t',str(view))
  self.assertEqual([e for e in view['events'] if e['event']=='corrupt'],[dict(turn=g.turn,event='corrupt',player=0)])
 def test_generated_only_root_and_literal_variant(self):
  self.assertTrue({'DMF_064','DMF_064t'}<=cards.TOKEN_IDS&cards.PLAYABLE_TOKENS);self.assertFalse({'DMF_064','DMF_064t'}&cards.COLLECTIBLE_IDS)

 def test_terminal_damage_stops_the_hand_upgrade(self):
  g=self.game();c=g._add(0,'DMF_064');g.players[1].health=1;s=g._add(0,'EX1_279')
  g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==s.uid and a.target==g.hero_id(1)))
  self.assertTrue(g.terminal);self.assertEqual(c.card_id,'DMF_064')
