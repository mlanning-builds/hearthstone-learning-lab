"""All Imbue consumer declarations, with explicit fixture-only admission."""
import json,unittest
from unittest.mock import patch
import test_expanded_generation as fixtures
from expanded import cards,Action
from expanded.imbue_consumers import RULES,DEATH_EFFECTS,WILD_GODS,WILD_POOL,TWO
from expanded.pools import GenerationPool
from engine.game import Card
from engine.cards import UnsupportedCard
from standard.catalog import load_catalog

class ImbueConsumerTests(unittest.TestCase):
 def setUp(self):
  self.g=fixtures.GenerationTests().game();self.g.cards.update({c['id']:c for c in load_catalog() if c['id'] in RULES});self.g._generation_pools={}
  for table,values in ((cards.RULES,RULES),(cards.DEATH_EFFECTS,DEATH_EFFECTS)):
   context=patch.dict(table,values);context.start();self.addCleanup(context.stop)
 @property
 def p(self):return self.g.players[0]
 @property
 def q(self):return self.g.players[1]
 def add(self,cid):
  c=Card(self.g._new_id(),cid);self.g._enter_hand(0,c);return c
 def play(self,cid,target=0):
  c=self.add(cid);self.p.mana=10;self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid and a.target==target));return c
 def op(self,op):
  self.g._start_play_effects([op],dict(owner=0,source=None,target=0,bonus=0,lifesteal=False));self.g._settle(allow_event_choices=True)
 def choose(self,i=0):self.g.step(Action('choose',choices=(i,)))
 def install(self,req,ids):self.g._generation_pools[(req,self.p.hero_class)]=GenerationPool('fixture',tuple(ids),'Controlled fixture; not production review')
 def cycle(self):self.g.step(Action('end'));self.g.step(Action('end'))
 def start_hamuul(self,deck):
  self.p.starting_deck=deck;self.p.imbue_start_checked=False;self.g._imbue_start_game(0)
 def test_all_nineteen_declared_and_staged(self):
  from expanded.pending_definitions import DEFINITIONS
  self.assertEqual(set(RULES),{cid for cid,d in DEFINITIONS.items() if d['family']=='imbue'});self.assertEqual(len(RULES),19);self.assertFalse(set(RULES)&cards.COLLECTIBLE_IDS)
 def test_all_simple_battlecries_imbue_once(self):
  for cid in ('EDR_449','EDR_451','EDR_800','EDR_852','END_001'):
   with self.subTest(cid=cid):
    self.p.board=[];before=self.p.imbue_count;self.play(cid);self.assertEqual(self.p.imbue_count,before+1)
 def test_deathrattles_imbue(self):
  for cid in DEATH_EFFECTS:
   m=self.g._summon(0,cid);before=self.p.imbue_count;m.health=0;self.g._settle();self.assertEqual(self.p.imbue_count,before+1)
 def test_silenced_deathrattle_does_not_imbue(self):
  m=self.g._summon(0,'EDR_451');self.g._silence(m);m.health=0;self.g._settle();self.assertEqual(self.p.imbue_count,0)
 def test_drake_battlecry_and_death_both_imbue(self):
  self.play('EDR_451');self.p.minions[0].health=0;self.g._settle();self.assertEqual(self.p.imbue_count,2)
 def test_houndmaster_draws_beast_then_imbues(self):
  beast=next(cid for cid,d in self.g.cards.items() if 'BEAST' in d.get('races',[]));self.p.deck=[beast];self.play('EDR_226');self.assertEqual(self.p.hand[0].card_id,beast);self.assertEqual(self.p.imbue_count,1)
 def test_aspect_heal_draw_imbue(self):
  self.p.health=20;self.play('EDR_231',-1);self.assertEqual(self.p.health,24);self.assertEqual(len(self.p.hand),1);self.assertEqual(self.p.imbue_count,1)
 def test_aegis_summon_taunt_before_imbue(self):
  self.install(TWO,['CORE_EX1_012']);self.play('EDR_264');self.assertIn('TAUNT',self.p.minions[0].keywords);self.assertEqual(self.p.imbue_count,1)
 def test_aegis_missing_pool_rolls_back_play(self):
  with self.assertRaises(UnsupportedCard):self.play('EDR_264')
  self.assertEqual(self.p.imbue_count,0);self.assertEqual(self.p.mana,10)
 def test_aegis_full_board_still_imbues(self):
  for _ in range(7):self.g._summon(0,'CORE_EX1_012')
  self.install(TWO,['CORE_EX1_012']);self.play('EDR_264');self.assertEqual(len(self.p.minions),7);self.assertEqual(self.p.imbue_count,1)
 def test_living_garden_choices_only_physical_minions(self):
  c=self.add('CORE_EX1_012');self.add('CORE_CS2_029');self.play('EDR_518');self.assertEqual(self.p.imbue_count,1);self.assertEqual([o['uid'] for o in self.g.pending_choice['options']],[c.uid]);self.choose();self.assertEqual(c.cost_delta,-1);self.assertEqual(self.p.discoveries_total,0)
 def test_living_garden_empty_hand_no_choice(self):
  self.play('EDR_518');self.assertIsNone(self.g.pending_choice);self.assertEqual(self.p.imbue_count,1)
 def test_garden_choice_private(self):
  self.add('CORE_EX1_012');self.play('EDR_518');self.assertEqual(self.g.observe(1)['pending_choice'],{'owner':0,'waiting':True})
 def test_wisprider_free_trigger_does_not_consume_power(self):
  before=self.p.hero_power_uses;self.play('EDR_519');self.assertEqual(self.q.health,29);self.assertFalse(self.p.power_used);self.assertEqual(self.p.hero_power_uses,before)
 def test_wisprider_triggers_already_used_power(self):
  self.p.power_used=True;self.play('EDR_519');self.assertEqual(self.q.health,29);self.assertTrue(self.p.power_used)
 def test_wisprider_imbues_before_free_trigger(self):
  self.g._imbue(0,2);self.play('EDR_519');self.assertEqual(self.p.imbue_count,3);self.assertEqual(self.q.health,27)
 def test_unconnected_wisprider_power_fails_without_payment(self):
  self.p.hero_class='PRIEST'
  with self.assertRaises(UnsupportedCard):self.play('EDR_519')
  self.assertEqual(self.p.mana,10);self.assertEqual(self.p.imbue_count,0)
 def test_dreamweaver_no_target_below_two(self):
  self.play('EDR_860');self.assertEqual(self.q.health,30)
 def test_dreamweaver_threshold_damage_and_lifesteal(self):
  self.g._imbue(0,2);m=self.g._summon(1,'CORE_EX1_012');self.p.health=20;self.play('EDR_860',m.uid);self.assertNotIn(m,self.q.minions);self.assertEqual(self.p.health,24)
 def test_spirit_gatherer_adds_wisp(self):
  self.play('EDR_871');self.assertEqual(self.p.hand[0].card_id,'EDR_851t');self.assertEqual(self.p.imbue_count,1)
 def test_finality_draws_undead_and_imbues_twice(self):
  undead=next(cid for cid,d in self.g.cards.items() if 'UNDEAD' in d.get('races',[]));self.p.deck=[undead];self.play('END_003');self.assertEqual(self.p.hand[0].card_id,undead);self.assertEqual(self.p.imbue_count,2)
 def test_eventuality_damage_then_imbue(self):
  self.play('END_000',-2);self.assertEqual(self.q.health,28);self.assertEqual(self.p.imbue_count,1)
 def test_picker_threshold(self):
  self.play('FIR_921');self.assertFalse(self.p.hand);self.g._imbue(0,2);self.play('FIR_921');self.assertEqual(len(self.p.hand),2)
 def test_malorne_requires_explicit_wild_pool(self):
  with self.assertRaises(UnsupportedCard):self.play('EDR_888')
  self.assertEqual(self.p.mana,10)
 def test_malorne_four_imbues_sets_cost_one(self):
  self.install(WILD_POOL,['EDR_895']);self.g._imbue(0,4);self.play('EDR_888');self.choose();self.assertEqual(self.g._cost(self.p.hand[0],0),1)
 def test_malorne_below_four_retains_cost(self):
  self.install(WILD_POOL,['EDR_895']);self.play('EDR_888');self.choose();self.assertEqual(self.g._cost(self.p.hand[0],0),self.g.cards['EDR_895']['cost'])
 def test_non_wild_legendary_rejected(self):
  self.install(WILD_POOL,['CORE_EX1_012'])
  with self.assertRaises(UnsupportedCard):self.play('EDR_888')
 def test_hamuul_nature_condition_and_once_only(self):
  self.start_hamuul(['EDR_845','CORE_EX1_154']);self.g._imbue_start_game(0);self.assertTrue(self.p.hamuul_active);self.assertEqual(self.p.imbue_count,1)
 def test_hamuul_non_nature_spell_disables(self):
  self.start_hamuul(['EDR_845','CORE_CS2_029']);self.assertFalse(self.p.hamuul_active);self.assertEqual(self.p.imbue_count,0)
 def test_hamuul_no_spells_satisfies_condition(self):
  self.start_hamuul(['EDR_845','CORE_EX1_012']);self.assertTrue(self.p.hamuul_active)
 def test_hamuul_every_three_casts_persists_without_source(self):
  self.start_hamuul(['EDR_845']);
  for n in range(1,7):
   self.play('CORE_EX1_169');self.assertEqual(self.p.imbue_count,1+n//3)
  self.assertEqual(self.p.hamuul_spells,6)
 def test_opponent_casts_do_not_advance_hamuul(self):
  self.start_hamuul(['EDR_845']);self.g._queue_event('spell_cast',owner=1,card_id='CORE_EX1_169',cost=0);self.g._settle();self.assertEqual(self.p.hamuul_spells,0)
 def test_priestess_debuff_lasts_through_enemy_turn(self):
  m=self.g._summon(1,'CORE_EX1_012');self.play('EDR_970');self.assertEqual(m.attack,0);self.g.step(Action('end'));self.assertEqual(m.attack,0);self.g.step(Action('end'));self.assertEqual(m.attack,1)
 def test_stacked_debuffs_restore_negative_attack_correctly(self):
  m=self.g._summon(1,'CORE_EX1_012');self.play('EDR_970');self.play('EDR_970');self.assertEqual(m.attack_deficit,-3);self.cycle();self.assertEqual((m.attack,m.attack_deficit),(1,0))
 def test_silence_does_not_restore_expired_debuff_as_bonus(self):
  m=self.g._summon(1,'CORE_EX1_012');self.play('EDR_970');self.g._silence(m);self.cycle();self.assertEqual(m.attack,1)
 def test_copied_debuff_retains_expiration(self):
  m=self.g._summon(1,'CORE_EX1_012');self.play('EDR_970');copy=self.g._summon(1,m.card_id,copy_from=m);self.cycle();self.assertEqual((m.attack,copy.attack),(1,1))
 def test_death_knight_first_undead_only_and_resets_each_turn(self):
  self.p.hero_class='DEATHKNIGHT';self.g._imbue(0,3)
  cid=next(cid for cid,d in self.g.cards.items() if d['type']=='MINION' and 'UNDEAD' in d.get('races',[]) and cards.RULES.get(cid,('none',[]))[0]=='none' and d['cost']<5)
  base=self.g.cards[cid]['attack'];self.play(cid);self.play(cid);self.assertEqual(sorted(m.attack for m in self.p.minions if m.card_id==cid),sorted([base,base+3]));self.cycle();self.play(cid);self.assertEqual(sum(m.attack==base+3 for m in self.p.minions if m.card_id==cid),2)
 def test_death_knight_recruited_undead_does_not_use_first_play(self):
  self.p.hero_class='DEATHKNIGHT';self.g._imbue(0,2);cid=next(cid for cid,d in self.g.cards.items() if d['type']=='MINION' and 'UNDEAD' in d.get('races',[]));m=self.g._summon(0,cid);self.assertEqual(m.attack,self.g.cards[cid]['attack']);self.assertNotEqual(self.p.undead_play_turn,self.g.turn)
 def test_counter_features_and_observations_are_public(self):
  self.start_hamuul(['EDR_845']);view=self.g.observe(1);self.assertTrue(view['players'][0]['hamuul_active']);json.dumps(view)

 def test_internal_cast_does_not_publish_player_cast_for_hamuul(self):
  self.start_hamuul(['EDR_845']);self.op(('cast_fixed_spell','CORE_EX1_169','random'));self.assertEqual(self.p.hamuul_spells,0)
 def test_hamuul_counter_survives_turn_change(self):
  self.start_hamuul(['EDR_845']);self.play('CORE_EX1_169');self.play('CORE_EX1_169');self.cycle();self.play('CORE_EX1_169');self.assertEqual(self.p.imbue_count,2)
 def test_undead_play_before_power_replacement_uses_first_slot(self):
  cid=next(cid for cid,d in self.g.cards.items() if d['type']=='MINION' and 'UNDEAD' in d.get('races',[]) and cards.RULES.get(cid,('none',[]))[0]=='none' and d['cost']<5)
  self.play(cid);self.p.hero_class='DEATHKNIGHT';self.g._imbue(0,3);self.play(cid);self.assertTrue(all(m.attack==self.g.cards[cid]['attack'] for m in self.p.minions if m.card_id==cid))
 def test_wild_membership_does_not_accept_arbitrary_legendary(self):
  from expanded.generation import request_matches
  catalog={c['id']:c for c in load_catalog()};self.assertEqual(len(WILD_GODS),11);self.assertTrue(all(request_matches(WILD_POOL,catalog[cid],'MAGE') for cid in WILD_GODS));self.assertFalse(request_matches(WILD_POOL,catalog['EDR_888'],'MAGE'))
 def test_hamuul_counter_changes_model_features(self):
  from expanded.features import encode_decision
  self.start_hamuul(['EDR_845']);view=self.g.observe(0);decision=dict(actor=0,observation=view,actions=view['legal_actions']);before=encode_decision(decision);view['players'][0]['hamuul_spells']=2;self.assertNotEqual(before,encode_decision(decision))

 def test_expiry_observation_uses_viewer_relative_turn_owner(self):
  self.g._summon(1,'CORE_EX1_012');self.play('EDR_970')
  for viewer,label in ((0,'self'),(1,'opponent')):
   effects=self.g.observe(viewer)['players'][1]['board'][0]['imbue_attack_expiries'];self.assertEqual(effects[0]['expires_at_turn_of'],label);self.assertNotIn('owner',effects[0])
  self.assertEqual(self.q.minions[0].imbue_attack_expiries[0]['owner'],0)

 def test_internal_finality_imbues_without_paid_play(self):
  self.op(('cast_fixed_spell','END_003','random'));self.assertEqual(self.p.imbue_count,2);self.assertEqual(self.p.cards_played,0)
