"""Behavioral witnesses for source-audit repairs; no training."""
import unittest
from copy import deepcopy
import test_expanded_generation as fixtures
from engine.game import Card
from expanded import cards
from expanded.historical_choose_splits import SPLIT_BRANCHES
from expanded.historical_copy_batches import choose_branch_cards
from expanded import gelbin

class AuditRepairTests(unittest.TestCase):
 def setUp(self):
  self.g=fixtures.GenerationTests().game()
  self.p,self.q=self.g.players
 def run_ops(self,ops,**kw):
  ctx=dict(owner=0,source=None,target=0,bonus=0,lifesteal=False)
  ctx.update(kw)
  self.g._start_play_effects(ops,ctx)
  self.g._settle(allow_event_choices=True)
 def test_passive_cost_aura_keeps_kalecgos_discover(self):
  self.run_ops(cards.RULES['DAL_609'][1],card_id='DAL_609')
  self.assertIsNotNone(self.g.pending_choice)
  self.assertEqual(len(self.g.pending_choice['options']),3)
 def test_popgar_battlecry_adds_two_sludges(self):
  self.run_ops(cards.RULES['WW_091'][1],card_id='WW_091')
  self.assertEqual([c.card_id for c in self.p.hand],['WW_044t','WW_044t'])
 def test_all_split_families_produce_physical_executable_branches(self):
  for cid,pair in SPLIT_BRANCHES.items():
   with self.subTest(cid=cid):
    parent=Card(self.g._new_id(),cid)
    parent.cost_delta=-1
    children=choose_branch_cards(self.g,0,parent)
    self.assertEqual(tuple(c.card_id for c in children),pair)
    self.assertEqual(len({c.uid for c in children}),2)
    for i,child in enumerate(children):
     self.assertEqual(child.cost_delta,-1)
     effects=cards.CHOICES[cid][i][2]
     if cid=='YOD_001':effects=[op for op in effects if op!=('add','YOD_001ts',1)]
     self.assertEqual(cards.RULES[child.card_id],(cards.CHOICES[cid][i][1],effects))
 def test_reversed_suffix_wrath_and_panther_execute_correct_branch(self):
  for cid,index,token in [('EX1_160',1,'EX1_160a'),('SW_422',1,'SW_422a')]:
   with self.subTest(cid=cid):
    child=choose_branch_cards(self.g,0,Card(self.g._new_id(),cid))[index]
    self.assertEqual(child.card_id,token)
    before=len(self.p.minions)
    self.run_ops(cards.RULES[token][1],card_id=token)
    self.assertEqual(len(self.p.minions),before+1)
 def test_new_aura_placement_bypasses_paid_cast_and_repeat(self):
  self.p.deck=[Card(self.g._new_id(),cid) for cid in ('WW_341','TTN_854','TOY_808','TTN_908')]
  self.p.spell_repeat_charges=2
  self.run_ops([('gelbin_auras',)])
  self.assertFalse(self.p.deck)
  self.assertEqual(self.p.spell_repeat_charges,2)
  self.assertFalse(self.p.spells_turn)
  self.assertEqual(len(self.p.historical_deputization_auras),1)
  self.assertEqual(len(self.p.historical_inventor_auras),1)
  self.assertEqual(len(self.p.historical_finish_auras),1)
  self.assertEqual(len(self.p.scheduled_effects),1)

 def test_historical_automatic_spell_frames_execute(self):
  for cid in ['AV_342', 'BOT_257', 'BOT_600', 'BT_740', 'CS2_046', 'CS2_073', 'CS2_114', 'DAL_010', 'DAL_071', 'DMF_058', 'DRG_301', 'DS1_183', 'EX1_126', 'EX1_158', 'EX1_251', 'EX1_339', 'EX1_392', 'EX1_537', 'EX1_544', 'EX1_578', 'EX1_581', 'GVG_015', 'LOOT_504', 'RLK_843', 'ULD_160', 'ULD_256', 'UNG_103', 'UNG_832', 'UNG_961', 'YOD_020']:
   with self.subTest(cid=cid):
    self.g=fixtures.GenerationTests().game()
    self.p,self.q=self.g.players
    self.g._summon(0,'CORE_EX1_162')
    self.g._summon(1,'CORE_EX1_162')
    self.assertTrue(self.g._supports_internal_spell(cid,0))
    self.run_ops([('cast_fixed_spell',cid,'random')])
    self.assertIsNone(self.g.pending_choice)

 def test_front_reduces_multiple_minions_with_floor_and_expires(self):
  self.run_ops(cards.RULES['AV_119'][1],card_id='AV_119')
  a=self.g._add(0,'CORE_EX1_162');b=self.g._add(0,'CORE_EX1_162')
  self.assertEqual(self.g._cost(a,0),1)
  from expanded.historical_play_batches import consume_discounts
  consume_discounts(self.g,0,a)
  self.assertEqual(self.g._cost(b,0),1)
  self.g.step(__import__('expanded',fromlist=['Action']).Action('end'))
  self.assertFalse(any(e.get('minimum')==1 for e in self.p.cost_effects))
 def test_roll_bones_draws_through_deathrattle_then_stops(self):
  self.p.deck=[Card(self.g._new_id(),'CORE_CS2_029'),Card(self.g._new_id(),'EX1_029')]
  self.run_ops(cards.RULES['ICC_201'][1],card_id='ICC_201')
  self.assertEqual([c.card_id for c in self.p.hand],['EX1_029','CORE_CS2_029'])
  self.assertFalse(self.p.deck)
 def test_roll_bones_stops_on_fatigue_without_infinite_repeat(self):
  self.p.deck=[];before=self.p.health
  self.run_ops(cards.RULES['ICC_201'][1],card_id='ICC_201')
  self.assertEqual(self.p.health,before-1)
 def test_skirt_steals_only_available_attack_and_restores_at_end(self):
  m=self.g._summon(1,'CORE_EX1_162');original=m.attack
  self.run_ops(cards.RULES['VAC_931'][1],card_id='VAC_931',target=m.uid)
  self.assertEqual(m.attack,0)
  self.assertEqual(self.g._hero_attack(0),original)
  self.g.step(__import__('expanded',fromlist=['Action']).Action('end'))
  self.assertEqual(m.attack,original)
  self.assertEqual(self.g._hero_attack(0),0)
 def test_all_you_can_eat_finds_three_distinct_types(self):
  self.p.deck=[Card(self.g._new_id(),cid) for cid in ('CORE_EX1_162','EX1_319','CS2_050','CORE_CS2_029')]
  self.run_ops(cards.RULES['VAC_528'][1],card_id='VAC_528')
  self.assertEqual(len(self.p.hand),3)
  self.assertTrue(all(self.g._card_data(c)['type']=='MINION' for c in self.p.hand))

 def test_silvermoon_immune_expires_but_stats_remain(self):
  m=self.g._summon(0,'CORE_EX1_162');a,h=m.attack,m.max_health
  self.run_ops(cards.RULES['WORK_017'][1],target=m.uid,card_id='WORK_017')
  self.assertEqual((m.attack,m.max_health),(a+2,h+2))
  self.assertEqual(self.g._damage(m.uid,1),0)
  self.g.step(__import__('expanded',fromlist=['Action']).Action('end'))
  self.assertNotIn('IMMUNE',self.g._effective_keywords(m))
  self.assertEqual((m.attack,m.max_health),(a+2,h+2))
 def test_brochure_flips_preserve_physical_cost_enchantment(self):
  from expanded.historical_harmonics import execute,turn_entries
  for cid in ('WORK_017','WORK_030'):
   c=self.g._add(0,cid);c.cost_delta=-1;uid=c.uid
   entries=turn_entries(self.g,'end');e=next(e for e in entries if e['order']==uid)
   execute(self.g,e['operations'][0],dict(owner=0))
   self.assertEqual((c.uid,c.card_id,c.cost_delta),(uid,cid+'t',-1))
 def test_icecrown_freezes_original_neighbors_when_target_dies(self):
  a=self.g._summon(1,'CORE_EX1_162');b=self.g._summon(1,'CORE_EX1_162');c=self.g._summon(1,'CORE_EX1_162')
  self.run_ops(cards.RULES['WORK_030'][1],target=b.uid,card_id='WORK_030')
  self.assertNotIn(b,self.q.minions)
  self.assertGreaterEqual(a.frozen_until,0);self.assertGreaterEqual(c.frozen_until,0)
 def test_blackrock_damage_applies_bonus_to_each_victim(self):
  a=self.g._summon(1,'CORE_EX1_162');b=self.g._summon(1,'CORE_EX1_162');c=self.g._summon(1,'CORE_EX1_162')
  for m in (a,b,c):self.g._buff(m,0,8)
  before=[m.health for m in (a,b,c)]
  self.run_ops(cards.RULES['WORK_030t'][1],target=b.uid,card_id='WORK_030t',spell=True,bonus=1)
  self.assertEqual([m.health for m in (a,b,c)],[before[0]-2,before[1]-4,before[2]-2])

 def test_rising_winds_split_draw_does_not_grant_parent_twinspell(self):
  self.p.deck=[Card(self.g._new_id(),'CORE_CS2_029')]
  child=choose_branch_cards(self.g,0,Card(self.g._new_id(),'YOD_001'))[0]
  self.run_ops(cards.RULES[child.card_id][1],card_id=child.card_id)
  self.assertEqual([c.card_id for c in self.p.hand],['CORE_CS2_029'])

 def test_each_historical_aura_placement_activates_aura_conditions(self):
  for cid in ('WW_341','TTN_854','TOY_808','TTN_908'):
   with self.subTest(cid=cid):
    self.g=fixtures.GenerationTests().game();self.p,self.q=self.g.players
    self.p.deck=[Card(self.g._new_id(),cid)]
    self.assertFalse(self.g._batch30_state('aura_active',0))
    self.run_ops([('gelbin_auras',)])
    self.assertTrue(self.g._batch30_state('aura_active',0))

 def test_birdwatching_draws_selected_and_buffs_all_friendly_copies(self):
  from expanded import Action
  cid='CORE_EX1_162'
  self.p.deck=[Card(self.g._new_id(),cid),Card(self.g._new_id(),cid)]
  held=Card(self.g._new_id(),cid);self.p.hand=[held]
  minion=self.g._summon(0,cid)
  enemy=self.g._summon(1,cid)
  before=(minion.attack,minion.max_health,enemy.attack,enemy.max_health)
  self.run_ops(cards.RULES['VAC_408'][1],card_id='VAC_408')
  self.assertEqual(len(self.g.pending_choice['options']),1)
  self.g.step(Action('choose',choices=(0,)))
  self.assertEqual(len(self.p.deck),1)
  self.assertEqual(len(self.p.hand),2)
  for card in self.p.deck+self.p.hand:
   self.assertEqual((card.attack_bonus,card.health_bonus),(2,1))
  self.assertEqual((minion.attack,minion.max_health),(before[0]+2,before[1]+1))
  self.assertEqual((enemy.attack,enemy.max_health),before[2:])

 def test_jade_telegram_keeps_duplicate_physical_offers_and_resumes(self):
  from expanded import Action
  self.q.hand=[Card(self.g._new_id(),'CORE_CS2_029') for _ in range(3)]
  originals={c.uid for c in self.q.hand}
  self.run_ops(cards.RULES['WON_078'][1],card_id='WON_078')
  choice=self.g.pending_choice
  self.assertEqual(len(choice['options']),3)
  selected=self.q.hand[choice['options'][0]['index']]
  self.assertEqual(len(self.p.minions),0)
  self.g.step(Action('choose',choices=(0,)))
  self.assertEqual(len(self.q.hand),2)
  self.assertIn(selected,self.q.deck)
  self.assertEqual({c.uid for c in self.q.hand}|{selected.uid},originals)
  self.assertEqual(len(self.p.minions),1)
  self.assertEqual((self.p.minions[0].attack,self.p.minions[0].health),(1,1))

 def test_doomerang_uses_weapon_damage_and_returns_reset_weapon(self):
  self.run_ops([('equip','EX1_398t')])
  self.p.weapon['attack']=4
  self.p.weapon['durability']=1
  self.p.equipped_card.attack_bonus=3
  target=self.g._summon(1,'CORE_EX1_162')
  self.g._buff(target,0,10)
  before=target.health
  self.run_ops(cards.RULES['ICC_233'][1],card_id='ICC_233',target=target.uid,spell=True,bonus=7)
  self.assertEqual(target.health,before-4)
  self.assertIsNone(self.p.weapon)
  self.assertIsNone(self.p.equipped_card)
  self.assertEqual(len(self.p.hand),1)
  self.assertEqual(self.p.hand[0].card_id,'EX1_398t')
  self.assertEqual(self.p.hand[0].attack_bonus,0)
  self.assertFalse(getattr(self.p,'historical_broken_weapons',[]))

 def test_doomerang_without_weapon_does_not_damage(self):
  target=self.g._summon(1,'CORE_EX1_162');before=target.health
  self.run_ops(cards.RULES['ICC_233'][1],card_id='ICC_233',target=target.uid,spell=True)
  self.assertEqual(target.health,before)

 def test_contraband_stash_replays_five_occurrences_not_five_identities(self):
  from expanded.replay_history import ReplayRecord
  for cid,count in [('DS1_175',7),('CORE_EX1_162',2),('CORE_CS2_029',2)]:
   for _ in range(count):
    card=Card(self.g._new_id(),cid)
    self.p.replay_history.append(ReplayRecord(1,0,card,1,(),0,-1))
  self.run_ops(cards.RULES['AV_405'][1],card_id='AV_405')
  self.assertEqual(len(self.p.minions),5)
  self.assertEqual({m.card_id for m in self.p.minions},{'DS1_175'})
  self.assertEqual(len(self.p.replay_history),11)

 def test_contraband_stash_with_short_history_replays_every_eligible_card(self):
  from expanded.replay_history import ReplayRecord
  card=Card(self.g._new_id(),'DS1_175')
  self.p.replay_history.append(ReplayRecord(1,0,card,1,(),0,-1))
  self.run_ops(cards.RULES['AV_405'][1],card_id='AV_405')
  self.assertEqual(len(self.p.minions),1)
