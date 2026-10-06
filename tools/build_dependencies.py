"""Audit explicit card references without inferring effects from rules text.

Usage: python tools/build_dependencies.py --engine-root staging/rebased-88
This imports declarations and validates frozen metadata; it runs no games.
"""
import argparse
from collections import Counter
import ast
import gzip
import hashlib
import json
from pathlib import Path
import sys


def strings(value):
    if isinstance(value,str):
        yield value
    elif isinstance(value,(tuple,list,set,frozenset)):
        for child in value:yield from strings(child)
    elif isinstance(value,dict):
        for child in value.values():yield from strings(child)


def closure(start,graph):
    visited=set();pending=list(graph.get(start,()))
    while pending:
        item=pending.pop()
        if item in visited:continue
        visited.add(item);pending.extend(graph.get(item,()))
    return sorted(visited)


IDENTITY_SETS={'COIN_IDS','COLLECTIBLE_IDS','PASSIVE','TOKEN_IDS','PLAYABLE_TOKENS','NO_CORPSE'}
METADATA_MAPS={'LOCAL_TOKENS','TOKENS'}


def reference_role(node,parents):
    """Classify syntax only; this never certifies generation semantics.

    Known inventory containers are not generation operations. All literals stay
    in the report so classification cannot hide unresolved dependencies.
    """
    ancestors=[];current=node
    while current in parents:
        current=parents[current];ancestors.append(current)
    for ancestor in ancestors:
        if isinstance(ancestor,ast.Assign):
            names={target.id for target in ancestor.targets if isinstance(target,ast.Name)}
            if names & IDENTITY_SETS:return 'identity_inventory'
            if names & METADATA_MAPS:return 'metadata_record'
    parent=parents.get(node)
    if isinstance(parent,ast.Dict) and any(key is node for key in parent.keys):
        return 'declaration_key'
    if any(isinstance(a,ast.Compare) for a in ancestors):return 'identity_comparison'
    return 'unresolved_expression'


def build(root):
    sys.path.insert(0,str(root))
    from expanded import cards
    from expanded.status import code_fingerprint
    registry=cards.registry()
    with gzip.open(root/'data/standard/all_cards.json.gz','rt',encoding='utf-8') as f:
        metadata={c['id']:c for c in json.load(f)}
    metadata.update(registry)
    graph={};edges=[];unassigned=[];source_hashes={}
    # Extract literal keyed declarations, including choices, triggers and
    # death effects. References can mean comparison as well as generation.
    for directory in ('expanded','engine'):
        for path in sorted((root/directory).glob('*.py')):
            source=path.read_text();relative=str(path.relative_to(root))
            source_hashes[relative]=hashlib.sha256(source.encode()).hexdigest()
            tree=ast.parse(source);assigned_nodes=set()
            parents={child:parent for parent in ast.walk(tree) for child in ast.iter_child_nodes(parent)}
            for node in tree.body:
                if not isinstance(node,ast.Assign) or not isinstance(node.value,ast.Dict):continue
                for key,value in zip(node.value.keys,node.value.values):
                    if not isinstance(key,ast.Constant) or key.value not in metadata:continue
                    try:definition=ast.literal_eval(value)
                    except (ValueError,TypeError):continue
                    for child in ast.walk(value):assigned_nodes.add(id(child))
                    for target in sorted(set(strings(definition)) & metadata.keys()):
                        graph.setdefault(key.value,set()).add(target)
                        edges.append(dict(source=key.value,target=target,file=relative,line=value.lineno,
                                          target_registered=target in registry))
            # Hard-coded branches and computed declarations require review:
            # do not falsely assign their references to a generating card.
            for node in ast.walk(tree):
                if isinstance(node,ast.Constant) and isinstance(node.value,str) and node.value in metadata and id(node) not in assigned_nodes:
                    unassigned.append(dict(card_id=node.value,file=relative,line=node.lineno,registered=node.value in registry,reference_role=reference_role(node,parents)))
    roots=sorted(cards.COLLECTIBLE_IDS)
    rows=[]
    for cid in roots:
        reachable=closure(cid,graph)
        rows.append(dict(card_id=cid,declared_reachable_references=reachable,
                         missing_registered_references=sorted(set(reachable)-registry.keys()),
                         semantic_dependency_closure_certified=False))
    missing=sorted({cid for row in rows for cid in row['missing_registered_references']})
    roles=dict(sorted(Counter(item['reference_role'] for item in unassigned).items()))
    report=dict(schema=2,engine_root=str(root),code_fingerprint=code_fingerprint(),
                collectible_roots=len(roots),registered_cards=len(registry),
                source_sha256=source_hashes,declared_reference_edges=edges,
                missing_registered_references=missing,roots=rows,
                unassigned_source_references=unassigned,unassigned_reference_roles=roles,
                full_dependency_closure_certified=False,
                limitations=['References are not necessarily generation edges.',
                             'Reference roles describe syntax only; all occurrences are retained.',
                             'Computed IDs and dynamic pools require explicit semantic review.',
                             'A registered record does not prove all of its behavior is implemented.',
                             'No rules text is parsed into executable effects.'])
    out=root/'runs/dependency_audit';out.mkdir(parents=True,exist_ok=True)
    (out/'references.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(collectible_roots=len(roots),declared_edges=len(edges),missing_registered_references=missing,unassigned_references=len(unassigned),reference_roles=roles,full_dependency_closure_certified=False)))
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--engine-root',type=Path,required=True)
    args=parser.parse_args();build(args.engine_root.resolve())
