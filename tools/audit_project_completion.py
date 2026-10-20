"""Static project audit. No Game, training, gameplay or test execution."""
from pathlib import Path
import ast,csv,gzip,hashlib,json,sys
from collections import Counter
from dataclasses import asdict
ROOT=Path(__file__).resolve().parents[1]
C=ROOT/'staging/rebased-88';D=ROOT/'docs/engine-audit';sys.path.insert(0,str(C))
from expanded import cards
from expanded.status import code_fingerprint
from expanded.dependencies import declaration_operations,dependency_report
from expanded.generation_cards import PoolRequest,pool
from expanded.historical_generation_catalog import load_universe,historical_contract
from expanded.historical_generation import requests_for
from expanded.historical_spell_continuation import GIFT
from standard.catalog import CLASSES,load_catalog
R=cards.registry();U=load_universe();FP=code_fingerprint()
source={p:p.read_text() for base in (C/'expanded',C/'engine',ROOT/'hearthstone_sim') for p in base.glob('*.py')}
trees={p:ast.parse(t,filename=str(p)) for p,t in source.items()}
def refs(relative,needle=None):
 p=C/relative
 if not p.exists():p=ROOT/relative
 if not p.exists():return []
 lines=p.read_text().splitlines()
 found=[i for i,t in enumerate(lines,1) if needle is None or needle in t]
 return [dict(path=str(p.relative_to(ROOT)),line=i,text=lines[i-1].strip()[:220]) for i in found[:8]]
def evidence(*pairs):return [r for file,needle in pairs for r in refs(file,needle)]
# Broad metadata envelope is NOT automatically the reachable outcome set.
envelope=[]
for kind in ('MINION','SPELL','WEAPON','HERO','LOCATION'):
 ids=set(historical_contract(pool(era='past',card_type=kind),'MAGE',U).card_ids)
 envelope.append(dict(type=kind,eligible=len(ids),registered=len(ids&set(R)),missing=[dict(id=k,name=U.records[k]['name']) for k in sorted(ids-set(R))]))
# Derive roots from actual normalized Warden contract, not old cached counts.
warden,=requests_for('TIME_052');minions=set(historical_contract(warden,'MAGE',U).card_ids)
standard={c['id']:c for c in load_catalog()}
spells=set(historical_contract(pool(era='past',card_type='SPELL'),'MAGE',U).card_ids)
missing_spells=sorted(spells-set(R));assert len(missing_spells)==28
# Every literal root and currently declared historical request, all eleven classes.
ops=declaration_operations(vars(cards))
for cid,ids in GIFT.items():
 for cid2 in ids:ops.setdefault(cid,[]).append(('add',cid2,1))
literal=dependency_report(ops,R,roots=R)
request_roots={}
def visit(x,root):
 if isinstance(x,PoolRequest) and x.era=='past':request_roots.setdefault(x,set()).add(root)
 elif isinstance(x,(tuple,list)):
  for v in x:visit(v,root)
for cid,values in ops.items():
 if cid in R:visit(values,cid)
declared=[]
for req,roots in sorted(request_roots.items(),key=lambda x:repr(x[0])):
 ids=set().union(*(set(historical_contract(req,k,U).card_ids) for k in CLASSES))
 declared.append(dict(request=asdict(req),source_roots=sorted(roots),eligible=len(ids),missing=sorted(ids-set(R))))
# Explicit runtime-computed requests inspected, not claimed exhaustive.
computed=[]
for cid,req in [('TIME_861',pool(era='past',card_type='SPELL')),('TIME_704',pool(era='past',card_type='SPELL',minimum=7,classes='own_or_neutral')),('TIME_707',pool(era='past',mechanic='CHOOSE_ONE'))]:
 ids=set().union(*(set(historical_contract(req,k,U).card_ids) for k in CLASSES))
 computed.append(dict(source_root=cid,request=asdict(req),eligible=len(ids),missing=sorted(ids-set(R))))
# Per-identity structural ledger: bindings are deliberately not semantic certification.
identity_ledger=[]
all_ids=set(R)|set(standard)|minions|spells
for cid in sorted(all_ids):
 data=R.get(cid) or U.records.get(cid) or standard.get(cid,{})
 identity_ledger.append(dict(id=cid,name=data.get('name',cid),type=data.get('type'),standard_root=cid in standard,warden_minion_root=cid in minions,historical_spell_root=cid in spells,registered=cid in R,tables=[name for name in ('RULES','DEATH_EFFECTS','TRIGGERS','AURAS','START_EFFECTS','END_EFFECTS','CHOICES','WEAPON_TRIGGERS','LOCATION_RULES') if cid in getattr(cards,name,{})],semantic_completion='not_certified_by_static_audit'))

# Separate genuine unsupported behavior from all defensive validation raises.
guards=[]
for path,tree in trees.items():
 for n in ast.walk(tree):
  if isinstance(n,ast.Raise) and n.exc is not None:
   call=n.exc
   if isinstance(call,ast.Call) and isinstance(call.func,ast.Name) and call.func.id in ('UnsupportedCard','NotImplementedError'):
    guards.append(dict(path=str(path.relative_to(ROOT)),line=n.lineno,exception=call.func.id,expression=ast.get_source_segment(source[path],n) or '',classification='requires_context_review_not_automatically_missing_code'))
# Concrete source-confirmed coding tasks; effort bands are judgment, not time estimates.
TASKS=[]
complexity={'AV_119':'medium','AV_269':'medium','AV_400':'medium','AV_405':'large','BAR_323':'large','BOT_912':'large','BT_753':'medium','DMF_224':'medium','DMF_249':'medium','GDB_140':'large','GDB_233':'large','GDB_873':'medium','ICC_201':'medium','ICC_233':'medium','NEW1_036':'medium','OG_118':'large','ONY_033':'large','SCH_305':'large','ULD_286':'large','VAC_408':'large','VAC_528':'medium','VAC_931':'medium','VAC_941':'large','WON_078':'medium','WON_113':'large','WORK_017':'medium','WORK_030':'medium','YOP_024':'medium'}
for cid in missing_spells:
 card=U.records[cid]
 TASKS.append(dict(id='CARD:'+cid,area='card_effect',title=card['name'],status='missing',required_behavior=card.get('text',''),evidence=[dict(check='historical_spell_contract_minus_current_registry',card_id=cid,registered=False)],action='Implement printed program, required outputs and production dispatch; strict schemas, hashes and dependencies; meaningful affected rule checks.',done_when='Root and all required generated outputs execute through production paths with documented behavior and passing targeted cases.',effort_band=complexity[cid],effort_confidence='low; relative judgment, excludes undiscovered dependencies',validation='not_implemented'))
for op in ('muradin_return','brox_return','historic_gigafin_dispose','hammer_shuffle'):
 TASKS.append(dict(id='ENGINE:inherit:'+op,area='deathrattle_inheritance',title='Inherited physical relationship: '+op,status='partial',required_behavior='Retain the correct physical-object relationship when this Deathrattle is inherited, including ownership, copying and donor departure.',evidence=evidence(('expanded/death_inheritance.py','PHYSICAL_REVIEW'),('expanded/death_inheritance.py',"name in PHYSICAL_REVIEW"),('expanded/death_inheritance.py','Inherited physical-card relationship requires review')),action='Establish intended inherited physical-link semantics and implement binding/execution rather than unreviewed_inherited_physical rejection.',done_when='Controlled real inheritance/copy/repeat/control/death cases resolve without the explicit unsupported marker, with correct physical identity semantics.',effort_band='large',effort_confidence='low; rules evidence required',validation='explicitly_unsupported_case'))
TASKS.append(dict(id='ENGINE:overlapping_control',area='temporary_control',title='Overlapping temporary-control timers',status='partial',required_behavior='Support a second temporary control effect on an entity already carrying a return deadline.',evidence=evidence(('expanded/temporary_control.py','Overlapping control timers require reviewed ordering')),action='Represent and resolve stacked ownership/return obligations at the correct controller deadlines; preserve copy/silence/transform semantics.',done_when='Nested steals and returns have source-backed ordering and pass bounded rule cases without UnsupportedCard.',effort_band='large',effort_confidence='low; rules evidence required',validation='explicitly_unsupported_case'))
fields=['historical_stormwind_draw_discount','historical_stormwind_tamsin','historical_stormwind_tavish','historical_stormwind_power_targets','historical_stormwind_power_zero']
features=(C/'expanded/features.py').read_text();assert all(name not in features for name in fields)
TASKS.append(dict(id='INTERFACE:stormwind_features',area='policy_features',title='Encode five public Questline reward flags',status='partial',required_behavior='Expose persistent draw discount, Tamsin redirection, Tavish refresh, Hunter target permission and zero-cost-power state to the current feature encoder.',evidence=evidence(*[('expanded/game.py',"public['"+name+"']") for name in fields],('expanded/features.py','state[side]={k:p[k]')),missing_fields=fields,action='Add and version feature encoding for these public flags and check otherwise identical observations produce different features. Preserve previous models.',done_when='Each of the five flag changes is observable in encoded features without exposing opponent-private information; checkpoint/schema handling is explicit.',effort_band='small',effort_confidence='medium; limited interface change',validation='static_omission_confirmed'))
# Reconcile old fidelity entries without pretending an imported binding is a finished effect.
fidelity=json.loads((C/'expanded/fidelity_gaps.json').read_text())
OVERRIDES={
 'healing_aggregation':('stale_missing_code_claim','Conversion and multipliers already have runtime bodies; remaining aggregation/modifier-order fidelity is unverified.',evidence(('expanded/healing_replacement.py','def _ruby_heal'),('expanded/healing_replacement.py',"self._active('EX1_591'"),('expanded/systems.py','if spell:amount*='),('expanded/systems.py','_ruby_heal'))),
 'morchie_outcome_retention':('stale_no_runtime_claim','Morchie has a registered body and Rewind runtime hooks. This does not prove all outcome-retention semantics.',evidence(('expanded/morchie.py',"RULES="),('expanded/rewind.py',"END_036"))),
 'transformation_exceptional_bodies':('stale_no_runtime_claim','Divergence/Alternate Reality have registered transformation bodies. Computed pool closure and copy/rounding behavior remain separate.',evidence(('expanded/transformations.py',"'TIME_030'"),('expanded/transformations.py',"'TIME_707'"),('expanded/transformations.py','def _mutation_halves'))),
 'physical_custom_payload_contracts':('stale_unbound_approximation_claim','Avatar/pack and constructed special defaults have owner-authorized approximation policies. Exact rules and payload fidelity are not certified.',refs('APPROXIMATIONS.md','special-approximations-v1')),
 'devourer_source_bound_deathrattle_payload':('confirmed_partial','Four inherited physical relationships still reject explicitly; represented separately as four coding tasks.',evidence(('expanded/death_inheritance.py','PHYSICAL_REVIEW'),('expanded/death_inheritance.py','unreviewed_inherited_physical'))),
 'temporary_control_return':('confirmed_partial','Overlapping temporary-control deadlines explicitly reject; represented separately as a coding task.',evidence(('expanded/temporary_control.py','Overlapping control timers'))),
}
reconciled=[]
for g in fidelity['gaps']:
 item=dict(g)
 item['audit_classification']='unresolved_review_not_proven_missing_code'
 item['current_registry_presence']={cid:cid in R for cid in g.get('cards',[])}
 item['source_evidence']=[]
 if g['id'] in OVERRIDES:
  status,note,ev=OVERRIDES[g['id']];item.update(audit_classification=status,audit_note=note,source_evidence=ev)
 reconciled.append(item)
# Contract checklist for the whole simulator. Unknown semantics stay unknown.
AREAS=[
 ('scope','Patch-pinned catalog and eleven-class legality','expanded/decks.py','def validate','standard_legality'),
 ('construction','Exceptional decks, sideboards, runes and opening replacement','expanded/deck_setup.py',None,'constructed_opening_copies'),
 ('opening','First player, opening hands, mulligan and initial powers','expanded/provenance.py','def _mulligan',None),
 ('transactions','Legal actions, atomic execution and rollback','expanded/action_runner.py','def run',None),
 ('turns','Start/end phases, expiry, skipped and extra turns','expanded/lifecycle.py','def _finish_turn','extra_turn_scheduling'),
 ('resources','Mana growth, temporary mana, Overload and alternative payments','expanded/mana_accounting.py','def ','alternate_play_payment_precedence'),
 ('costs','Cost setters, reductions, taxes and attached timestamp precedence','expanded/game.py','for effect in p.cost_effects','cost_set_modifier_order'),
 ('targeting','Target restrictions, immunity, stealth and redirection','expanded/game.py','def _attack_targets','random_target_replacement'),
 ('combat','Normal/forced attacks, precombat interruption and cleave','expanded/combat_resolver.py','def ','precombat_event_generalization'),
 ('damage','Damage batching, shields, Poisonous, replacement and Lifesteal','expanded/systems.py','def _damage','batch60_combat_death_order'),
 ('healing','Healing, conversion, multipliers, overheal and prevention','expanded/healing_replacement.py','def _ruby_heal','healing_aggregation'),
 ('deaths','Death waves, Deathrattles, resurrection and Reborn','expanded/death_inheritance.py','def ','devourer_source_bound_deathrattle_payload'),
 ('summons','Entry, listeners, board capacity, adjacency and Dormant','expanded/summons.py',None,'summon_listener_phase_order'),
 ('auras','Continuous stats/keywords, stat setters, Silence and expiry','expanded/systems.py','def _refresh_auras','crystal_core_base_stats'),
 ('copying','Physical copy, enchantment retention, fresh replay and transform','expanded/provenance.py','def _copy_card','copy_state_completeness'),
 ('control','Control transfer, nested steals and owner-bound deadlines','expanded/temporary_control.py','def ','temporary_control_return'),
 ('zones','Draw/burn, fatigue, hand/deck movement, discard and shuffle','expanded/zone_manager.py','def ','draw_event_continuations'),
 ('choices','Discover, physical-zone choices and nested continuations','expanded/choice_resolver.py','def resolve','discover_followup_timing'),
 ('spells','Paid/automatic spell casts, countering, repetition and histories','expanded/spell_casting.py','def ','internal_spell_cast_attribution'),
 ('secrets','Secret placement, shared zones and resolution order','expanded/secrets.py',None,'secret_extensions'),
 ('quests','Quest/Questline progress, reward delivery and per-turn resets','expanded/historical_stormwind_questline_finish.py',None,'quest_progress_and_location_death_timing'),
 ('powers','Primary/secondary Hero Powers, replacement, cost and usage','expanded/hero_powers.py','def _replace_primary_power','replacement_and_secondary_power_timing'),
 ('locations','Locations, charges/cooldown, destruction and untouchable permanents','expanded/permanents.py',None,'quest_progress_and_location_death_timing'),
 ('keywords','Keyword/state families and held upgrades','expanded/historical_upgrades.py',None,'held_upgrade_reference_fidelity'),
 ('generation','Declared, computed, constructed and recursively generated outcomes','expanded/dependencies.py','complete_dependency_coverage=False','generated_dependency_closure'),
 ('approximations','Labeled owner-authorized special policies and provenance','APPROXIMATIONS.md','special-approximations-v1',None),
 ('observation','Player-private observations and public physical payloads','expanded/game.py','def observe','physical_custom_payload_contracts'),
 ('features','Policy encoding, current state flags and schema versions','expanded/features.py','def encode_decision',None),
 ('environment','Reset/step, current actor, stale actions, terminal/truncation/rewards','expanded/environment.py','def ',None),
 ('replay','Deterministic replay, seeds and clone state','expanded/replay_history.py',None,None),
 ('checkpoints','Dataset/model fingerprints, feature schema and resume rejection','expanded/features.py','SCHEMA =',None),
 ('notebooks','Candidate Jupyter paths and import isolation','hearthstone_sim/_bootstrap.py','def ',None),
 ('regression','Current-source consolidated non-training regression evidence','expanded/status.py','fixtures_passed=',None),
]
areas=[]
ids={g['id']:g for g in reconciled}
for key,title,path,needle,gap in AREAS:
 ev=refs(path,needle)
 area=dict(id='AREA:'+key,title=title,status='implemented_unvalidated',source_evidence=ev,acceptance='Require controlled production-path cases for the named contract and current-source receipts; independent reference evidence for disputed game rules.',related_gap=gap)
 if gap:
  area['status']='partial_or_fidelity_unresolved';area['required_followup']=ids[gap]['required_evidence'] if gap in ids else 'Inspect linked fidelity entry.'
 if key=='features':area.update(status='partial',coding_tasks=['INTERFACE:stormwind_features'])
 if key=='control':area.update(status='partial',coding_tasks=['ENGINE:overlapping_control'])
 if key=='generation':area.update(status='partial',required_followup='Complete computed requests and recursive generated behavior; 19 inspected declared historical requests have no direct missing IDs, but selected computed requests still require the 28 spells.')
 if key=='regression':area.update(status='validation_pending',required_followup='Run consolidated non-training suite after implementation and repair failures on unchanged source. Five latest focused checks are not a full pass.')
 if not ev:area['status']='source_anchor_not_found';area['required_followup']='Find actual active implementation before deciding whether missing.'
 areas.append(area)
summary=dict(audit_date='2026-10-19',fingerprint=FP,scope='Pinned eleven-class Standard simulator, all reachable generated effects, and existing owner-operated Jupyter policy boundary; exact client fidelity distinct from approved approximation mode.',audit_kind='static_source_and_saved_evidence; no game/test/training execution',whole_game_coding_percentage=None,percentage_unavailable_reason='No exhaustive semantic requirement inventory or completed-effort baseline exists. Registration, AST presence, defensive guards and fidelity-entry counts cannot supply it. This audit establishes concrete lower-bound coding work and exposes review coverage.',inventory=dict(standard=dict(total=len(standard),registered=len(set(standard)&set(R)),missing=sorted(set(standard)-set(R))),warden_minions=dict(total=len(minions),registered=len(minions&set(R)),missing=sorted(minions-set(R))),historical_spells=dict(total=len(spells),registered=len(spells&set(R)),missing=missing_spells),registry_records=len(R)),known_coding_tasks=len(TASKS),known_coding_task_breakdown=dict(Counter(t['area'] for t in TASKS)),fidelity_entries=len(reconciled),fidelity_audit_classifications=dict(Counter(g['audit_classification'] for g in reconciled)),requirement_families=len(areas),requirement_family_status=dict(Counter(a['status'] for a in areas)),historical_archive_envelope=envelope,archive_envelope_warning='81 unregistered weapons and 8 locations exist in the broad archive envelope; NOT counted as required merely because they are archived. Current declared Paladin past-weapon request is closed. Reachability must be established before adding them to required work.',declared_historical_requests=declared,computed_historical_requests= computed,literal_dependencies=literal,unsupported_raise_sites=len(guards),guard_warning='Defensive errors are not automatically missing implementations. Individual semantic review remains required.',implementation_completion_proven=False,regression_execution=False,training_execution=False)
OUT=D/'project-completion-audit';OUT.mkdir(exist_ok=True)
for name,obj in [('summary.json',summary),('coding-tasks.json',TASKS),('requirements.json',areas),('fidelity-reconciliation.json',reconciled),('unsupported-guards.json',guards),('card-implementation-inventory.json',identity_ledger)]: (OUT/name).write_text(json.dumps(obj,indent=2)+'\n')
with (OUT/'coding-tasks.csv').open('w',newline='') as stream:
 w=csv.writer(stream);w.writerow(['id','area','title','status','effort_band','required_behavior','done_when','source'])
 for t in TASKS:w.writerow([t['id'],t['area'],t['title'],t['status'],t['effort_band'],t['required_behavior'],t['done_when'],'; '.join(e.get('path',e.get('check',''))+(':'+str(e['line']) if 'line' in e else '') for e in t['evidence'])])
def mdref(e):return f"[{e['path']}:{e['line']}](<{ROOT/e['path']}:{e['line']}>)" if 'path' in e else e['check']
text=['# Simulator implementation audit — October 19, 2026','', '**Result: 34 concrete coding tasks confirmed (28 missing spell roots and six engine/interface cases), plus unresolved semantic and dependency review. This is a lower bound, not a complete estimate of effort. No defensible whole-game percentage is established.**','', '## What was actually inspected','',f'- Current runtime registry and hash-verified historical contracts, across all eleven classes. Candidate fingerprint: `{FP}`.',f'- {len(source)} Python source files parsed; {len(guards)} explicit UnsupportedCard/NotImplementedError raise sites indexed. Defensive guards were not counted as defects.', '- All declared literal dependencies: '+str(literal['roots_checked'])+' roots, '+str(literal['edges'])+' edges, '+str(len(literal['missing_ids']))+' missing IDs. The dependency checker explicitly excludes computed/helper semantics.', '- Nineteen distinct directly declared historical requests, evaluated for all eleven classes: zero missing direct registered outcomes. Separately checked computed requests include TIME_861, TIME_704 and TIME_707.', '- All 160 old fidelity entries preserved and annotated. Entries not independently reconciled are explicitly review-required, not counted as new bugs.', '- Thirty-three simulator/interface requirement families indexed to source. Presence of code does not establish semantic completion.', '- Existing saved test receipts inspected; no tests, gameplay experiments or training executed for this audit.','', '## Concrete coding work','', '| ID | Missing or partial behavior | Relative effort | Source evidence |','| --- | --- | --- | --- |']
for t in TASKS:
 text.append('| '+t['id']+' | '+t['title']+' | '+t['effort_band']+' | '+'; '.join(mdref(e) for e in t['evidence'][:2])+' |')
text+=['', 'Effort bands are qualitative judgments about the remaining task, not hours, independently measured estimates, or fractions of the project. Required outputs may expand card tasks. Four physical-link tasks share one inheritance subsystem and may share implementation work.','', '## Corrections to earlier progress statements','', '- Healing-to-damage conversion is already implemented in healing_replacement.py and called from Systems._heal. The old statement that it is wholly unimplemented is stale. Exact modifier and aggregation fidelity remain unresolved.', '- M orchie (END_036), Divergence (TIME_030), and Alternate Reality (TIME_707) have registered runtime bodies despite old not_implemented entries. Registration does not establish all their semantics.', '- Avatar and other authorized specials have approximate default contracts; they are not all unbound. Exact probabilities remain unknown and are not required for the explicitly approved approximate mode.', '- Five Questline world flags reach public observations but are absent from the feature encoder; legal actions alone do not replace that information for the policy.', '- The historical archive includes 81 unregistered weapons and eight unregistered locations. Those are not automatically required outcomes. Do not inflate the missing count by treating every archived card as reachable. The declared historical Paladin weapon pool has 27 outcomes and zero direct registration gaps.', '', '## Remaining verification and potential coding scope','', '| Requirement family | Current classification | Evidence |','| --- | --- | --- |']
for area in areas:text.append('| '+area['title']+' | '+area['status']+' | '+'; '.join(mdref(e) for e in area['source_evidence'][:2])+' |')
text+=['', 'Full per-entry acceptance criteria, current-behavior statements, source locations and review status are in the adjacent JSON ledgers. Do not interpret unresolved_review as missing_code or implemented_unvalidated as fully_correct.','', '## Why this does not produce an exact percentage of the game','', 'The 5,856-card census measures registrations, with 28 missing roots (0.478%). Shared behavior and interactions are not equal-sized card records. The 34 known coding tasks, 33 requirement families and 160 fidelity entries overlap and use different units; adding them into a single denominator would invent precision. Unknown semantic coverage is not zero remaining work.','', 'To close the audit, review each unresolved fidelity contract against current dispatch and targeted independent rules evidence; enumerate compound contracts into non-overlapping cases; trace dynamic generation recursively; classify every resulting case as complete/partial/missing with acceptance evidence. Only then can a fixed-checklist implementation percentage be published. A percentage of engineering effort additionally needs estimates for completed and remaining work; source lines and test counts are not suitable substitutes.','', '## Work order','', '1. Implement the 28 spell roots in cost/resource, combat, physical-zone/replay and choice/generation families, including generated outputs.', '2. Resolve the five explicit unsupported engine cases (four inheritance relationships and stacked control) and the five-flag feature omission.', '3. Reconcile remaining fidelity contracts and computed dependency reachability; promote newly confirmed implementation holes into coding-tasks.json rather than treating all review notes as missing code.', '4. Run targeted non-training checks for changed families, then a consolidated unchanged-source regression. Preserve failed receipts and repair defects.', '5. Verify the existing Jupyter environment, observation privacy, feature/version compatibility and terminal/truncation semantics without executing training.', '', '## Artifacts','', '- [coding-tasks.csv](coding-tasks.csv): actionable confirmed coding list.', '- [coding-tasks.json](coding-tasks.json): required behavior, evidence and completion criteria.', '- [requirements.json](requirements.json): simulator and training-interface coverage map.', '- [fidelity-reconciliation.json](fidelity-reconciliation.json): all 160 old entries with explicit reconciliation state.', '- [unsupported-guards.json](unsupported-guards.json): source-indexed explicit guards requiring context review.', '- [summary.json](summary.json): reproducible counts, contracts and audit limits.', '- [card-implementation-inventory.json](card-implementation-inventory.json): every registered or tracked root identity and its declaration tables; no semantic certification.','']
(OUT/'README.md').write_text('\n'.join(text).replace('M orchie','Morchie'))
print(json.dumps({k:summary[k] for k in ('fingerprint','known_coding_tasks','known_coding_task_breakdown','fidelity_audit_classifications','requirement_family_status','unsupported_raise_sites')}))
print(OUT/'README.md')
