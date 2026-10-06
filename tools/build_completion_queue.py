"""Build a conservative all-card work queue, not a playable-card allowlist.

Unknown selectors are reported, never broadened or replaced with supported
cards. Graph edges are candidate dependencies, not certified pool membership.
"""
import argparse
from collections import Counter,defaultdict
from dataclasses import asdict,is_dataclass
import gzip,hashlib,json,sys
from pathlib import Path

# Relative engineering estimates for scheduling only; not time predictions.
EFFORT={
 'control':2,'hidden_state':3,'conditional_aura':2,'infinity':3,'secret':2,
 'deathrattle':3,'stored_cards':4,'persistent':4,'replacement_effect':5,
 'dark_gift':3,'rewind':5,'map':4,'void_soul':3,'animal_companion':4,
 'leyline':4,'imbue':6,'herald':7,'transformation':5,'automatic_casting':6,
 'automatic_play':7,'location':4,'quest':6,'colossal':7,'fabled':7,
 'setup':7,'deck_construction':5,'custom_creation':8,'custom_choice':4,
 'hidden_choice':4,'stored_spells':7,'timeline':6,'generation':4,'discover':4,
}
SELECTOR_OPS={'discover','discover_with_dark_gift','random_card','generate',
 'summon_random','cast_random_spells','fill_hand_random','fill_board_random',
 'replace_hand_and_deck_random','transform_random','replace_selected_with_random',
 'generate_and_heal_total_cost','summon_random_then_attack','summon_random_bind',
 'generate_and_track_physical_cards','discover_with_refresh','generate_random',
 'summon_random_mana_budget','summon_random_for_captured_owner'}


def components(graph):
    """Deterministic Tarjan SCCs; external nodes are not silently admitted."""
    index={};low={};stack=[];active=set();result=[]
    def visit(node):
        index[node]=low[node]=len(index);stack.append(node);active.add(node)
        for other in sorted(graph[node]):
            if other not in graph:continue
            if other not in index:visit(other);low[node]=min(low[node],low[other])
            elif other in active:low[node]=min(low[node],index[other])
        if low[node]==index[node]:
            group=[]
            while True:
                other=stack.pop();active.remove(other);group.append(other)
                if other==node:break
            result.append(sorted(group))
    for node in sorted(graph):
        if node not in index:visit(node)
    return sorted(result,key=lambda group:(-len(group),group))


def walk(value):
    yield value
    if isinstance(value,dict):
        for child in value.values():yield from walk(child)
    elif isinstance(value,(tuple,list)):
        for child in value:yield from walk(child)


def selector_request(selector,pool):
    """Translate only the exact, known subset. Return unresolved keys too."""
    mapping={'type':'card_type','tribe':'tribe','school':'school','rarity':'rarity',
             'era':'era','rune':'rune','mechanic':'mechanic','class':'classes','classes':'classes',
             'minimum_cost':'minimum','maximum_cost':'maximum','minimum_tribes':'minimum_tribes','family':'family'}
    args={};unknown=[]
    for key,value in selector.items():
        if key=='rune' and isinstance(value,str):args['rune']=value.lower()
        elif key=='cost' and type(value) is int:args.update(minimum=value,maximum=value)
        elif key in mapping and isinstance(value,(str,int)) and not isinstance(value,bool):args[mapping[key]]=value
        else:unknown.append(key)
    if unknown:return None,sorted(unknown)
    try:return pool(**args),[]
    except (TypeError,ValueError):return None,['unsupported_selector_value']


def named_runtime_bindings():
    """Explicit runtime identities, separate from effect/timing certification.

    No entourage/name guess and no permissive catch-all. Unlisted operations
    remain unresolved. These bindings identify dependencies; they never admit
    their source card or imply complete generated pools.
    """
    from expanded import colossals,dragon_soul,evolving_locations,genn,herald,quest_families
    bindings={}
    for cid,layout in colossals.LAYOUTS.items():
        bindings[(cid,'summon_appendages_by_dependency')]=(tuple(limb for limb,side in layout),
                                                         'expanded/colossals.py:LAYOUTS')
    bindings[('CATA_EVENT_110','replace_self_with_dependency_family')]=(dragon_soul.ESSENCES,
                                                                      'expanded/dragon_soul.py:ESSENCES')
    for cid,stages in evolving_locations.TIMELINES.items():
        bindings[(cid,'advance_dependency_to_present')]=(stages[1:],
                                                        'expanded/evolving_locations.py:TIMELINES')
    # Bind only the reviewed runtime declaration, rather than the source's
    # entourage (which may include unrelated display/choice records).
    bindings[('CATA_561','add_token_by_dependency')]=((herald.RULES['CATA_561'][1][1][1],),
                                                    'expanded/herald.py:RULES[CATA_561]')
    bindings[('CATA_615','transform_self_by_dependency')]=(tuple(genn.TOKEN_RULES),
                                                        'expanded/genn.py:TOKEN_RULES')
    bindings[('JAIL_443','shuffle_token_by_dependency_into_victim_deck')]=(('JAIL_443t',),
                                                          'expanded/replacements.py:_replace_plague_damage')
    rewards={
        ('END_017','tick_and_tock'):'END_017t',
        ('TLC_229','ashalon'):'TLC_229t14',
        ('TLC_460','origin_stone'):'TLC_460t',
        ('TLC_602','latorvius'):'TLC_602t',
        ('TLC_631','gorishi_colossus'):'TLC_631t',
        ('TLC_830','shokk'):'TLC_830t',
        ('TLC_817','lifes_breath'):quest_families.HALVES[0],
        ('TLC_817','deaths_touch'):quest_families.HALVES[1],
    }
    for (cid,label),reward in rewards.items():
        if reward not in quest_families.TOKEN_RULES:
            raise ValueError('Named Quest reward has no runtime declaration: '+reward)
        bindings[(cid,'add_reward_by_dependency',label)]=((reward,),
                                                         'expanded/quest_families.py:TOKEN_RULES')
    return bindings


def build(engine_root):
    sys.path.insert(0,str(engine_root))
    from expanded.pending_definitions import DEFINITIONS
    from expanded.cards import COLLECTIBLE_IDS,registry
    from expanded.generation_cards import PoolRequest,pool,requests_for
    from expanded import exceptional_finish,minion_forge,custom_builders,morchie,random_targets,counterfeits,dragon_soul,titanographer,kindred,remaining_setup,hand_investigations,tiny_pal,healing_replacement,stat_rules,genn,replacements,turn_deadlines,infinity,deck_setup,fabled_effects,stored_obligations,learned_spells,zone_triggers,temporary_control,starting_rules,evolving_locations,colossal_bodies,herald,colossals,generation_cards,generation_extensions,dark_gift_generators,transformations,rewind_generators,imbue_consumers,choice_generators,historical_generation,health_generation,dormant_generation,conditional_discover,attack_generation,event_generation,exceptional_generation,leylines,maps,automatic_casting,future_summons
    from expanded.generation import request_matches
    from expanded.selectors import HERO_CLASSES
    from standard.catalog import load_catalog
    catalog={d['id']:d for d in load_catalog()}
    archive={d['id']:d for d in json.load(gzip.open(engine_root/'data/standard/all_cards.json.gz','rt'))}
    live=set(COLLECTIBLE_IDS)&catalog.keys();pending=set(catalog)-live;registered=set(registry())
    if set(DEFINITIONS)!=pending:raise ValueError('Every pending collectible must have exactly one staged recipe')
    rows=[];graph={cid:set() for cid in pending};impact=Counter()
    from expanded import quest_families
    declarations=set(exceptional_finish.RULES)|set(minion_forge.RULES)|set(custom_builders.RULES)|set(morchie.RULES)|set(random_targets.RULES)|set(counterfeits.RULES)|set(dragon_soul.RULES)|set(titanographer.RULES)|set(kindred.RULES)|set(remaining_setup.RULES)|set(hand_investigations.RULES)|set(tiny_pal.RULES)|set(healing_replacement.RULES)|set(stat_rules.RULES)|set(genn.RULES)|set(replacements.RULES)|set(turn_deadlines.RULES)|set(infinity.RULES)|set(deck_setup.RULES)|set(quest_families.RULES)|set(fabled_effects.RULES)|set(stored_obligations.RULES)|set(learned_spells.RULES)|set(zone_triggers.RULES)|set(temporary_control.RULES)|set(starting_rules.RULES)|set(starting_rules.STAGED_RULES)|set(evolving_locations.RULES)|set(generation_cards.RULES)|set(generation_extensions.RULES)|set(dark_gift_generators.RULES)|set(transformations.RULES)|set(rewind_generators.RULES)|set(imbue_consumers.RULES)|set(choice_generators.RULES)|set(historical_generation.RULES)|set(health_generation.RULES)|set(dormant_generation.RULES)|set(conditional_discover.RULES)|set(attack_generation.RULES)|set(event_generation.RULES)|set(exceptional_generation.RULES)|set(leylines.RULES)|set(maps.RULES)|set(automatic_casting.RULES)|set(future_summons.RULES)|set(herald.RULES)|set(colossal_bodies.RULES)
    named_bindings=named_runtime_bindings()
    for cid in sorted(pending):
        d=DEFINITIONS[cid];hooks=d['hooks'];requests=set(exceptional_finish.requests_for(cid))|set(custom_builders.requests_for(cid))|set(morchie.requests_for(cid))|set(counterfeits.requests_for(cid))|set(titanographer.requests_for(cid))|set(remaining_setup.requests_for(cid))|set(hand_investigations.requests_for(cid))|set(tiny_pal.requests_for(cid))|set(quest_families.requests_for(cid))|set(fabled_effects.requests_for(cid))|set(stored_obligations.requests_for(cid))|set(learned_spells.requests_for(cid))|set(evolving_locations.requests_for(cid))|set(requests_for(cid))|set(generation_extensions.requests_for(cid))|set(transformations.requests_for(cid))|set(rewind_generators.requests_for(cid))|set(imbue_consumers.requests_for(cid))|set(choice_generators.requests_for(cid))|set(historical_generation.requests_for(cid))|set(health_generation.requests_for(cid))|set(dormant_generation.requests_for(cid))|set(conditional_discover.requests_for(cid))|set(event_generation.requests_for(cid))|set(exceptional_generation.requests_for(cid))|set(maps.requests_for(cid))|set(automatic_casting.requests_for(cid))|set(future_summons.requests_for(cid))|set(herald.requests_for(cid))|set(colossal_bodies.requests_for(cid))
        unresolved=[];mapped_dependencies=[];references=set(catalog[cid].get('entourage',()))
        if cid=='TLC_631':references.add('TLC_631t')
        if cid=='END_017':references.add('END_017t')
        if cid=='TLC_830':references.add('TLC_830t')
        if cid=='TLC_460':references.add('TLC_460t')
        if cid=='CATA_470':references.add('CATA_470t1')
        if cid=='TLC_EVENT_400':references.add('ICC_828t')
        if cid=='CAP_405':references.update(custom_builders.TRIAL_IDS);references.update('CAP_405t'+str(n) for n in range(1,10));references.update(c+'b' for c in custom_builders.TRIAL_IDS);references.update(('LOOT_368','CS2_065'))
        if cid=='TLC_100':references.update(custom_builders.LOCATION_IDS);references.update('TLC_100t'+str(t)+str(n) for t in (1,2,3) for n in range(1,8));references.add('DINO_136t')
        if cid=='JAIL_504':references.update(counterfeits.TOKEN_RULES);references.update(('CFM_621_m2','JAIL_504tt01'))
        if cid==dragon_soul.ROOT:references.update(dragon_soul.ESSENCES);references.add(dragon_soul.ROOT+'t6t')
        if cid=='TLC_452':references.update(titanographer.FORMS);references.update(titanographer.TOKENS)
        if cid=='JAIL_458':references.update(tiny_pal.AMMUNITION)
        if cid=='CATA_615':references.update(('CATA_615t','AT_132_ROGUEt',*genn.POWERS.values()))
        if cid=='TLC_602':references.update(('TLC_602t',*quest_families.LATORVIUS_REWARDS,'UNG_920t2','UNG_934t2','UNG_829t2','UNG_829t3',quest_families.PLANT,*quest_families.ADAPTATIONS))
        if cid=='TLC_229':references.update(('TLC_229t14',quest_families.PLANT,*quest_families.ADAPTATIONS))
        if cid==quest_families.ROOT:
            references.update(quest_families.SUBQUESTS+quest_families.HALVES+(quest_families.COMBINED,))
        if cid in fabled_effects.RULES:
            from expanded.fabled_decks import BUNDLES
            references.update(BUNDLES[cid])
            if cid=='TIME_211':
                from expanded.azshara import UPGRADES
                references.update(UPGRADES.values())
            if cid=='TIME_619':references.update(fabled_effects.BOONS)
            if cid=='TIME_005':references.add('TIME_005t9t')
            if cid=='TIME_009':
                from expanded.gelbin import AURA_IDS
                references.update(AURA_IDS)
            if cid=='TIME_020':
                from expanded.broxigar import TOKEN_RULES
                references.update(TOKEN_RULES)
        if cid in learned_spells.RULES:references.add(cid+'t')
        if cid=='JAIL_887':references.update(('JAIL_887t2','JAIL_887t3'))
        if cid in evolving_locations.TIMELINES:references.update(evolving_locations.TIMELINES[cid])
        if cid=='CATA_527':references.add('CATA_527t2')
        if cid=='CATA_190h':references.update(set(herald.CATACLYSMS)|{'CATA_190p','CATA_190t14'})
        if cid in colossals.LAYOUTS:references.update(limb for limb,side in colossals.LAYOUTS[cid])
        if cid in herald.RULES and cid!='CATA_190h':references.update(herald.SOLDIERS.values())
        if cid=='CATA_561':references.add('CATA_561t')
        if cid in herald.UNRESOLVED:unresolved.append(dict(operation='herald_exception',reason=[herald.UNRESOLVED[cid]]))
        if cid in automatic_casting.UNRESOLVED:unresolved.append(dict(operation='automatic_casting',reason=[automatic_casting.UNRESOLVED[cid]]))
        if cid in rewind_generators.UNRESOLVED:unresolved.append(dict(operation='rewind_family',reason=[rewind_generators.UNRESOLVED[cid]]))
        if cid=='CORE_EDR_004_2026':requests.update(rewind_generators.BEAST_GIFT.alternatives)
        if cid in transformations.UNRESOLVED:unresolved.append(dict(operation='transformation_family',reason=[transformations.UNRESOLVED[cid]]))
        for gift_request in dark_gift_generators.requests_for(cid):
            if gift_request.historical:unresolved.append(dict(operation='dark_global_discover',reason=['historical_membership_contract']))
            else:requests.update(gift_request.alternatives)
        for value in walk(hooks):
            if isinstance(value,PoolRequest):requests.add(value)
            elif isinstance(value,str) and value in archive and value!=cid:references.add(value)
            elif isinstance(value,(list,tuple)) and value and isinstance(value[0],str):
                name=value[0]
                if name in SELECTOR_OPS:
                    found=False
                    for child in value[1:]:
                        if isinstance(child,dict):
                            request,unknown=selector_request(child,pool)
                            if request is not None:requests.add(request);found=True
                            else:unresolved.append(dict(operation=name,selector=child,reason=unknown))
                            break
                    if not found and not any(isinstance(v,PoolRequest) for v in value):
                        unresolved.append(dict(operation=name,reason=['dynamic_or_nonstandard_pool']))
                if 'dependency' in name or name in ('summon_token_by_dependency','add_token_by_dependency'):
                    specific=(cid,name,value[2]) if len(value)>2 and isinstance(value[2],str) else None
                    binding=named_bindings.get(specific,named_bindings.get((cid,name)))
                    if binding is not None:
                        ids,source=binding
                        references.update(ids)
                        mapped_dependencies.append(dict(operation=name,card_ids=list(ids),source=source,
                                                        interaction_review_complete=False))
                    else:
                        unresolved.append(dict(operation=name,reason=['named_dependency_requires_mapping']))
        if cid in ('CATA_567','EDR_529','TLC_235'):
            # Planning superset only: reachable Costs still require separate contracts.
            requests.add(pool(card_type='MINION'))
            unresolved.append(dict(operation='dynamic_transformation_cost',reason=['reachable_cost_pool_contracts_required']))
        candidate_ids=set();contexts=[]
        for request in sorted(requests,key=repr):
            if request.era=='past':
                unresolved.append(dict(operation='historical_generation',selector=asdict(request),reason=['complete_historical_membership_and_outcome_closure']))
                contexts.append(dict(selector=asdict(request),candidate_ids=[],membership_reviewed=False))
                continue
            matches=set()
            for owner in sorted(HERO_CLASSES):
                matches.update(k for k,record in catalog.items() if request_matches(request,record,owner))
            candidate_ids.update(matches)
            contexts.append(dict(selector=asdict(request),candidate_ids=sorted(matches),membership_reviewed=False))
        missing=(candidate_ids|references)&pending
        graph[cid]=missing;impact.update(missing-{cid})
        tokens=references-catalog.keys();token_missing=tokens-registered
        barriers=['recipe_behavior_review','integration_validation']
        if cid in quest_families.RULES:barriers.append('compound_quest_reward_review')
        if cid in fabled_effects.RULES:barriers.append('fabled_bundle_effects_and_interactions_review')
        if cid in stored_obligations.RULES:barriers.append('stored_obligation_identity_and_timing_review')
        if cid in learned_spells.RULES:barriers.append('learned_spell_targets_pools_and_budget_review')
        if cid in evolving_locations.RULES:barriers.append('evolving_location_and_replacement_timing_review')
        if cid in temporary_control.RULES:barriers.append('control_return_order_and_overlap_review')
        if cid in starting_rules.STAGED_RULES:barriers.append('overdraw_recovery_timing_review')
        if cid in zone_triggers.RULES:barriers.append('hero_death_and_zone_trigger_timing_review')
        final_modules=(replacements,genn,stat_rules,tiny_pal,healing_replacement,hand_investigations,remaining_setup,kindred,titanographer,dragon_soul,counterfeits,random_targets,morchie,custom_builders,minion_forge,exceptional_finish)
        if any(cid in module.RULES for module in final_modules):barriers.append('staged_runtime_contract_and_interaction_review')
        if cid in minion_forge.RULES or cid in exceptional_finish.RULES:
            barriers.append('incomplete_runtime_or_production_contract')
            unresolved.append(dict(operation='exceptional_runtime',reason=['curated_components_distribution_or_immunity_incomplete']))
        if cid not in declarations:barriers.append('runtime_declaration_missing')
        if cid in transformations.RULES or cid in genn.RULES:barriers.append('transformation_pool_and_interaction_review')
        if cid in rewind_generators.RULES or cid in morchie.RULES:barriers.append('rewind_pool_and_interaction_review')
        if cid in historical_generation.RULES:barriers.append('historical_membership_and_behavior_review')
        if cid in event_generation.RULES or cid in exceptional_generation.RULES:barriers.append('generation_lifecycle_pool_and_interaction_review')
        if cid in herald.RULES:barriers.append('herald_army_timing_offclass_and_pool_review')
        if cid in colossal_bodies.RULES:barriers.append('colossal_body_pool_and_order_review')
        elif cid in colossals.LAYOUTS:barriers.append('colossal_entry_only_body_and_limb_abilities_pending')
        if cid in future_summons.RULES:barriers.append('future_summon_pool_and_scaling_review')
        if cid in automatic_casting.RULES or cid=='FIR_959':barriers.append('automatic_cast_pool_and_interaction_review')
        if cid in maps.RULES:barriers.append('map_original_options_and_pool_review')
        if cid in leylines.RULES:barriers.append('leyline_pool_and_upgrade_review')
        if cid in attack_generation.RULES:barriers.append('dynamic_attack_pool_and_combat_review')
        if cid in conditional_discover.RULES:barriers.append('any_demon_scope_and_conditional_discount_review')
        if cid in dormant_generation.RULES:barriers.append('dormant_generation_pool_and_entry_review')
        if cid in health_generation.RULES:barriers.append('health_payment_generation_review')
        if cid in choice_generators.RULES:barriers.append('choice_generation_pool_and_interaction_review')
        if cid in imbue_consumers.RULES:barriers.append('imbue_class_powers_pool_and_interaction_review')
        if contexts:barriers.append('generation_membership_review')
        if missing:barriers.append('pending_collectible_outcomes')
        if token_missing:barriers.append('unimplemented_explicit_tokens')
        if unresolved:barriers.append('unresolved_selector_or_dependency')
        rows.append(dict(card_id=cid,name=catalog[cid]['name'],family=d['family'],
            record_sha256=hashlib.sha256(json.dumps(catalog[cid],sort_keys=True).encode()).hexdigest(),
            runtime_declaration_present=cid in declarations,
            runtime_declaration_note='Presence is not a review of every hook or proof of executable completion.',
            blockers=barriers,explicit_references=sorted(references),unimplemented_explicit_tokens=sorted(token_missing),
            mapped_dependencies=mapped_dependencies,
            missing_candidate_collectibles=sorted(missing),candidate_pool_contexts=contexts,
            unresolved=unresolved))
    groups=components(graph)
    cyclic=[g for g in groups if len(g)>1 or (g and g[0] in graph[g[0]])]
    by_family=defaultdict(list)
    for row in rows:by_family[row['family']].append(row)
    families=[]
    for family,members in by_family.items():
        ids={r['card_id'] for r in members};affected={k for k,v in graph.items() if k not in ids and v&ids}
        effort=EFFORT.get(family,8)
        families.append(dict(family=family,card_ids=sorted(ids),remaining=len(ids),
            staged_runtime_declarations=sum(r['runtime_declaration_present'] for r in members),
            external_generators_affected=len(affected),relative_effort=effort,
            priority_score=round((len(ids)+len(affected))/effort,2),
            unresolved_cards=sum(bool(r['unresolved']) for r in members),
            proposed_sequence=['review_printed_behavior_and_dependencies','implement_shared_runtime',
                               'connect_every_family_member_and_token','focused_interaction_checks',
                               'review_complete_outcome_pools','admit_closed_dependency_group','consolidated_regression']))
    families.sort(key=lambda row:(-row['priority_score'],row['family']))
    for rank,row in enumerate(families,1):row['priority']=rank
    return dict(schema=1,scope='All frozen Standard collectibles; generated dependencies included, historical pools explicitly unresolved.',
        catalog_size=len(catalog),live_collectibles=len(live),remaining_collectibles=len(pending),
        completion_target='Zero unsupported collectible behavior and required generated outcomes, followed by fidelity gates.',
        methodology='Conservative candidate graph. Explicit runtime identity bindings resolve named dependencies only; independent behavior review and pool gates remain. Scores are relative effort and fan-out, not measured time.',
        source_sha256=hashlib.sha256(Path(__file__).read_bytes()+b''.join((engine_root/path).read_bytes() for path in ('expanded/exceptional_finish.py','expanded/minion_forge.py','expanded/custom_builders.py','expanded/morchie.py','expanded/random_targets.py','expanded/counterfeits.py','expanded/dragon_soul.py','expanded/titanographer.py','expanded/kindred.py','expanded/remaining_setup.py','expanded/hand_investigations.py','expanded/tiny_pal.py','expanded/healing_replacement.py','expanded/stat_rules.py','expanded/genn.py','expanded/replacements.py','expanded/turn_deadlines.py','expanded/infinity.py','expanded/deck_setup.py','expanded/historical_vanilla.py','expanded/historical_simple.py','expanded/historical_numeric.py','expanded/automatic_cards.py','expanded/discover_offer.py','expanded/adapt.py','expanded/quest_families.py','expanded/quest_progress.py','expanded/muradin.py','expanded/azshara.py','expanded/fabled_decks.py','expanded/fabled_effects.py','expanded/gelbin.py','expanded/broxigar.py','expanded/rafaam.py','expanded/garona.py','expanded/stored_obligations.py','expanded/learned_spells.py','expanded/zone_triggers.py','expanded/temporary_control.py','expanded/starting_rules.py','expanded/evolving_locations.py','expanded/pending_definitions.py','expanded/cards.py','expanded/generation_cards.py','expanded/generation_extensions.py','expanded/dark_gift_generators.py','expanded/transformations.py','expanded/rewind_generators.py','expanded/imbue_consumers.py','expanded/choice_generators.py','expanded/historical_generation.py','expanded/health_generation.py','expanded/dormant_generation.py','expanded/conditional_discover.py','expanded/attack_generation.py','expanded/event_generation.py','expanded/exceptional_generation.py','expanded/leylines.py','expanded/maps.py','expanded/automatic_casting.py','expanded/future_summons.py','expanded/colossals.py','expanded/herald.py','expanded/colossal_bodies.py','expanded/herald_values.json','expanded/generation.py','data/standard/cards.json'))).hexdigest(),
        unresolved_cards=sum(bool(row['unresolved']) for row in rows),
        cyclic_candidate_groups=cyclic,family_queue=families,cards=rows)


def markdown(report):
    out=['# All-card completion queue','',
         f"{report['live_collectibles']} live collectibles; {report['remaining_collectibles']} pending. No card-count batch limit.",'',
         'Generated output: run `tools/build_completion_queue.py --engine-root staging/rebased-88` from the project root. JSON contains every card, selector, explicit token and unresolved dependency.','',
         '**Planning candidates, not approved pools.** A missing edge does not prove no dependency; unresolved selectors and named tokens remain blockers. Runtime declaration presence is not completed behavior. Explicit mapped dependencies resolve identity only; behavior, timing, complete pools and live admission remain separate gates.','',
         f"{report['unresolved_cards']} cards have unresolved selector/dependency mappings. {len(report['cyclic_candidate_groups'])} candidate cyclic groups require coordinated review and admission; the largest has {max(map(len,report['cyclic_candidate_groups']),default=0)} cards.",'',
         'The priority score is (family size + distinct external generators affected) / relative effort. Effort is an explicit engineering estimate, not a delivery estimate. Break ties and dependency cycles using reviewed mechanics; do not enable incomplete pools.','',
         '| Priority | Family | Pending | Runtime declarations present | External generators affected | Relative effort | Score |',
         '| --- | --- | ---: | ---: | ---: | ---: | ---: |']
    for r in report['family_queue']:out.append(f"| {r['priority']} | {r['family']} | {r['remaining']} | {r['staged_runtime_declarations']} | {r['external_generators_affected']} | {r['relative_effort']} | {r['priority_score']} |")
    out+=['','## Completion gates','',
          '1. Review each printed effect and resolve named tokens, dynamic selectors and historical pools.',
          '2. Implement shared behavior and all family bindings; test interactions with controlled complete fixture pools.',
          '3. Review actual production membership. Complete all behavior in a cyclic group before admitting it together.',
          '4. Run consolidated regression and random legal-game checks against an unchanged source fingerprint.',
          '5. Resolve independent fidelity gaps; then proceed to learning and deck optimization.','',
          'The former fixed 60-card ledger is historical evidence only. It is not the work queue or a completion constraint.']
    return '\n'.join(out)+'\n'


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--engine-root',type=Path,required=True);parser.add_argument('--output-dir',type=Path)
    args=parser.parse_args();root=args.engine_root.resolve();out=args.output_dir or root/'../../docs/engine-audit'
    report=build(root);out.mkdir(parents=True,exist_ok=True)
    (out/'completion-queue.json').write_text(json.dumps(report,indent=2)+'\n')
    (out/'completion-queue.md').write_text(markdown(report))
    print(json.dumps({k:report[k] for k in ('live_collectibles','remaining_collectibles','unresolved_cards')}))
    print(json.dumps([{'family':r['family'],'remaining':r['remaining'],'score':r['priority_score']} for r in report['family_queue'][:6]]))

if __name__=='__main__':main()
