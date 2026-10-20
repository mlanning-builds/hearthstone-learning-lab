"""Focused historical Mage outcome behavior, without training."""
from copy import deepcopy
import unittest
from expanded import Game,Action,random_deck
from expanded.cards import RULES,DAMAGE_FREEZERS
from expanded.generation_cards import pool

class HistoricalMagePoolTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  g=Game([random_deck('MAGE',31),random_deck('MAGE',53)],seed=71,record=True)
  g.step(Action('mulligan'));g.step(Action('mulligan'))
  for p in g.players:
   p.hand=[];p.board=[];p.deck=[];p.mana=p.max_mana=10;p.health=30;p.armor=0
  cls.prototype=g
 def game(self):return deepcopy(self.prototype)
 def play(self,g,cid,target=0):
  c=g._add(0,cid)
  action=next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid and a.target==target)
  g.step(action)
 def test_snowman_chain_and_freeze(self):
  g=self.game()
  for spell,body,stats,next_spell in (('AV_282','AV_282t',3,'AV_282t2'),('AV_282t2','AV_282t3',6,'AV_282t4'),('AV_282t4','AV_282t5',9,None)):
   g.players[0].mana=10;self.play(g,spell)
   m=g.players[0].minions[-1]
   self.assertEqual((m.card_id,m.attack,m.health),(body,stats,stats))
   self.assertIn(body,DAMAGE_FREEZERS)
   if next_spell:self.assertIn(next_spell,[c.card_id for c in g.players[0].hand])
  m=g.players[0].minions[-1]
  g._deal_effect(g.hero_id(1),1,dict(owner=0,source=m,spell=False,bonus=0))
  self.assertGreaterEqual(g.players[1].frozen_until,0)
 def test_ray_freezes_then_damages_and_only_original_creates_copy(self):
  g=self.game();m=g._summon(1,'CS2_182');health=m.health
  self.play(g,'DAL_577',m.uid);self.assertEqual(m.health,health)
  self.assertGreaterEqual(m.frozen_until,0)
  self.assertEqual([c.card_id for c in g.players[0].hand],['DAL_577ts'])
  c=g.players[0].hand[0]
  g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid and a.target==m.uid))
  self.assertEqual(m.health,health-2);self.assertEqual(g.players[0].hand,[])
 def test_supernova_fills_only_available_slots_with_one_cost_fire(self):
  g=self.game();g._add(0,'CORE_CS2_029')
  self.play(g,'GDB_301')
  self.assertEqual(len(g.players[0].hand),10)
  for c in g.players[0].hand[1:]:
   self.assertIn('FIRE',str(g._card_data(c).get('spellSchool','')))
   self.assertEqual(g._cost(c,0),1)
 def test_huddle_respects_existing_board_and_full_pool(self):
  g=self.game();m=g._summon(0,'CS2_182');self.play(g,'WORK_012')
  self.assertEqual(len(g.players[0].board),7);self.assertIs(g.players[0].minions[0],m)
  from expanded.selectors import has_tribe
  self.assertTrue(all(has_tribe(g._card_data(n),'NAGA') for n in g.players[0].minions[1:]))
 def test_puzzle_box_uses_ten_native_random_casts(self):
  self.assertEqual(RULES['ULD_216'],('none',[('autocast_random',pool(card_type='SPELL'),10)]))

 def test_conditional_costs_use_live_state(self):
  g=self.game()
  dragon=g._add(0,'BRM_003');g.players[0].minions_died_turn=2;g.players[1].minions_died_turn=1
  self.assertEqual(g._cost(dragon,0),2)
  scorch=g._add(0,'TRL_313');self.assertEqual(g._cost(scorch,0),4)
  g.players[0].previous_tribes={'ELEMENTAL'};self.assertEqual(g._cost(scorch,0),1)
  flare=g._add(0,'GDB_305');base=g._cost(flare,0)
  g._summon(0,'CS2_033');self.assertEqual(g._cost(flare,0),base-1)
 def test_flow_distinguishes_owner(self):
  g=self.game();friendly=g._summon(0,'CS2_182');enemy=g._summon(1,'CS2_182')
  before=g._spell_damage(0);self.play(g,'VAC_428',friendly.uid)
  self.assertEqual(g._spell_damage(0),before+1)
  self.assertLess(friendly.frozen_until,0)
  self.play(g,'VAC_428',enemy.uid);self.assertGreaterEqual(enemy.frozen_until,0)
 def test_waves_second_damage_only_when_no_death(self):
  g=self.game();m=g._summon(1,'CS2_182');self.play(g,'VAC_953')
  self.assertEqual(m.health,1)
  g=self.game();m=g._summon(1,'CS2_182');g._summon(1,'CS2_231');self.play(g,'VAC_953')
  self.assertEqual(m.health,3)
 def test_mirror_entity_copies_live_buffs(self):
  g=self.game();m=g._summon(0,'CS2_182');g._buff(m,2,3)
  g._place_secret(1,'EX1_294');g._secret_event('after_card',0,source=m.uid,card_id=m.card_id)
  copy=g.players[1].minions[0]
  self.assertEqual((copy.attack,copy.health),(m.attack,m.health));self.assertEqual(g.players[1].secrets,[])
 def test_frozen_clone_resets_board_enchantments(self):
  g=self.game();m=g._summon(0,'CS2_182');g._buff(m,2,3)
  g._place_secret(1,'ICC_082');g._secret_event('after_card',0,source=m.uid,card_id=m.card_id)
  self.assertEqual(len(g.players[1].hand),2)
  for c in g.players[1].hand:self.assertEqual(g._card_stat(c,'attack',1),4)
 def test_vaporize_cancels_only_minion_attack_on_hero(self):
  g=self.game();m=g._summon(0,'CS2_182');g._place_secret(1,'EX1_594')
  self.assertTrue(g._secret_event('attack',0,source=m.uid,target=g.hero_id(1)))
  self.assertNotIn(m,g.players[0].board);self.assertEqual(g.players[1].health,30)
 def test_splitting_image_copies_attacked_minion(self):
  g=self.game();m=g._summon(1,'CS2_182');g._place_secret(1,'TRL_400')
  g._secret_event('attack',0,source=g.hero_id(0),target=m.uid)
  self.assertEqual(len(g.players[1].minions),2)
 def test_flame_ward_hits_only_attacking_side(self):
  g=self.game();a=g._summon(0,'CS2_182');b=g._summon(1,'CS2_182');g._place_secret(1,'ULD_239')
  a.summoned_turn=-1
  g.step(Action('attack',a.uid,g.hero_id(1)))
  self.assertEqual((a.health,b.health),(2,5))
  self.assertEqual(g.players[1].health,26)
  self.assertEqual(g.players[1].secrets,[])
 def test_portal_requires_space_and_summons_four_cost(self):
  g=self.game();g._place_secret(1,'BT_003');g._secret_event('after_spell',0)
  self.assertEqual(len(g.players[1].minions),1)
  self.assertEqual(g._card_stat(g.players[1].minions[0],'cost',1),4)
 def test_rigged_uses_opponents_turn_damage(self):
  from expanded.historical_secret_events import turn_entries
  for damaged in (False,True):
   g=self.game();s=g._place_secret(1,'DMF_107');g.players[1].deck=['CORE_CS2_029']*3
   if damaged:g.players[1].historical_opponent_turn_damage=dict(turn=g.turn,amount=1)
   entries=turn_entries(g,'end');self.assertEqual(len(entries),1)
   for op in entries[0]['operations']:g._effect(op,dict(owner=0,source=None,target=0,bonus=0))
   self.assertEqual(len(g.players[1].hand),0 if damaged else 3)
   self.assertEqual(s in g.players[1].secrets,damaged)

 def test_ruby_upgrade_only_while_held(self):
  from expanded.historical_lingering_spells import event
  g=self.game();c=g._add(0,'LOOT_103')
  for expected in ('LOOT_103','LOOT_103t1','LOOT_103t1','LOOT_103t2'):
   m=g._summon(0,'CS2_033');event(g,'minion_played',dict(owner=0,source=m.uid,card_id=m.card_id))
   self.assertEqual(c.card_id,expected)
  self.assertEqual(g.players[0].historical_elementals_played,4)
 def test_grand_finale_counts_each_previous_elemental(self):
  g=self.game();g.players[0].historical_elementals_previous=2;self.play(g,'DMF_104')
  self.assertEqual([m.card_id for m in g.players[0].minions],['DMF_104t']*3)
  self.assertTrue(all((m.attack,m.health)==(8,8) for m in g.players[0].minions))
 def test_deck_of_wonders_inserts_five_physical_scrolls(self):
  from expanded.on_draw_cards import CAST_EFFECTS
  g=self.game();self.play(g,'LOOT_106')
  self.assertEqual(len(g.players[0].deck),5)
  self.assertEqual([g._card_data(c)['id'] for c in g.players[0].deck],['LOOT_106t']*5)
  self.assertEqual(CAST_EFFECTS['LOOT_106t'],(('autocast_random',pool(card_type='SPELL'),1),))

 def test_wildfire_stacks_and_affects_power_damage(self):
  g=self.game();self.play(g,'BAR_546');self.play(g,'BAR_546')
  self.assertEqual(g.players[0].historical_permanent_power_damage,2)
  g.step(next(a for a in g.legal_actions() if a.kind=='power' and a.target==g.hero_id(1)))
  self.assertEqual(g.players[1].health,27)
 def test_siphon_only_exact_kill_discounts_spells(self):
  for health,discount in ((1,0),(2,1),(3,0)):
   g=self.game();m=g._summon(1,'CS2_182');m.health=health
   spell=g._add(0,'CORE_CS2_029');base=g._cost(spell,0)
   self.play(g,'AV_212',m.uid)
   self.assertEqual(g._cost(spell,0),base-discount)
 def test_blast_wave_counts_each_overkill_not_exact_kill(self):
  g=self.game()
  for health in (1,1,2,5):
   m=g._summon(1,'CS2_182');m.health=health
  self.play(g,'TRL_317');self.assertEqual(len(g.players[0].hand),2)
  self.assertTrue(all('MAGE' in g._card_data(c).get('cardClass','') for c in g.players[0].hand))

 def test_results_spell_damage_changes_summon_cost(self):
  g=self.game();m=g._summon(0,'CS2_182');m.rule_state['historical_spell_damage']=1
  self.play(g,'BOT_254');self.assertEqual(len(g.players[0].minions),3)
  self.assertEqual([g._card_stat(n,'cost',0) for n in g.players[0].minions[1:]],[3,3])
 def test_conjurer_summons_for_targets_controller(self):
  g=self.game();m=g._summon(1,'CS2_182');cost=g._card_stat(m,'cost',1)
  self.play(g,'DAL_177',m.uid)
  self.assertEqual(len(g.players[1].minions),2)
  self.assertTrue(all(g._card_stat(n,'cost',1)==cost for n in g.players[1].minions))
  self.assertEqual([c.card_id for c in g.players[0].hand],['DAL_177ts'])
 def test_drakefire_has_two_separate_discover_checkpoints(self):
  g=self.game();self.play(g,'ONY_029')
  self.assertIsNotNone(g.pending_choice)
  g.step(next(a for a in g.legal_actions() if a.kind=='choose'))
  self.assertEqual(len(g.players[0].minions),1);self.assertIsNotNone(g.pending_choice)
  g.step(next(a for a in g.legal_actions() if a.kind=='choose'))
  self.assertEqual(len(g.players[0].minions),2);self.assertIsNone(g.pending_choice)

 def test_spellbender_redirects_player_target(self):
  g=self.game();m=g._summon(0,'CS2_182');g._place_secret(1,'tt_010')
  self.play(g,'CORE_CS2_024',m.uid)
  self.assertEqual(m.health,5);self.assertEqual(g.players[1].secrets,[])
  self.assertEqual(g.players[1].minions,[])
 def test_spellbender_redirects_friendly_buff_without_target_recheck(self):
  g=self.game();m=g._summon(0,'CS2_182');g._place_secret(1,'tt_010')
  from expanded.historical_secret_events import redirect_spellbender
  uid=redirect_spellbender(g,0,m.uid);bender=g._force_live(uid)
  self.assertEqual((bender.card_id,bender.owner),('tt_010a',1))
 def test_duplicate_copies_dead_minion_plain(self):
  g=self.game();m=g._summon(1,'CS2_182');g._buff(m,2,3);g._place_secret(1,'FP1_018')
  g._deal_effect(m.uid,20,dict(owner=0,source=None,bonus=0,spell=False));g._settle()
  self.assertEqual([c.card_id for c in g.players[1].hand],['CS2_182']*2)
  self.assertTrue(all(g._card_stat(c,'attack',1)==4 for c in g.players[1].hand))
 def test_effigy_uses_dead_minions_cost(self):
  g=self.game();m=g._summon(1,'CS2_182');g._place_secret(1,'AT_002')
  cost=g._card_stat(m,'cost',1)
  g._deal_effect(m.uid,20,dict(owner=0,source=None,bonus=0,spell=False));g._settle()
  self.assertEqual(len(g.players[1].minions),1)
  self.assertEqual(g._card_stat(g.players[1].minions[0],'cost',1),cost)

 def test_ignite_shuffles_physical_increasing_base_damage(self):
  g=self.game();self.play(g,'SW_110',g.hero_id(1));self.assertEqual(g.players[1].health,28)
  c=g.players[0].deck.pop();g._enter_hand(0,c)
  g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid and a.target==g.hero_id(1)))
  self.assertEqual(g.players[1].health,25)
  self.assertEqual(g.players[0].deck[0].rule_state['historical_ignite_damage'],4)
 def test_spontaneous_combustion_target_is_conditional(self):
  g=self.game();self.play(g,'GDB_456');self.assertEqual(g.players[1].health,26)
  g=self.game();g.players[0].previous_tribes={'ELEMENTAL'}
  self.play(g,'GDB_456',g.hero_id(1));self.assertEqual(g.players[1].health,26)
 def test_tsunami_summons_then_forces_three_freezing_attacks(self):
  g=self.game();self.play(g,'VAC_509')
  self.assertEqual(len(g.players[0].minions),3);self.assertEqual(g.players[1].health,21)
  self.assertGreaterEqual(g.players[1].frozen_until,0)

 def test_creation_one_discover_summons_two_same_six_cost(self):
  g=self.game();self.play(g,'DAL_578')
  cid=g.pending_choice['options'][0]['card_id']
  g.step(next(a for a in g.legal_actions() if a.kind=='choose'))
  self.assertEqual([m.card_id for m in g.players[0].minions],[cid,cid])
  self.assertEqual(g.players[0].discoveries_this_turn,1)
 def test_ring_toss_corrupted_two_secrets_and_class_fallback(self):
  g=self.game();g.players[0].hero_class='DRUID';self.play(g,'DMF_105t')
  self.assertIsNotNone(g.pending_choice)
  g.step(next(a for a in g.legal_actions() if a.kind=='choose'))
  self.assertIsNotNone(g.pending_choice)
  actions=g.legal_actions();options=g.pending_choice['options'];existing={s.card_id for s in g.players[0].secrets}
  index=next((i for i,o in enumerate(options) if o['card_id'] not in existing),0)
  g.step(next(a for a in actions if a.kind=='choose' and a.choices==(index,)))
  self.assertEqual(len(g.players[0].secrets),2)
 def test_glacial_mysteries_puts_distinct_secrets_without_casting(self):
  g=self.game();g.players[0].deck=['EX1_294','EX1_294','EX1_594','CORE_CS2_029']
  self.play(g,'ICC_086')
  self.assertEqual({c.card_id for c in g.players[0].secrets},{'EX1_294','EX1_594'})
  self.assertEqual(len(g.players[0].deck),2)

 def test_combustion_excess_ignores_shield_absorption(self):
  g=self.game();left=g._summon(1,'CS2_182');center=g._summon(1,'CS2_182');right=g._summon(1,'CS2_182')
  center.health=1;center.keywords.add('DIVINE_SHIELD')
  self.play(g,'SCH_348',center.uid)
  self.assertEqual((left.health,center.health,right.health),(2,1,2))
 def test_rolling_edge_rolls_inwards_and_uses_health_budget(self):
  g=self.game();a=g._summon(1,'CS2_182');b=g._summon(1,'CS2_182');c=g._summon(1,'CS2_182')
  a.health=1;a.keywords.add('DIVINE_SHIELD');b.health=2
  self.play(g,'DRG_321',a.uid)
  self.assertEqual(a.health,1);self.assertNotIn(b,g.players[1].board);self.assertNotIn(c,g.players[1].board)
 def test_rolling_dormant_neighbor_blocks_further_hits(self):
  g=self.game();a=g._summon(1,'CS2_231');b=g._summon(1,'CS2_182');c=g._summon(1,'CS2_182')
  g._sleep_minion(b,2);self.play(g,'DRG_321',a.uid)
  self.assertEqual(c.health,5)
 def test_arcane_overflow_summons_excess_sized_remnant(self):
  g=self.game();m=g._summon(1,'CS2_182');m.health=3;self.play(g,'DED_517',m.uid)
  body=g.players[0].minions[0];self.assertEqual((body.card_id,body.attack,body.health),('DED_517t',5,5))

 def test_disco_full_historical_pool_rejects_missing_dependencies_before_rng(self):
  from expanded.historical_generation_catalog import historical_contract,load_universe
  from engine.cards import UnsupportedCard
  request=pool(era='past',card_type='SPELL',mechanic='SECRET')
  contract=historical_contract(request,'MAGE',load_universe())
  self.assertEqual(len(contract.card_ids),64)
  g=self.game();self.assertFalse(set(contract.card_ids)-g.cards.keys())
  # Keep the rejection contract tested after closing the historical pool:
  # remove one actual eligible implementation from this isolated game.
  missing_id='AT_002';self.assertIn(missing_id,contract.card_ids)
  del g.cards[missing_id]
  self.assertEqual(set(contract.card_ids)-g.cards.keys(),{missing_id})
  before=g.rng.getstate()
  with self.assertRaisesRegex(UnsupportedCard,'eligible effects not implemented'):self.play(g,'WON_040')
  self.assertEqual(g.rng.getstate(),before);self.assertEqual(g.players[0].secrets,[])
