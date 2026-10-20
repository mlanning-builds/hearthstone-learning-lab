"""Extend completion audit with an exhaustive static source inventory.

This finds explicit coverage limits and declaration loss, not all silent bugs.
No gameplay, training, model updates or regression suites are executed.
"""
from pathlib import Path
import ast,csv,json,runpy,sys
from collections import Counter,defaultdict
from dataclasses import asdict
ROOT=Path(__file__).resolve().parents[1]
B=runpy.run_path(str(ROOT/'tools/audit_project_completion.py'))
C=B['C'];D=B['OUT'];R=B['R'];U=B['U'];FP=B['FP'];refs=B['refs'];evidence=B['evidence'];source=B['source'];trees=B['trees']
from expanded import cards
from expanded.effect_schema import validate_namespace
from expanded.generation_cards import PoolRequest,pool
from expanded.generation_families import reviewed_contract
from expanded.historical_generation_catalog import historical_contract
from expanded.generation_catalog import load_universe as standard_universe,standard_contract
from expanded.historical_copy_batches import CHOOSE_SPELL_BRANCHES
from expanded.gelbin import AURA_IDS,AURA_RULES
from standard.catalog import CLASSES
TASKS=list(B['TASKS']);findings=[]
def add(key,title,path,needle,trigger,action,kind='confirmed_partial',effort='large',cards_=()):
 ev=refs(path,needle);assert ev,(key,path,needle)
 row=dict(id='SOURCE:'+key,title=title,classification=kind,affected_cards=list(cards_),evidence=ev,trigger=trigger,action=action,done_when='Source-backed behavior is implemented through the production path, with controlled affected-rule cases and no unsupported guard for valid states.',effort_band=effort)
 findings.append(row)
 if kind in ('confirmed_partial','default_contract_missing','confirmed_dispatch_loss'):
  TASKS.append(dict(id=row['id'],area='source_confirmed_behavior',title=title,status='partial',required_behavior=trigger,evidence=ev,action=action,done_when=row['done_when'],effort_band=effort,effort_confidence='low; qualitative remaining work only',validation=kind))
add('bashana_contract','Bashana allocation contract has no production default','expanded/learned_spells.py','Missing reviewed Bashana carve allocation distribution','Play MEND_046 with room for at least one Runed Treant. carve_allocation_contract is only read; no production assignment found.','Establish complete allocation probabilities and full-hand semantics; provide a sourced contract and connected default. Do not invent probabilities.', 'default_contract_missing',cards_=('MEND_046',))
add('watfin_contract','Watfin suspicious-mutation contract has no production default','expanded/exceptional_finish.py','Missing reviewed suspicious mutation distribution','Play JAIL_EVENT_100; suspicious_mutation_contract is only read and the default approximation installer does not supply it.','Establish complete name/type/stat/cost mutation semantics and distribution and connect them to the default simulator.','default_contract_missing',cards_=('JAIL_EVENT_100',))
add('malygos_repeats','Stacked Malygos spell repetitions reject','expanded/fabled_effects.py','Malygos repetition stacking needs reviewed semantics','Cast an Arcane spell with multiple qualifying Malygos sources or another active repeat effect.','Implement repeat composition and exact checkpoint/target/charge ordering.',cards_=('TIME_852t1',))
add('sinestra_repeats','Stacked Sinestra spell repetitions reject','expanded/colossal_bodies.py','Sinestra repetition stacking needs reviewed semantics','Cast an off-class spell with multiple Sinestras or another repeat effect.','Implement repeat composition across Sinestra and other repetition sources.',cards_=('CATA_154',))
add('atiesh_lifesteal','Atiesh plus spell Lifesteal rejects','expanded/game.py','Atiesh spell Lifesteal interaction needs reviewed semantics','Resolve a damaging Lifesteal spell while TIME_890t is equipped.','Resolve additive/multiplied damage, Lifesteal healing and replacement ordering.',cards_=('TIME_890t',))
add('vyranoth_remainder','Vyranoth uneven distribution rejects','expanded/stat_rules.py','Vyranoth remainder distribution requires reviewed ordering','Starting minion Costs total 100, but current deck-minion count does not divide 50.','Establish allocation of leftover Attack/Health, implement it and verify conservation and weighting.',cards_=('CATA_213',))
add('companion_cost_gap','Animal Companion upgrades reject empty successor costs','expanded/future_summons.py','Companion replacement at empty successor Cost requires reviewed boundary semantics','An upgraded companion has no eligible Beast at the next requested cost.','Implement the actual empty-cost boundary behavior without restricting the outcome pool.',cards_=('MEND_300','MEND_303','MEND_307'))
add('underbelly_generated','Generated King of the Underbelly lacks fallback behavior','expanded/remaining_setup.py','Generated Underbelly has no reviewed fallback contraband pool','Play generated JAIL_831 in a game without submitted contraband selections.','Establish and implement generated-card fallback selections and complete candidate membership.',cards_=('JAIL_831',))
add('king_llane_duplicates','Garona rejects multiple held King Llanes','expanded/garona.py','Multiple held King Llane copies require independent resolution evidence','Garona resolves with multiple TIME_875t in the opposing hand.','Implement physical victim selection/order and destruction/health effects for duplicates.',cards_=('TIME_875','TIME_875t'))
add('excavate_class_change','Legendary Excavate class-transition reward is unresolved','expanded/historical_excavate.py','Class changed before Legendary Excavate reward','Reach fourth-tier excavation, then resolve it after changing into a class without CLASS_REWARDS.','Establish reward-tier routing after class changes and implement correct history/resource transitions.')
add('silas_full_nonminion','Silas rotation rejects an all-non-minion full receiving board','expanded/historical_copy_batches.py','Silas rotation into seven non-rotating entities','Rotate a minion toward a full board containing no transferable edge minion.','Implement position/capacity/destruction semantics for incoming minions alongside locations/permanents.')
add('behemoth_duplicates','Blackwater Lure rejects multiple Behemoths','expanded/historical_colossal.py','Multiple Blackwater Behemoths need a reviewed Lure target contract','Resolve a Lure with more than one controlled Blackwater Behemoth.','Implement actual parent/identity/random choice semantics for duplicated/stolen Behemoths.',cards_=('TSC_216',))
add('muradin_second_hammer','Muradin rejects binding a second physical Hammer','expanded/muradin.py','Binding a second Hammer requires reviewed replacement semantics','Repeat Muradin retrieval while holding a bound Hammer and another physical Hammer exists.','Implement replacement/coexistence and copy/return ownership semantics.',cards_=('TIME_209',))
add('colossal_copy_entry','Dormant or silenced Colossal copy entry rejects','expanded/colossals.py','Colossal dormant/silenced-copy entry requires reviewed semantics','Summon a copy of a silenced or Dormant Colossal, or supply Dormant duration on Colossal entry.','Implement correct body/appendage entry and ordering for these states.')
add('rogue_free_imbue','Free triggering of Rogue Imbued power rejects','expanded/imbue_consumers.py','Free Rogue Imbue Rewind timing awaits conformance review','Wisprider triggers END_000p, for example after off-class acquisition.','Integrate free Rewind activation, choice state and timing without a paid-power action.',cards_=('EDR_519','END_000p'))
add('camouflage_exhausted','Camouflage Mount rejects an exhausted Bonus Effect pool','expanded/historical_utility_spells.py','Camouflage Mount has no eligible Bonus Effect','Cast the mount on a minion already carrying all eligible Bonus Effects.','Establish and implement no-new-keyword/Deathrattle Chameleon behavior.')
# Direct dispatcher-loss comparison: separate legitimate location activation from lost minion Battlecries.
shadowed={}
for name,module in list(sys.modules.items()):
 if not name.startswith('expanded.') or name=='expanded.cards':continue
 for table in ('RULES','TOKEN_RULES'):
  values=getattr(module,table,{})
  if not isinstance(values,dict):continue
  for cid,rule in values.items():
   if cid in R and isinstance(rule,(tuple,list)) and len(rule)==2 and rule[1] and cards.RULES.get(cid)==('none',[]):
    shadowed.setdefault(cid,[]).append(dict(module=name,table=table,program=repr(rule)))
for cid,module,needle in [('DAL_609','historical_generation_primitives.py',"'DAL_609':"),('WW_091','historical_copy_batches.py',"'WW_091':")]:
 assert cid in shadowed and R[cid]['type']=='MINION'
 add('lost_battlecry_'+cid,R[cid]['name']+' Battlecry overwritten by empty final binding','expanded/'+module,needle,'Final cards.RULES entry is (none, []), although its original declaration contains a nonempty Battlecry and frozen text still requires it.','Preserve both passive/cost rules and the original Battlecry during declaration merge; add paid-play regression.',kind='confirmed_dispatch_loss',effort='small',cards_=(cid,))
# Enumerate all missing Jerry split identities, rather than hide twenty-six cases in one vague note.
choose_gaps=[cid for cid,d in R.items() if d.get('collectible') and d.get('type')=='SPELL' and 'CHOOSE_ONE' in d.get('mechanics',()) and cid not in CHOOSE_SPELL_BRANCHES]
for cid in sorted(choose_gaps):
 add('jerry_split_'+cid,'Jerry Rig Carpenter cannot split '+R[cid]['name'],'expanded/historical_copy_batches.py','Jerry split family missing','A deck contains '+cid+' when Jerry preflights all actual eligible Choose One spells.','Add the two real branch identities/programs and preserve physical Card modifiers and correct hand-entry behavior.',effort='medium',cards_=(cid,))
aura_gaps=sorted(AURA_IDS-set(AURA_RULES))
for cid in aura_gaps:
 add('aura_placement_'+cid,'Gelbin cannot directly place '+R.get(cid,U.records.get(cid,{})).get('name',cid),'expanded/gelbin.py','Aura placement is not implemented','Gelbin sees '+cid+' in the owner deck. Direct placement differs from ordinary casting.','Implement a direct-placement Aura program with correct duration, source and listener semantics. Link to its ordinary card task if still unwritten.',effort='medium',cards_=(cid,))
# Guards requiring a legal-reachability witness, not automatically confirmed missing behavior.
for key,title,path,needle,trigger in [
 ('nested_effect_frames','Nested card-effect frame boundary','expanded/resolution.py','Nested card-effect frames are not supported yet','Starting an additional play frame while another frame is suspended.'),
 ('nested_minion_frames','Nested minion after-play boundary','expanded/summons.py','Nested minion after-play sequences are not supported','Starting another minion after-play sequence during an active one.'),
 ('choice_event_boundary','Choice-disallowed event boundary','expanded/systems.py','Choices inside this event boundary are not supported','A valid listener opens a choice in an event marked allow_choices=False.'),
 ('reentrant_listener','Re-entrant event-listener boundary','expanded/systems.py','Re-entrant trigger compensation is not supported','The same listener/wanted pair re-enters outside the four explicit exceptions.'),
 ('right_side_departed_source','Right-side summon continuation after source departure','expanded/systems.py','Right-side summon source left play','A source leaves before a right-side summon continuation.'),
 ('forge_target_modes','Composite Battlecry target conflict','expanded/minion_forge.py','Incompatible composite Battlecry targets','Two parts would require incompatible target modes; zero such pairs in current default Nefarius/Zombeast contracts.'),
 ('composite_dormancy','Composite minion conflicting Dormant durations','expanded/game.py','Conflicting composite Dormant durations','A compiled composite has multiple distinct Dormant durations; determine if any default pair can produce it.'),
 ('herald_ambiguous','Off-class multi-army Herald routing','expanded/herald.py','Off-class Herald army selection requires reviewed routing','Owner has no army and source classes do not uniquely identify one. Establish a valid source witness.'),
 ('learned_choose_targets','Learned Choose One branch-specific targeting','expanded/learned_spells.py','Learned Choose One targeting requires branch-specific review','A learned spell has different non-none target modes across branches. Crystal Power is structurally affected; verify reachable learning pool.'),
 ('void_soul_cap','Void Soul scaling silently caps at ten','expanded/future_summons.py','p.void_soul_level=min(10','Future upgrades at level ten are clamped; establish whether the client caps, skips empty costs or continues.'),
]:
 add(key,title,path,needle,trigger,'Establish a reachable valid case and intended rule. If reachable, implement it; otherwise document the invariant that makes the guard defensive.',kind='reachability_or_fidelity_review')
# Schema holes are a separate robustness coding package, not 515 missing card effects.
reports=validate_namespace(vars(cards));uncovered=sorted(set().union(*(v.uncovered for v in reports.values())))
TASKS.append(dict(id='VALIDATION:operand_schemas',area='definition_validation',title='Detailed operand schemas for '+str(len(uncovered))+' operation names',status='partial',required_behavior='Malformed effect operands must fail at declaration validation. Current validator reports these names without detailed arity/type schemas.',evidence=refs('expanded/effect_schema.py','schema=SCHEMAS.get(name)'),action='Define operand and nested-program schemas; verify malformed operands are rejected. Do not conflate schema coverage with effect fidelity.',done_when='Every admitted operation has a matching detailed schema or a narrowly documented alternative validator.',effort_band='large',effort_confidence='low; 515 names vary substantially in complexity',validation='static_schema_gap',operation_names=uncovered))
# Full static inventory: every file, class/function, explicit raise and generation call.
functions=[];all_raises=[];generation_calls=[];stubs=[];literal_refs=defaultdict(list)
for path,tree in trees.items():
 rel=str(path.relative_to(ROOT));text=source[path];parents={child:node for node in ast.walk(tree) for child in ast.iter_child_nodes(node)}
 def enclosing(node):
  found=[]
  while node in parents:
   node=parents[node]
   if isinstance(node,(ast.ClassDef,ast.FunctionDef,ast.AsyncFunctionDef)):found.append(node.name)
  return '.'.join(reversed(found))
 for node in ast.walk(tree):
  if isinstance(node,ast.Constant) and isinstance(node.value,str) and node.value in R:
   literal_refs[node.value].append(dict(path=rel,line=node.lineno,context=enclosing(node)))
  if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)):
   functions.append(dict(path=rel,line=node.lineno,name=enclosing(node)+'.'+node.name))
   body=node.body
   if body and isinstance(body[0],ast.Expr) and isinstance(body[0].value,ast.Constant) and isinstance(body[0].value.value,str):body=body[1:]
   if len(body)==1 and (isinstance(body[0],ast.Pass) or isinstance(body[0],ast.Return) and (body[0].value is None or isinstance(body[0].value,ast.Constant) and body[0].value.value in (False,None))):stubs.append(dict(path=rel,line=node.lineno,function=node.name))
  if isinstance(node,ast.Raise):
   all_raises.append(dict(path=rel,line=node.lineno,context=enclosing(node),expression=ast.get_source_segment(text,node)))
  if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id in ('pool','PoolRequest'):
   constant={};dynamic={}
   for kw in node.keywords:
    try:constant[kw.arg]=ast.literal_eval(kw.value)
    except (ValueError,TypeError):dynamic[kw.arg]=ast.get_source_segment(text,kw.value)
   generation_calls.append(dict(path=rel,line=node.lineno,context=enclosing(node),constant_kwargs=constant,dynamic_kwargs=dynamic,args=[ast.get_source_segment(text,a) for a in node.args],membership_audited=False))
# Resolve constant requests against all class contracts, without pretending dynamic selectors are covered.
SU=standard_universe()
for item in generation_calls:
 if item['args'] or item['dynamic_kwargs'] or None in item['constant_kwargs']:continue
 try:
  req=pool(**item['constant_kwargs']);out=set();covered=True
  for hero in CLASSES:
   contract=reviewed_contract(req,hero)
   if contract is None:contract=historical_contract(req,hero,U) if req.era=='past' else standard_contract(req,hero,SU)
   if contract is None:covered=False;break
   out.update(contract.card_ids)
  item.update(membership_audited=covered,request=asdict(req),eligible_union=len(out),missing_direct_ids=sorted(out-set(R)))
 except Exception as ex:item.update(membership_error=type(ex).__name__+': '+str(ex))
# Every old fidelity entry receives source anchors, but source linkage is not semantic proof.
fidelity=json.loads((D/'fidelity-reconciliation.json').read_text())
for item in fidelity:
 ev=[]
 for cid in item.get('cards',[]):ev.extend(literal_refs.get(cid,[])[:12])
 if ev:item['source_evidence']=item.get('source_evidence',[])+ev[:24]
 item['source_linkage_complete']=bool(item['source_evidence'])
 item['semantic_resolution_complete']=False
# All 508 previously identified explicit unsupported guards are retained with context.
guards=json.loads((D/'unsupported-guards.json').read_text());limits={(e['path'],e['line']):f['id'] for f in findings for e in f['evidence']}
for g in guards:
 e=g['expression'].lower();key=(g['path'],g['line']);g['containing_context']=next((r['context'] for r in all_raises if (r['path'],r['line'])==key),'')
 if key in limits:g.update(classification='documented_limit_or_missing_contract',finding=limits[key])
 elif any(w in e for w in ('invalid','unknown','malformed','duplicate','must be','requires exactly','cannot receive two','mismatch','changed; review','outside the source','differs from source','must retain','must cover')):g['classification']='defensive_validation_candidate'
 elif any(w in e for w in ('cannot overwrite','cannot replace','sequence already','selected','left hand','left its deck','source changed','was not offered','no longer available','must be detached','use zone casting')):g['classification']='state_or_scheduling_invariant_requires_call_path_review'
 elif any(w in e for w in ('distribution','policy','contract','recipe','printing','treasure weights','deck weights','offer','distractor')):g['classification']='contract_validation_or_exact_mode_gate'
 elif any(w in e for w in ('not implemented','not admitted','no on-play','lacks internal','missing','unwritten','not connected')):g['classification']='dependency_or_dispatch_gate_requires_reachability_review'
 else:g['classification']='context_review_required'
# Find source-level public-field to feature omissions; these are review candidates only.
feature_text=(C/'expanded/features.py').read_text();public={}
for node in ast.walk(trees[C/'expanded/game.py']):
 if isinstance(node,ast.Assign):
  for target in node.targets:
   if isinstance(target,ast.Subscript) and isinstance(target.value,ast.Name) and target.value.id=='public':
    sub=target.slice
    if isinstance(sub,ast.Constant) and isinstance(sub.value,str):public.setdefault(sub.value,[]).append(node.lineno)
feature_candidates=[dict(field=k,lines=v,classification='not_named_in_feature_encoder; review whether relevant/player-level/indirectly represented') for k,v in sorted(public.items()) if k not in feature_text]
# Pair conflict guard proven unreachable through the present default component contracts.
from expanded.nefarius_pools import contracts as nc
from expanded.zombeast_pools import contracts as zc
pairs={}
for contracts,kind in ((nc(),'dragon'),(zc(),'zombeast')):
 pairs[kind]=[(a.card_id,b.card_id) for a in contracts[(kind,1)] for b in contracts[(kind,2)] if R[a.card_id]['cost']+R[b.card_id]['cost']<=10 and a.target!='none' and b.target!='none' and a.target!=b.target]
summary=dict(date='2026-10-19',fingerprint=FP,static_inventory_complete_for_scanned_sources=True,semantic_audit_complete=False,whole_game_completion_percentage=None,scope_limit='All candidate expanded/ and engine/ plus public facade top-level Python files parsed. This does not establish all behavioral contracts, execution paths or independent client fidelity.',python_files=len(source),functions=len(functions),raise_sites=len(all_raises),unsupported_guard_sites=len(guards),guard_classifications=dict(Counter(g['classification'] for g in guards)),function_stubs=stubs,known_coding_work_packages=len(TASKS),coding_work_package_breakdown=dict(Counter(t['area'] for t in TASKS)),source_findings=len(findings),source_finding_classifications=dict(Counter(f['classification'] for f in findings)),jerry_missing_split_cases=len(choose_gaps),gelbin_missing_direct_placement_cases=len(aura_gaps),uncovered_operand_schema_names=len(uncovered),generation_call_sites=len(generation_calls),generation_calls_with_fully_constant_kwargs=sum(not x['dynamic_kwargs'] and not x['args'] for x in generation_calls),generation_calls_with_membership_checked=sum(x['membership_audited'] for x in generation_calls),generation_calls_requiring_review=sum(not x['membership_audited'] for x in generation_calls),fidelity_entries=len(fidelity),fidelity_entries_with_source_links=sum(g['source_linkage_complete'] for g in fidelity),fidelity_entries_semantically_closed=0,public_feature_review_candidates=len(feature_candidates),default_forge_incompatible_pairs=pairs,card_shadowed_nonempty_bindings=shadowed,missing_default_contracts=['carve_allocation_contract','suspicious_mutation_contract'],no_regressions_or_gameplay_or_training_executed=True)
for name,value in [('source-audit-summary.json',summary),('coding-tasks-expanded.json',TASKS),('source-findings.json',findings),('function-inventory.json',functions),('all-raise-sites.json',all_raises),('generation-call-sites.json',generation_calls),('unsupported-guards-classified.json',guards),('fidelity-source-review.json',fidelity),('public-feature-review.json',feature_candidates)]: (D/name).write_text(json.dumps(value,indent=2)+'\n')
with (D/'coding-tasks-expanded.csv').open('w',newline='') as file:
 w=csv.writer(file);w.writerow(['id','title','area','status','effort','action','done_when'])
 for t in TASKS:w.writerow([t['id'],t['title'],t['area'],t['status'],t['effort_band'],t['action'],t['done_when']])
lines=['# Expanded source audit — October 19, 2026','',f'**{len(TASKS)} confirmed coding work packages**, including 28 missing roots, two lost Battlecries, explicit unsupported cases, missing defaults, 26 Jerry split cases, five Aura placement cases, the earlier inheritance/control/feature cases, and one schema-coverage package. These units differ in size and overlap in dependencies; this is not a percentage or schedule.','',f'All {len(source)} selected Python files were parsed, {len(functions)} functions indexed, {len(all_raises)} raises indexed, and all {len(guards)} UnsupportedCard/NotImplementedError sites classified. This is exhaustive static enumeration within the stated files, **not an exhaustive semantic audit or a guarantee of no other missing behavior**.','', '## Material findings','', '- Kalecgos and Pop’gar lose their Battlecries during declaration assembly. Their registration counts overstated implementation completion. Empty location play programs for Bloodpetal Biome and Ruby Sanctum are intentional activation separation, not the same defect.', '- Bashana and Watfin require runtime distributions that are read but never assigned by production code/default profiles. These are registered Standard cards with incomplete executable defaults.', '- Jerry Rig Carpenter preflights all eligible Choose One spells, but 26 registered spells have no split-family mapping. They reject rather than being excluded from the pool.','- Gelbin recognizes five historical Auras that it cannot directly place. Celestial Aura is also one of the 28 missing spell roots; the other four are already registered with ordinary-cast effects but lack this placement path.', '- Stacked Malygos/Sinestra repeats, Atiesh spell Lifesteal, Vyranoth remainder allocation, generated Underbelly, duplicate Llanes/Behemoths/Hammers, Rogue free Imbue and several boundary interactions have explicit coverage limits.',f'- {len(uncovered)} admitted operation names lack detailed schemas. This is one validation-coverage family with many subcases, not that many missing card effects.', '- Default Nefarius and Zombeast contracts have zero affordable pairs with incompatible non-none target modes. That particular forge guard is not presently counted as a confirmed missing default-pool implementation.','', '## Concrete source findings','', '| Finding | Classification | Trigger |','| --- | --- | --- |']
for f in findings:lines.append('| '+f['title']+' | '+f['classification']+' | '+f['trigger'].replace('|','/')+' |')
lines+=['', '## Coverage still unresolved','',f'- {summary["generation_calls_requiring_review"]} generation call sites remain dynamic, invalid to resolve without context, or outside the constant-contract resolver. They are individually listed with source/function and parameter expressions. Do not mistake a constant-request scan for complete recursive generation closure.',f'- {summary["fidelity_entries_with_source_links"]}/160 old fidelity entries have current source links. **None is declared semantically closed solely by this linking pass.** The remaining contract-by-contract review must establish actual rules and supported paths.',f'- {len(feature_candidates)} public-field names are not named in the feature encoder. Five Questline flags are confirmed omissions; others may be intentionally omitted, indirectly represented, or not player-level fields and require individual review.', '- Generic dispatch fallback errors and pending-choice guards cannot be counted as bugs merely because they raise. A valid reachable witness is needed.', '- No new regressions, game traces, training, or independent-client comparisons were run. Saved tests only certify their own source fingerprints.', '', '## Read these ledgers','', '- [Expanded coding tasks](coding-tasks-expanded.csv) — current concrete implementation work, actions and acceptance criteria.', '- [Source findings](source-findings.json) — source lines and triggering conditions for each finding.', '- [Generation call sites](generation-call-sites.json) — every pool/PoolRequest call and unresolved parameter expressions.', '- [Fidelity source review](fidelity-source-review.json) — all 160 entries with available current anchors; unresolved semantics remain explicit.', '- [Classified unsupported guards](unsupported-guards-classified.json) — all explicit guards, including defensive checks and exact-mode contracts.', '- [Function inventory](function-inventory.json) and [all raises](all-raise-sites.json) — complete static source surfaces.', '- [Schema and totals](source-audit-summary.json) — counts and coverage limitations.', '', 'The earlier 34-task ledger was a lower bound. Use this expanded ledger for the newly found concrete work, but do not label the whole-game semantic audit finished. An exact whole-game percentage remains unjustified until the dynamic/reachable contracts and behavior cases are actually resolved.','']
(D/'EXPANDED-AUDIT.md').write_text('\n'.join(lines))
base=D/'README.md';base.write_text('> **Newer, broader audit:** [Expanded source audit](EXPANDED-AUDIT.md) and [expanded coding ledger](coding-tasks-expanded.csv) supersede the initial 34-task lower bound below.\n\n'+base.read_text())
print(json.dumps(summary,default=str)[:4500]);print(D/'EXPANDED-AUDIT.md')
