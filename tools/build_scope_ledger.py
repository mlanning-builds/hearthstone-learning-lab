"""Static planning ledger. Never imports simulator modules or executes games.
Run: python tools/build_scope_ledger.py --project PATH --output PATH
Grouping is a search aid, not a semantic rules implementation or coverage claim.
"""
import argparse, ast, csv, gzip, hashlib, html, io, json, re
from collections import Counter, defaultdict
from pathlib import Path

FAMILIES = {
 'resolution_events': ('Play, summon, death and turn event ordering', r'\b(battlecry|deathrattle|after|whenever|summon|reborn|end of|start of)\b', ['game.py:_play','game.py:_summon','systems.py:_queue_event','lifecycle.py:_settle','resolution.py:_resume_play_effects']),
 'enchantments': ('Stats, costs, auras, copy and Silence', r'\b(copy|copies|cost|costs|silence|transform|becomes?|set|double|swap|give|gain|gains|have|has)\b|[+-]\d', ['game.py:_cost','game.py:_create_minion','systems.py:_refresh_auras','systems.py:_silence','batch_effects.py:_set_card_cost']),
 'generation_choices': ('Generation eligibility and resumable choices', r'\b(discover|random|choose|choice|add|get)\b', ['systems.py:_discover_deck','systems.py:_resolve_choice','game.py:_add','resolution.py:_resume_play_effects']),
 'combat_damage': ('Attack legality, damage and healing', r'\b(attack|attacks|damage|heal|restore|rush|charge|taunt|windfury|lifesteal|poisonous|immune|stealth|elusive|divine shield|freeze|frozen)\b', ['game.py:_attack','game.py:_resolve_combat','game.py:_attack_targets','systems.py:_damage','systems.py:_heal']),
 'zones_history': ('Draw, discard, shuffle, resurrection and history', r'\b(draw|discard|shuffle|resurrect|resummon|died|destroyed|played|cast|hand|deck|graveyard|return)\b', ['systems.py:_draw','systems.py:_discard_cards','systems.py:_shuffle_hand_card','systems.py:_after_play','batch_effects.py:_batch_effect']),
 'resources_classes': ('Mana, Corpses, class resources and Hero Powers', r'\b(corpses?|runes?|overload|mana|hero power|combo|outcast|overheal)\b', ['game.py:_power','game.py:_power_cost','game.py:_play','batch_effects.py:_batch_effect']),
 'secrets_locations': ('Secrets, locations and activations', r'\b(secret|location|durability|weapon)\b', ['secrets.py:_secret_event','locations.py:_place_location','game.py:_equip']),
 'dormant': ('Dormant and awakening', r'\b(dormant|awaken|awakens)\b', ['game.py:legal_actions','lifecycle.py:_begin_turn']),
 'quests': ('Quests, progress and rewards', r'\b(quest|questline|sidequest|reward)\b', ['systems.py:_queue_event','game.py:observe']),
 'hero_replacement': ('Hero replacement and alternate powers', r'\b(replace|replacement|hero card)\b', ['game.py:_play','game.py:_base_power']),
 'rewind': ('Rewind and state restoration', r'\brewind\b', ['game.py:step','resolution.py:_resume_play_effects']),
 'modern_keywords': ('Modern composite mechanics', r'\b(imbue|herald|shatter|prepare|kindred|fabled|colossal|imbued|heralded|starship|titan|miniaturize|gigantify|forge|infuse|excavate|disguised)\b', ['batch_effects.py:_kindred','game.py:_play','systems.py:_system_effect']),
 'deck_legality': ('Format and exceptional deck construction', r'\b(start of game|starting deck|deckbuilding|deck building|rune|runes|fabled)\b|deck.*\b(40|50|60)\b', ['decks.py:validate','decks.py:eligible']),
 'fallback_review': ('Unclassified card-specific behavior', r'(?!)', ['game.py:_effect','systems.py:_system_effect','batch_effects.py:_batch_effect']),
}
PRIORITY = ['resolution_events','enchantments','generation_choices','deck_legality','combat_damage','zones_history','resources_classes','secrets_locations','dormant','quests','hero_replacement','rewind','modern_keywords','fallback_review']

def digest(data): return hashlib.sha256(data).hexdigest()
def fingerprint(root):
 paths=(sorted((root/'expanded').glob('*.py'))+sorted((root/'expanded').glob('*.json'))+sorted((root/'engine').glob('*.py'))+[root/'data/standard/manifest.json',root/'standard/catalog.py']+sorted((root/'tests').glob('test_expanded*.py')))
 h=hashlib.sha256()
 for p in paths:h.update(str(p.relative_to(root)).encode());h.update(p.read_bytes())
 return h.hexdigest()
def classify(card):
 text=html.unescape(re.sub('<[^>]+>',' ',card.get('text',''))).lower()
 text+=' '+' '.join(card.get('mechanics',[])+card.get('referencedTags',[])).lower()
 if card.get('type')=='HERO':text+=' hero card'
 if card.get('type')=='LOCATION':text+=' location'
 if card.get('runes'):text+=' runes'
 result=[]
 for key,(_,pattern,_) in FAMILIES.items():
  matches=sorted(set(m.group(0) for m in re.finditer(pattern,text)))
  if matches:result.append({'system':key,'matched_terms':matches,'method':'provisional_metadata_text_hint'})
 return result or [{'system':'fallback_review','matched_terms':[],'method':'no_hint_matched_not_vanilla_certification'}]

def build(project, output):
 candidate=project/'staging/rebased-88';before=fingerprint(candidate);inputs={}
 spec_path=Path(__file__).with_name('scope_ledger_spec.json')
 spec=json.loads(spec_path.read_text())
 def read(path):
  data=path.read_bytes();inputs[str(path.relative_to(project))]=digest(data);return data
 manifest=json.loads(read(project/'data/standard/manifest.json'))
 for name,wanted in manifest['files_sha256'].items():
  if Path(name).name!=name:raise ValueError('Invalid manifest path')
  if digest(read(project/'data/standard'/name))!=wanted:raise ValueError('Catalog hash mismatch: '+name)
 catalog=json.loads(read(project/'data/standard/cards.json'));ids={c['id'] for c in catalog}
 if len(ids)!=len(catalog) or len(catalog)!=manifest['standard_catalog_count']:raise ValueError('Catalog IDs/count inconsistent')
 archive=json.loads(gzip.decompress(read(project/'data/standard/all_cards.json.gz')));metadata={c['id']:c for c in archive}
 if len(metadata)!=len(archive):raise ValueError('Archive IDs duplicated')
 tags=json.loads(read(project/'data/standard/card_tags.json'))
 index=json.loads(read(candidate/'expanded/implementation_index.json'));written=set(index['implemented_card_ids'])
 if not written<=ids or len(written)!=index['effect_implementations_written']:raise ValueError('Implementation inventory inconsistent')
 gaps=json.loads(read(candidate/'expanded/fidelity_gaps.json'))['gaps']
 receipt_path=candidate/'runs/expanded_validation/validation.json';receipt=json.loads(read(receipt_path))
 dependency_path=candidate/'runs/dependency_audit/references.json';prior_dependency=json.loads(read(dependency_path)) if dependency_path.exists() else None
 references=defaultdict(list);tests=defaultdict(list);declarations=defaultdict(list);edges=[];entrypoints={};source_urls={}
 source_paths=sorted((candidate/'expanded').glob('*.py'))+sorted((candidate/'engine').glob('*.py'))
 # Include local token metadata without evaluating any executable expression.
 for path in source_paths:
  source=read(path).decode();tree=ast.parse(source)
  for node in tree.body:
   if isinstance(node,ast.Assign) and isinstance(node.value,ast.Dict):
    for k,v in zip(node.value.keys,node.value.values):
     if isinstance(k,ast.Constant) and isinstance(k.value,str):
      try:raw=ast.literal_eval(v)
      except (ValueError,TypeError):continue
      if isinstance(raw,dict) and raw.get('type') and ('name' in raw or k.value.startswith('TOKEN_')):metadata.setdefault(k.value,dict(raw,id=k.value))
 for path in source_paths:
  source=read(path).decode();tree=ast.parse(source);rel=str(path.relative_to(project))
  parents={child:node for node in ast.walk(tree) for child in ast.iter_child_nodes(node)}
  for node in ast.walk(tree):
   if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)):
    entrypoints.setdefault(path.name+':'+node.name,[]).append({'file':rel,'line':node.lineno})
   if isinstance(node,ast.Constant) and isinstance(node.value,str) and node.value in metadata:
    ancestor=node;container=None
    while ancestor in parents:
     ancestor=parents[ancestor]
     if isinstance(ancestor,(ast.FunctionDef,ast.AsyncFunctionDef)):container=ancestor.name;break
    references[node.value].append({'file':rel,'line':node.lineno,'function':container,'meaning':'literal_occurrence_only'})
  for node in tree.body:
   if isinstance(node,ast.Assign) and isinstance(node.value,ast.Dict):
    names=[n.id for n in node.targets if isinstance(n,ast.Name)]
    for key,value in zip(node.value.keys,node.value.values):
     if not isinstance(key,ast.Constant) or key.value not in metadata:continue
     try:literal=ast.literal_eval(value)
     except (ValueError,TypeError):literal=None
     declarations[key.value].append({'file':rel,'line':value.lineno,'registries':names,'literal_definition':literal,'fully_literal':literal is not None})
     for target in sorted({n.value for n in ast.walk(value) if isinstance(n,ast.Constant) and isinstance(n.value,str) and n.value in metadata}):
      edges.append({'source':key.value,'target':target,'file':rel,'line':value.lineno,'meaning':'literal_reference_not_certified_generation'})
 for path in sorted((candidate/'tests').glob('test_expanded*.py')):
  tree=ast.parse(read(path).decode());rel=str(path.relative_to(project))
  for node in ast.walk(tree):
   if isinstance(node,ast.FunctionDef) and node.name.startswith('test_'):
    for cid in {n.value for n in ast.walk(node) if isinstance(n,ast.Constant) and isinstance(n.value,str) and n.value in metadata}:
     tests[cid].append({'file':rel,'line':node.lineno,'test':node.name,'meaning':'literal_reference_not_assertion_coverage'})
 # Evidence catalog is searchable, but a URL in a document is not a verified trace.
 doc_index=[]
 for path in sorted((project/'docs').glob('*.md')):
  content=read(path).decode();urls=sorted(set(re.findall(r'https?://[^\s<>\)\]]+',content)))
  mentions=sorted(set(re.findall(r'\b[A-Za-z][A-Za-z0-9]*_[A-Za-z0-9_]+\b',content)) & metadata.keys())
  if mentions:doc_index.append({'file':str(path.relative_to(project)),'card_ids':mentions,'urls':urls,'evidence_quality':'unreviewed_document_reference'})
 graph=defaultdict(set)
 for edge in edges:graph[edge['source']].add(edge['target'])
 def closure(cid):
  seen=set();pending=list(graph[cid])
  while pending:
   x=pending.pop()
   if x in seen:continue
   seen.add(x);pending.extend(graph[x]-seen)
  return sorted(seen)
 rows=[]
 for c in sorted(catalog,key=lambda c:c['id']):
  cid=c['id'];hints=classify(c)
  rows.append({'id':cid,'name':c['name'],'raw_card':c,'raw_tags':tags.get(cid),'metadata_imported':True,'effect_written':cid in written,'implementation_inventory_status':'written_unverified' if cid in written else 'missing',
   'system_hints':hints,'reviewed_system_owners':None,'semantic_mapping_reviewed':False,'source_declarations':declarations[cid],'source_literal_references':references[cid],'test_literal_references':tests[cid],
   'suite_evidence_ref':'validation_evidence','per_card_regression_certified':False,'independent_validation':'not_certified',
   'declared_reference_closure':closure(cid),'dependency_closure_certified':False,
   'specific_fidelity_gap_ids':[g['id'] for g in gaps if cid in g.get('cards',[])],
   'global_fidelity_gap_ids':[g['id'] for g in gaps if not g.get('cards')],
   'document_references':[d['file'] for d in doc_index if cid in d['card_ids']]})
 generated=[]
 for cid in sorted(set(references)-ids):
  raw=metadata[cid]
  generated.append({'id':cid,'raw_card':raw,'role':'non_target_catalog_reference_not_proven_generated','collectible_in_archive':raw.get('collectible',False),'source_references':references[cid],
   'incoming_declared_references':[e for e in edges if e['target']==cid],'test_literal_references':tests[cid],'system_hints':classify(raw),'implementation_status':'not_inferred_from_reference','eligible_for_generation':None,'dependency_closure_certified':False})
 backlog=[]
 prerequisites={'resolution_events':[],'enchantments':['resolution_events'],'generation_choices':['resolution_events','deck_legality'],'deck_legality':[],'combat_damage':['resolution_events','enchantments'],'zones_history':['resolution_events','enchantments'],'resources_classes':['resolution_events','deck_legality'],'secrets_locations':['resolution_events','combat_damage'],'dormant':['resolution_events'],'quests':['resolution_events','zones_history'],'hero_replacement':['resources_classes','enchantments'],'rewind':['resolution_events','zones_history','enchantments'],'modern_keywords':['resolution_events','generation_choices'],'fallback_review':[]}
 for rank,key in enumerate(PRIORITY,1):
  matches=[r for r in rows if key in [h['system'] for h in r['system_hints']]]
  backlog.append({'priority':rank,'id':key,'title':FAMILIES[key][0],'mapping_status':'provisional_overlapping_candidates','candidate_card_ids':[r['id'] for r in matches],'missing_effect_card_ids':[r['id'] for r in matches if not r['effect_written']],
   'counts':{'candidate_cards':len(matches),'missing_effects':sum(not r['effect_written'] for r in matches)},'prerequisites':prerequisites[key],
   'current_code_entrypoints':[{'symbol':symbol,'locations':entrypoints.get(symbol,[]),'status':'existing_code_to_review' if entrypoints.get(symbol) else 'no_matching_entrypoint_found'} for symbol in FAMILIES[key][2]],
   'acceptance_scenario_ids':spec[key]['acceptance_scenario_ids'],'work_required':spec[key]['work_required'],'completion_status':'not_certified','independent_evidence_required':'Patch-matched expected traces or authoritative rules for each affected interaction; historical implementations are comparison evidence only.'})
 report={'schema':1,'scope':'Regular Standard, all classes; frozen patch, not live rotation certification','patch':manifest['patch'],'as_of':manifest['as_of'],'candidate_root':'staging/rebased-88','candidate_fingerprint':before,'input_sha256':inputs,
  'counts':{'catalog':len(rows),'written':len(written),'missing':len(ids-written),'semantic_mappings_reviewed':0,'dependency_closures_certified':0,'independently_certified_cards':0,'non_target_referenced_records':len(generated),'recorded_fidelity_gaps':len(gaps)},
  'validation_evidence':{'receipt_file':str(receipt_path.relative_to(project)),'receipt':receipt,'matches_current_candidate':bool(receipt.get('success') and receipt.get('fingerprint')==before),'per_card_pass_not_inferred':True},
  'prior_dependency_evidence':{'file':str(dependency_path.relative_to(project)),'fingerprint':prior_dependency.get('code_fingerprint') if prior_dependency else None,'matches_current_candidate':bool(prior_dependency and prior_dependency.get('code_fingerprint')==before),'semantic_closure_certified':False},
  'builder_sha256':digest(Path(__file__).read_bytes()),'specification_sha256':digest(spec_path.read_bytes()),'full_standard_ready':False,'limitations':['Text/tag grouping is provisional and overlapping, not executable behavior.','All reviewed system owners remain null pending semantic review.','Source and test literals are references, not proof of implementation or assertions.','Non-target source references can be heroes, metadata, or historical identities, not necessarily generated objects.','Computed IDs, metadata-linked objects and dynamic pool members are not fully enumerated; recursive semantic closure remains open.','Existing suite receipt applies only to its recorded fingerprint.'],
  'cards':rows}
 pools={'schema':1,'status':'unresolved_pool_inventory','complete':False,'candidate_source_card_ids':[r['id'] for r in rows if any(h['system']=='generation_choices' for h in r['system_hints'])],
  'required_fields_per_reviewed_pool':['source_card_id','effect_or_operation','zone','format_patch','eligibility_predicate','exclusions','weighting','replacement_rule','owner_class_context','complete_member_ids','recursive_dependencies','evidence'],
  'reviewed_pools':[],'warning':'Broad random/choice hints include target randomness and deck choices; not all candidates generate cards. Never substitute the implemented subset for the legal pool.'}
 if fingerprint(candidate)!=before:raise ValueError('Candidate changed during inventory')
 assert len({r['id'] for r in rows})==manifest['standard_catalog_count']
 assert all(r['raw_tags'] is not None for r in rows)
 assert not(set(r['id'] for r in generated)&ids)
 assert all(e['source'] in metadata and e['target'] in metadata for e in edges)
 assert all(r['reviewed_system_owners'] is None and not r['dependency_closure_certified'] for r in rows)
 output.mkdir(parents=True,exist_ok=True)
 artifacts={'coverage-ledger.json':report,'shared-system-backlog.json':{'schema':1,'ordering':'dependency-risk-first; counts are provisional, not measured effort','systems':backlog},'generated-references.json':{'schema':1,'complete':False,'records':generated,'declared_edges':edges},'generation-pools.json':pools,'rule-document-index.json':{'schema':1,'documents':doc_index},'known-fidelity-gaps.json':{'schema':1,'gaps':gaps}}
 for name,data in artifacts.items():(output/name).write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
 with (output/'coverage-ledger.csv').open('w',newline='') as f:
  w=csv.writer(f);w.writerow(['id','name','class','type','effect_written','provisional_systems','mapping_reviewed','dependencies_certified','source_references','test_literal_references'])
  for r in rows:w.writerow([r['id'],r['name'],r['raw_card'].get('cardClass'),r['raw_card']['type'],r['effect_written'],';'.join(h['system'] for h in r['system_hints']),False,False,len(r['source_literal_references']),len(r['test_literal_references'])])
 counts=report['counts'];lines=['# Scope checkpoint — 2026-09-23','','Static inventory only. No simulator, notebook, game, training or engine fixture executed.','',f"Catalog: **{counts['catalog']}**. Effects written: **{counts['written']}**. Missing: **{counts['missing']}**.",f"Current suite receipt matches candidate: **{report['validation_evidence']['matches_current_candidate']}**. Last receipt: {receipt['tests_run']} checks; do not treat it as current.",'','All card IDs have inventory rows. **Semantic mapping is not complete:** reviewed owners remain null for all rows. This block establishes the ledger and a review queue; it does not complete milestone 1.','','| Priority | Shared system | Candidate cards* | Missing effects* |','| --- | --- | ---: | ---: |']
 for b in backlog:lines.append(f"| {b['priority']} | {b['title']} | {b['counts']['candidate_cards']} | {b['counts']['missing_effects']} |")
 lines+=['','*Overlapping text/tag hints, not verified affected-card counts or additive totals. Exact candidate IDs, matching terms, entry points and prerequisites are in the JSON files.','','## Files','','- `coverage-ledger.json`: raw card records/tags, references, receipt linkage and explicit unknowns for every catalog ID.','- `coverage-ledger.csv`: compact inventory for browsing.','- `shared-system-backlog.json`: prioritized provisional groups, exact IDs, prerequisites and source entry points.','- `generated-references.json`: non-target literal references, kept separate from collectible coverage.','- `generation-pools.json`: unresolved pool review queue and required schema.','- `rule-document-index.json`: existing document references; their URLs are not automatically trusted as conformance evidence.','- `known-fidelity-gaps.json`: snapshot of the existing gap register.','- `rule-evidence-checklist.md`: twelve high-impact scenarios and evidence acceptance requirements.','','## Next bounded block','','Proposed ceiling: 90 active minutes. Review the summon/play lifecycle and its affected-card mapping first. Deliver an explicit phase contract, a checked source-to-event map, and evidence status for scenarios 1–4. Implement no new collectible cards. If independent outcomes cannot be established, report the missing evidence and stop instead of guessing. Other mechanic-family mappings remain a review backlog; no whole-project completion estimate yet.']
 (output/'CHECKPOINT.md').write_text('\n'.join(lines)+'\n')
 result={'counts':counts,'receipt_matches_current':report['validation_evidence']['matches_current_candidate'],'candidate_fingerprint':before,'structural_checks':'passed','engine_executed':False}
 (output/'structural-checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--project',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);a=parser.parse_args();build(a.project.resolve(),a.output.resolve())
