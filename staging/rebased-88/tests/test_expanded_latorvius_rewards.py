import gzip,json,unittest
from pathlib import Path
from unittest.mock import patch
import test_expanded_generation as fixtures
from engine.game import Card
from expanded import Action,cards,quest_families
from expanded.adapt import ADAPTATIONS,PLANT

class LatorviusRewardTests(unittest.TestCase):
 def setUp(self):
  self.fx=fixtures.GenerationTests();self.g=self.fx.game();self.p=self.g.players[0]
  ids=set(quest_families.TOKEN_RULES)|set(ADAPTATIONS)|{PLANT,'UNG_934t2','UNG_829t2'}
  with gzip.open(Path(__file__).resolve().parents[1]/'data/standard/all_cards.json.gz','rt') as f:self.g.cards.update({c['id']:c for c in json.load(f) if c['id'] in ids})
  ctx=patch.dict(cards.RULES,quest_families.TOKEN_RULES);ctx.start();self.addCleanup(ctx.stop)
 def play(self,cid):
  self.p.mana=10;c=self.g._add(0,cid);self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid));return c
 def test_barnabus_changes_only_existing_deck_minions(self):
  physical=Card(self.g._new_id(),'CORE_EX1_162');physical.attack_bonus=2;physical.cost_delta=4
  self.p.deck=[physical,'CORE_EX1_012','CORE_CS2_029'];hand=self.g._add(0,'CORE_EX1_162');self.play('UNG_116t')
  self.assertIs(self.p.deck[0],physical);self.assertEqual(physical.attack_bonus,2)
  self.assertEqual([self.g._cost(c,0) for c in self.p.deck[:2]],[0,0]);self.assertEqual(self.p.deck[2],'CORE_CS2_029');self.assertFalse(hasattr(hand,'set_cost'))
 def test_barnabus_discount_survives_draw(self):
  self.p.deck=['CORE_EX1_162'];self.play('UNG_116t');self.g._draw(0);self.assertEqual(self.g._cost(self.p.hand[-1],0),0)
 def test_barnabus_does_not_discount_future_cards(self):
  self.play('UNG_116t');new=Card(self.g._new_id(),'CORE_EX1_162');self.p.deck.append(new);self.assertFalse(hasattr(new,'set_cost'))
 def test_carnassa_shuffles_twenty_unique_raptors_and_has_rush(self):
  before=len(self.p.deck);self.play('UNG_920t1');brood=[c for c in self.p.deck if isinstance(c,Card) and c.card_id=='UNG_920t2']
  self.assertEqual(len(self.p.deck),before+20);self.assertEqual(len(brood),20);self.assertEqual(len({c.uid for c in brood}),20);self.assertIn('RUSH',self.p.minions[0].keywords)
 def test_brood_battlecry_draws(self):
  before=len(self.p.deck);self.play('UNG_920t2');self.assertEqual(len(self.p.deck),before-1);self.assertEqual(len(self.p.hand),1)
 def test_summoned_brood_does_not_draw(self):
  before=len(self.p.deck);self.g._summon(0,'UNG_920t2');self.assertEqual(len(self.p.deck),before)
 def test_amara_sets_current_and_max_health_preserving_armor(self):
  self.p.health=3;self.p.armor=7;self.play('UNG_940t8');self.assertEqual((self.p.health,self.p.max_health,self.p.armor),(40,40,7));self.assertIn('TAUNT',self.p.minions[0].keywords)
 def test_amara_health_setting_does_not_record_healing(self):
  self.p.health=3;before=self.p.healing_done_turn;self.play('UNG_940t8');self.assertEqual(self.p.healing_done_turn,before)
 def test_galvadon_has_five_sequential_adapts_without_ashalon_grants(self):
  self.play('UNG_954t1');count=0
  while self.g.pending_choice:
   self.assertEqual(self.g.pending_choice['kind'],'minion_adapt');self.assertEqual(len(self.g.pending_choice['options']),3)
   self.g.step(Action('choose',choices=(0,)));count+=1;self.assertLessEqual(count,5)
  self.assertEqual(count,5);self.assertEqual(self.p.ashalon_adaptations,[])
 def test_galvadon_summon_does_not_offer_battlecry(self):
  self.g._summon(0,'UNG_954t1');self.assertIsNone(self.g.pending_choice)

 def test_sulfuras_installs_permanent_power(self):
  self.p.power_used=True;self.play('UNG_934t1');self.assertEqual(self.p.primary_power['card_id'],'UNG_934t2');self.assertFalse(self.p.power_used)
  self.g._break_weapon(0);self.assertEqual(self.p.primary_power['card_id'],'UNG_934t2')
 def test_sulfuras_power_cost_damage_and_use_limit(self):
  self.play('UNG_934t1');before=self.g.players[1].health;mana=self.p.mana
  self.g.step(next(a for a in self.g.legal_actions() if a.kind=='power'));self.assertEqual(self.g.players[1].health,before-8);self.assertEqual(self.p.mana,mana-2);self.assertFalse(any(a.kind=='power' for a in self.g.legal_actions()))
 def test_sulfuras_has_no_two_use_expiry(self):
  self.play('UNG_934t1');self.g.players[1].health=100
  for _ in range(3):
   self.p.power_used=False;self.p.mana=10;self.g.step(next(a for a in self.g.legal_actions() if a.kind=='power'))
  self.assertEqual(self.p.primary_power['card_id'],'UNG_934t2');self.assertEqual(self.g.players[1].health,76)
 def test_sulfuras_random_damage_not_boosted_by_spell_damage(self):
  self.g._summon(0,'CORE_EX1_012');self.play('UNG_934t1');before=self.g.players[1].health
  self.g.step(next(a for a in self.g.legal_actions() if a.kind=='power'));self.assertEqual(self.g.players[1].health,before-8)
 def test_megafin_fills_only_available_slots(self):
  self.fx.install(self.g,quest_families.MURLOCS,['CORE_EX1_509'])
  for _ in range(3):self.g._add(0,'TOKEN_COIN')
  self.play('UNG_942t');self.assertEqual(len(self.p.hand),10);self.assertEqual(sum(c.card_id=='CORE_EX1_509' for c in self.p.hand),7)
 def test_megafin_generated_cards_keep_normal_cost(self):
  self.fx.install(self.g,quest_families.MURLOCS,['CORE_EX1_509']);self.play('UNG_942t')
  self.assertTrue(all(self.g._cost(c,0)==self.g.cards[c.card_id]['cost'] for c in self.p.hand));self.assertEqual(len({c.uid for c in self.p.hand}),10)
 def test_megafin_full_hand_battlecry_does_not_overflow(self):
  self.fx.install(self.g,quest_families.MURLOCS,['CORE_EX1_509'])
  for _ in range(10):self.g._add(0,'TOKEN_COIN')
  self.fx.run_ops(self.g,quest_families.TOKEN_RULES['UNG_942t'][1]);self.assertEqual(len(self.p.hand),10);self.assertTrue(all(c.card_id=='TOKEN_COIN' for c in self.p.hand))
 def test_megafin_rejects_missing_pool(self):
  from engine.cards import UnsupportedCard
  with self.assertRaises(UnsupportedCard):self.play('UNG_942t')
 def test_megafin_pool_dependency_declared(self):
  self.assertEqual(quest_families.requests_for('UNG_942t'),{quest_families.MURLOCS})

 def test_portal_occupies_slot_without_becoming_minion(self):
  self.play('UNG_829t1');self.assertEqual(len(self.p.board),1);self.assertEqual(len(self.p.permanents),1);self.assertFalse(self.p.minions)
 def test_portal_has_no_rift_activation(self):
  self.play('UNG_829t1');self.g._add(0,'TOKEN_COIN');uid=self.p.permanents[0].uid
  self.assertFalse(any(a.kind=='activate' and a.source==uid for a in self.g.legal_actions()))
 def test_portal_summons_two_imps_on_own_end(self):
  self.play('UNG_829t1');self.g.step(Action('end'));self.assertEqual([x.card_id for x in self.p.board],['UNG_829t3','UNG_829t2','UNG_829t3'])
  self.assertEqual([(m.attack,m.health) for m in self.p.minions],[(3,2),(3,2)])
  self.g.step(Action('end'));self.assertEqual(len(self.p.minions),2)
 def test_portal_respects_one_remaining_slot(self):
  self.play('UNG_829t1')
  for _ in range(5):self.g._summon(0,'CORE_EX1_162')
  self.g.step(Action('end'));self.assertEqual(len(self.p.board),7);self.assertEqual(sum(m.card_id=='UNG_829t3' for m in self.p.minions),1)
 def test_portal_cannot_open_on_full_board(self):
  for _ in range(7):self.g._summon(0,'CORE_EX1_162')
  self.play('UNG_829t1');self.assertFalse(self.p.permanents);self.assertEqual(len(self.p.board),7)
 def test_portal_survives_minion_board_clear(self):
  self.play('UNG_829t1');self.g._summon(0,'CORE_EX1_162');self.fx.run_ops(self.g,[('destroy_all_minions',)])
  self.assertEqual(len(self.p.permanents),1);self.assertFalse(self.p.minions)
 def test_two_portals_each_trigger(self):
  self.play('UNG_829t1');self.play('UNG_829t1');self.g.step(Action('end'));self.assertEqual(len(self.p.permanents),2);self.assertEqual(len(self.p.minions),4)

 def test_latorvius_partitions_nine_distinct_rewards(self):
  self.fx.install(self.g,quest_families.MURLOCS,['CORE_EX1_509']);self.p.deck=[];self.play('TLC_602t')
  hand=[c.card_id for c in self.p.hand];deck=[c.card_id for c in self.p.deck]
  self.assertEqual(len(hand),2);self.assertEqual(len(deck),7);self.assertEqual(set(hand+deck),set(quest_families.LATORVIUS_REWARDS));self.assertFalse(set(hand)&set(deck))
 def test_latorvius_overflow_does_not_shuffle_chosen_rewards(self):
  self.fx.install(self.g,quest_families.MURLOCS,['CORE_EX1_509']);self.p.deck=[]
  for _ in range(9):self.g._add(0,'TOKEN_COIN')
  self.play('TLC_602t');self.assertEqual(len(self.p.hand),10);self.assertEqual(len(self.p.deck),7)
  handreward=self.p.hand[-1].card_id;self.assertNotIn(handreward,[c.card_id for c in self.p.deck])
 def test_latorvius_missing_dependency_rejects_before_rng_or_generation(self):
  from engine.cards import UnsupportedCard
  self.fx.install(self.g,quest_families.MURLOCS,['CORE_EX1_509']);self.g.cards.pop('UNG_829t2');before=self.g.rng.getstate();hand=list(self.p.hand);deck=list(self.p.deck)
  with self.assertRaises(UnsupportedCard):self.fx.run_ops(self.g,[('latorvius_rewards',)])
  self.assertEqual(self.g.rng.getstate(),before);self.assertEqual(self.p.hand,hand);self.assertEqual(self.p.deck,deck)
 def test_latorvius_missing_murloc_contract_rejects(self):
  from engine.cards import UnsupportedCard
  before=self.g.rng.getstate()
  with self.assertRaises(UnsupportedCard):self.fx.run_ops(self.g,[('latorvius_rewards',)])
  self.assertEqual(self.g.rng.getstate(),before)
 def test_latorvius_repeat_has_fresh_nine_reward_set(self):
  self.fx.install(self.g,quest_families.MURLOCS,['CORE_EX1_509']);self.p.deck=[];self.fx.run_ops(self.g,[('latorvius_rewards',),('latorvius_rewards',)])
  from collections import Counter
  self.assertEqual(Counter(c.card_id for c in self.p.hand+self.p.deck),Counter({cid:2 for cid in quest_families.LATORVIUS_REWARDS}))
