import unittest,gzip,json
from pathlib import Path
from copy import deepcopy
from unittest.mock import patch
import test_expanded_generation as fixtures
from expanded import cards,learned_spells as rules,Action
from engine.game import Card
from engine.cards import UnsupportedCard
from expanded.generation_cards import pool
from expanded.pools import GenerationPool
from expanded.features import encode_decision

class LearnedSpellTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with gzip.open(Path(__file__).resolve().parents[1]/'data/standard/all_cards.json.gz','rt') as f:cls.records={c['id']:c for c in json.load(f)}
 def setUp(self):
  self.g=fixtures.GenerationTests().game();self.p,self.q=self.g.players;self.g._generation_pools={}
  self.g.cards.update({cid:deepcopy(self.records[cid]) for cid in rules.RULES.keys()|rules.TOKEN_RULES.keys()})
  p=patch.dict(cards.RULES,{**rules.RULES,**rules.TOKEN_RULES});p.start();self.addCleanup(p.stop)
 def contract(self,request,ids):self.g._generation_pools[(request,self.p.hero_class)]=GenerationPool('fixture',tuple(ids),'Controlled test membership')
 def spell(self,cid,cost=7,mode='character',ops=None,school='NATURE'):
  self.g.cards[cid]=dict(id=cid,name=cid,type='SPELL',cost=cost,spellSchool=school,cardClass='MAGE',collectible=True,set='EXPERT1')
  p=patch.dict(cards.RULES,{cid:(mode,[('damage',2)] if ops is None else ops)});p.start();self.addCleanup(p.stop)
  return cid
 def run_ops(self,ops,**kw):
  ctx=dict(owner=0,source=None,target=0,bonus=0,lifesteal=False);ctx.update(kw)
  self.g._start_play_effects(ops,ctx);self.g._settle(allow_event_choices=True)
 def pupil(self,cid):
  card=self.g._add(0,'TIME_704t');card._learned_spell=cid;return card
 def play(self,card,target=0):
  action=next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==card.uid and a.target==target)
  self.g.step(action)
 def test_mentor_binds_selected_spell_to_exact_pupil(self):
  cid=self.spell('TEST_PAST');self.contract(rules.PAST_LARGE,[cid]);self.run_ops([('learned_mentor',)])
  card=self.p.hand[-1];self.g.step(Action('choose',choices=(0,)))
  self.assertEqual(card._learned_spell,cid);self.assertEqual(self.p.discoveries_total,1);self.assertEqual(len(self.p.hand),1)
 def test_mentor_choice_is_private_and_clone_resumes(self):
  cid=self.spell('TEST_PAST');self.contract(rules.PAST_LARGE,[cid]);self.run_ops([('learned_mentor',)])
  self.assertNotIn(cid,str(self.g.observe(1)['pending_choice']));clone=deepcopy(self.g)
  for g in (self.g,clone):g.step(Action('choose',choices=(0,)))
  self.assertEqual(self.g.observe(0),clone.observe(0))
 def test_pupil_selects_target_not_random_and_cast_is_not_hand_play(self):
  cid=self.spell('TEST_PAST');c=self.pupil(cid);self.play(c,-2)
  self.assertEqual(self.q.health,28);self.assertEqual(self.p.health,30);self.assertEqual(self.p.cards_played,1);self.assertFalse(self.p.spells_turn)
 def test_pupil_without_targets_can_be_played_and_spell_fizzles(self):
  cid=self.spell('TEST_PAST',mode='enemy_minion');c=self.pupil(cid);self.play(c)
  self.assertEqual(len(self.p.minions),1);self.assertEqual(self.q.health,30)
 def test_selected_target_disappearing_does_not_retarget(self):
  cid=self.spell('TEST_PAST',mode='minion');c=self.pupil(cid);m=self.g._summon(1,'NEW1_034');target=m.uid;self.q.board.remove(m)
  self.run_ops([('learned_cast',)],physical_card=c,target=target);self.assertEqual(self.q.health,30)
 def test_no_target_spell_ignores_extraneous_battlecry_target(self):
  cid=self.spell('TEST_PAST',mode='none',ops=[('armor',3)]);c=self.pupil(cid)
  self.run_ops([('learned_cast',)],physical_card=c,target=-2);self.assertEqual(self.p.armor,3)
 def test_internal_spell_does_not_inherit_minion_lifesteal(self):
  cid=self.spell('TEST_PAST');c=self.pupil(cid);self.p.health=20
  self.run_ops([('learned_cast',)],physical_card=c,target=-2,lifesteal=True);self.assertEqual(self.p.health,20)
 def test_pupil_carries_payload_through_board_copy_and_bounce(self):
  cid=self.spell('TEST_PAST');c=self.pupil(cid);self.play(c,-2);m=self.p.minions[0]
  copied=self.g._summon(0,m.card_id,copy_from=m);self.assertEqual(copied._learned_spell,cid)
  self.g._bounce(m);self.assertEqual(self.p.hand[-1]._learned_spell,cid)
 def test_shuffle_preserves_learned_spell_but_resets_hand_buffs(self):
  cid=self.spell('TEST_PAST');c=self.pupil(cid);c.attack_bonus=7
  shuffled=self.g._shuffle_hand_card(0,c);self.assertEqual(shuffled._learned_spell,cid);self.assertEqual(shuffled.attack_bonus,0)
 def test_typhoon_style_shuffle_preserves_bound_spell(self):
  cid=self.spell('TEST_PAST');c=self.pupil(cid);self.play(c,-2)
  self.run_ops([('b60_shuffle_all',)]);found=[c for p in self.g.players for c in p.deck if isinstance(c,Card) and c.card_id=='TIME_704t']
  self.assertEqual(len(found),1);self.assertEqual(found[0]._learned_spell,cid)
 def test_transformation_into_other_minion_does_not_inherit_bound_spell(self):
  cid=self.spell('TEST_PAST');c=self.pupil(cid);self.play(c,-2);m=self.g._transform(self.p.minions[0],'NEW1_034');self.assertFalse(hasattr(m,'_learned_spell'))
 def test_hand_transformation_removes_intrinsic_learned_spell(self):
  cid=self.spell('TEST_PAST');c=self.pupil(cid);self.g._b60_transform_card(c,'NEW1_034');self.assertFalse(hasattr(c,'_learned_spell'))
 def test_missing_historical_contract_preserves_hand_and_rng(self):
  state=self.g.rng.getstate()
  with self.assertRaises(UnsupportedCard):self.run_ops([('learned_mentor',)])
  self.assertFalse(self.p.hand);self.assertEqual(self.g.rng.getstate(),state)
 def test_mentor_full_hand_burns_pupil_but_resolves_discover(self):
  cid=self.spell('TEST_PAST');self.contract(rules.PAST_LARGE,[cid])
  for _ in range(10):self.g._add(0,'TOKEN_COIN')
  self.run_ops([('learned_mentor',)]);self.g.step(Action('choose',choices=(0,)));self.assertEqual(len(self.p.hand),10);self.assertEqual(self.p.discoveries_total,1)
 def nature(self):
  ids=[self.spell('TEST_NATURE_'+str(cost),cost=cost,mode='none',ops=[('armor',1)]) for cost in (0,2,4,10)]
  self.contract(rules.NATURE,ids);return ids
 def test_carve_allocates_twelve_mana_to_three_treants(self):
  self.nature();self.run_ops([('learned_carve',)]);self.assertEqual(len(self.p.hand),3)
  self.assertEqual(sum(self.g.cards[c._learned_spell]['cost'] for c in self.p.hand),12)
 def test_carve_one_hand_slot_maximizes_available_budget(self):
  self.nature()
  for _ in range(9):self.g._add(0,'TOKEN_COIN')
  self.run_ops([('learned_carve',)]);self.assertEqual(self.p.hand[-1]._learned_spell,'TEST_NATURE_10');self.assertEqual(len(self.p.hand),10)
 def test_carve_full_hand_does_not_consume_rng_for_bound_payloads(self):
  self.nature()
  for _ in range(10):self.g._add(0,'TOKEN_COIN')
  state=self.g.rng.getstate();self.run_ops([('learned_carve',)]);self.assertEqual(self.g.rng.getstate(),state)
 def test_carve_bound_spells_not_revealed_in_enemy_observation(self):
  self.nature();self.run_ops([('learned_carve',)]);self.assertNotIn('TEST_NATURE',json.dumps(self.g.observe(1)));self.assertIn('learned_spell',json.dumps(self.g.observe(0)))
 def test_carve_rejects_unsupported_pool_member_without_filtering(self):
  self.nature();self.g.cards['UNSUPPORTED']=dict(id='UNSUPPORTED',name='Unsupported',type='SPELL',cost=1,spellSchool='NATURE',cardClass='MAGE')
  self.contract(rules.NATURE,['UNSUPPORTED'])
  with self.assertRaises(UnsupportedCard):self.run_ops([('learned_carve',)])
  self.assertFalse(self.p.hand)
 def test_bulb_initial_level_and_fixed_cost(self):
  self.run_ops([('learned_bulb',)]);c=self.p.hand[0];self.assertEqual(c.rule_state['bulb_level'],1);self.assertEqual(self.g._cost(c,0),3)
 def test_bulb_owner_start_upgrade_once_and_not_opponent(self):
  self.run_ops([('learned_bulb',)]);c=self.p.hand[0];self.assertEqual(self.g._learned_turn_entries('end'),[])
  self.g.current=1;self.assertEqual(self.g._learned_turn_entries('start'),[]);self.g.current=0
  self.run_ops([('learned_bulb_tick',c.uid),('learned_bulb_tick',c.uid)]);self.assertEqual(c.rule_state['bulb_level'],2)
 def test_bulb_casts_three_spells_at_snapshot_level(self):
  self.run_ops([('learned_bulb',)]);c=self.p.hand[0];c.rule_state['bulb_level']=4
  cid=self.spell('TEST_FOUR',cost=4,mode='none',ops=[('armor',2)]);self.contract(pool(card_type='SPELL',minimum=4,maximum=4),[cid]);self.play(c)
  self.assertEqual(self.p.armor,6);self.assertEqual(self.p.cards_played,1);self.assertEqual(self.p.spells_turn,['MEND_100t'])
 def test_bulb_caps_at_ten_without_increasing_mana_cost(self):
  self.run_ops([('learned_bulb',)]);c=self.p.hand[0];c.rule_state['bulb_level']=10;self.run_ops([('learned_bulb_tick',c.uid)])
  self.assertEqual(c.rule_state['bulb_level'],10);self.assertEqual(self.g._cost(c,0),3)
 def test_bulb_missing_pool_step_rolls_back_payment(self):
  self.run_ops([('learned_bulb',)]);c=self.p.hand[0];before=self.g.observe(0)
  with self.assertRaises(UnsupportedCard):self.play(c)
  self.assertEqual(self.g.observe(0),before)
 def test_learned_spell_is_encoded_without_private_payload_objects(self):
  cid=self.spell('TEST_PAST');self.pupil(cid);view=self.g.observe(0);encoded=encode_decision(dict(actor=0,observation=view,actions=view['legal_actions']))
  self.assertIn(cid,str(encoded));json.dumps(view)
