"""Validation for the explicit, reviewed legacy operand-shape catalog."""
import json
from pathlib import Path
from functools import lru_cache

@lru_cache(maxsize=1)
def contracts():
 data=json.loads(Path(__file__).with_name('legacy_operand_catalog.json').read_text())
 if data.get('format_version')!=1:raise ValueError('Unsupported operand catalog version')
 operations=data['operations']
 if not isinstance(operations,dict) or not operations:raise ValueError('Empty operand catalog')
 return operations

def matches(shape,value):
 kind=shape['kind']
 if kind=='int':return type(value) is int
 if kind=='bool':return type(value) is bool
 if kind=='none':return value is None
 if kind=='text':return isinstance(value,str) and bool(value)
 if kind=='literal':return type(value) is type(shape['value']) and value==shape['value']
 if kind=='sequence':return isinstance(value,(tuple,list)) and len(value)==len(shape['items']) and all(matches(spec,item) for spec,item in zip(shape['items'],value))
 if kind=='pool':
  from .generation_cards import PoolRequest
  return isinstance(value,PoolRequest)
 if kind=='gift':
  from .effect_schema import _gift_request
  return _gift_request(value)
 raise ValueError('Unknown operand contract kind: '+kind)

def accepts(name,operands):
 variants=contracts().get(name)
 if variants is None:return None
 return any(len(operands)==len(variant) and all(matches(spec,value) for spec,value in zip(variant,operands)) for variant in variants)
