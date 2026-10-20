"""Compile full sourced Zayle candidate lists; no default distribution or admission."""
import hashlib
import json
from pathlib import Path
from engine.cards import UnsupportedCard
from .decks import Deck
from .historical_starting_decks import Recipe,RecipeContract,validate_contract,EVIL,PATCH

DIGEST='eed4262fc6064c23f87145dcf0b5fc86d33ffc2ce1f6e1f39dff86a26524068f'

def compile_contract(cards,*,weights,distribution_source,pinned_recipe_source):
 """Caller supplies evidence confirming these exact recipes and selection odds.

 The stored lists are source candidates, not a claim of pinned client fidelity.
 This compiler never marks the production root implemented or installs defaults.
 """
 for source in (distribution_source,pinned_recipe_source):
  if not isinstance(source,str) or not source.strip():
   raise UnsupportedCard('Zayle requires pinned recipe and distribution evidence')
 if not isinstance(weights,dict) or set(weights)!=set(EVIL) or any(type(n) is not int or n<=0 for n in weights.values()):
  raise UnsupportedCard('Zayle requires explicit positive weights for all five decks')
 raw=(Path(__file__).resolve().parents[1]/'data/historical/zayle_recipe_candidates.json').read_bytes()
 if hashlib.sha256(raw).hexdigest()!=DIGEST:raise UnsupportedCard('Zayle candidate recipe data changed')
 data=json.loads(raw);rows=data['recipes']
 if len(rows)!=5 or {row['hero_class'] for row in rows}!=set(EVIL):raise UnsupportedCard('Incomplete Zayle recipe list')
 recipes=[]
 for row in rows:
  hero=row['hero_class'];expanded=[]
  for cid,count in row['cards']:
   if not isinstance(cid,str) or type(count) is not int or count<=0:raise UnsupportedCard('Malformed Zayle card count')
   expanded.extend([cid]*count)
  recipes.append(Recipe('ZAYLE_'+hero,Deck(hero,tuple(expanded)),weights[hero]))
 contract=RecipeContract('DAL_800',json.dumps(dict(recipe_source=pinned_recipe_source,distribution_source=distribution_source,candidate_sources=data['sources']),sort_keys=True),PATCH,tuple(recipes),True)
 return validate_contract(contract,cards)
