"""Emit explicit structural contracts for the legacy authored effect grammar.

Run from the candidate directory with PYTHONPATH=. This reads Python effect
programs, never card text, and does not run a game or start training. New operand
forms must be reviewed before replacing the checked-in catalog.
"""
from pathlib import Path
from collections import defaultdict
import json
from expanded import cards,effect_schema
from expanded.generation_cards import PoolRequest
from expanded.dark_gift_generators import GiftRequest


def main():
 reports=effect_schema.validate_namespace(vars(cards))
 uncovered=set().union(*(report.uncovered for report in reports.values()))
 # Once installed, retain the original named inventory when rebuilding.
 destination=Path('expanded/legacy_operand_catalog.json')
 if destination.exists():uncovered.update(json.loads(destination.read_text())['operations'])
 records=cards.registry();signatures=defaultdict(list)
 def shape(value):
  if type(value) is bool:return {'kind':'bool'}
  if type(value) is int:return {'kind':'int'}
  if value is None:return {'kind':'none'}
  if isinstance(value,str):return {'kind':'text'} if value in records else {'kind':'literal','value':value}
  if isinstance(value,PoolRequest):return {'kind':'pool'}
  if isinstance(value,GiftRequest):return {'kind':'gift'}
  if isinstance(value,(tuple,list)):return {'kind':'sequence','items':[shape(item) for item in value]}
  raise TypeError('Unreviewed operand type: '+type(value).__name__)
 def walk(value):
  if isinstance(value,(tuple,list)):
   if value and isinstance(value[0],str) and value[0] in uncovered:
    signature=[shape(operand) for operand in value[1:]]
    if signature not in signatures[value[0]]:signatures[value[0]].append(signature)
   for child in value:walk(child)
  elif isinstance(value,dict):
   for child in value.values():walk(child)
 for name in effect_schema.RULE_TABLES|effect_schema.OP_TABLES|effect_schema.PAIRED_TABLES|{'CHOICES'}:walk(getattr(cards,name,{}))
 missing=uncovered-set(signatures)
 if missing:raise ValueError('No authored operand witnesses: '+str(sorted(missing)))
 data=dict(format_version=1,scope='Explicit arity, type, literal selector and nested-container shapes of the 515 formerly uncovered authored operation names. Not executable-handler or game-fidelity certification.',operations={name:sorted(values,key=lambda value:json.dumps(value,sort_keys=True)) for name,values in sorted(signatures.items())})
 destination.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
 print(len(signatures),'explicit legacy operation contracts written')

if __name__=='__main__':main()
