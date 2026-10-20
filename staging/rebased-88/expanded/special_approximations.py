"""Owner-authorized runnable approximations. No Blizzard fidelity claim.

Versioned policy choices are recorded in observations and game events. Source
candidate recipes are retained in full. No training or gameplay search occurs.
"""
from pathlib import Path
from functools import lru_cache
import gzip
import json
from engine.cards import UnsupportedCard
from .identities import identity_resolver
VERSION='special-approximations-v1'
POLICIES={
 'BOT_914':'Synthetic Standard class recipes (two deterministic mana-curve variants per class), NOT Blizzard deck recipes; uniform selection.',
 'DAL_800':'Five documented 2020 decks; uniform deck selection; pinned-build continuity unverified.',
 'GDB_854':'Uniform distinct eligible branch pairs, rejecting pairs with two targeted choices; canonical parent deduplication.',
 'GIFT_01':'Uniform class, uniform DK rune hand; prefer original collectible printings; documented hand order and DH tokens.',
 'REV_022':'Uniform physical correct answer; two distinct Standard class/neutral distractors absent from the answer zone; shuffled offers.',
 'SCH_199':'Uniform choice among all 38 board forms once per match unless explicitly configured.',
 'TOY_373':'Public-state usefulness thresholds, then uniform useful spell and uniform legal enemy target.',
 'TOY_700':'Eleven documented experimental recipes; uniform classes and distinct Rogue treasures; collectible original printings; rainbow DK.',
 'UNG_851':'Independent conditional rarity slots, C29/R28/E24/L19 weights; last slot E24/L19 guarantees Epic-or-better; uniform identities.',
 'CORE_WON_145':'Same boosted five-slot model as Elise, full pinned pack-eligible Standard expansion pool; no shop pity or collection protection.',
 'WW_0700':'Uniform initial bullet; uniform different next bullet, no consecutive repeats.',
 'ULD_003':'Existing 139-offer public-state heuristic.',
 'TOY_700t9t2':'Existing shared Zephrys heuristic.'}
ROOT=Path(__file__).resolve().parents[1]

@lru_cache(maxsize=1)
def frozen_records():
 return {d['id']:d for d in json.load(gzip.open(ROOT/'data/standard/all_cards.json.gz','rt'))}

def choose_printing(ids,cards):
 # Semantic type/collectibility resolves hero skins sharing a card name.
 metadata=frozen_records()
 candidates=[cid for cid in ids if not cid.startswith('HERO_') and metadata.get(cid,{}).get('collectible') and metadata[cid].get('type') in ('MINION','SPELL','WEAPON','HERO','LOCATION')]
 if not candidates:raise UnsupportedCard('No collectible recipe printing: '+repr(ids))
 return min(candidates,key=lambda cid:(cid.startswith(('CORE_','LEG_','VAN_')),cid))

def iconic_contract(cards):
 from .historical_iconic_hands import IconicCard,IconicHand,IconicHandsContract
 data=json.loads((ROOT/'data/standard/harth-iconic-hand-candidates.json').read_text())
 hands=[]
 for row in data['hands']:
  key=row['key'];hero='DEATHKNIGHT' if key.startswith('DEATHKNIGHT_') else key
  ids=[slot['candidate_printings'][0]['card_id'] if hero=='DEMONHUNTER' else choose_printing([x['card_id'] for x in slot['candidate_printings']],cards) for slot in row['slots']]
  hands.append(IconicHand(key,hero,tuple(IconicCard(cid) for cid in ids),1 if hero=='DEATHKNIGHT' else 3))
 return IconicHandsContract(tuple(hands),'APPROXIMATE '+VERSION,'36.6.0.251952',True,'APPROXIMATE uniform class then DK rune hand')

def experimental_contract(cards):
 from .historical_experimental_decks import compile_contract
 from .historical_kazakusan import TREASURES
 from .selectors import HERO_CLASSES
 data=json.loads((ROOT/'data/historical/experimental_recipe_candidates.json').read_text())
 printings={(r['hero_class'],e['name']):choose_printing(e['candidate_ids'],cards) for r in data['recipes'] for e in r['entries'] if e['resolved_id'] is None}
 pool=set(TREASURES)-{'ONY_005ta11','ONY_005ta2','ONY_005ta4'}
 return compile_contract(cards,printings=printings,weights={c:1 for c in HERO_CLASSES},treasure_weights={cid:1 for cid in pool},deathknight_runes=(1,1,1),source='APPROXIMATE '+VERSION,distribution_source='APPROXIMATE uniform classes and treasures')

def synthetic_recipes(cards):
 """Explicit proxy recipes, not a reconstruction of client deck recipes.

 Deterministic metadata construction only; no simulation, deck search or learning.
 Uses the complete legal pool before selecting two fixed curve templates.
 """
 from standard.catalog import load_catalog
 from .selectors import HERO_CLASSES,has_class
 from .decks import Deck,RUNES
 from .historical_starting_decks import Recipe,RecipeContract,PATCH,validate_contract
 resolve=identity_resolver(cards);recipes=[]
 from .fabled_decks import BUNDLES
 excluded=set(BUNDLES)|{'BOT_914','DAL_800','TOY_700','JAIL_397','JAIL_430','REV_018','CORE_REV_018','TOY_330','ETC_080','JAIL_831'}
 for hero in HERO_CLASSES:
  runes=(1,1,1) if hero=='DEATHKNIGHT' else (0,0,0)
  by_identity={}
  for d in load_catalog():
   if d['id'] in excluded or not has_class(d,hero,include_neutral=True):continue
   if any(d.get('runeCost',{}).get(r,0)>n for r,n in zip(RUNES,runes)):continue
   # Fabled cards and custom construction packages need explicit sideboards.
   if any(m in d.get('mechanics',()) for m in ('FABLED',)):continue
   if d['type'] not in ('MINION','SPELL','WEAPON','HERO','LOCATION'):continue
   by_identity.setdefault(resolve(d),d)
  pool=list(by_identity.values())
  for variant in (0,1):
   # Stable curve-oriented templates with class cards first at each cost.
   ordered=sorted(pool,key=lambda d:(abs(d.get('cost',0)-(3 if variant==0 else 6)),d.get('cardClass')=='NEUTRAL',d['id']))
   ids=[]
   for d in ordered:
    copies=1 if d.get('rarity')=='LEGENDARY' else 2
    ids.extend([d['id']]*min(copies,30-len(ids)))
    if len(ids)==30:break
   recipes.append(Recipe('APPROX_SYNTHETIC_'+hero+'_'+str(variant),Deck(hero,tuple(ids),runes),1))
 return validate_contract(RecipeContract('BOT_914','APPROXIMATE synthetic proxy recipes '+VERSION,PATCH,tuple(recipes),True),cards)

def opening_contracts(cards,roots):
 result={}
 if 'BOT_914' in roots:result['BOT_914']=synthetic_recipes(cards)
 if 'DAL_800' in roots:
  from .historical_zayle_recipes import compile_contract
  from .historical_starting_decks import EVIL
  result['DAL_800']=compile_contract(cards,weights={c:1 for c in EVIL},distribution_source='APPROXIMATE uniform five decks',pinned_recipe_source='APPROXIMATE documented 2020 lists '+VERSION)
 if 'TOY_700' in roots:result['TOY_700']=experimental_contract(cards)
 return result

def pack_contract(cards,ids):
 # Approximate odds are design parameters, not official/estimated exact odds.
 groups={r:tuple(sorted(cid for cid in ids if cards[cid].get('rarity')==r)) for r in ('COMMON','RARE','EPIC','LEGENDARY')}
 if any(not v for v in groups.values()):raise UnsupportedCard('Incomplete approximate pack rarity pools')
 weights={'COMMON':29,'RARE':28,'EPIC':24,'LEGENDARY':19}
 # Equal conditional identity probability via common integer denominator.
 from math import gcd
 denominator=1
 for values in groups.values():denominator=denominator*len(values)//gcd(denominator,len(values))
 ordinary=tuple((weights[r]*(denominator//len(values)),cid) for r,values in groups.items() for cid in values)
 guaranteed=tuple((weights[r]*(denominator//len(groups[r])),cid) for r in ('EPIC','LEGENDARY') for cid in groups[r])
 return dict(source='APPROXIMATE '+VERSION,approximate=True,model='independent_slots',slots=(ordinary,ordinary,ordinary,ordinary,guaranteed))

def uluu_pair(game,owner,card):
 from standard.catalog import load_catalog
 from .cards import CHOICES
 from .historical_uluu import EXCLUDED_PARENTS
 resolve=identity_resolver(game.cards)
 excluded={resolve(game.cards[cid]) for cid in EXCLUDED_PARENTS}
 parents={}
 for d in load_catalog():
  if not d.get('collectible') or 'CHOOSE_ONE' not in d.get('mechanics',()) or resolve(d) in excluded:continue
  parents.setdefault(resolve(d),d['id'])
 options=[]
 for cid in sorted(parents.values()):
  if cid not in CHOICES:raise UnsupportedCard('Unwritten Uluu Choose One parent: '+cid)
  for index,branch in enumerate(CHOICES[cid]):options.append((cid,index,branch[1]!='none'))
 pairs=[(a,b) for i,a in enumerate(options) for b in options[i+1:] if not (a[2] and b[2])]
 if not pairs:raise UnsupportedCard('Empty Uluu branch-pair pool')
 a,b=game.rng.choice(pairs)
 if game.rng.randrange(2):a,b=b,a
 return tuple(dict(parent_id=x[0],branch_index=x[1]) for x in (a,b))

def holmes_offer(game,owner,clue,zones):
 from standard.catalog import load_catalog
 from .selectors import has_class
 from .historical_holmes import CLUES
 resolve=identity_resolver(game.cards);actual=zones[CLUES.index(clue)]
 correct=game.rng.choice(actual);cid=correct if isinstance(correct,str) else correct.card_id
 valid={resolve(game._card_data(c)) for c in actual}
 distractors={}
 for d in load_catalog():
  if resolve(d) not in valid and has_class(d,game.players[1-owner].hero_class,include_neutral=True):distractors.setdefault(resolve(d),d['id'])
 if len(distractors)<2:raise UnsupportedCard('Insufficient distinct Holmes distractors')
 ids=[cid]+game.rng.sample(sorted(distractors.values()),2);game.rng.shuffle(ids)
 return ids

def helpful_spells(state):
 owner=state['owner'];p=state['players'][owner];q=state['players'][1-owner]
 enemy=[m for m in q['board'] if m['kind']=='MINION' and not m.get('dormant')]
 own=[m for m in p['board'] if m['kind']=='MINION']
 spells=['CS2_029','CS2_024'] # Face damage always considered helpful.
 if any(m['health']==1 for m in enemy):spells.append('EX1_277')
 if enemy:spells.extend(('CS2_032','CS2_028'))
 if any(m['attack']>1 or m['health']>1 or m.get('keywords') for m in enemy):spells.append('CS2_022')
 if len(p['board'])<7:spells.append('CS2_027')
 if p['deck_count'] and p['hand_count']<=7:spells.append('CS2_023')
 if p.get('secret_count',0)<5:spells.extend(('EX1_287','EX1_289'))
 return dict(useful_spells=tuple(spells),approximate=True)

def install(game):
 from standard.catalog import load_catalog
 from .historical_elise_pack import OUTCOMES
 from .historical_wisdomball import WisdomballPolicy,SPELLS
 from .historical_lone_ranger import RENO_BULLETS
 game.approximation_profile=dict(version=VERSION,validated=False,policies=dict(POLICIES))
 game.historical_harth_contract=iconic_contract(game.cards)
 game.historical_uluu_pair=uluu_pair;game.historical_holmes_offer=holmes_offer
 game.wisdomball_policy=WisdomballPolicy('APPROXIMATE '+VERSION,'36.6.0.251952',SPELLS,helpful_spells,complete=False,approximate=True)
 game.ungoro_pack_contract=pack_contract(game.cards,OUTCOMES)
 # Keep all pack-eligible Standard expansion identities, never a written subset.
 ids=tuple(d['id'] for d in load_catalog() if d.get('collectible') and d.get('set') not in ('CORE','CORE_HIDDEN','LEGACY','EVENT') and d.get('rarity') in ('COMMON','RARE','EPIC','LEGENDARY') and d.get('type') in ('MINION','SPELL','WEAPON','HERO','LOCATION'))
 game.standard_pack_contract=pack_contract(game.cards,ids)
 game.reno_bullet_contract=dict(source='APPROXIMATE '+VERSION,approximate=True,initial={cid:1 for cid in RENO_BULLETS},transitions={old:{cid:int(cid!=old) for cid in RENO_BULLETS} for old in RENO_BULLETS})
