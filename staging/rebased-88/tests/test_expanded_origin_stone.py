import unittest,gzip,json
from pathlib import Path
from unittest.mock import patch
import test_expanded_generation as fixtures
from expanded import cards,quest_families,Action
from expanded.generation_cards import pool,discover
class OriginStoneTests(unittest.TestCase):
 def setUp(self):
  self.fx=fixtures.GenerationTests();self.g=self.fx.game();self.p,self.q=self.g.players
  with gzip.open(Path(__file__).resolve().parents[1]/'data/standard/all_cards.json.gz','rt') as f:self.g.cards.update({c['id']:c for c in json.load(f) if c['id'] in ('TLC_460','TLC_460t')})
  p=patch.dict(cards.RULES,{**quest_families.RULES,**quest_families.TOKEN_RULES});p.start();self.addCleanup(p.stop)
  self.r=pool();self.fx.install(self.g,self.r,['CORE_EX1_162','TOKEN_COIN','CORE_CS2_029'])
 def play(self,cid):
  self.p.mana=10;c=self.g._add(0,cid);self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid))
 def offer(self,ids=None):
  if ids:self.fx.install(self.g,self.r,ids)
  self.fx.run_ops(self.g,[discover(self.r)])
 def choose(self,cid=None):
  i=next((i for i,o in enumerate(self.g.pending_choice['options']) if o['card_id']==cid),0);self.g.step(Action('choose',choices=(i,)))
 def test_eight_discovers_award_weapon(self):
  self.play('TLC_460')
  for _ in range(8):self.offer(['TOKEN_COIN']);self.choose()
  self.assertIsNone(self.p.quest);self.assertEqual(self.p.hand[-1].card_id,'TLC_460t')
 def test_offer_alone_does_not_progress(self):
  self.play('TLC_460');self.offer();self.assertEqual(self.p.quest['progress'],0)
 def test_other_options_execute_and_selected_stays_in_hand(self):
  self.play('TLC_460t');self.offer();self.choose('CORE_CS2_029');self.assertEqual([m.card_id for m in self.p.minions],['CORE_EX1_162']);self.assertEqual(self.p.hand[-1].card_id,'CORE_CS2_029');self.assertEqual(self.p.weapon['durability'],7)
 def test_last_charge_still_executes(self):
  self.play('TLC_460t');self.p.weapon['durability']=1;self.offer(['CORE_EX1_162','TOKEN_COIN']);self.choose('TOKEN_COIN');self.assertIsNone(self.p.weapon);self.assertEqual(len(self.p.minions),1)
 def test_single_option_consumes_charge_without_extra_card(self):
  self.play('TLC_460t');self.offer(['TOKEN_COIN']);self.choose();self.assertEqual(self.p.weapon['durability'],7);self.assertEqual(len(self.p.hand),1)
 def test_other_player_weapon_does_not_trigger(self):
  self.g._equip(1,'TLC_460t');self.offer(['CORE_EX1_162','TOKEN_COIN']);self.choose('TOKEN_COIN');self.assertEqual(self.q.weapon['durability'],8);self.assertEqual(self.p.minions,[])
 def test_generated_minion_is_not_paid_play(self):
  self.play('TLC_460t');count=self.p.cards_played;self.offer(['CORE_EX1_162','TOKEN_COIN']);self.choose('TOKEN_COIN');self.assertEqual(self.p.cards_played,count)
 def test_full_hand_still_plays_unchosen(self):
  self.play('TLC_460t')
  for _ in range(10):self.g._add(0,'TOKEN_COIN')
  self.offer(['CORE_EX1_162','TOKEN_COIN']);self.choose('TOKEN_COIN');self.assertEqual(len(self.p.hand),10);self.assertEqual(len(self.p.minions),1)
 def test_secret_identity_not_in_opponent_observation(self):
  self.play('TLC_460t');self.offer(['CORE_EX1_287','TOKEN_COIN']);self.choose('TOKEN_COIN');self.assertEqual(len(self.p.secrets),1);self.assertNotIn('CORE_EX1_287',json.dumps(self.g.observe(1)))
 def test_queued_trigger_does_not_damage_replacement_weapon(self):
  self.play('TLC_460t');uid=self.p.equipped_card.uid;self.g._equip(0,'CS2_082');before=self.p.weapon['durability'];self.g._effect(('origin_execute',uid,('TOKEN_COIN',)),dict(owner=0,source=None));self.assertEqual(self.p.weapon['durability'],before)
