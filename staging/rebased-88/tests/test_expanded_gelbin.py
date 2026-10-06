import unittest,gzip,json
from pathlib import Path
from copy import deepcopy
from unittest.mock import patch
import test_expanded_generation as fixtures
from expanded import cards,gelbin as rules,Action
from engine.game import Card
from engine.cards import UnsupportedCard

class GelbinTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.root=Path(__file__).resolve().parents[1]
  with gzip.open(cls.root/'data/standard/all_cards.json.gz','rt') as f:cls.records={c['id']:c for c in json.load(f)}
 def setUp(self):
  self.g=fixtures.GenerationTests().game();self.p,self.q=self.g.players
  self.g.cards.update({cid:deepcopy(self.records[cid]) for cid in (*rules.RULES,*rules.AURA_IDS)})
  p=patch.dict(cards.RULES,{**rules.RULES,**rules.TOKEN_RULES});p.start();self.addCleanup(p.stop)
 def run_ops(self,ops,**kw):
  ctx=dict(owner=0,source=None,target=0,bonus=0,lifesteal=False);ctx.update(kw)
  self.g._start_play_effects(ops,ctx);self.g._settle(allow_event_choices=True)
 def play(self,cid):
  self.p.mana=10;card=self.g._add(0,cid);self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==card.uid));return card
 def cycle(self):self.g.step(Action('end'));self.g.step(Action('end'))
 def test_tag_inventory_is_explicit_and_matches_pinned_xml_inventory(self):
  data=json.loads((self.root/'../../docs/engine-audit/fabled-aura-source-inventory.json').read_text())
  self.assertEqual(rules.AURA_IDS,{r['card_id'] for r in data['cards']});self.assertEqual(len(rules.AURA_IDS),15)
 def test_placement_rules_match_existing_live_aura_declarations(self):
  for cid in ('CATA_480','END_011','JAIL_327','TIME_700','TTN_851','EDR_259e1'):self.assertEqual(rules.AURA_RULES[cid],cards.RULES[cid])
 def test_one_physical_copy_of_each_aura_leaves_deck(self):
  a=Card(self.g._new_id(),'TIME_009t1');b=Card(self.g._new_id(),'TIME_009t1');c=Card(self.g._new_id(),'TIME_009t2');self.p.deck=[a,b,c,'CORE_CS2_029']
  self.play('TIME_009');self.assertEqual(len(self.p.deck),2);self.assertIn('CORE_CS2_029',self.p.deck);self.assertEqual(sum(x is a or x is b for x in self.p.deck),1);self.assertEqual(len(self.p.scheduled_effects),2)
 def test_all_five_standard_auras_and_two_companions_place(self):
  self.p.deck=[cid for cid in rules.AURA_RULES if cid!='EDR_259e1'];self.play('TIME_009')
  self.assertFalse(self.p.deck);self.assertEqual(len(self.p.scheduled_effects),5);self.assertEqual(self.g._end_trigger_count(0),2);self.assertEqual(len(self.q.timed_cost_increases),1)
 def test_placement_is_not_paid_cast_draw_or_repeat(self):
  self.p.deck=['TIME_009t1','CORE_CS2_029'];self.p.spell_repeat_charges=2;auctioneer=self.g._summon(0,'JAIL_718');self.q.secrets.append(Card(self.g._new_id(),'CORE_EX1_287'))
  self.play('TIME_009');self.assertEqual(self.p.mana,2);self.assertEqual(self.p.spell_repeat_charges,2);self.assertEqual(len(self.p.scheduled_effects),1);self.assertFalse(self.p.spells_turn);self.assertEqual([e['card_id'] for e in self.p.played_history],['TIME_009']);self.assertFalse(self.p.hand);self.assertEqual(len(self.q.secrets),1)
 def test_existing_aura_does_not_block_new_copy(self):
  self.play('TIME_009t1');self.p.deck=['TIME_009t1'];self.play('TIME_009');self.assertEqual(len(self.p.scheduled_effects),2)
 def test_duration_modifier_on_physical_deck_card_survives_placement(self):
  c=Card(self.g._new_id(),'TIME_009t1');c.rule_state={'aura_duration_delta':2};self.p.deck=[c];self.play('TIME_009');self.assertEqual(self.p.scheduled_effects[0]['remaining'],5)
 def test_generated_name_does_not_define_membership(self):
  self.g.cards['TEST_FAKE_AURA']=dict(id='TEST_FAKE_AURA',name='Fake Aura',type='SPELL',cost=1,cardClass='PALADIN');self.p.deck=['TEST_FAKE_AURA'];self.play('TIME_009');self.assertEqual(self.p.deck,['TEST_FAKE_AURA']);self.assertFalse(self.p.scheduled_effects)
 def test_unsupported_historical_aura_rejects_before_payment_or_rng(self):
  self.p.deck=['TIME_009t1','TTN_908'];c=self.g._add(0,'TIME_009');before=deepcopy(self.g.observe(0));rng=self.g.rng.getstate();action=next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid)
  with self.assertRaisesRegex(UnsupportedCard,'not implemented'):self.g.step(action)
  self.assertEqual(self.g.observe(0),before);self.assertEqual(self.g.rng.getstate(),rng)
 def test_missing_stored_payload_rejects_before_other_aura_moves(self):
  self.p.deck=['TIME_009t1','EDR_259e1']
  with self.assertRaisesRegex(UnsupportedCard,'stored spell'):self.run_ops([('gelbin_auras',)])
  self.assertEqual(self.p.deck,['TIME_009t1','EDR_259e1']);self.assertFalse(self.p.scheduled_effects)
 def test_stored_aura_payload_survives_direct_placement(self):
  c=Card(self.g._new_id(),'EDR_259e1');c.stored_spell=Card(self.g._new_id(),'CORE_EX1_606');c.aura_duration=2;self.p.deck=[c,'CORE_CS2_029'];self.play('TIME_009')
  self.assertIs(self.p.scheduled_effects[0]['stored_card'],c.stored_spell);self.assertEqual(self.p.scheduled_effects[0]['remaining'],2)
  self.g.step(Action('end'));self.assertEqual(self.p.armor,5)
 def test_gnomish_heals_all_friendly_characters_only(self):
  self.p.health=10;self.q.health=10;m=self.g._summon(0,'NEW1_034');self.g._buff(m,0,5);m.health=1;self.play('TIME_009t1');self.g.step(Action('end'))
  self.assertEqual(self.p.health,14);self.assertEqual(m.health,5);self.assertEqual(self.q.health,10)
 def test_gnomish_ticks_three_owner_ends_and_expires(self):
  self.p.health=1;self.play('TIME_009t1')
  for expected in (5,9,13):self.cycle();self.assertEqual(self.p.health,expected)
  self.assertFalse(self.p.scheduled_effects);self.cycle();self.assertEqual(self.p.health,13)
 def test_mekkatorque_buffs_and_shields_same_friendly_minion(self):
  a=self.g._summon(0,'NEW1_034');b=self.g._summon(0,'NEW1_034');self.play('TIME_009t2');self.g.step(Action('end'))
  buffed=[m for m in (a,b) if 'DIVINE_SHIELD' in m.keywords];self.assertEqual(len(buffed),1);self.assertEqual(buffed[0].attack,8);self.assertEqual(buffed[0].max_health,6)
 def test_mekkatorque_empty_board_consumes_tick_without_rng(self):
  self.play('TIME_009t2');rng=self.g.rng.getstate();self.g.step(Action('end'));self.assertEqual(self.p.scheduled_effects[0]['remaining'],2);self.assertEqual(self.g.rng.getstate(),rng)
 def test_sandfury_does_not_double_companion_aura_tick(self):
  self.p.health=10;self.play('CATA_480');self.play('TIME_009t1');self.g.step(Action('end'));self.assertEqual(self.p.health,14)
 def test_both_companions_count_as_active_auras(self):
  for cid in rules.TOKEN_RULES:
   self.p.scheduled_effects=[];self.play(cid);self.assertTrue(self.g._batch30_state('aura_active',0))
 def test_companions_can_be_internally_cast(self):
  for cid in rules.TOKEN_RULES:self.assertTrue(self.g._supports_internal_spell(cid))
  self.run_ops([('cast_fixed_spell','TIME_009t2','random')]);self.assertEqual(self.p.scheduled_effects[0]['source_card_id'],'TIME_009t2');self.assertFalse(self.p.played_history)
 def test_companion_can_be_traded_without_activating(self):
  c=self.g._add(0,'TIME_009t1');self.g.step(next(a for a in self.g.legal_actions() if a.kind=='trade' and a.source==c.uid));self.assertFalse(self.p.scheduled_effects);self.assertTrue(any(self.g._card_data(x)['id']==c.card_id for x in self.p.deck))
 def test_gelbin_silence_and_death_do_not_remove_placed_aura(self):
  self.p.deck=['TIME_009t1'];self.play('TIME_009');m=self.p.minions[0];self.g._silence(m);m.health=0;self.g._settle();self.assertEqual(len(self.p.scheduled_effects),1)
 def test_full_hand_does_not_prevent_direct_aura_placement(self):
  for _ in range(10):self.g._add(0,'TOKEN_COIN')
  self.p.deck=['TIME_009t1'];self.run_ops([('gelbin_auras',)]);self.assertFalse(self.p.deck);self.assertEqual(len(self.p.hand),10);self.assertEqual(len(self.p.scheduled_effects),1)
 def test_placed_aura_public_view_has_no_physical_card_or_provenance(self):
  c=Card(self.g._new_id(),'TIME_009t1');c._starting_owner=0;self.p.deck=[c];self.play('TIME_009')
  for viewer in (0,1):
   effect=self.g.observe(viewer)['players'][0]['scheduled_effects'][0];self.assertEqual(effect['source_card_id'],c.card_id);self.assertNotIn('_starting_owner',str(effect));self.assertNotIn('physical_card',effect)
