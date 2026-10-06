import unittest,gzip,json
from pathlib import Path
from unittest.mock import patch
import test_expanded_generation as fixtures
from expanded import cards,quest_families,Action
from engine.game import Card
class AshalonTests(unittest.TestCase):
 def setUp(self):
  self.g=fixtures.GenerationTests().game();self.p,self.q=self.g.players
  ids={'TLC_229','TLC_229t14',quest_families.PLANT,*quest_families.ADAPTATIONS}
  with gzip.open(Path(__file__).resolve().parents[1]/'data/standard/all_cards.json.gz','rt') as f:self.g.cards.update({c['id']:c for c in json.load(f) if c['id'] in ids})
  p=patch.dict(cards.RULES,{**quest_families.RULES,**quest_families.TOKEN_RULES});p.start();self.addCleanup(p.stop)
 def play(self,cid):
  self.p.mana=10;c=self.g._add(0,cid);self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid))
 def tribe(self,*tribes):
  cid='TEST_TRIBES';self.g.cards[cid]=dict(id=cid,type='MINION',attack=1,races=list(tribes));self.g._quest_card_played(0,Card(self.g._new_id(),cid))
 def test_six_distinct_types_award(self):
  self.play('TLC_229')
  for t in ('BEAST','DEMON','DRAGON','MURLOC','PIRATE','TOTEM'):self.tribe(t)
  self.assertIsNone(self.p.quest);self.assertEqual(self.p.hand[0].card_id,'TLC_229t14')
 def test_dual_type_counts_once(self):
  self.play('TLC_229');self.tribe('BEAST','DRAGON');self.assertEqual(self.p.quest['progress'],1)
 def test_all_counts_once(self):
  self.play('TLC_229');self.tribe('ALL');self.assertEqual(self.p.quest['progress'],1)
 def test_duplicate_and_untyped_do_not_progress(self):
  self.play('TLC_229');self.tribe('BEAST');self.tribe('BEAST');self.tribe();self.assertEqual(self.p.quest['progress'],1)
 def test_two_choices_store_two_grants(self):
  self.play('TLC_229t14');chosen=[]
  for _ in range(2):
   self.assertEqual(len(self.g.pending_choice['options']),3);chosen.append(self.g.pending_choice['options'][0]['card_id']);self.g.step(Action('choose',choices=(0,)))
  self.assertIsNone(self.g.pending_choice);self.assertEqual(self.p.ashalon_adaptations,chosen)
 def test_later_play_receives_grants(self):
  self.p.ashalon_adaptations=['UNG_999t3','UNG_999t5'];self.play('CORE_EX1_162');m=self.p.minions[0];self.assertEqual(m.attack,self.g.cards[m.card_id]['attack']+3);self.assertIn('ELUSIVE',m.keywords)
 def test_summoned_minion_does_not_receive_grants(self):
  self.p.ashalon_adaptations=['UNG_999t3'];m=self.g._summon(0,'CORE_EX1_162');self.assertEqual(m.attack,self.g.cards[m.card_id]['attack'])
 def test_silence_does_not_remove_player_grants(self):
  self.p.ashalon_adaptations=['UNG_999t5'];self.play('CORE_EX1_162');self.g._silence(self.p.minions[0]);self.assertEqual(self.p.ashalon_adaptations,['UNG_999t5'])
 def test_public_grants_exposed(self):
  self.p.ashalon_adaptations=['UNG_999t5'];self.assertEqual(self.g.observe(1)['players'][0]['ashalon_adaptations'],['UNG_999t5'])
