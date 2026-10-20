"""Full eleven-class experimental opening pipeline; source certification pending.

Exceptional sizes, cross-class/copy-limit exceptions, treasure setup and hero
health belong to these recipes, never to ordinary constructed validation.
No default weights or printing choices are invented.
"""
from dataclasses import dataclass
from pathlib import Path
import hashlib,json
from engine.cards import UnsupportedCard
from .decks import Deck
from .selectors import HERO_CLASSES
from .pools import require_fixed_cards
PATCH='36.6.0.251952'
DIGEST='853385a4121770019c9b22ef8624251646e6b2d7b7e913066d1d0ba74ff7c9a7'
@dataclass(frozen=True)
class ExperimentalRecipe:
 hero_class:str
 cards:tuple
 runes:tuple
 weight:int
 health:int
 treasure_pool:tuple=()
 treasure_weights:tuple=()
 zero_lackeys:bool=False
@dataclass(frozen=True)
class ExperimentalContract:
 recipes:tuple
 source:str
 distribution_source:str
 build:str=PATCH
 complete:bool=False
 root_id:str='TOY_700'

def validate(contract,cards):
 if not isinstance(contract,ExperimentalContract) or contract.complete is not True or contract.build!=PATCH or contract.root_id!='TOY_700':raise UnsupportedCard('Incomplete experimental opening contract')
 if any(not isinstance(v,str) or not v.strip() for v in (contract.source,contract.distribution_source)):raise UnsupportedCard('Experimental recipes require printing/setup and distribution evidence')
 if not isinstance(contract.recipes,tuple) or len(contract.recipes)!=11 or any(not isinstance(r,ExperimentalRecipe) for r in contract.recipes):raise UnsupportedCard('Experimental recipes must cover all eleven classes')
 if {r.hero_class for r in contract.recipes}!=set(HERO_CLASSES):raise UnsupportedCard('Incomplete or repeated experimental class')
 for row in contract.recipes:
  if type(row.weight) is not int or row.weight<=0:raise UnsupportedCard('Invalid explicit experimental deck weight')
  size=20 if row.hero_class=='WARLOCK' else 40 if row.hero_class=='SHAMAN' else 30
  fixed=22 if row.hero_class=='ROGUE' else size
  if not isinstance(row.cards,tuple) or len(row.cards)!=fixed or any(not isinstance(cid,str) for cid in row.cards):raise UnsupportedCard('Experimental fixed recipe size mismatch')
  if any(cid in ('BOT_914','DAL_800','TOY_700') for cid in row.cards):raise UnsupportedCard('Recursive opening provider in experimental deck')
  require_fixed_cards(row.cards,cards)
  if row.health!=(40 if row.hero_class=='SHAMAN' else 30):raise UnsupportedCard('Experimental health mismatch')
  if not isinstance(row.runes,tuple) or len(row.runes)!=3 or any(type(n) is not int or n<0 for n in row.runes) or sum(row.runes)!=(3 if row.hero_class=='DEATHKNIGHT' else 0):raise UnsupportedCard('Invalid experimental rune profile')
  if type(row.zero_lackeys) is not bool or row.zero_lackeys!=(row.hero_class=='WARRIOR'):raise UnsupportedCard('Invalid experimental Lackey setup')
  if row.hero_class=='ROGUE':
   from .historical_kazakusan import TREASURES
   expected=set(TREASURES)-{'ONY_005ta11','ONY_005ta2','ONY_005ta4'}
   if not isinstance(row.treasure_pool,tuple) or len(row.treasure_pool)!=25 or set(row.treasure_pool)!=expected:raise UnsupportedCard('Experimental Rogue must retain all 25 eligible treasures')
   if not isinstance(row.treasure_weights,tuple) or len(row.treasure_weights)!=25 or any(type(w) is not int or w<=0 for w in row.treasure_weights):raise UnsupportedCard('Missing explicit treasure weights')
   require_fixed_cards(row.treasure_pool,cards)
  elif row.treasure_pool or row.treasure_weights:raise UnsupportedCard('Unexpected experimental treasure setup')
 return contract

def select(contract,cards,rng):
 validate(contract,cards)
 row=rng.choices(contract.recipes,weights=[r.weight for r in contract.recipes],k=1)[0]
 ids=list(row.cards)
 if row.treasure_pool:
  remaining=list(zip(row.treasure_pool,row.treasure_weights))
  for _ in range(8):
   index=rng.choices(range(len(remaining)),weights=[w for _,w in remaining],k=1)[0]
   cid,_=remaining.pop(index);ids.append(cid)
 return Deck(row.hero_class,tuple(ids),row.runes),dict(starting_health=row.health,zero_lackeys=row.zero_lackeys,recipe_key='EXPERIMENTAL_'+row.hero_class)

def compile_contract(cards,*,printings,weights,treasure_weights,deathknight_runes,source,distribution_source):
 raw=(Path(__file__).resolve().parents[1]/'data/historical/experimental_recipe_candidates.json').read_bytes()
 if hashlib.sha256(raw).hexdigest()!=DIGEST:raise UnsupportedCard('Experimental candidate source changed')
 data=json.loads(raw)
 if not isinstance(weights,dict) or set(weights)!=set(HERO_CLASSES):raise UnsupportedCard('All eleven explicit deck weights required')
 if not isinstance(printings,dict):raise UnsupportedCard('Printing choices must be keyed by class and card name')
 expected_keys={(row['hero_class'],entry['name']) for row in data['recipes'] for entry in row['entries'] if entry['resolved_id'] is None}
 if set(printings)!=expected_keys:raise UnsupportedCard('Every ambiguous printing requires one explicit choice, without extra overrides')
 recipes=[]
 for row in data['recipes']:
  hero=row['hero_class'];ids=[]
  for entry in row['entries']:
   cid=entry['resolved_id'] or printings[(hero,entry['name'])]
   if cid not in entry['candidate_ids']:raise UnsupportedCard('Printing choice is outside the source candidate list')
   ids.extend([cid]*entry['count'])
  pool=tuple(row.get('treasure_setup',{}).get('pool_ids',()))
  if pool and (not isinstance(treasure_weights,dict) or set(treasure_weights)!=set(pool)):raise UnsupportedCard('All eligible treasure weights required')
  recipes.append(ExperimentalRecipe(hero,tuple(ids),deathknight_runes if hero=='DEATHKNIGHT' else (0,0,0),weights[hero],row['starting_health'],pool,tuple(treasure_weights[cid] for cid in pool),hero=='WARRIOR'))
 return validate(ExperimentalContract(tuple(recipes),source,distribution_source,complete=True),cards)

def apply_setup(game,selections):
 for selection in selections:
  if selection['source_card']!='TOY_700':continue
  p=game.players[selection['owner']]
  p.health=p.max_health=selection['starting_health']
  p.historical_experimental_zero_lackeys=selection['zero_lackeys']
