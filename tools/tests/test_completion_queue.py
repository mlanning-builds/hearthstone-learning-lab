import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location('completion_queue',Path(__file__).resolve().parents[1]/'build_completion_queue.py')
queue=importlib.util.module_from_spec(spec);spec.loader.exec_module(queue)

class CompletionQueueTests(unittest.TestCase):
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
  self.assertTrue(all(row['blockers'] for row in r['cards']))
  dark=next(row for row in r['family_queue'] if row['family']=='dark_gift')
  self.assertEqual(dark['staged_runtime_declarations'],dark['remaining'])

 def test_new_shared_systems_remain_review_gated(self):
  root=Path(__file__).resolve().parents[2]/'staging/rebased-88';r=queue.build(root)
  rows={row['card_id']:row for row in r['cards']}
  from expanded import evolving_locations,temporary_control,zone_triggers,starting_rules
  from expanded.cards import COLLECTIBLE_IDS
  for cid in (set(evolving_locations.RULES)|set(temporary_control.RULES)|set(zone_triggers.RULES)|set(starting_rules.STAGED_RULES)) - COLLECTIBLE_IDS:
   self.assertTrue(rows[cid]['runtime_declaration_present'])
   self.assertIn('integration_validation',rows[cid]['blockers'])
   self.assertNotIn('runtime_declaration_missing',rows[cid]['blockers'])
  for cid,stages in evolving_locations.TIMELINES.items():
   if cid in rows:self.assertTrue(set(stages)<=set(rows[cid]['explicit_references']))
  self.assertIn('CATA_527t2',rows['CATA_527']['explicit_references'])
  requests=rows['CATA_527']['candidate_pool_contexts']
  self.assertTrue(any(r['selector'].get('excluded_mechanic')=='COLOSSAL' for r in requests))

 def test_stored_families_have_runtime_and_review_gates(self):
  root=Path(__file__).resolve().parents[2]/'staging/rebased-88';r=queue.build(root)
  rows={row['card_id']:row for row in r['cards']}
  from expanded.cards import COLLECTIBLE_IDS
  for cid in set(('MEND_046','MEND_100','TIME_704','JAIL_719','TIME_861')) - COLLECTIBLE_IDS:
   self.assertTrue(rows[cid]['runtime_declaration_present']);self.assertIn('integration_validation',rows[cid]['blockers'])
  for cid in ('MEND_046','MEND_100','TIME_704'):self.assertIn(cid+'t',rows[cid]['explicit_references'])
  for family in ('stored_cards','stored_spells'):
   row=next(x for x in r['family_queue'] if x['family']==family);self.assertEqual(row['remaining'],row['staged_runtime_declarations'])

 def test_transformation_runtime_and_exception_accounting(self):
  root=Path(__file__).resolve().parents[2]/'staging/rebased-88';r=queue.build(root)
  family=next(row for row in r['family_queue'] if row['family']=='transformation')
  self.assertEqual(family['remaining'],14);self.assertEqual(family['staged_runtime_declarations'],14)
  rows=[row for row in r['cards'] if row['family']=='transformation']
  self.assertTrue(all('transformation_pool_and_interaction_review' in row['blockers'] for row in rows if row['runtime_declaration_present']))
  self.assertTrue(all(row['unresolved'] for row in rows if not row['runtime_declaration_present']))

 def test_rewind_runtime_and_explicit_keyword_dependencies(self):
  root=Path(__file__).resolve().parents[2]/'staging/rebased-88';r=queue.build(root)
  family=next(row for row in r['family_queue'] if row['family']=='rewind')
  self.assertEqual(family['remaining'],12);self.assertEqual(family['staged_runtime_declarations'],12)
  machine=next(row for row in r['cards'] if row['card_id']=='TIME_035')
  self.assertIn('TIME_038',machine['missing_candidate_collectibles']);self.assertNotIn('TIME_035',machine['missing_candidate_collectibles'])
  morchie=next(row for row in r['cards'] if row['card_id']=='END_036');self.assertTrue(morchie['runtime_declaration_present']);self.assertIn('rewind_pool_and_interaction_review',morchie['blockers'])

 def test_all_imbue_consumers_staged_with_class_power_gate(self):
  root=Path(__file__).resolve().parents[2]/'staging/rebased-88';r=queue.build(root)
  family=next(row for row in r['family_queue'] if row['family']=='imbue');self.assertEqual(family['remaining'],19);self.assertEqual(family['staged_runtime_declarations'],19)
  self.assertTrue(all('imbue_class_powers_pool_and_interaction_review' in row['blockers'] for row in r['cards'] if row['family']=='imbue'))

 def test_rune_selector_normalizes_and_remains_explicit(self):
  result,unknown=queue.selector_request({'rune':'BLOOD'},lambda **kw:kw)
  self.assertEqual(result,dict(rune='blood'));self.assertFalse(unknown)

 def test_33_choice_generation_declarations_keep_review_gate(self):
  root=Path(__file__).resolve().parents[2]/'staging/rebased-88';r=queue.build(root)
  from expanded.choice_generators import RULES
  rows={row['card_id']:row for row in r['cards']}
  self.assertEqual(len(RULES),33)
  self.assertTrue(all(rows[c]['runtime_declaration_present'] for c in RULES))
  self.assertTrue(all('choice_generation_pool_and_interaction_review' in rows[c]['blockers'] for c in RULES))
  self.assertTrue(any(p['selector']['rune']=='blood' for p in rows['CORE_RLK_066']['candidate_pool_contexts']))

 def test_historical_selector_remains_explicit(self):
  result,unknown=queue.selector_request({'era':'past'},lambda **kw:kw)
  self.assertEqual(result,dict(era='past'));self.assertFalse(unknown)

 def test_historical_and_health_declarations_keep_gates(self):
  root=Path(__file__).resolve().parents[2]/'staging/rebased-88';r=queue.build(root)
  from expanded import historical_generation as hg, health_generation as hp
  rows={row['card_id']:row for row in r['cards']}
  for cid in hg.RULES:
   self.assertTrue(rows[cid]['runtime_declaration_present'])
   self.assertIn('historical_membership_and_behavior_review',rows[cid]['blockers'])
   self.assertTrue(rows[cid]['unresolved'])
  for cid in hp.RULES:
   self.assertTrue(rows[cid]['runtime_declaration_present'])
   self.assertIn('health_payment_generation_review',rows[cid]['blockers'])

 def test_generation_families_have_bodies_but_keep_gates(self):
  root=Path(__file__).resolve().parents[2]/'staging/rebased-88';r=queue.build(root)
  for family in ('generation','discover','leyline','map'):
   row=next(row for row in r['family_queue'] if row['family']==family)
   self.assertEqual(row['remaining'],row['staged_runtime_declarations'])
  self.assertNotIn('TLC_479',[row['card_id'] for row in r['cards']])

 def test_automatic_casting_bodies_and_exceptions(self):
  root=Path(__file__).resolve().parents[2]/'staging/rebased-88';r=queue.build(root)
  family=next(row for row in r['family_queue'] if row['family']=='automatic_casting')
  self.assertEqual((family['remaining'],family['staged_runtime_declarations']),(7,7))
  rows=[row for row in r['cards'] if row['family']=='automatic_casting']
  self.assertTrue(all('automatic_cast_pool_and_interaction_review' in row['blockers'] for row in rows if row['runtime_declaration_present'] and row['card_id']!='TIME_009'))
  self.assertTrue(all(row['unresolved'] for row in rows if not row['runtime_declaration_present']))

 def test_dynamic_transformation_cost_dependencies_are_visible(self):
  root=Path(__file__).resolve().parents[2]/'staging/rebased-88';r=queue.build(root)
  rows={row['card_id']:row for row in r['cards']}
  for cid in ('CATA_567','EDR_529','TLC_235'):
   self.assertTrue(rows[cid]['unresolved']);self.assertIn('CATA_139',rows[cid]['missing_candidate_collectibles'])

 def test_future_summon_families_have_all_bodies_with_gates(self):
  root=Path(__file__).resolve().parents[2]/'staging/rebased-88';r=queue.build(root)
  for family in ('animal_companion','void_soul'):
   row=next(row for row in r['family_queue'] if row['family']==family)
   self.assertEqual(row['remaining'],3 if family=='animal_companion' else 4)
   self.assertEqual(row['remaining'],row['staged_runtime_declarations'])
   self.assertTrue(all('future_summon_pool_and_scaling_review' in c['blockers'] for c in r['cards'] if c['family']==family))

 def test_colossal_entry_layouts_expose_tokens_without_completion_credit(self):
  root=Path(__file__).resolve().parents[2]/'staging/rebased-88';r=queue.build(root)
  from expanded.colossals import LAYOUTS
  from expanded.colossal_bodies import RULES as BODY_RULES
  rows={row['card_id']:row for row in r['cards']}
  for cid,layout in LAYOUTS.items():
   row=rows[cid]
   self.assertEqual(row['runtime_declaration_present'],cid in BODY_RULES)
   self.assertTrue({limb for limb,side in layout}<=set(row['explicit_references']))
   self.assertIn('colossal_body_pool_and_order_review' if cid in BODY_RULES else 'colossal_entry_only_body_and_limb_abilities_pending',row['blockers'])

 def test_herald_sources_have_bodies_but_keep_review_gates(self):
  root=Path(__file__).resolve().parents[2]/'staging/rebased-88';r=queue.build(root)
  from expanded.herald import RULES,SOLDIERS,UNRESOLVED
  rows={row['card_id']:row for row in r['cards']}
  family=next(row for row in r['family_queue'] if row['family']=='herald')
  self.assertEqual((family['remaining'],family['staged_runtime_declarations']),(15,15))
  for cid in RULES:
   self.assertTrue(rows[cid]['runtime_declaration_present'])
   self.assertIn('herald_army_timing_offclass_and_pool_review',rows[cid]['blockers'])
   if cid!='CATA_190h':self.assertTrue(set(SOLDIERS.values())<=set(rows[cid]['explicit_references']))
  for cid in UNRESOLVED:
   self.assertFalse(rows[cid]['runtime_declaration_present']);self.assertTrue(rows[cid]['unresolved'])

 def test_all_colossal_bodies_have_runtime_but_keep_review_gates(self):
  root=Path(__file__).resolve().parents[2]/'staging/rebased-88';r=queue.build(root)
  family=next(row for row in r['family_queue'] if row['family']=='colossal')
  self.assertEqual((family['remaining'],family['staged_runtime_declarations']),(11,11))
  rows={row['card_id']:row for row in r['cards']}
  for cid in ('CATA_154','CATA_300'):
   self.assertTrue(rows[cid]['runtime_declaration_present']);self.assertIn('colossal_body_pool_and_order_review',rows[cid]['blockers'])

 def test_fabled_runtime_keeps_companion_and_review_dependencies(self):
  root=Path(__file__).resolve().parents[2]/'staging/rebased-88';r=queue.build(root)
  rows={row['card_id']:row for row in r['cards']}
  from expanded.fabled_decks import BUNDLES
  from expanded.cards import COLLECTIBLE_IDS
  for cid in set(('TIME_609','TIME_850','TIME_005','TIME_875','TIME_020','TIME_009','TIME_852','TIME_619','TIME_890','TIME_211','TIME_209')) - COLLECTIBLE_IDS:
   self.assertTrue(rows[cid]['runtime_declaration_present'])
   self.assertTrue(set(BUNDLES[cid])<=set(rows[cid]['explicit_references']))
   self.assertIn('fabled_bundle_effects_and_interactions_review',rows[cid]['blockers'])
  self.assertIn('TIME_005t9t',rows['TIME_005']['explicit_references'])
  self.assertTrue({'TIME_020t5','TIME_020t5t'}<=set(rows['TIME_020']['explicit_references']))
  self.assertTrue({'TIME_009t1','TIME_009t2','EDR_259e1'}<=set(rows['TIME_009']['explicit_references']))
  self.assertTrue(rows['TIME_209']['runtime_declaration_present'])

 def test_compound_quest_keeps_all_reward_dependencies(self):
  root=Path(__file__).resolve().parents[2]/'staging/rebased-88';r=queue.build(root)
  row=next(c for c in r['cards'] if c['card_id']=='TLC_817')
  self.assertTrue(row['runtime_declaration_present'])
  self.assertTrue({'TLC_817t','TLC_817t2','TLC_817t3','TLC_817t4','TLC_817t5'}<=set(row['explicit_references']))
  self.assertIn('compound_quest_reward_review',row['blockers'])

 def test_final_paths_do_not_admit_incomplete_contracts(self):
  root=Path(__file__).resolve().parents[2]/'staging/rebased-88';report=queue.build(root)
  rows={r['card_id']:r for r in report['cards']}
  self.assertTrue(all(r['runtime_declaration_present'] for r in rows.values()))
  from expanded.cards import COLLECTIBLE_IDS
  self.assertEqual(report['live_collectibles'],len(COLLECTIBLE_IDS))
  self.assertEqual(report['live_collectibles']+report['remaining_collectibles'],1185)
  self.assertTrue({'JAIL_397','JAIL_430','JAIL_421','TIME_618','TIME_850','JAIL_719','TLC_251'}<=COLLECTIBLE_IDS)
  for cid in ('CATA_470','TLC_EVENT_400','CORE_WON_145','JAIL_EVENT_100','FIR_959'):
   self.assertIn('incomplete_runtime_or_production_contract',rows[cid]['blockers'])
   self.assertTrue(rows[cid]['unresolved'])


class RuntimeBindingTests(unittest.TestCase):
 def report(self):
  return queue.build(Path(__file__).resolve().parents[2]/'staging/rebased-88')

 def test_colossal_identities_are_mapped_without_admission_or_fidelity_credit(self):
  report=self.report();rows={r['card_id']:r for r in report['cards']}
  from expanded.colossals import LAYOUTS
  from expanded.cards import COLLECTIBLE_IDS
  for cid,layout in LAYOUTS.items():
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
  for cid,expected in (('CATA_561',{'CATA_561t'}),('CATA_615',{'CATA_615t'}),('JAIL_443',{'JAIL_443t'})):
   mapped={c for m in rows[cid]['mapped_dependencies'] for c in m['card_ids']}
   self.assertEqual(mapped,expected)
   self.assertTrue(expected<=set(rows[cid]['explicit_references']))
   self.assertIn('recipe_behavior_review',rows[cid]['blockers'])

 def test_unmapped_tokens_and_historical_pool_gates_remain_unresolved(self):
  rows={r['card_id']:r for r in self.report()['cards']}
  self.assertTrue(any(u['operation']=='shuffle_token_by_dependency' for u in rows['JAIL_879']['unresolved']))
  self.assertTrue(any(u['operation']=='historical_generation' for u in rows['END_027']['unresolved']))

 def test_compound_quest_rewards_are_bound_to_their_distinct_halves(self):
  row=next(r for r in self.report()['cards'] if r['card_id']=='TLC_817')
  mapped=[m for m in row['mapped_dependencies'] if m['operation']=='add_reward_by_dependency']
  self.assertEqual([m['card_ids'] for m in mapped],[['TLC_817t3'],['TLC_817t4']])
  self.assertTrue(all(not m['interaction_review_complete'] for m in mapped))
  self.assertIn('compound_quest_reward_review',row['blockers'])
  self.assertIn('integration_validation',row['blockers'])
