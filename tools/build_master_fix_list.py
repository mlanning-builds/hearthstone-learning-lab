from pathlib import Path
import ast,csv,hashlib,json,re,sys
from collections import Counter,defaultdict
ROOT=Path(__file__).resolve().parents[1];C=ROOT/'staging/rebased-88';D=ROOT/'docs/engine-audit/project-completion-audit';sys.path.insert(0,str(C))
from expanded import cards
from expanded.status import code_fingerprint
from expanded.historical_generation_catalog import load_universe,historical_contract
from expanded.generation_cards import pool
R=cards.registry();U=load_universe();FP=code_fingerprint()
tasks=json.loads((D/'coding-tasks-expanded.json').read_text())
def ev(file,needle):
 p=C/file;ls=p.read_text().splitlines();indices=[i for i,s in enumerate(ls,1) if needle in s];assert indices,(file,needle)
 return [dict(path=str(p.relative_to(ROOT)),line=i,text=ls[i-1].strip()) for i in indices[:4]]
if not any(t['id']=='GENERATION:zilliax_bare' for t in tasks):
 tasks.append(dict(id='GENERATION:zilliax_bare',area='generation_membership_and_payload',title='Resolve bare Zilliax generation versus required physical modules',status='partial',required_behavior='The current TIME_052 past-minion contract includes TOY_330; entry/play rejects an unbound two-module definition. Resolve the membership/payload contradiction using the actual frozen-patch rule.',evidence=ev('expanded/historical_zilliax.py','random bare generation is forbidden')+ev('expanded/generation.py',"if 'TITAN' in data.get"),action='Verify generation bans against appropriate sources, then correct eligibility or provide the required legitimate generated definition. Preserve historical implementations and never filter merely because an outcome is difficult.',done_when='Every eligible random outcome is executable; ineligible Zilliax is excluded only under a sourced rule, with complete pool and explicit-copy cases tested.',effort_band='medium',effort_confidence='low; rule evidence required',validation='source_contract_inconsistency_confirmed'))
# Current full-run result when available; never select an unrelated older receipt.
receipts=[]
for p in (C/'runs/expanded_validation').glob('validation-*.json'):
 try:x=json.loads(p.read_text())
 except (ValueError,OSError):continue
 if x.get('fingerprint')==FP:receipts.append((x.get('completed_at',''),p,x))
receipt=max(receipts,key=lambda v:v[0]) if receipts else None
regression=dict(status='running',terminal_receipt=None,log='/private/tmp/hearthstone-completion-audit-regressions.log')
if receipt:
 _,path,result=receipt;regression=dict(status='finished',terminal_receipt=str(path),report=result,log='/private/tmp/hearthstone-completion-audit-regressions.log')
log=Path(regression['log']).read_text() if Path(regression['log']).exists() else ''
# Preliminary logs can contain nested worker fixture runs; raw message counts are NOT authoritative test totals.
regression['raw_started_messages']=len(re.findall(r'^Rule start:',log,re.M));regression['raw_failure_messages']=len(re.findall(r'^Rule failure:',log,re.M))
regression['log_warning']='Interleaved workers and worker-orchestration fixtures can repeat failure messages. Only the completed receipt determines totals.'
# These root causes already have source tracebacks; inspect receipt to add any additional cause after completion.
for key,title,path,needle,action in [
 ('TESTS:feature_schema_version','Repair outdated feature-v60 expectations after v61 change','expanded/features.py',"SCHEMA = 'visible-action-features-v61'",'Update stale fixture expectations to the intended schema and verify semantic feature/privacy assertions still hold. Preserve checkpoint version rejection; do not weaken compatibility checks.'),
 ('TESTS:quest_cost_helper','Repair quest-cost helper/caller compatibility','expanded/quests.py','self._cost(card,owner) if paid_cost is None else paid_cost','Avoid requiring or recomputing a paid Cost when the active objective does not use it, or update the caller contract/fixtures consistently. Preserve actual-paid-cost tracking for Stormwind objectives and audit legacy callbacks.'),
]:
 if any(t['id']==key for t in tasks):continue
 tasks.append(dict(id=key,area='regression_repair',title=title,status='partial',required_behavior='Resolve the corresponding observed current-source rule-suite failure family.',evidence=ev(path,needle),action=action,done_when='All affected checks pass and the consolidated unchanged-source receipt has no related errors.',effort_band='small',effort_confidence='medium; failure cause inspected',validation='observed_nontraining_regression_failure'))
# Stable families consolidate many per-card cases without erasing their individual acceptance criteria.
def group(t):
 i=t['id']
 if i.startswith('CARD:'):return '01 — Implement 28 historical spell roots and their outputs'
 if i.startswith('CAST_ADMISSION:'):return '02 — Repair automatic casting for 30 written historical spells'
 if i.startswith('SOURCE:jerry_split_'):return '03 — Complete Jerry Rig Carpenter split families'
 if i.startswith('SOURCE:aura_placement_'):return '04 — Complete Gelbin direct Aura placement'
 if i.startswith('SOURCE:lost_battlecry_'):return '05 — Restore overwritten Kalecgos and Pop’gar Battlecries'
 if i.startswith('ENGINE:inherit:'):return '06 — Resolve four inherited physical Deathrattle relationships'
 if i in ('SOURCE:bashana_contract','SOURCE:watfin_contract'):return '07 — Supply working Bashana and Watfin default contracts'
 if i in ('SOURCE:malygos_repeats','SOURCE:sinestra_repeats','SOURCE:atiesh_lifesteal'):return '08 — Resolve spell repetition and Atiesh Lifesteal interactions'
 if i in ('ENGINE:overlapping_control',):return '09 — Support overlapping temporary-control returns'
 if i.startswith('INTERFACE:'):return '10 — Complete the existing policy feature boundary'
 if i.startswith('VALIDATION:'):return '11 — Complete detailed effect-operand validation'
 if i.startswith('GENERATION:'):return '12 — Resolve generation eligibility and physical definitions'
 if i.startswith('TESTS:'):return '13 — Repair current-source regression failures'
 return '14 — Finish remaining explicitly unsupported card interactions'
groups=defaultdict(list)
for t in tasks:groups[group(t)].append(t['id'])
# Every deferred review statement is retained with provenance, not mistaken for a present bug.
notes=defaultdict(list);batch_index=[]
for p in sorted((ROOT/'docs/engine-audit').glob('*deferred-validation.json')):
 x=json.loads(p.read_text());n=0
 for key in ('review_pending','deferred','unvalidated','deferred_review','deferred_behavior_review','research_limitations'):
  val=x.get(key)
  if isinstance(val,list):
   for statement in val:
    if isinstance(statement,str):notes[statement].append(dict(report=str(p.relative_to(ROOT)),field=key));n+=1
 batch_index.append(dict(path=str(p.relative_to(ROOT)),review_statements=n,fingerprint=x.get('fingerprint',x.get('candidate_fingerprint')),status=x.get('status')))
notes=[dict(id='ARCHIVE:'+str(i+1).zfill(4),statement=text,provenance=paths,status='historical_review_request_not_proven_current_defect') for i,(text,paths) in enumerate(sorted(notes.items()))]
fidelity=json.loads((D/'fidelity-source-review.json').read_text())
for g in fidelity:
 g['linked_coding_tasks']=[t['id'] for t in tasks if set(g.get('cards',())) & (set(t.get('affected_cards',()))|({t['id'].split(':',1)[1]} if t['id'].startswith(('CARD:','CAST_ADMISSION:')) else set()))]
 if 'EDR_854' in g.get('cards',[]):g['metadata_reference_issue']='EDR_854 is absent from the frozen archive and runtime registry. Resolve this stale identifier in the ledger; do not invent a new card implementation.'
# Determine actual player-level omissions; entity-level hand fields are encoded recursively and are not automatically defects.
game=(C/'expanded/game.py').read_text();tree=ast.parse(game);observe=next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name=='observe');playerloop=next(n for n in observe.body if isinstance(n,ast.For) and 'owner' in ast.unparse(n.target));playerkeys={}
for n in ast.walk(playerloop):
 if isinstance(n,ast.Assign):
  for q in n.targets:
   if isinstance(q,ast.Subscript) and isinstance(q.value,ast.Name) and q.value.id=='public' and isinstance(q.slice,ast.Constant) and isinstance(q.slice.value,str):playerkeys[q.slice.value]=n.lineno
 if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and isinstance(n.func.value,ast.Name) and n.func.value.id=='public' and n.func.attr=='update':
  for kw in n.keywords:
   if kw.arg:playerkeys[kw.arg]=n.lineno
featuretext=(C/'expanded/features.py').read_text();literalstrings={n.value for n in ast.walk(ast.parse(featuretext)) if isinstance(n,ast.Constant) and isinstance(n.value,str)}
player_omissions=[dict(field=k,line=v,scope='public player field',status='not_named_in_encoder; decide intended representation and test equivalent/different feature maps') for k,v in sorted(playerkeys.items()) if k not in literalstrings]
# Check every game/helper method reference against actual Game MRO, without creating a game.
from expanded.game import Game
classes={c.__name__ for c in Game.__mro__};unresolved=[];checked=0
for p in (C/'expanded').glob('*.py'):
 st=ast.parse(p.read_text());parents={child:node for node in ast.walk(st) for child in ast.iter_child_nodes(node)}
 for n in ast.walk(st):
  if not isinstance(n,ast.Call) or not isinstance(n.func,ast.Attribute) or not isinstance(n.func.value,ast.Name) or not n.func.attr.startswith('_'):continue
  obj=n;classname=None
  while obj in parents:
   obj=parents[obj]
   if isinstance(obj,ast.ClassDef):classname=obj.name;break
  if n.func.value.id!='game' and not(n.func.value.id=='self' and classname in classes):continue
  checked+=1
  if not hasattr(Game,n.func.attr):unresolved.append(dict(path=str(p.relative_to(ROOT)),line=n.lineno,method=n.func.attr))
assert not unresolved
quest_result=Path('/private/tmp/hearthstone-questline-audit-results.log').read_text()
evidence_dir=D/'evidence';evidence_dir.mkdir(exist_ok=True)
(evidence_dir/'questline-audit.py').write_text(Path('/private/tmp/hearthstone_questline_audit.py').read_text())
(evidence_dir/'questline-audit-results.txt').write_text(quest_result)
(evidence_dir/'questline-audit-note.txt').write_text('Four final controlled checks passed. The first draft expected 10 Armor while drawing from an empty deck; native fatigue correctly spent 1 Armor. The fixture was corrected by supplying an actual deck card, without changing simulator code. These checks cover eight root starts, Park stage rewards, Tavish refresh and Kurtrus draw discounts only. They are not full Questline/client validation.\n')
master=dict(date='2026-10-19',fingerprint=FP,status='consolidated_source_and_recorded_obligations; semantic exhaustiveness not proven',confirmed_coding_items=len(tasks),coding_families={k:dict(count=len(v),ids=v) for k,v in sorted(groups.items())},coding_tasks=tasks,rule_verification_contracts=fidelity,conditional_source_limits=json.loads((D/'source-findings.json').read_text()),archival_review_sources=len(batch_index),archival_distinct_statements=len(notes),archival_status='Preserved for reconciliation; not that many new bugs or independent tasks.',player_field_encoder_omissions=player_omissions,game_method_references_checked=checked,unresolved_game_method_references=unresolved,regression=regression,questline_audit=dict(checks=4,passed=4,full_conformance=False),unknowns='A source inventory plus internal tests cannot prove every possible game interaction correct. All known recorded verification contracts are included, but no exact whole-game percentage or zero-undiscovered-defects claim is made.')
(D/'master-work-ledger.json').write_text(json.dumps(master,indent=2)+'\n');(D/'archival-review-requests.json').write_text(json.dumps(notes,indent=2)+'\n');(D/'deferred-batch-index.json').write_text(json.dumps(batch_index,indent=2)+'\n');(D/'player-feature-omissions.json').write_text(json.dumps(player_omissions,indent=2)+'\n')
with (D/'MASTER-CODING-LIST.csv').open('w',newline='') as file:
 w=csv.writer(file);w.writerow(['family','id','title','status','effort','required_behavior','action','done_when'])
 for t in tasks:w.writerow([group(t),t['id'],t['title'],t['status'],t['effort_band'],t['required_behavior'],t['action'],t['done_when']])
def link(e):
 return '['+e['path']+':'+str(e['line'])+'](<'+str(ROOT/e['path'])+':'+str(e['line'])+'>)' if 'path' in e else str(e.get('check','metadata evidence'))
lines=['# Master remaining-work list','', 'Snapshot: October 19, 2026. Scope: pinned Standard across all eleven classes, required generated outcomes and the existing Jupyter training boundary. Source fingerprint: `'+FP+'`.','',f'**{len(tasks)} confirmed coding/repair entries in {len(groups)} consolidated families.** They are different-sized cases, not {len(tasks)} missing cards and not a percentage of the game. The remainder of this document also includes all 160 recorded rule-verification contracts, conditional source limits, and the deferred-review archive.','', 'This is a consolidated accounting of source-confirmed defects and recorded unresolved obligations. It is not a proof that every possible silent interaction error has been discovered. No arbitrary completion percentage is supplied.','', '## Coding and repair families','', '| Family | Entries |','| --- | ---: |']
for k,v in sorted(groups.items()):lines.append('| '+k+' | '+str(len(v))+' |')
lines+=['', 'The policy feature item is broader than five Questline flags: '+str(len(player_omissions))+' public player-field names are absent from the encoder. Some are intentionally unnecessary or indirectly inferable; decide and test the required representation. This is a limitation of the existing lossy baseline, not '+str(len(player_omissions))+' proven simulation-rule defects. The full observation API and a replacement model encoder may use them directly.','', '## Every confirmed coding entry','']
for family,ids in sorted(groups.items()):
 lines+=['### '+family,'']
 for t in [t for t in tasks if t['id'] in ids]:
  lines+=['- **'+t['id']+' — '+t['title']+'**', '  - Required: '+t['required_behavior'], '  - Work: '+t['action'], '  - Completion: '+t['done_when'], '  - Evidence: '+'; '.join(link(e) for e in t['evidence'][:3])]
 lines.append('')
lines+=['## Current non-training validation','', '- Full regression: **'+regression['status']+'**. Raw interleaved log messages are not final test counts.','- Log: `/private/tmp/hearthstone-completion-audit-regressions.log`.','- Four additional controlled Questline checks pass; script/results are in `evidence/`. No simulator behavior was changed to obtain those passes.','- No training, learning updates, deck search or notebook training cells were run.','']
if receipt:
 result=receipt[2];lines+=['- Final receipt: ['+receipt[1].name+'](<'+str(receipt[1])+'>).','- Tests: '+str(result['tests_run'])+'; failures: '+str(len(result['failures']) if isinstance(result['failures'],list) else result['failures'])+'; errors: '+str(len(result['errors']) if isinstance(result['errors'],list) else result['errors'])+'; source unchanged: '+str(result['source_unchanged'])+'.','']
lines+=['## Every recorded rule-verification contract','', 'These are required investigations and checks, **not 160 confirmed bugs**. Some descriptions are stale. Correct the descriptions against current code, establish expected behavior, and add a coding item only when a real unsupported/wrong behavior is found. Owner-authorized special approximations stay separately labeled.','']
for i,g in enumerate(fidelity,1):
 lines+=['### V'+str(i).zfill(3)+' — '+g['id'],'', '- Current recorded status: `'+g['status']+'`.','- Cards: '+(', '.join('`'+c+'`' for c in g.get('cards',[])) or 'Shared system / multiple families')+'.','- Acceptance/review: '+g['required_evidence'],'- Source: '+'; '.join(link(e) for e in g['source_evidence'][:3]),'']
 if g.get('audit_note'):lines.insert(len(lines)-1,'- Reconciliation: '+g['audit_note'])
 if g.get('metadata_reference_issue'):lines.insert(len(lines)-1,'- Ledger correction: '+g['metadata_reference_issue'])
lines+=['## Remaining conditional source limits','', 'These ten source guards/caps are individually recorded below. They require a valid reachable witness and intended-rule decision before being called missing code; do not rewrite a defensive guard without evidence.','']
for x in master['conditional_source_limits']:
 if x['classification']=='reachability_or_fidelity_review':lines+=['- **'+x['title']+'**: '+x['trigger']+' '+x['action']]
lines+=['', 'The inherited Broxigar chain also rejects unbound returns with multiple waiting originals. Normal copies preserve `_brox_chain` through provenance; review fresh resurrection/generated-chain paths before choosing ownership behavior. This condition is in the existing Broxigar verification contract and must not be lost among generic guards.','', '## Coverage and archives','', '- All 357 active candidate/public-facade Python files were parsed; 1,612 functions, 758 raises, 508 unsupported-code sites and 818 generation calls were indexed.','- '+str(checked)+' Game/helper method references resolve against the actual Game MRO; zero unresolved method names were found. This is structural evidence only.','- All registered/tracked card identities have a declaration-table inventory; no registration is labeled semantically certified by that inventory.','- Dynamic Standard selector sites are bounded by the registered Standard universe for root coverage. Four generic kwargs forwarding definitions and the historical Dark Gift route remain separately identified. This does not prove generated execution or probability laws.','- All 160 fidelity records are source-linked. `EDR_854` is a stale nonexistent archive identifier, not a new card to invent.','- All '+str(len(batch_index))+' deferred-validation reports were inventoried. '+str(len(notes))+' distinct archived review statements are retained in [archival-review-requests.json](archival-review-requests.json). They overlap and include obsolete counts/instructions, so are not added to the coding-task total.','- Complete machine-readable ledgers: [master-work-ledger.json](master-work-ledger.json) and [MASTER-CODING-LIST.csv](MASTER-CODING-LIST.csv).','', '## Exit checklist for a reliable training candidate','', '1. Complete source-confirmed card/effect, generated outcome and valid-state crash fixes; preserve complete eligible pools.','2. Resolve conditional limits that are reachable in the pinned format, and reconcile the rule-verification contracts to an explicit supported/approximate/unsupported decision. Do not claim unknown cases are exact.','3. Obtain a passing consolidated non-training suite on unchanged final source and repair every actual failure, retaining failed receipts.','4. Check Jupyter import isolation, observation privacy, legal actions, reward/termination/truncation handling, feature coverage and checkpoint schema with the current candidate, without starting training.','5. Document the frozen patch, remaining approved approximations and training scope. The owner then runs training manually.','', 'Architecture rewrites, publishing to GitHub, replacing saved models and running training are not part of this audit or prerequisites to resolving the listed simulator defects.','']
(D/'MASTER-REMAINING-WORK.md').write_text('\n'.join(lines))
assert len({t['id'] for t in tasks})==len(tasks)
print(json.dumps(dict(coding_items=len(tasks),coding_families=len(groups),verification_contracts=len(fidelity),deferred_sources=len(batch_index),archival_review_statements=len(notes),public_player_field_omissions=len(player_omissions),method_references_checked=checked,regression=regression['status'])))
