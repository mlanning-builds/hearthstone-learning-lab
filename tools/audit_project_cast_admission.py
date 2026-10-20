from pathlib import Path
import json,ast,csv,sys
from types import SimpleNamespace,MethodType
from collections import Counter
ROOT=Path(__file__).resolve().parents[1];C=ROOT/'staging/rebased-88';D=ROOT/'docs/engine-audit/project-completion-audit';sys.path.insert(0,str(C))
from expanded import cards
from expanded.spell_casting import SpellCasting,INTERNAL_OPERATIONS,INTERNAL_TARGETS
from expanded.historical_generation_catalog import load_universe,historical_contract
from expanded.generation_cards import pool
from expanded.generation_catalog import load_universe as standard_universe
from expanded.dark_gift_generators import requests_for as gift_requests
from dataclasses import replace
from standard.catalog import CLASSES
R=cards.registry();U=load_universe();SU=standard_universe()
TASKS=json.loads((D/'coding-tasks-expanded.json').read_text());summary=json.loads((D/'source-audit-summary.json').read_text());admission=[]
# Call only the metadata/operand predicates on a metadata-only receiver. No Game instance.
probe=SimpleNamespace(cards=R,current=0,players=[SimpleNamespace(hero_class='MAGE'),SimpleNamespace(hero_class='MAGE')]);probe._supports_internal_operations=MethodType(SpellCasting._supports_internal_operations,probe)
for cid,d in sorted(R.items()):
 if not d.get('collectible') or d.get('type')!='SPELL':continue
 owners=[]
 for hero in CLASSES:
  probe.players[0].hero_class=hero
  if SpellCasting._supports_internal_spell(probe,cid,0):owners.append(hero)
 mode,ops=cards.RULES.get(cid,('missing',()))
 admission.append(dict(id=cid,name=d['name'],past_census=cid in U.members,allowed_classes=owners,mode=mode,mode_admitted=mode in INTERNAL_TARGETS,root_operations=[dict(name=op[0],admitted=op[0] in INTERNAL_OPERATIONS) for op in ops]))
failed=[x for x in admission if not x['allowed_classes'] and x['past_census']]
assert len(failed)==30
for row in failed:
 cid=row['id'];TASKS.append(dict(id='CAST_ADMISSION:'+cid,area='automatic_spell_admission',title='Automatic casting rejects '+row['name'],status='partial',required_behavior='Registered historical spell is included in broad past-spell generation but its operations are not admitted for internal casting.',evidence=[dict(path='staging/rebased-88/expanded/spell_casting.py',line=94,check='_supports_internal_spell returns False for every hero class on metadata-only receiver'),dict(check='operand_admission',root_operations=row['root_operations'])],action='Review native operation semantics in internal contexts and wire admitted opcodes/checkpoint support; do not merely whitelist without checking target/choice/death/payment behavior.',done_when='Production internal-cast preflight accepts all valid owner contexts and affected automatic/paid rule cases preserve behavior.',effort_band='medium',effort_confidence='low; some shared admission fixes, some resumable behavior review',validation='metadata_predicate_refusal_confirmed'))
# Close root-registration coverage for dynamic selectors by a conservative superset proof.
calls=json.loads((D/'generation-call-sites.json').read_text());bounded=0;forwarders=0
for x in calls:
 if x['membership_audited']:continue
 if 'null' in x['dynamic_kwargs']:
  x['coverage_resolution']='kwargs_factory_forwarder';x['coverage_note']='Generic forwarding definition, not an additional root pool. Caller contracts are separately listed; changes to era/family at runtime need dataflow review.';forwarders+=1
 else:
  assert 'era' not in x['dynamic_kwargs'] and 'era' not in x['constant_kwargs']
  x['coverage_resolution']='standard_catalog_superset_registered';x['coverage_note']='Era is the default Standard; dynamic cost/class/type/tribe/school filters select subsets of the 1,185-record Standard universe. Every identity in that superset is registered. This proves only absence of additional missing root registrations, not executable behavior, empty-result semantics, distribution, or dynamic validity.';bounded+=1
# The one dynamic historical Dark Gift route is explicit and minion-only.
gifts=[]
for cid in R:
 for req in gift_requests(cid):
  if req.historical:
   ids=set().union(*(set(historical_contract(replace(a,era='past'),hero,U).card_ids) for a in req.alternatives for hero in CLASSES))
   gifts.append(dict(source=cid,eligible=len(ids),missing=sorted(ids-set(R)),alternatives=[str(x) for x in req.alternatives]))
# Link all nine generic old gaps to the actual relevant implementations.
generic={
 'copy_state_completeness':('expanded/game.py','m.rule_state=deepcopy(copy_from.rule_state)'),
 'generated_dependency_closure':('expanded/dependencies.py','complete_dependency_coverage=False'),
 'standard_legality':('expanded/decks.py','def validate'),
 'copied_freeze_expiry':('expanded/game.py','m.frozen_until=copy_from.frozen_until'),
 'minion_postplay_phase_contract':('expanded/summons.py','def _resume_minion_after_play'),
 'automatic_choice_attribution':('expanded/spell_casting.py','def _automatic'),
 'internal_secret_and_delayed_state':('expanded/spell_casting.py','INTERNAL_OPERATIONS'),
 'pinned_standard_generation_membership':('expanded/generation_catalog.py','def standard_contract'),
 'large_recipe_registration_scope':('expanded/cards.py','RULES.update'),
}
fidelity=json.loads((D/'fidelity-source-review.json').read_text())
for item in fidelity:
 if not item['source_linkage_complete']:
  rel,needle=generic[item['id']];p=C/rel;lines=p.read_text().splitlines();loc=[(i,t) for i,t in enumerate(lines,1) if needle in t]
  if not loc and item['id']=='automatic_choice_attribution':loc=[(i,t) for i,t in enumerate(lines,1) if 'Automatic choice chain exceeds' in t]
  assert loc,item['id']
  item['source_evidence']=[dict(path=str(p.relative_to(ROOT)),line=i,text=t.strip()) for i,t in loc[:5]];item['source_linkage_complete']=True
 # Keep semantic status honest: linking a card or function is not a conformance proof.
 item['remaining_work_type']='rule_or_interaction_review' if 'reference' in item.get('status','') or 'unverified' in item.get('status','') else 'implementation_and_rule_review'
 item['semantic_resolution_complete']=False
summary.update(known_coding_work_packages=len(TASKS),coding_work_package_breakdown=dict(Counter(t['area'] for t in TASKS)),automatic_cast_predicate_checked_collectible_spells=len(admission),automatic_cast_predicate_rejected_past_spells=len(failed),automatic_cast_predicate_other_refusals=[x for x in admission if not x['allowed_classes'] and not x['past_census']],dynamic_standard_superset_sites=bounded,generic_pool_factory_definitions=forwarders,historical_dark_gift_routes=gifts,fidelity_entries_with_source_links=sum(x['source_linkage_complete'] for x in fidelity),semantic_audit_complete=False,remaining_audit='Per-contract independent rules and interaction conformance, dynamic validity/empty pools, defensive guard reachability, and silent behavioral defects are not exhausted by this static inventory.')
for name,obj in [('source-audit-summary.json',summary),('coding-tasks-expanded.json',TASKS),('automatic-cast-admission.json',admission),('generation-call-sites.json',calls),('fidelity-source-review.json',fidelity)]: (D/name).write_text(json.dumps(obj,indent=2)+'\n')
with (D/'coding-tasks-expanded.csv').open('w',newline='') as stream:
 w=csv.writer(stream);w.writerow(['id','title','area','status','effort','action','done_when'])
 for t in TASKS:w.writerow([t['id'],t['title'],t['area'],t['status'],t['effort_band'],t['action'],t['done_when']])
p=D/'EXPANDED-AUDIT.md';s=p.read_text().replace('**84 confirmed coding work packages**','**114 confirmed coding work packages**')
s+='\n\n## Automatic-cast admission and dynamic-pool follow-up\n\nThe metadata-only internal-cast predicate was checked for every registered collectible spell across all eleven hero classes; no Game instance or episode was created. **Thirty registered historical spells are refused in every class.** Their actual native programs exist, but their operation names are absent from automatic-cast admission. Each is now an explicit coding task; admission must be connected with proper context semantics, not blindly whitelisted.\n\n'
s+='| Card | Current refused operations |\n| --- | --- |\n'
for x in failed:s+='| '+x['id']+' — '+x['name']+' | '+', '.join(y['name'] for y in x['root_operations'] if not y['admitted'])+' |\n'
s+=f'\nOf the original 136 dynamic request sites, **{bounded} are bounded by the fully registered Standard catalog**; their root registration coverage can therefore be established without enumerating dynamic costs. **{forwarders} are generic kwargs factories**, not four additional card pools. The explicitly historical Dark Gift route was also checked. This improves registration coverage only: dynamic empty-pool rules, targeting, cast support, probabilities and copied payload execution remain unproven.\n\nAll **160 fidelity records now have source anchors**. That is a complete linkage inventory, not 160 completed behavioral reviews. The whole-game coding percentage remains undefined; source enumeration cannot establish that no silent rule errors remain.\n'
p.write_text(s)
print(json.dumps({k:summary[k] for k in ('known_coding_work_packages','coding_work_package_breakdown','automatic_cast_predicate_rejected_past_spells','dynamic_standard_superset_sites','generic_pool_factory_definitions','fidelity_entries_with_source_links')}))
