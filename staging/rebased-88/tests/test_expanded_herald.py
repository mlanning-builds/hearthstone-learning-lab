"""Candidate Herald timing and six army bodies, not client conformance."""
import gzip,json,unittest
from pathlib import Path
from copy import deepcopy
from unittest.mock import patch
import test_expanded_generation as fixtures
from expanded import cards,locations,Action
from expanded.herald import RULES,DEATH_EFFECTS,END_EFFECTS,LOCATION_RULES,SOLDIERS,ARMIES,ARMY_OF,VALUES,multiplier
from expanded.colossals import LAYOUTS
from expanded.generation_cards import pool
from expanded.pools import GenerationPool
from engine.cards import UnsupportedCard
from engine.game import Card

class HeraldTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with gzip.open(Path(__file__).resolve().parents[1]/'data/standard/all_cards.json.gz','rt') as f:cls.records={c['id']:c for c in json.load(f)}
 def setUp(self):
  self.g=fixtures.GenerationTests().game();self.g._generation_pools={};self.g.players[0].hero_class='WARRIOR'
  ids=set(RULES)|set(ARMY_OF)|set(LAYOUTS)|{'CATA_561t'}
  self.g.cards.update({cid:deepcopy(self.records[cid]) for cid in ids})
  for table,values in ((cards.RULES,RULES),(cards.DEATH_EFFECTS,DEATH_EFFECTS),(cards.END_EFFECTS,END_EFFECTS),(locations.LOCATION_RULES,LOCATION_RULES)):
   context=patch.dict(table,values);context.start();self.addCleanup(context.stop)
 @property
 def p(self):return self.g.players[0]
 @property
 def q(self):return self.g.players[1]
 def op(self,*ops,source=None,owner=0):
  self.g._start_play_effects(ops,dict(owner=owner,source=source,target=0,bonus=0,lifesteal=False));self.g._settle(allow_event_choices=True)
 def play(self,cid,target=0):
  self.p.mana=10;c=Card(self.g._new_id(),cid);self.g._enter_hand(0,c)
  self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid and a.target==target));return c
 def contract(self,request,ids):self.g._generation_pools[(request,self.p.hero_class)]=GenerationPool('fixture',tuple(ids),'Controlled test membership; not reviewed full pool')
 def prep(self,hero):
  self.p.hero_class=hero
  if hero=='ROGUE':self.contract(pool(card_type='SPELL',classes='other'),['CORE_CS2_029'])
  if hero=='DEATHKNIGHT':
   for n in (2,4,8):
    cid='TEST_COST_'+str(n);self.g.cards[cid]=dict(id=cid,name=cid,type='MINION',cardClass='NEUTRAL',cost=n,attack=1,health=1,mechanics=[])
    self.contract(pool(card_type='MINION',minimum=n,maximum=n),[cid])
 def test_all_fifteen_sources_remain_staged(self):
  from expanded.pending_definitions import DEFINITIONS
  from expanded.herald import UNRESOLVED
  pending={cid for cid,d in DEFINITIONS.items() if d['family']=='herald'}
  self.assertEqual(set(RULES)|set(UNRESOLVED),pending);self.assertFalse(set(RULES)&cards.COLLECTIBLE_IDS)
 def test_multiplier_has_two_thresholds_and_caps(self):
  self.assertEqual([multiplier(n) for n in range(8)],[1,1,2,2,4,4,4,4])
  for bad in (-1,True,1.5):
   with self.assertRaises(ValueError):multiplier(bad)
 def test_all_six_armies_use_owner_class(self):
  for hero,cid in SOLDIERS.items():
   with self.subTest(hero=hero):
    self.p.board=[];self.p.hand=[];self.p.herald_count=0;self.prep(hero);self.op(('herald',))
    self.assertEqual(self.p.minions[0].card_id,cid);self.assertEqual(self.p.herald_count,1)
 def test_soldier_snapshots_before_increment(self):
  for _ in range(5):self.op(('herald',))
  self.assertEqual([m.rule_state['herald_multiplier'] for m in self.p.minions],[1,1,2,2,4])
  self.assertEqual([m.attack for m in self.p.minions],[2,2,4,4,8])
 def test_old_soldiers_do_not_retroactively_upgrade(self):
  self.op(('herald',));old=self.p.minions[0];old.health=1
  for _ in range(3):self.op(('herald',))
  self.assertEqual((old.attack,old.health,old.max_health),(2,1,1))
 def test_full_board_still_records_use(self):
  for _ in range(7):self.g._summon(0,'NEW1_034')
  self.op(('herald',));self.assertEqual(self.p.herald_count,1);self.assertEqual(len(self.p.board),7)
 def test_missing_soldier_does_not_increment(self):
  del self.g.cards[SOLDIERS['WARRIOR']]
  with self.assertRaises(UnsupportedCard):self.op(('herald',))
  self.assertEqual(self.p.herald_count,0);self.assertFalse(self.p.board)
 def test_off_class_routing_not_guessed(self):
  self.p.hero_class='MAGE'
  with self.assertRaisesRegex(UnsupportedCard,'Off-class'):self.op(('herald',))
  self.assertEqual(self.p.herald_count,0)
 def test_players_have_independent_counts(self):
  self.q.hero_class='WARRIOR';self.op(('herald',));self.op(('herald',),owner=1)
  self.assertEqual((self.p.herald_count,self.q.herald_count),(1,1))
 def test_ravager_grants_rush_only_to_its_soldier(self):
  self.op(('herald',));self.play('CATA_160')
  self.assertNotIn('RUSH',self.p.minions[0].keywords);self.assertIn('RUSH',self.p.minions[-1].keywords)
 def test_ravager_does_not_grant_rush_when_board_full(self):
  for _ in range(6):self.g._summon(0,'NEW1_034')
  self.play('CATA_160');self.assertEqual(self.p.herald_count,1)
  self.assertNotIn('RUSH',self.p.minions[-1].keywords)
 def test_follower_heralds_on_death_not_play(self):
  self.play('CATA_158');self.assertEqual(self.p.herald_count,0)
  self.p.minions[0].health=0;self.g._settle(allow_event_choices=True);self.assertEqual(self.p.herald_count,1)
 def test_silenced_follower_does_not_herald(self):
  self.play('CATA_158');m=self.p.minions[0];self.g._silence(m);m.health=0;self.g._settle(allow_event_choices=True);self.assertEqual(self.p.herald_count,0)
 def test_weapon_heralds_on_play(self):
  self.play('CATA_580');self.assertEqual(self.p.herald_count,1);self.assertEqual(self.p.weapon['card_id'],'CATA_580')
 def test_location_heralds_only_on_activation(self):
  self.play('CATA_492');self.assertEqual(self.p.herald_count,0);self.assertFalse(self.p.hand)
  self.g.step(next(a for a in self.g.legal_actions() if a.kind=='activate'))
  self.assertEqual(self.p.herald_count,1);self.assertEqual(len(self.p.hand),1);self.assertEqual(self.p.locations[0].durability,1)
 def test_last_location_charge_frees_soldier_slot(self):
  self.play('CATA_492');loc=self.p.locations[0];loc.durability=1
  for _ in range(6):self.g._summon(0,'NEW1_034')
  self.g.step(next(a for a in self.g.legal_actions() if a.kind=='activate'))
  self.assertEqual(len(self.p.board),7);self.assertFalse(self.p.locations);self.assertEqual(self.p.minions[-1].card_id,SOLDIERS['WARRIOR'])
 def test_ritual_adds_two_rush_tokens(self):
  self.play('CATA_561');self.assertEqual([c.card_id for c in self.p.hand],['CATA_561t']*2);self.assertEqual(self.p.herald_count,1)
 def test_disciple_heals_on_death(self):
  self.p.health=10;self.play('CATA_725');body=next(m for m in self.p.minions if m.card_id=='CATA_725');body.health=0;self.g._settle(allow_event_choices=True);self.assertEqual(self.p.health,13)
 def test_warrior_death_uses_snapshot_not_current_count(self):
  self.op(('herald',));m=self.p.minions[0];self.p.herald_count=4;m.health=0
  self.g._settle(allow_event_choices=True);self.assertEqual(self.q.health,28)
 def test_warrior_upgraded_death_does_not_use_spell_damage(self):
  self.p.herald_count=4;m=self.g._summon(0,SOLDIERS['WARRIOR']);m.health=0
  self.g._settle(allow_event_choices=True);self.assertEqual(self.q.health,22)
 def test_dh_soldier_attack_upgrade(self):
  self.prep('DEMONHUNTER');self.p.herald_count=2;self.op(('herald',));self.assertEqual(self.p.temporary_attack,2)
 def test_dh_appendage_effect_on_summon_not_transform(self):
  self.prep('DEMONHUNTER');old=self.g._summon(0,'NEW1_034');self.g._transform(old,'CATA_151t');self.g._settle(allow_event_choices=True)
  self.assertEqual(self.p.temporary_attack,0)
  self.g._summon(0,'CATA_151t');self.g._settle(allow_event_choices=True);self.assertEqual(self.p.temporary_attack,1)
 def test_fel_infusion_lifesteal_hero_attack(self):
  self.prep('DEMONHUNTER');self.p.health=10;self.play('CATA_530')
  self.g.step(next(a for a in self.g.legal_actions() if a.kind=='attack' and a.source==-1 and a.target==-2));self.assertEqual(self.p.health,11)
  self.g.turn+=1;self.assertFalse(self.g.observe(0)['players'][0]['hero_lifesteal'])
 def test_rogue_generates_one_spell_with_scaled_discount(self):
  self.prep('ROGUE');self.p.herald_count=4;self.op(('herald',))
  self.assertEqual(len(self.p.hand),1);self.assertEqual(self.p.hand[0].cost_delta,-4)
 def test_missing_generation_pool_rolls_back_play(self):
  self.p.hero_class='ROGUE';c=Card(self.g._new_id(),'CATA_722');self.g._enter_hand(0,c);state=(self.p.mana,self.g.rng.getstate())
  with self.assertRaises(UnsupportedCard):self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid))
  self.assertEqual((self.p.mana,self.g.rng.getstate()),state);self.assertEqual(self.p.herald_count,0);self.assertFalse(self.p.board)
 def test_dk_generates_exact_cost_health_payment(self):
  self.prep('DEATHKNIGHT');self.p.herald_count=2;self.op(('herald',))
  c=self.p.hand[0];self.assertEqual(c.card_id,'TEST_COST_4');self.assertTrue(c.rule_state['health_payment']);self.assertEqual(c.rule_state['health_payment_until'],self.g.turn)
 def test_shaman_aura_is_adjacent_and_scaled(self):
  self.prep('SHAMAN');left=self.g._summon(0,'NEW1_034');self.p.herald_count=2;self.op(('herald',));right=self.g._summon(0,'NEW1_034');far=self.g._summon(0,'NEW1_034')
  self.assertEqual((left.aura_attack,right.aura_attack,far.aura_attack),(2,2,0))
  self.g._silence(self.p.minions[1]);self.assertEqual((left.aura_attack,right.aura_attack),(0,0))
 def test_warlock_consumes_right_and_buffs_snapshot_amount(self):
  self.prep('WARLOCK');self.p.herald_count=2;self.op(('herald',));source=self.p.minions[0];victim=self.g._summon(0,'NEW1_034')
  self.op(('herald_consume_right',),source=source)
  self.assertNotIn(victim,self.p.board);self.assertEqual((source.attack,source.max_health),(6,6))
 def test_warlock_does_not_eat_a_location(self):
  self.prep('WARLOCK');self.op(('herald',));source=self.p.minions[0];loc=self.g._place_location(0,'CATA_492');self.op(('herald_consume_right',),source=source)
  self.assertIn(loc,self.p.board);self.assertEqual(source.attack,1)
 def test_warlock_end_turn_runs_through_scheduler(self):
  self.prep('WARLOCK');self.op(('herald',));source=self.p.minions[0];victim=self.g._summon(0,'NEW1_034');self.g._end_turn()
  self.assertNotIn(victim,self.p.board);self.assertEqual(source.attack,3)
 def test_chogall_replacement_does_not_silently_eat_friendly(self):
  self.prep('WARLOCK');source=self.g._summon(0,SOLDIERS['WARLOCK']);self.g._summon(0,'NEW1_034');self.g._summon(0,'CATA_726')
  self.g.players[1].deck=[];self.op(('herald_consume_right',),source=source)
  self.assertEqual(len(self.p.minions),5);self.assertEqual(source.attack,1)
 def test_colossal_scales_limbs_not_main_body(self):
  self.p.herald_count=4;body=self.g._summon(0,'CATA_150')
  self.assertEqual(body.attack,self.records['CATA_150']['attack'])
  for m in self.p.minions:
   if m is not body:self.assertEqual(m.attack,self.records[m.card_id]['attack']*4)
 def test_copy_keeps_army_snapshot_without_double_scaling(self):
  self.p.herald_count=2;m=self.g._summon(0,SOLDIERS['WARRIOR']);self.p.herald_count=4;copy=self.g._summon(0,m.card_id,copy_from=m)
  self.assertEqual((copy.attack,copy.rule_state['herald_multiplier']),(4,2))
 def test_transform_takes_current_army_level(self):
  m=self.g._summon(0,'NEW1_034');self.p.herald_count=4;new=self.g._transform(m,SOLDIERS['WARRIOR']);self.assertEqual(new.attack,8)
 def test_counter_visible_to_both_players(self):
  self.op(('herald',))
  for viewer in (0,1):self.assertEqual(self.g.observe(viewer)['players'][0]['herald_count'],1)
 def test_animation_damage_hits_enemies_after_herald(self):
  target=self.g._summon(1,'NEW1_034');self.play('CATA_156')
  self.assertNotIn(target,self.q.board);self.assertEqual(self.p.herald_count,1);self.assertEqual(len(self.p.minions),1)
 def test_rite_without_combo_does_not_need_target(self):
  self.play('CATA_785');self.assertEqual(self.q.health,30);self.assertEqual(self.p.herald_count,1)
 def test_rite_combo_deals_damage(self):
  self.p.cards_played=1;self.play('CATA_785',target=-2);self.assertEqual(self.q.health,27)
 def test_copied_colossal_replacement_creates_fresh_limbs(self):
  model=self.g._summon(0,'CATA_150');target=self.g._summon(1,'NEW1_034')
  self.g._entity_choice(dict(kind='entity_tribute',target_uid=target.uid),dict(uid=model.uid))
  self.assertNotIn(target,self.q.board);self.assertEqual([m.card_id for m in self.q.board],['CATA_150t','CATA_150','CATA_150t1'])
  replacement=self.q.board[1]
  self.assertTrue(all(m.rule_state['colossal_parent']==replacement.uid for m in (self.q.board[0],self.q.board[2])))
 def test_copied_replacement_missing_limb_keeps_target(self):
  model=self.g._summon(0,'CATA_150');target=self.g._summon(1,'NEW1_034');del self.g.cards['CATA_150t1']
  with self.assertRaises(UnsupportedCard):self.g._entity_choice(dict(kind='entity_tribute',target_uid=target.uid),dict(uid=model.uid))
  self.assertEqual(self.q.board,[target])
 def test_full_board_no_dh_on_summon_attack(self):
  self.prep('DEMONHUNTER')
  for _ in range(7):self.g._summon(0,'NEW1_034')
  self.op(('herald',));self.assertEqual(self.p.temporary_attack,0);self.assertEqual(self.p.herald_count,1)
 def test_internal_herald_spell_has_no_paid_spell_history(self):
  self.op(('cast_fixed_spell','CATA_561','random'))
  self.assertEqual(self.p.herald_count,1);self.assertEqual(len(self.p.hand),2);self.assertFalse(self.p.spells_turn)
