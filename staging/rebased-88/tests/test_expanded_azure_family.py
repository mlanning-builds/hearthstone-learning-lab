import unittest,gzip,json
from pathlib import Path
from copy import deepcopy
from unittest.mock import patch
import test_expanded_generation as fixtures
from expanded import cards,fabled_effects as rules,Action
from engine.cards import UnsupportedCard

class AzureFamilyTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  root=Path(__file__).resolve().parents[1]
  with gzip.open(root/'data/standard/all_cards.json.gz','rt') as f:cls.records={c['id']:c for c in json.load(f)}
 def setUp(self):
  self.g=fixtures.GenerationTests().game();self.p,self.q=self.g.players
  self.g.cards.update({cid:deepcopy(self.records[cid]) for cid in ('TIME_852','TIME_852t1','TIME_852t3')})
  self.g.cards['TEST_ARCANE']=dict(self.g.cards['CORE_CS2_029'],id='TEST_ARCANE',spellSchool='ARCANE')
  self.g.cards['TEST_ALL']=dict(self.g.cards['NEW1_034'],id='TEST_ALL',races=['ALL'],race='ALL')
  patcher=patch.dict(cards.RULES,{**rules.RULES,**rules.TOKEN_RULES,'TEST_ARCANE':('character',[('damage',6)]),'TEST_ALL':('none',[])})
  patcher.start();self.addCleanup(patcher.stop)
 def run_ops(self,ops,**kw):
  ctx=dict(owner=0,source=None,target=0,bonus=0,lifesteal=False);ctx.update(kw)
  self.g._start_play_effects(ops,ctx);self.g._settle(allow_event_choices=True)
 def play(self,cid,target=0):
  self.p.mana=10;c=self.g._add(0,cid);a=next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid and a.target==target);self.g.step(a);return c
 def cost(self,cid):
  c=self.g._add(0,cid);value=self.g._cost(c,0);self.p.hand.remove(c);return value
 def pair(self):return self.g._summon(0,'TIME_852'),self.g._summon(0,'TIME_852t1')
 def test_lone_queen_needs_another_dragon(self):
  self.g._summon(0,'TIME_852');self.assertEqual(self.cost('TEST_ARCANE'),4)
  self.g._summon(0,'NEW1_034');self.assertEqual(self.cost('TEST_ARCANE'),4)
 def test_queen_discounts_only_owner_arcane_spells(self):
  self.pair();self.assertEqual(self.cost('TEST_ARCANE'),2);self.assertEqual(self.cost('CORE_CS2_029'),4)
  c=self.g._add(1,'TEST_ARCANE');self.assertEqual(self.g._cost(c,1),4)
 def test_two_queens_qualify_each_other_and_stack_to_zero(self):
  self.g._summon(0,'TIME_852');self.g._summon(0,'TIME_852');self.assertEqual(self.cost('TEST_ARCANE'),0)
 def test_silenced_dragon_counts_but_silenced_queen_does_not_discount(self):
  queen,king=self.pair();self.g._silence(king);self.assertEqual(self.cost('TEST_ARCANE'),2)
  self.g._silence(queen);self.assertEqual(self.cost('TEST_ARCANE'),4)
 def test_dormant_or_dead_dragon_does_not_qualify(self):
  queen,king=self.pair();king.dormant=2;self.assertEqual(self.cost('TEST_ARCANE'),4)
  king.dormant=0;king.health=0;self.assertEqual(self.cost('TEST_ARCANE'),4)
 def test_all_tribe_qualifies(self):
  self.g._summon(0,'TIME_852');self.g._summon(0,'TEST_ALL');self.assertEqual(self.cost('TEST_ARCANE'),2)
 def test_paid_arcane_repeats_effect_but_pays_and_records_once(self):
  self.pair();self.play('TEST_ARCANE',-2);self.assertEqual(self.q.health,18);self.assertEqual(self.p.mana,8);self.assertEqual([r['card_id'] for r in self.p.played_history],['TEST_ARCANE'])
 def test_fire_spell_and_lone_king_do_not_repeat(self):
  self.g._summon(0,'TIME_852t1');self.play('TEST_ARCANE',-2);self.assertEqual(self.q.health,24)
  self.g._summon(0,'TIME_852');self.play('CORE_CS2_029',-2);self.assertEqual(self.q.health,18)
 def test_silence_stops_repeat(self):
  queen,king=self.pair();self.g._silence(king);self.play('TEST_ARCANE',-2);self.assertEqual(self.q.health,24)
 def test_internal_arcane_cast_repeats_without_paid_history(self):
  self.pair();self.run_ops([('cast_fixed_spell','TEST_ARCANE','selected')],target=-2);self.assertEqual(self.q.health,18);self.assertFalse(self.p.played_history)
 def test_competing_repeat_rejects_and_rolls_back(self):
  self.pair();self.p.spell_repeat_charges=1;c=self.g._add(0,'TEST_ARCANE');before=deepcopy(self.g.observe(0));rng=self.g.rng.getstate()
  with self.assertRaisesRegex(UnsupportedCard,'Malygos repetition stacking'):self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid and a.target==-2))
  self.assertEqual(self.g.observe(0),before);self.assertEqual(self.g.rng.getstate(),rng)
 def test_multiple_kings_reject_unknown_repeat_stacking(self):
  self.g._summon(0,'TIME_852t1');self.g._summon(0,'TIME_852t1')
  with self.assertRaisesRegex(UnsupportedCard,'Malygos repetition stacking'):self.play('TEST_ARCANE',-2)
 def test_oathstone_resurrects_duplicates_and_all_tribe_not_enemy_deaths(self):
  self.p.death_history=['TIME_852','TIME_852','TEST_ALL','NEW1_034'];self.q.death_history=['TIME_852t1'];self.play('TIME_852t3')
  self.assertCountEqual([m.card_id for m in self.p.minions],['TIME_852','TIME_852','TEST_ALL'])
 def test_oathstone_resurrects_printed_stats_not_death_buffs(self):
  queen=self.g._summon(0,'TIME_852');self.g._buff(queen,8,8);queen.health=0;self.g._settle();self.play('TIME_852t3');m=self.p.minions[0];self.assertEqual((m.attack,m.health),(2,8))
 def test_oathstone_full_board_does_not_remove_history(self):
  for _ in range(7):self.g._summon(0,'NEW1_034')
  self.p.death_history=['TIME_852']*9;self.play('TIME_852t3');self.assertEqual(len(self.p.minions),7);self.assertEqual(self.p.death_history,['TIME_852']*9)
 def test_oathstone_empty_and_internal_cast(self):
  self.play('TIME_852t3');self.assertFalse(self.p.minions)
  self.p.death_history=['TIME_852'];self.run_ops([('cast_fixed_spell','TIME_852t3','random')]);self.assertEqual(self.p.minions[0].card_id,'TIME_852')
 def test_root_remains_staged(self):self.assertNotIn('TIME_852',cards.COLLECTIBLE_IDS)
