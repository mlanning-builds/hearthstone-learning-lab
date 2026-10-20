"""Recursively immutable JSON records shared across rollback snapshots.

The per-game registry remains mutable; mutable fixture replacements still copy.
"""
class FrozenDict(dict):
 def _immutable(self,*args,**kwargs):raise TypeError('Static card metadata is immutable; replace the record explicitly.')
 __setitem__=__delitem__=clear=pop=popitem=setdefault=update=__ior__=_immutable
 def __deepcopy__(self,memo):memo[id(self)]=self;return self
class FrozenList(list):
 def _immutable(self,*args,**kwargs):raise TypeError('Static card metadata is immutable; replace the record explicitly.')
 __setitem__=__delitem__=append=clear=extend=insert=pop=remove=reverse=sort=__iadd__=__imul__=_immutable
 def __deepcopy__(self,memo):memo[id(self)]=self;return self

def freeze(value):
 if isinstance(value,dict):return FrozenDict({key:freeze(item) for key,item in value.items()})
 if isinstance(value,list):return FrozenList(freeze(item) for item in value)
 return value

def freeze_registry(records):return {cid:freeze(record) for cid,record in records.items()}

def thaw(value):
 """Create mutable fixture or derived-definition data from frozen records."""
 if isinstance(value,dict):return {key:thaw(item) for key,item in value.items()}
 if isinstance(value,list):return [thaw(item) for item in value]
 return value
