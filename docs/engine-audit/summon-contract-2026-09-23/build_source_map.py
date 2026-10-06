"""Read-only AST inventory; no simulator imports or execution."""
import ast,hashlib,json
from pathlib import Path
p=Path('/Users/matthewlanning/Desktop/HearthStone AI /death-knight-lab');root=p/'staging/rebased-88'
methods={'_summon','_create_minion','_queue_event','_secret_event','_settle','_damage_batch','_start_play_effects','_after_play'}
rows=[];hashes={};functions=[]
for path in sorted((root/'expanded').glob('*.py')):
 data=path.read_bytes();rel=str(path.relative_to(p));hashes[rel]=hashlib.sha256(data).hexdigest();tree=ast.parse(data);parents={child:n for n in ast.walk(tree) for child in ast.iter_child_nodes(n)}
 for n in ast.walk(tree):
  if isinstance(n,ast.FunctionDef):functions.append({'file':rel,'function':n.name,'line':n.lineno,'end_line':n.end_lineno})
  if not isinstance(n,ast.Call) or not isinstance(n.func,ast.Attribute) or n.func.attr not in methods:continue
  parent=n;fn=None;branches=[]
  while parent in parents:
   parent=parents[parent]
   if isinstance(parent,ast.If):branches.append({'line':parent.lineno,'condition':ast.unparse(parent.test)})
   if isinstance(parent,ast.FunctionDef):fn=parent.name;break
  rows.append({'file':rel,'line':n.lineno,'function':fn,'callee':n.func.attr,'expression':ast.unparse(n),'enclosing_if_conditions':branches,'mapping_type':'static_callsite_not_execution_trace'})
report={'schema':1,'scope':'candidate expanded Python direct attribute calls only; excludes inherited engine implementations and dynamic dispatch','source_sha256':hashes,'functions':functions,'calls':rows,'counts':{m:sum(r['callee']==m for r in rows) for m in sorted(methods)}}
Path('/private/tmp/hs-summon-contract/source-event-map.json').write_text(json.dumps(report,indent=2)+'\n')
print(report['counts'])
