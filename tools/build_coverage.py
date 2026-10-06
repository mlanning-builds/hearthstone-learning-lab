"""Build a source inventory only. Never imports the engine or executes tests.

Run from anywhere with Python's standard library. Entries are declarations and
references, not inferred executable rules or proof of per-card correctness.
"""
import ast
import hashlib
import json
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]

def literal_entries(path):
    tree = ast.parse(path.read_text(), filename=str(path))
    for node in tree.body:
        if not isinstance(node, ast.Assign) or not isinstance(node.value, ast.Dict):
            continue
        names = [n.id for n in node.targets if isinstance(n, ast.Name)]
        for key, value in zip(node.value.keys, node.value.values):
            if not isinstance(key, ast.Constant) or not isinstance(key.value, str):
                continue
            try:
                definition = ast.literal_eval(value)
            except (ValueError, TypeError):
                definition = None
            for name in names:
                yield key.value, dict(file=str(path.relative_to(ROOT)), line=value.lineno,
                                      registry=name, literal_definition=definition)

def fingerprint(root=None):
    root = ROOT if root is None else root
    h = hashlib.sha256()
    paths = (sorted((root/'expanded').glob('*.py')) + sorted((root/'expanded').glob('*.json'))
             + sorted((root/'engine').glob('*.py')) + [root/'data/standard/manifest.json', root/'standard/catalog.py']
             + sorted((root/'tests').glob('test_expanded*.py')))
    for path in paths:
        h.update(str(path.relative_to(root)).encode()); h.update(path.read_bytes())
    return h.hexdigest()

def validation_evidence(root):
    path=root/'runs/expanded_validation/validation.json'
    receipt=json.loads(path.read_text()) if path.exists() else None
    current=fingerprint(root)
    return dict(code_fingerprint=current,suite_receipt=receipt,
                suite_receipt_matches_current_code=bool(receipt and receipt.get('success') and receipt.get('fingerprint')==current))

def build():
    catalog = json.loads((ROOT/'data/standard/cards.json').read_text())
    manifest = json.loads((ROOT/'data/standard/manifest.json').read_text())
    for name, digest in manifest['files_sha256'].items():
        if Path(name).name != name:
            raise ValueError('Invalid catalog file name')
        if hashlib.sha256((ROOT/'data/standard'/name).read_bytes()).hexdigest() != digest:
            raise ValueError('Frozen catalog changed: '+name)
    ids = {c['id'] for c in catalog}
    if len(ids) != len(catalog) or len(ids) != manifest['standard_catalog_count']:
        raise ValueError('Duplicate IDs or inconsistent catalog count')
    active = set(json.loads((ROOT/'expanded/implementation_index.json').read_text())['implemented_card_ids'])
    stage = json.loads((ROOT/'staging/standard-200/progress.json').read_text())
    staged = set(stage['staged_cards'])
    if active & staged or not (active | staged) <= ids:
        raise ValueError('Invalid active/staged inventory')
    declarations = {}
    # Inspect literal declarations only. Computed sets, special-case branches,
    # and imported legacy behavior are not fabricated into a complete mapping.
    paths = [ROOT/'expanded/cards.py', ROOT/'expanded/locations.py', ROOT/'expanded/secrets.py',
             ROOT/'staging/rebased-88/expanded/cards.py']
    for path in paths:
        for cid, entry in literal_entries(path):
            if cid in ids:
                declarations.setdefault(cid, []).append(entry)
    references = {}
    for path in sorted((ROOT/'tests').glob('test_expanded*.py')):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                for cid in {n.value for n in ast.walk(node) if isinstance(n, ast.Constant)
                            and isinstance(n.value, str) and n.value in ids}:
                    references.setdefault(cid, []).append(dict(file=str(path.relative_to(ROOT)),
                                                               test=node.name, line=node.lineno))
    receipt_path = ROOT/'runs/expanded_validation/validation.json'
    receipt = json.loads(receipt_path.read_text()) if receipt_path.exists() else None
    current = fingerprint()
    candidate_evidence=validation_evidence(ROOT/'staging/rebased-88')
    rows = []
    for c in sorted(catalog, key=lambda c:c['id']):
        cid = c['id']
        rows.append(dict(id=cid, name=c['name'], classes=c.get('classes') or [c.get('cardClass')],
                         type=c['type'], set=c['set'], imported_mechanics=c.get('mechanics',[]),
                         state='active_written' if cid in active else 'staged_unvalidated' if cid in staged else 'unimplemented',
                         declarations=[e for e in declarations.get(cid,[]) if
                                       e['file'].startswith('staging/') == (cid in staged)] if cid in active|staged else [],
                         active_test_literal_references=references.get(cid,[]),
                         semantic_review='pending', required_systems=None,
                         generated_dependency_closure='not_certified', independent_validation='pending'))
    report = dict(schema=2, scope='Regular Hearthstone Standard; excludes Mercenaries and Battlegrounds',
                  patch=manifest['patch'], legality_as_of=manifest['as_of'], code_fingerprint=current,
                  counts=dict(Counter(row['state'] for row in rows)), catalog_count=len(rows),
                  suite_receipt=receipt,
                  suite_receipt_matches_current_code=bool(receipt and receipt.get('success') and receipt.get('fingerprint')==current),
                  active_validation_scope="Root active engine only", candidate_validation=candidate_evidence,
                  semantic_map_complete=False, full_standard_ready=False,
                  notes=['Imported mechanic tags are metadata, not executable rules.',
                         'Literal test references include fixtures and opponents; they are not per-card validation.',
                         'No card has been marked fully reviewed by this inventory.',
                         'Literal declaration extraction omits computed/imported rules and special-case dispatch.',
                         'Rebased candidate is isolated; semantic review and full milestone integration remain.'], cards=rows)
    out = ROOT/'docs/coverage';out.mkdir(parents=True,exist_ok=True)
    (out/'standard-inventory.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    lines = ['# Standard implementation inventory', '',
             'Generated by `tools/build_coverage.py` using JSON and Python AST inspection only.', '',
             f"Pinned patch: **{manifest['patch']}**. Catalog cutoff: **{manifest['as_of']}**.", '',
             f"**{len(active)} active; {len(staged)} staged; {len(ids-active-staged)} without an active or staged implementation.**", '',
             'This is a complete card inventory, **not a complete semantic dependency map**. Required systems and generated dependency closure remain under review. No behavior is inferred from rules text.', '',
             f"Active engine suite receipt matches current source: **{report['suite_receipt_matches_current_code']}**. This is suite-level evidence only.", '',
             f"Candidate suite receipt matches current source: **{candidate_evidence['suite_receipt_matches_current_code']}**. This is separate from integration and per-card fidelity review.", '',
             'The JSON companion contains source locations, literal definitions, imported mechanic tags and test references. Test references may merely use the card as a fixture.', '',
             '| ID | Card | Class | Implementation |', '| --- | --- | --- | --- |']
    for row in rows:
        name=row['name'].replace('|','\\|').replace('\n',' ')
        lines.append(f"| `{row['id']}` | {name} | {', '.join(row['classes'])} | {row['state']} |")
    (out/'README.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({k:report[k] for k in ('catalog_count','counts','suite_receipt_matches_current_code','semantic_map_complete')}))

if __name__ == '__main__':
    build()
