"""Whizbang/Zayle opening replacement with complete sourced recipe contracts.

No built-in decklists or guessed selection weights. All recipes must be written
before selection; unsupported outcomes are never dropped. Experimental Whizbang
requires additional special setup and is deliberately not claimed by this path.
"""
from collections import Counter
from dataclasses import dataclass
from engine.cards import UnsupportedCard
from .decks import Deck,RUNES
from .selectors import HERO_CLASSES,has_class
from .identities import identity_resolver

ROOTS=frozenset(('BOT_914','DAL_800'))
EVIL=frozenset(('PRIEST','ROGUE','SHAMAN','WARLOCK','WARRIOR'))
PATCH='36.6.0.251952'

@dataclass(frozen=True)
class Recipe:
 key: str
 deck: Deck
 weight: int

@dataclass(frozen=True)
class RecipeContract:
 root_id: str
 source: str
 patch: str
 recipes: tuple
 complete: bool=False


def validate_contract(contract,cards):
 if not isinstance(contract,RecipeContract) or contract.root_id not in ROOTS:
  raise UnsupportedCard('Unknown opening recipe contract')
 if contract.complete is not True or contract.patch!=PATCH or not isinstance(contract.source,str) or not contract.source.strip():
  raise UnsupportedCard('Opening recipes require complete sourced pinned-build evidence')
 if not isinstance(contract.recipes,tuple) or not contract.recipes:raise UnsupportedCard('Empty opening recipe contract')
 keys=set();coverage=Counter();resolve=identity_resolver(cards)
 for recipe in contract.recipes:
  if not isinstance(recipe,Recipe) or not isinstance(recipe.key,str) or not recipe.key or recipe.key in keys:
   raise UnsupportedCard('Invalid or duplicate opening recipe key')
  keys.add(recipe.key)
  if type(recipe.weight) is not int or recipe.weight<=0:raise UnsupportedCard('Opening recipe weights must be explicit positive integers')
  deck=recipe.deck
  if not isinstance(deck,Deck) or deck.hero_class not in HERO_CLASSES:raise UnsupportedCard('Invalid opening recipe class')
  coverage[deck.hero_class]+=1
  if not isinstance(deck.cards,tuple) or len(deck.cards)!=30:raise UnsupportedCard('Ordinary opening recipes require thirty cards')
  if not isinstance(deck.runes,tuple) or len(deck.runes)!=3 or any(type(n) is not int or n<0 for n in deck.runes) or sum(deck.runes)!=(3 if deck.hero_class=='DEATHKNIGHT' else 0):raise UnsupportedCard('Invalid recipe rune configuration')
  if deck.beatrix_minion is not None or deck.contraband_beasts or deck.etc_band or deck.zilliax_modules:
   raise UnsupportedCard('Recipe custom physical setup requires its complete generated dependency integration')
  from .fabled_decks import expand_bundle_ids
  try:expanded=tuple(expand_bundle_ids(deck.cards))
  except ValueError as exc:raise UnsupportedCard(str(exc)) from exc
  if expanded!=deck.cards:raise UnsupportedCard('Recipe Fabled bundle expansion requires complete physical setup before selection')
  counts=Counter();limits={}
  for cid in deck.cards:
   if cid in ROOTS or cid=='TOY_700':raise UnsupportedCard('Recursive opening-deck provider in recipe')
   if cid not in cards:raise UnsupportedCard('Unwritten opening recipe dependency: '+str(cid))
   data=cards[cid]
   if not data.get('collectible') or data.get('type') not in ('MINION','SPELL','WEAPON','HERO','LOCATION'):raise UnsupportedCard('Invalid recipe card identity: '+cid)
   if not has_class(data,deck.hero_class,include_neutral=True):raise UnsupportedCard('Recipe class mismatch: '+cid)
   if any(data.get('runeCost',{}).get(rune,0)>n for rune,n in zip(RUNES,deck.runes)):raise UnsupportedCard('Recipe rune mismatch: '+cid)
   identity=resolve(data);counts[identity]+=1;limits[identity]=1 if data.get('rarity')=='LEGENDARY' else 2
  if any(amount>limits[key] for key,amount in counts.items()):raise UnsupportedCard('Recipe violates canonical copy limits')
 expected={hero:2 for hero in HERO_CLASSES} if contract.root_id=='BOT_914' else {hero:1 for hero in EVIL}
 if dict(coverage)!=expected:raise UnsupportedCard('Incomplete full-class opening recipe coverage')
 return contract


def replace_submitted(decks,cards,rng,contracts=None):
 contracts={} if contracts is None else contracts
 if not isinstance(contracts,dict):raise UnsupportedCard('Opening recipe contracts must be keyed by source card')
 prepared=[]
 for owner,deck in enumerate(decks):
  roots=(ROOTS|{'TOY_700'}).intersection(deck.cards)
  if not roots:continue
  if len(deck.cards)!=1 or len(roots)!=1:raise UnsupportedCard('Whizbang/Zayle must be the sole submitted card')
  root=next(iter(roots));contract=contracts.get(root)
  if contract is None:raise UnsupportedCard('Missing complete opening deck recipes: '+root)
  if root=='TOY_700':
   from .historical_experimental_decks import validate as validate_experimental
   validate_experimental(contract,cards)
  else:validate_contract(contract,cards)
  if contract.root_id!=root:raise UnsupportedCard('Opening contract source mismatch')
  prepared.append((owner,root,contract))
 # Validate both players and every possible recipe before consuming any RNG.
 result=list(decks);selections=[]
 for owner,root,contract in prepared:
  if root=='TOY_700':
   from .historical_experimental_decks import select
   selected,setup=select(contract,cards,rng)
   result[owner]=selected
   selections.append(dict(owner=owner,source_card=root,source=contract.source,**setup))
   continue
  recipe=rng.choices(contract.recipes,weights=[row.weight for row in contract.recipes],k=1)[0]
  result[owner]=recipe.deck
  selections.append(dict(owner=owner,source_card=root,recipe_key=recipe.key,source=contract.source))
 return result,tuple(selections)
