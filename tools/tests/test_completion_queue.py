import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

spec=importlib.util.spec_from_file_location('completion_queue',Path(__file__).resolve().parents[1]/'build_completion_queue.py')
queue=importlib.util.module_from_spec(spec);spec.loader.exec_module(queue)

class CompletionQueueTests(unittest.TestCase):
 def assert_registered_families(self,module_names):
  import importlib,json
  root=Path(__file__).resolve().parents[2]/'staging/rebased-88'
  report=queue.build(root);pending={row['card_id'] for row in report['cards']}
  from expanded.cards import COLLECTIBLE_IDS
  gaps=json.loads((root/'expanded/fidelity_gaps.json').read_text())['gaps']
  self.assertTrue(any(g['id']=='large_recipe_registration_scope' and g['status']=='incomplete' for g in gaps))
  for name in module_names:
   with self.subTest(family=name):
    rules=importlib.import_module('expanded.'+name).RULES
    self.assertTrue(rules);self.assertTrue(set(rules)<=COLLECTIBLE_IDS)
    self.assertFalse(set(rules)&pending)

 def test_cycle_is_one_group(self):
  self.assertEqual(queue.components({'a':{'b'},'b':{'a'},'c':set()}),[['a','b'],['c']])
 def test_no_cycle_in_dependency_chain(self):
  self.assertEqual(queue.components({'a':{'b'},'b':{'c'},'c':set()}),[['a'],['b'],['c']])
 def test_external_dependency_not_admitted(self):
  self.assertEqual(queue.components({'a':{'external'}}),[['a']])
 def test_self_cycle_retained(self):self.assertEqual(queue.components({'a':{'a'}}),[['a']])
 def test_unknown_selector_not_broadened(self):
  calls=[]
  result,unknown=queue.selector_request({'type':'MINION','timeline':'unverified'},lambda **kw:calls.append(kw))
  self.assertIsNone(result);self.assertEqual(unknown,['timeline']);self.assertFalse(calls)
 def test_dynamic_cost_not_broadened(self):
  result,unknown=queue.selector_request({'cost':('remaining_mana',)},lambda **kw:kw)
  self.assertIsNone(result);self.assertEqual(unknown,['cost'])
 def test_exact_cost_maps_both_bounds(self):
  result,unknown=queue.selector_request({'type':'MINION','cost':3},lambda **kw:kw)
  self.assertEqual(result,dict(card_type='MINION',minimum=3,maximum=3));self.assertFalse(unknown)
 def test_nested_ids_are_visited(self):
  self.assertIn('TOKEN_ID',list(queue.walk({'battlecry':(('summon','TOKEN_ID',1),)})))
 def test_full_catalog_accounting_and_determinism(self):
  root=Path(__file__).resolve().parents[2]/'staging/rebased-88';r=queue.build(root);r2=queue.build(root)
  self.assertEqual(r,r2);ids=[row['card_id'] for row in r['cards']]
  self.assertEqual(len(ids),len(set(ids)));self.assertEqual(len(ids),r['remaining_collectibles'])
  self.assertEqual(r['live_collectibles']+len(ids),r['catalog_size'])
  self.assertEqual(sum(row['remaining'] for row in r['family_queue']),len(ids))
  self.assertTrue(all(row['blockers'] and row['unresolved'] for row in r['cards']))

 def test_new_shared_systems_remain_review_gated(self):
  self.assert_registered_families(('evolving_locations','temporary_control','zone_triggers'))

 def test_stored_families_have_runtime_and_review_gates(self):
  self.assert_registered_families(('learned_spells','stored_obligations'))

 def test_transformation_runtime_and_exception_accounting(self):
  self.assert_registered_families(('transformations',))

 def test_rewind_runtime_and_explicit_keyword_dependencies(self):
  self.assert_registered_families(('rewind_generators','morchie'))
  from expanded.rewind_generators import DEATH_EFFECTS
  self.assertTrue(DEATH_EFFECTS['TIME_035'])

 def test_all_imbue_consumers_staged_with_class_power_gate(self):
  self.assert_registered_families(('imbue_consumers',))

 def test_rune_selector_normalizes_and_remains_explicit(self):
  result,unknown=queue.selector_request({'rune':'BLOOD'},lambda **kw:kw)
  self.assertEqual(result,dict(rune='blood'));self.assertFalse(unknown)

 def test_33_choice_generation_declarations_keep_review_gate(self):
  self.assert_registered_families(('choice_generators',))
  from expanded.choice_generators import RULES
  self.assertEqual(len(RULES),33)

 def test_historical_selector_remains_explicit(self):
  result,unknown=queue.selector_request({'era':'past'},lambda **kw:kw)
  self.assertEqual(result,dict(era='past'));self.assertFalse(unknown)

 def test_historical_and_health_declarations_keep_gates(self):
  self.assert_registered_families(('historical_generation','health_generation'))
  from expanded.historical_generation_catalog import load_universe,historical_contract
  from expanded.generation_cards import pool
  from expanded.cards import registry
  contract=historical_contract(pool(era='past',card_type='MINION'),'MAGE',load_universe())
  self.assertTrue(contract.card_ids)
  self.assertFalse(set(contract.card_ids)-registry().keys())

 def test_generation_families_have_bodies_but_keep_gates(self):
  self.assert_registered_families(('generation_cards','generation_extensions','leylines','maps'))

 def test_automatic_casting_bodies_and_exceptions(self):
  self.assert_registered_families(('automatic_casting',))
  from expanded.cards import COLLECTIBLE_IDS
  self.assertIn('FIR_959',COLLECTIBLE_IDS)

 def test_dynamic_transformation_cost_dependencies_are_visible(self):
  request,unknown=queue.selector_request({'type':'MINION','cost':('target_cost',1)},lambda **kw:kw)
  self.assertIsNone(request);self.assertEqual(unknown,['cost'])
  self.assert_registered_families(('transformations',))

 def test_future_summon_families_have_all_bodies_with_gates(self):
  self.assert_registered_families(('future_summons',))

 def test_colossal_entry_layouts_expose_tokens_without_completion_credit(self):
  root=Path(__file__).resolve().parents[2]/'staging/rebased-88';r=queue.build(root)
  from expanded.colossals import LAYOUTS
  from expanded.colossal_bodies import RULES as BODY_RULES
  rows={row['card_id']:row for row in r['cards']}
  for cid,layout in LAYOUTS.items():
   if cid not in rows:continue
   row=rows[cid]
   self.assertEqual(row['runtime_declaration_present'],cid in BODY_RULES)
   self.assertTrue({limb for limb,side in layout}<=set(row['explicit_references']))
   self.assertIn('colossal_body_pool_and_order_review' if cid in BODY_RULES else 'colossal_entry_only_body_and_limb_abilities_pending',row['blockers'])

 def test_herald_sources_have_bodies_but_keep_review_gates(self):
  self.assert_registered_families(('herald',))
  from expanded.herald import SOLDIERS
  from expanded.cards import registry
  self.assertTrue(set(SOLDIERS.values())<=registry().keys())

 def test_all_colossal_bodies_have_runtime_but_keep_review_gates(self):
  self.assert_registered_families(('colossal_bodies',))
  from expanded.colossals import LAYOUTS
  from expanded.cards import registry
  records=registry()
  for cid in ('CATA_153','CATA_154','CATA_155','CATA_488'):
   self.assertTrue({limb for limb,side in LAYOUTS[cid]}<=records.keys())

 def test_fabled_runtime_keeps_companion_and_review_dependencies(self):
  root=Path(__file__).resolve().parents[2]/'staging/rebased-88';r=queue.build(root)
  rows={row['card_id']:row for row in r['cards']}
  from expanded.fabled_decks import BUNDLES
  from expanded.cards import COLLECTIBLE_IDS
  for cid in set(('TIME_609','TIME_850','TIME_005','TIME_875','TIME_020','TIME_009','TIME_852','TIME_619','TIME_890','TIME_211','TIME_209')) - COLLECTIBLE_IDS:
   self.assertTrue(rows[cid]['runtime_declaration_present'])
   self.assertTrue(set(BUNDLES[cid])<=set(rows[cid]['explicit_references']))
   self.assertIn('fabled_bundle_effects_and_interactions_review',rows[cid]['blockers'])
  from expanded.cards import TOKEN_IDS,PLAYABLE_TOKENS
  self.assertTrue({'TIME_005','TIME_020','TIME_209'}<=COLLECTIBLE_IDS)
  self.assertTrue({'TIME_005t9t','TIME_020t5','TIME_020t5t'}<=TOKEN_IDS & PLAYABLE_TOKENS)
  self.assertNotIn('TIME_009',rows)
  self.assertIn('TIME_009',COLLECTIBLE_IDS)
  self.assertTrue({'TIME_009t1','TIME_009t2'}<=TOKEN_IDS & PLAYABLE_TOKENS)
  self.assertNotIn('TIME_209',rows)

 def test_integrated_compound_quest_and_rewards_leave_pending_queue(self):
  root=Path(__file__).resolve().parents[2]/'staging/rebased-88';r=queue.build(root)
  from expanded.cards import COLLECTIBLE_IDS,TOKEN_IDS,PLAYABLE_TOKENS
  self.assertNotIn('TLC_817',{c['card_id'] for c in r['cards']});self.assertIn('TLC_817',COLLECTIBLE_IDS)
  self.assertTrue({'TLC_817t','TLC_817t2','TLC_817t3','TLC_817t4','TLC_817t5'}<=TOKEN_IDS & PLAYABLE_TOKENS)

 def test_completed_final_paths_leave_pending_queue(self):
  root=Path(__file__).resolve().parents[2]/'staging/rebased-88';report=queue.build(root)
  rows={r['card_id']:r for r in report['cards']}
  from expanded.cards import COLLECTIBLE_IDS
  self.assertEqual(report['live_collectibles'],len(COLLECTIBLE_IDS))
  self.assertEqual(report['live_collectibles']+report['remaining_collectibles'],1185)
  self.assertFalse(rows)
  self.assertTrue({'CATA_470','TLC_EVENT_400','CORE_WON_145'}<=COLLECTIBLE_IDS)

class RuntimeBindingTests(unittest.TestCase):
 def report(self):
  return queue.build(Path(__file__).resolve().parents[2]/'staging/rebased-88')

 def test_colossal_identities_are_mapped_without_admission_or_fidelity_credit(self):
  report=self.report();rows={r['card_id']:r for r in report['cards']}
  from expanded.colossals import LAYOUTS
  from expanded.cards import COLLECTIBLE_IDS
  for cid,layout in LAYOUTS.items():
   if cid not in rows:continue
   row=rows[cid]
   mapped=next(m for m in row['mapped_dependencies'] if m['operation']=='summon_appendages_by_dependency')
   self.assertEqual(mapped['card_ids'],[limb for limb,side in layout])
   self.assertFalse(mapped['interaction_review_complete'])
   self.assertNotIn(cid,COLLECTIBLE_IDS)
   self.assertIn('colossal_body_pool_and_order_review',row['blockers'])
   self.assertIn('integration_validation',row['blockers'])
   self.assertFalse(any(u['operation']=='summon_appendages_by_dependency' for u in row['unresolved']))

 def test_named_tokens_have_exact_runtime_bindings_and_stay_staged(self):
  rows={r['card_id']:r for r in self.report()['cards']}
  from expanded.cards import COLLECTIBLE_IDS,registry
  self.assertIn('JAIL_443',COLLECTIBLE_IDS);self.assertNotIn('JAIL_443',rows)
  self.assertIn('JAIL_443t',registry())
  self.assertIn('CATA_561',COLLECTIBLE_IDS);self.assertNotIn('CATA_561',rows)
  self.assertIn('CATA_561t',registry())

 def test_closed_genn_family_is_removed_from_pending_queue(self):
  rows={r['card_id']:r for r in self.report()['cards']}
  from expanded.cards import COLLECTIBLE_IDS,registry
  from expanded.genn import POWERS
  self.assertNotIn('CATA_615',rows);self.assertIn('CATA_615',COLLECTIBLE_IDS)
  records=registry()
  self.assertTrue({'CATA_615t','AT_132_ROGUEt',*POWERS.values()}<=set(records))

 def test_historical_pool_does_not_shrink_when_runtime_identity_is_missing(self):
  from expanded.cards import registry,on_draw_cards
  from expanded.historical_generation_catalog import load_universe,historical_contract
  from expanded.generation_cards import pool
  records=registry()
  self.assertIn('JAIL_879t',records);self.assertTrue(on_draw_cards.CAST_EFFECTS['JAIL_879t'])
  self.assertIn('END_027',records)
  contract=historical_contract(pool(era='past',card_type='MINION',tribe='DRAGON',classes='own_or_neutral'),'MAGE',load_universe())
  self.assertTrue(contract.card_ids)
  self.assertFalse(set(contract.card_ids)-records.keys())
  # Completed production pools should pass. Inject a real missing identity
  # to retain the negative audit case without requiring an unfinished engine.
  victim=next(cid for cid in contract.card_ids if 'COLOSSAL' not in records[cid].get('mechanics',()))
  with patch('expanded.cards.registry',return_value={cid:c for cid,c in records.items() if cid!=victim}):
   report=self.report()
  self.assertIn(victim,report['historical_generation']['unwritten_card_ids'])
  self.assertIn(victim,contract.card_ids)

 def test_compound_quest_rewards_keep_distinct_live_rules(self):
  from expanded.cards import RULES,DEATH_EFFECTS
  self.assertEqual(RULES['TLC_817t3'][1],[('copy_self_right',1)])
  self.assertEqual(RULES['TLC_817t4'][1],[])
  self.assertEqual(DEATH_EFFECTS['TLC_817t4'],[('soletos_damage',)])


class HistoricalScopeTests(unittest.TestCase):
 def test_standard_registration_count_cannot_hide_historical_backlog(self):
  root=Path(__file__).resolve().parents[2]/'staging/rebased-88'
  from expanded.cards import registry
  from expanded.historical_generation import requests_for
  from expanded.historical_generation_catalog import historical_contract,load_universe
  request,=requests_for('TIME_052')
  contract=historical_contract(request,'DEATHKNIGHT',load_universe())
  records=registry();victim=contract.card_ids[0]
  with patch('expanded.cards.registry',return_value={cid:c for cid,c in records.items() if cid!=victim}):
   report=queue.build(root)
  history=report['historical_generation']
  self.assertEqual(history['unwritten_card_ids'],[victim])
  self.assertEqual(history['eligible_minions'],len(contract.card_ids))
  self.assertGreater(history['unwritten_minions'],report['remaining_collectibles'])
  self.assertEqual(history['written_minions']+history['unwritten_minions'],history['eligible_minions'])
  self.assertEqual(len(history['unwritten_card_ids']),history['unwritten_minions'])
  self.assertFalse(history['recursive_closure_verified'])
  self.assertIn(str(history['unwritten_minions']),queue.markdown(report))
 def test_missing_historical_measurement_is_not_reported_as_zero(self):
  self.assertIn('not been measured',queue.historical_summary({}))
