"""Exact fixed summon recipes; fixtures do not approve historical generation pools."""
import unittest
from copy import deepcopy
from unittest.mock import patch
import test_expanded_generation as fixtures
from expanded import cards,Action
from expanded.historical_generation_catalog import load_universe
from expanded.historical_fixed_summons import RULES,TOKEN_RULES,DEATH_EFFECTS,TRIGGERS,GENERATED_IDS,FIXED_TOKEN_IDS
from engine.game import Card
class HistoricalFixedSummonTests(unittest.TestCase):
 def setUp(self):
  self.fx=fixtures.GenerationTests()
  for table,value in ((cards.RULES,{**RULES,**TOKEN_RULES}),(cards.DEATH_EFFECTS,DEATH_EFFECTS),(cards.TRIGGERS,TRIGGERS)):
   p=patch.dict(table,value);p.start();self.addCleanup(p.stop)
 def game(self):
  g=self.fx.game();u=load_universe();g.cards.update({cid:deepcopy(dict(u.records[cid])) for cid in GENERATED_IDS|FIXED_TOKEN_IDS});return g
 def play(self,g,cid,target=0):
  p=g.players[0];p.mana=10;c=g._add(0,cid)
  g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid and a.target==target));return c
 def test_all_literal_recipes_complete_paid_play(self):
  for cid in GENERATED_IDS:
   with self.subTest(cid=cid):
    g=self.game();target=0
    if RULES[cid][0]!='none':
     target=g._summon(1,'NEW1_034').uid
    self.play(g,cid,target);g.assert_invariants()
 def test_token_metadata_exact_and_closed(self):
  u=load_universe();self.assertFalse(FIXED_TOKEN_IDS-u.records.keys());self.assertFalse(GENERATED_IDS&FIXED_TOKEN_IDS)
 def test_flark_four_bombs_death_damage(self):
  g=self.game();self.play(g,'BOT_034');bombs=[m for m in g.players[0].minions if m.card_id=='BOT_031'];self.assertEqual(len(bombs),4)
  g._damage(bombs[0].uid,99);g._settle();self.assertEqual(g.players[1].health,28)
 def test_opponent_summon_count(self):
  g=self.game();self.play(g,'UNG_926');self.assertEqual([m.card_id for m in g.players[1].minions],['UNG_076t1']*3)
 def test_rascal_battlecry_and_death_other_controller(self):
  g=self.game();self.play(g,'ICC_025');p,q=g.players
  self.assertEqual(p.minions[1].card_id,'ICC_025t');g._damage(p.minions[0].uid,99);g._settle();self.assertEqual(q.minions[0].card_id,'ICC_025t')
 def test_twinspell_copy_added_once(self):
  g=self.game();self.play(g,'DAL_378');self.assertEqual([c.card_id for c in g.players[0].hand],['DAL_378ts']);self.play(g,'DAL_378ts');self.assertEqual(len(g.players[0].hand),1)
 def test_physical_self_copy_preserves_hand_buffs(self):
  g=self.game();p=g.players[0];p.mana=10;c=g._add(0,'CFM_668');c.attack_bonus=3;c.health_bonus=2
  g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid));self.assertEqual([(m.attack,m.health) for m in p.minions],[(g.cards["CFM_668"]["attack"]+3,g.cards["CFM_668"]["health"]+2)]*3)
 def test_saronite_literal_summon_does_not_copy_enchantments(self):
  g=self.game();p=g.players[0];p.mana=10;c=g._add(0,'ICC_466');c.attack_bonus=3
  g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid));self.assertEqual([m.attack for m in p.minions],[5,2])
 def test_zergling_literal_summon_does_not_replay_battlecry(self):
  g=self.game();self.play(g,'SC_010');self.assertEqual([m.card_id for m in g.players[0].minions],['SC_010']*2)
 def test_frosty_decor_token_death_has_armor(self):
  g=self.game();self.play(g,'VAC_305');m=g.players[0].minions[0];g._damage(m.uid,99);g._settle();self.assertEqual(g.players[0].armor,4)
 def test_inspire_on_owner_power_only(self):
  g=self.game();self.play(g,'AT_099');g.players[0].mana=10;g.step(Action('power',target=-2));self.assertEqual([m.card_id for m in g.players[0].minions],['AT_099','AT_099t'])
 def test_flash_sale_buff_includes_new_annoyotron(self):
  g=self.game();self.play(g,'TOY_716');m=g.players[0].minions[0];self.assertEqual((m.attack,m.max_health),(2,4));self.assertTrue({'TAUNT','DIVINE_SHIELD'}<=m.keywords)
