"""Historical Deathrattle recipes with physical death and weapon break paths."""
import unittest
from copy import deepcopy
from unittest.mock import patch
import test_expanded_generation as fixtures
from expanded import cards,Action
from expanded.historical_generation_catalog import load_universe
from expanded.historical_death_primitives import RULES,DEATH_EFFECTS,TOKEN_RULES,GENERATED_IDS,FIXED_TOKEN_IDS
from engine.game import Card

class HistoricalDeathPrimitiveTests(unittest.TestCase):
 def game(self):
  g=fixtures.GenerationTests().game();g.cards.update({cid:deepcopy(dict(load_universe().records[cid])) for cid in GENERATED_IDS|FIXED_TOKEN_IDS});return g
 def setUp(self):
  for table,value in ((cards.RULES,{**RULES,**TOKEN_RULES}),(cards.DEATH_EFFECTS,DEATH_EFFECTS)):
   p=patch.dict(table,value);p.start();self.addCleanup(p.stop)
 def play_and_kill(self,g,cid):
  p=g.players[0];p.mana=10;c=g._add(0,cid);g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid))
  if g.cards[cid]['type']=='WEAPON':g._break_weapon(0)
  else:
   m=next(m for m in p.minions if m.card_id==cid);g._damage(m.uid,99);g._settle()
  g.assert_invariants()
 def test_all_roots_paid_play_then_physical_death(self):
  for cid in GENERATED_IDS:
   with self.subTest(cid=cid):self.play_and_kill(self.game(),cid)
 def test_membership_and_literal_tokens(self):
  self.assertEqual(len(GENERATED_IDS),36);self.assertTrue(GENERATED_IDS<=set(load_universe().members));self.assertEqual(len(FIXED_TOKEN_IDS),4)
 def test_runts_are_three_distinct_literal_identities(self):
  g=self.game();self.play_and_kill(g,'LOE_089');self.assertEqual([m.card_id for m in g.players[0].minions],['LOE_089t','LOE_089t2','LOE_089t3'])
 def test_ponies_fit_after_death_slot_freed(self):
  g=self.game();p=g.players[0]
  for _ in range(6):g._summon(0,'NEW1_034')
  self.play_and_kill(g,'WORK_018');self.assertEqual(len(p.minions),7);self.assertEqual(sum(m.card_id=='WORK_018t' for m in p.minions),1)
 def test_armor_and_heal_owner(self):
  g=self.game();p,q=g.players;p.health=q.health=10
  self.play_and_kill(g,'BAR_535');self.assertEqual(p.armor,5)
  self.play_and_kill(g,'GIL_667');self.assertEqual((p.health,q.health),(16,10))
 def test_random_enemy_minion_damage_does_not_hit_hero(self):
  g=self.game();self.play_and_kill(g,'BOT_606');self.assertEqual(g.players[1].health,30)
 def test_random_enemy_character_damage_can_hit_hero(self):
  g=self.game();self.play_and_kill(g,'AV_704');self.assertEqual(g.players[1].health,22)
 def test_filtered_draw_uses_exact_school_then_second_checkpoint(self):
  g=self.game();p=g.players[0]
  for cid,school in [('HOLY_FIX','HOLY'),('SHADOW_FIX','SHADOW')]:g.cards[cid]=dict(id=cid,type='SPELL',name=cid,cost=0,spellSchool=school,cardClass='PRIEST')
  p.deck=[Card(g._new_id(),'CORE_CS2_029'),Card(g._new_id(),'HOLY_FIX'),Card(g._new_id(),'SHADOW_FIX')]
  self.play_and_kill(g,'AV_328');self.assertEqual([c.card_id for c in p.hand],['HOLY_FIX','SHADOW_FIX']);self.assertEqual([c.card_id for c in p.deck],['CORE_CS2_029'])
 def test_silence_prevents_literal_summon_deathrattle(self):
  g=self.game();p=g.players[0];m=g._summon(0,'WORK_018');g._silence(m);g._damage(m.uid,99);g._settle();self.assertFalse(p.minions)
 def test_elementium_geode_draw_damage_both_battlecry_and_death(self):
  g=self.game();self.play_and_kill(g,'DEEP_030');self.assertEqual((len(g.players[0].hand),g.players[0].health),(2,26))
 def test_deathrattle_filtered_draw_includes_only_actual_minion_mechanic(self):
  g=self.game();p=g.players[0];p.deck=[Card(g._new_id(),'CORE_CS2_029'),Card(g._new_id(),'BAR_026'),Card(g._new_id(),'NEW1_034')]
  self.play_and_kill(g,'BOT_509');self.assertEqual([c.card_id for c in p.hand],['BAR_026'])
 def test_combo_draw_can_draw_spell(self):
  g=self.game();p=g.players[0];g.cards['COMBO_FIX']=dict(id='COMBO_FIX',name='Combo',type='SPELL',cost=1,mechanics=['COMBO'],cardClass='ROGUE')
  p.deck=[Card(g._new_id(),'CORE_CS2_029'),Card(g._new_id(),'COMBO_FIX')];self.play_and_kill(g,'GIL_557');self.assertEqual(p.hand[0].card_id,'COMBO_FIX')
 def test_health_filter_draws_two_printed_one_health_minions(self):
  g=self.game();p=g.players[0]
  g.cards['ONE_FIX']=dict(id='ONE_FIX',name='One',type='MINION',cost=1,attack=9,health=1,cardClass='NEUTRAL')
  p.deck=[Card(g._new_id(),'NEW1_034'),Card(g._new_id(),'ONE_FIX'),Card(g._new_id(),'ONE_FIX')];self.play_and_kill(g,'ULD_438')
  self.assertEqual([c.card_id for c in p.hand],['ONE_FIX','ONE_FIX'])
