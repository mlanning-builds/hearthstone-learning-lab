"""Explicit literal generation dependencies; never infer behavior from card text.

This report covers named operation arguments, not dynamic pools or arbitrary
Python helpers. A clean report is not full dependency certification.
"""

# Positions are part of the engine operation schema, not string heuristics.
SINGLE = {'evolving_advance':1, 'store_highest_spell_aura':1, 'archmage_cast':1, 'cast_fixed_spell':1, 'combo_cast_fixed_spell':1, 'on_draw_shuffle':1, 'force_summon_group':1, 'bonus_summon':1, 'local_enemy_summon':1, 'local_spell_treant':1, 'local_fill_enemy_coins':1, 'add_spell_damage':1, 'at_current_end_add':1, 'add_to_player':2, 'summon_death_identity':1, 'summon_identity_buff':1, 'insert_fixed':1, 'bounce_then_summon':1, 'damage_then_summon_if_dead':2, 'fill_board_summon':1, 'summon':1, 'combo_summon':1, 'death_summon':1,
          'raise_corpses':1, 'tomb_guardians':1, 'add':1, 'equip':1}
GROUP = {'summon_fixed_random':1, 'death_summon_group':1, 'choose_fixed_summon':1}


def literal_dependencies(value):
    found=set()
    def visit(node):
        if not isinstance(node,(tuple,list)):
            return
        if node and isinstance(node[0],str):
            name=node[0]
            if name in SINGLE:
                index=SINGLE[name]
                if len(node)>index and isinstance(node[index],str):found.add(node[index])
            elif name in GROUP:
                index=GROUP[name]
                if len(node)>index and isinstance(node[index],(tuple,list)):
                    found.update(cid for cid in node[index] if isinstance(cid,str))
        for child in node:
            visit(child)
    visit(value)
    return found


def dependency_report(declarations, available, roots=None):
    """Report missing literal dependencies with a shortest path from each root.

    Cycles are valid graph structure. A leaf with no declarations can be a
    vanilla card; this function cannot certify that its behavior is complete.
    """
    available=set(available)
    graph={cid:sorted(literal_dependencies(rules)) for cid,rules in declarations.items()}
    roots=sorted(set(declarations) if roots is None else set(roots))
    failures=[]
    for root in roots:
        queue=[(root,[root])];seen={root};cursor=0
        while cursor<len(queue):
            cid,path=queue[cursor];cursor+=1
            if cid not in available:
                failures.append(dict(root=root,missing=cid,path=path))
                continue
            for target in graph.get(cid,()):
                if target not in seen:
                    seen.add(target);queue.append((target,path+[target]))
    return dict(scope='Explicit literal generation operation arguments only',
                complete_dependency_coverage=False,
                checked_operations=sorted(set(SINGLE)|set(GROUP)),
                roots_checked=len(roots),edges=sum(map(len,graph.values())),
                missing_ids=sorted({item['missing'] for item in failures}),
                missing_paths=failures,
                limitation='Dynamic pools, computed IDs, legacy/helper behavior and executable fidelity still require review.')


def declaration_operations(tables):
    """Extract operations using each table's schema, excluding trigger labels."""
    declarations={}
    for name in ('RULES','TRIGGERS','START_EFFECTS'):
        for cid,value in tables.get(name,{}).items():
            declarations.setdefault(cid,[]).append(value[1])
    for name in ('DEATH_EFFECTS','END_EFFECTS','END_EVERY_EFFECTS'):
        for cid,value in tables.get(name,{}).items():
            declarations.setdefault(cid,[]).append(value)
    for cid,choices in tables.get('CHOICES',{}).items():
        for label,target,operations in choices:
            declarations.setdefault(cid,[]).append(operations)
    # LOCATION_RULES contains target restrictions, not executable operations.
    return declarations


def current_dependency_report():
    from . import cards
    declarations=declaration_operations(vars(cards))
    # Timeline advancement is an explicit identity dependency even though
    # activation operations are assembled by the location lifecycle helper.
    from .evolving_locations import TIMELINES
    for root in cards.CLOSED_TIMELINE_ROOTS:
        stages=TIMELINES[root]
        for current,following in zip(stages,stages[1:]):
            declarations.setdefault(current,[]).append(('evolving_advance',following))
    registry=cards.registry()
    return dependency_report(declarations,registry,roots=cards.COLLECTIBLE_IDS)
