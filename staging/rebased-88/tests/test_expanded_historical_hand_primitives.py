"""Controlled effect conformance; not historical pool approval."""
import unittest
from copy import deepcopy
from unittest.mock import patch
import test_expanded_generation as fixtures
from expanded import cards,Action
from expanded.historical_generation_catalog import load_universe
from expanded.historical_hand_primitives import RULES,GENERATED_IDS,DEATH_EFFECTS,END_EFFECTS,START_EFFECTS,HistoricalHandPrimitives
from engine.game import Card

class HistoricalHandTests(unittest.TestCase):
 def setUp(self):
  self.fx=fixtures.GenerationTests();self.g=self.fx.game();self.p,self.q=self.g.players
  self.g.cards.update({cid:deepcopy(dict(load_universe().records[cid])) for cid in GENERATED_IDS})
  for table,value in ((cards.RULES,RULES),(cards.DEATH_EFFECTS,DEATH_EFFECTS),(cards.END_EFFECTS,END_EFFECTS),(cards.START_EFFECTS,START_EFFECTS)):
   p=patch.dict(table,value);p.start();self.addCleanup(p.stop)
  original=self.g._dispatch_effect
  def dispatch(op,ctx):
   if not HistoricalHandPrimitives._historical_hand_effect(self.g,op,ctx):return original(op,ctx)
  self.g._dispatch_effect=dispatch
 def play(self,cid):
  self.p.mana=10;c=self.g._add(0,cid)
  self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid));return c
 def hand(self,tribe=None):
  cid='HIST_HAND_FIX_'+str(len(self.p.hand));d=dict(id=cid,name=cid,type='MINION',cost=0,attack=2,health=3,cardClass='NEUTRAL',races=[tribe] if tribe else [])
  self.g.cards[cid]=d;self.g.cards[cid]['mechanics']=[]
  c=Card(self.g._new_id(),cid);self.p.hand.append(c);return c
 def test_exact_batch_members_are_historical_and_unadmitted_by_fixture(self):
  self.assertEqual(len(GENERATED_IDS),32);self.assertTrue(GENERATED_IDS<=set(load_universe().members))
 def test_self_injury_all_four_paid_roots(self):
  for cid,amount in [('AT_105',3),('BAR_069',6),('BOT_448',6),('VAC_934',10)]:
   self.p.board.clear();self.play(cid);m=self.p.minions[0]
   self.assertEqual(m.health,self.g.cards[cid]['health']-amount)
 def test_both_heroes_damage_and_spell_bonus(self):
  self.p.health=self.q.health=30;self.play('DMF_066');self.assertEqual((self.p.health,self.q.health),(26,26))
  self.fx.run_ops(self.g,[('historical_heroes_damage',4)],spell=True,bonus=2)
  self.assertEqual((self.p.health,self.q.health),(20,20))
 def test_both_heroes_heal_clamps_and_ignores_armor(self):
  self.p.health=29;self.q.health=15;self.p.armor=5;self.play('BAR_309')
  self.assertEqual((self.p.health,self.q.health,self.p.armor),(30,20,5))
 def test_mistress_death_heals_both_heroes(self):
  self.p.health=self.q.health=10;self.play('CFM_120');self.g._damage(self.p.minions[0].uid,99);self.g._settle()
  self.assertEqual((self.p.health,self.q.health),(14,14))
 def test_random_beast_buff_filters_and_keeps_opponent(self):
  beast=self.hand('BEAST');other=self.hand('DRAGON');spell=self.g._add(0,'CORE_CS2_029');self.play('CFM_334')
  self.assertEqual((beast.attack_bonus,beast.health_bonus),(2,2));self.assertEqual(other.attack_bonus,0);self.assertEqual(spell.attack_bonus,0)
 def test_all_dragon_buff_includes_all_tribes(self):
  a=self.hand('DRAGON');b=self.hand('ALL');c=self.hand('BEAST');self.play('DAL_147')
  self.assertEqual([x.attack_bonus for x in (a,b,c)],[3,3,0])
 def test_empty_random_hand_buff_does_not_consume_rng(self):
  before=self.g.rng.getstate();self.play('CFM_334');self.assertEqual(self.g.rng.getstate(),before)
 def test_crimson_commander_battlecry_and_death_stack(self):
  a=self.hand('DRAENEI');b=self.hand('DEMON');self.play('GDB_722');m=self.p.minions[0]
  self.g._damage(m.uid,99);self.g._settle();self.assertEqual((a.attack_bonus,a.health_bonus,b.attack_bonus),(4,2,0))
 def test_owner_end_all_and_random_hand_hooks(self):
  a=self.hand();self.play('CFM_639');self.play('CFM_754');self.g.step(Action('end'))
  self.assertEqual((a.attack_bonus,a.health_bonus),(3,3));self.g.step(Action('end'));self.assertEqual(a.attack_bonus,3)
 def test_owner_start_hand_hook(self):
  a=self.hand();self.play('BAR_033');self.g.step(Action('end'));self.assertEqual(a.attack_bonus,0)
  self.g.step(Action('end'));self.assertEqual(a.attack_bonus,1)
 def test_silence_removes_end_and_death_buffs(self):
  a=self.hand();self.play('CFM_639');self.g._silence(self.p.minions[0]);self.g.step(Action('end'));self.assertEqual(a.attack_bonus,0)
 def test_taunt_hand_buff_uses_keywords_not_tribes(self):
  a=self.hand();b=self.hand();self.g.cards[a.card_id]['mechanics']=['TAUNT'];self.play('ULD_256')
  self.assertEqual((a.attack_bonus,b.attack_bonus),(2,0))
 def test_demon_and_murloc_death_hooks_filter_hand(self):
  a=self.hand('DEMON');b=self.hand('MURLOC');c=self.hand('DRAGON')
  for cid in ('BOT_443','TSC_614'):
   self.play(cid);self.g._damage(self.p.minions[0].uid,99);self.g._settle()
  self.assertEqual([x.attack_bonus for x in (a,b,c)],[1,1,0])
 def test_single_random_buff_affects_exactly_one_physical_card(self):
  hand=[self.hand() for _ in range(4)];self.play('CFM_685')
  self.assertEqual(sorted(c.attack_bonus for c in hand),[0,0,0,5]);self.assertEqual(sorted(c.health_bonus for c in hand),[0,0,0,5])
 def test_bannerman_draws_minion_before_buffing_it(self):
  a=self.hand();self.p.deck=[Card(self.g._new_id(),'CORE_EX1_162')];self.play('SW_315')
  self.assertEqual(a.attack_bonus,1);self.assertEqual(len(self.p.hand),2);self.assertEqual(self.p.hand[-1].attack_bonus,1)
