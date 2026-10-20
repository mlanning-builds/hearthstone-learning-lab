"""Exact holding and Combo branches use physical paid minion plays."""
import gzip,json,unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch
import test_expanded_generation as fixtures
from expanded import Action,cards
from expanded.historical_conditional_battlecries import RULES,TOKEN_RULES,DEATH_EFFECTS,HistoricalConditionalBattlecries

class HistoricalConditionalTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.prototype=fixtures.GenerationTests().game()
  records={c['id']:c for c in json.load(gzip.open(Path('data/standard/all_cards.json.gz'),'rt'))}
  cls.extra_records={cid:records[cid] for cid in set(RULES)|set(TOKEN_RULES)|{'BRM_004t'}}
 def setUp(self):
  for table,values in ((cards.RULES,RULES|TOKEN_RULES),(cards.DEATH_EFFECTS,DEATH_EFFECTS)):
   manager=patch.dict(table,values);manager.start();self.addCleanup(manager.stop)
 def game(self):
  g=deepcopy(self.prototype)
  g.cards.update(deepcopy(self.extra_records))
  if not isinstance(g,HistoricalConditionalBattlecries):
   base=g.__class__
   class Harness(HistoricalConditionalBattlecries,base):
    def _split_fixed_summon(self,operation,context):
     result=self._historical_conditional_split(operation,context)
     return result if result is not None else super()._split_fixed_summon(operation,context)
    def _targets_for(self,cid,owner,mode_override=None):
     mode=mode_override if mode_override is not None else cards.RULES.get(cid,('none',))[0]
     result=self._historical_conditional_targets(cid,owner,mode)
     return result if result is not None else super()._targets_for(cid,owner,mode_override)
    def _effect(self,op,ctx):
     if not self._historical_conditional_effect(op,ctx):return super()._effect(op,ctx)
   g.__class__=Harness
  return g
 def play(self,g,cid,active=False):
  p=g.players[0]
  if active:p.cards_played=2;g._add(0,'CORE_EX1_043')
  g._summon(0,'CORE_CS2_188');g._summon(1,'CORE_CS2_188')
  c=g._add(0,cid);p.mana=10
  actions=[a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid]
  self.assertTrue(actions,cid);g.step(actions[0]);g.assert_invariants();return next((m for m in p.minions if m.card_id==cid),None)
 def test_every_printed_root_active_and_inactive_paid_play(self):
  for cid in RULES:
   for active in (False,True):
    with self.subTest(cid=cid,active=active):self.play(self.game(),cid,active)
 def test_played_dragon_cannot_satisfy_own_holding_effect(self):
  for cid,amount in (('BRM_004',2),('GIL_601',1),('RLK_916',1)):
   g=self.game();m=self.play(g,cid);self.assertEqual(m.attack,g.cards[cid]['attack']);self.assertEqual(m.health,g.cards[cid]['health'])
 def test_other_physical_dragon_enables_intrinsic_keywords(self):
  for cid,keyword in (('AT_071','CHARGE'),('GIL_601','RUSH'),('GIL_635','DIVINE_SHIELD'),('BT_262','LIFESTEAL')):
   g=self.game();m=self.play(g,cid,True);self.assertIn(keyword,m.keywords)
 def test_combo_scaled_stats_count_other_cards_only(self):
  for cid,mult in (('EX1_613',2),('UNG_063',1)):
   g=self.game();m=self.play(g,cid,True);self.assertEqual((m.attack,m.health),(g.cards[cid]['attack']+2*mult,g.cards[cid]['health']+2*mult))
 def test_si7_combo_damage_matches_pinned_three_damage(self):
  for cid,amount in (('EX1_134',3),):
   g=self.game();p=g.players[0];p.cards_played=1;c=g._add(0,cid);p.mana=10;before=g.players[1].health
   g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid and a.target==-2))
   self.assertEqual(g.players[1].health,before-amount)
 def test_death_holding_condition_checked_when_death_resolves(self):
  for cid in DEATH_EFFECTS:
   g=self.game();m=g._summon(0,cid);enemy=g._summon(1,'CORE_CS2_188');g._add(0,'CORE_EX1_043')
   g._damage(m.uid,30);g._settle();self.assertNotIn(enemy,g.players[1].minions)
 def test_no_holding_deathrattle_leaves_enemy_unchanged(self):
  for cid in DEATH_EFFECTS:
   g=self.game();m=g._summon(0,cid);enemy=g._summon(1,'CORE_CS2_188');before=enemy.health
   g._damage(m.uid,30);g._settle();self.assertEqual(enemy.health,before)
 def test_fixed_whelps_have_rush_only_where_printed(self):
  for cid,token in (('KAR_010','KAR_010a'),('ONY_001','ONY_001t')):
   g=self.game();self.play(g,cid,True);bodies=[m for m in g.players[0].minions if m.card_id==token]
   self.assertEqual(len(bodies),2);self.assertEqual(['RUSH' in m.keywords for m in bodies],[cid=='ONY_001']*2)
 def test_conditional_destroy_small_attack_filters_enemy(self):
  g=self.game();g._add(0,'CORE_EX1_043');small=g._summon(1,'CORE_CS2_188');large=g._summon(1,'CORE_EX1_043');friend=g._summon(0,'CORE_CS2_188')
  self.assertEqual(g._targets_for('KAR_033',0),[small.uid])
 def test_scaled_effect_uses_explicit_replay_snapshot(self):
  g=self.game();m=g._summon(0,'EX1_613');g.players[0].cards_played=9;before=m.attack
  g._historical_conditional_effect(('historical_combo_scaled_buff',2),dict(owner=0,source=m,target=0,prior_card_count=3));self.assertEqual(m.attack,before+6)
 def test_swap_attack_preserves_current_health(self):
  g=self.game();g._add(0,'CORE_EX1_043');enemy=g._summon(1,'CORE_EX1_043');c=g._add(0,'LOOT_528');g.players[0].mana=10;a,h=enemy.attack,enemy.health
  g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid and a.target==enemy.uid));source=next(m for m in g.players[0].minions if m.card_id=='LOOT_528')
  self.assertEqual(source.attack,a);self.assertEqual(enemy.attack,g.cards['LOOT_528']['attack']);self.assertEqual(enemy.health,h)

 def test_physical_source_excluded_from_conditional_target_offer(self):
  g=self.game();enemy=g._summon(1,'CORE_CS2_188');source=g._add(0,'RLK_915')
  self.assertEqual(g._historical_conditional_card_targets(source,0),[0])
  second=g._add(0,'RLK_915');self.assertIn(enemy.uid,g._historical_conditional_card_targets(source,0))

 def test_shadow_sculptor_draws_prior_count_through_frames(self):
  g=self.game();p=g.players[0];p.cards_played=3;p.deck=['CORE_CS2_188']*4;c=g._add(0,'YOD_017');p.mana=10
  g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid))
  self.assertEqual(len(p.hand),3);self.assertEqual(len(p.deck),1);self.assertEqual(p.cards_played,4)
