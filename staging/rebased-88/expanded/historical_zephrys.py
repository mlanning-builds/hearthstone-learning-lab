"""Zephrys choice execution, gated on the exact sourced public-state policy.

No heuristic replacement, hidden hand/deck inspection or implemented-only
candidate filtering. The owner-authorized default policy is explicitly approximate.
"""
from copy import deepcopy
from dataclasses import dataclass
from engine.cards import UnsupportedCard
from .identities import identity_resolver
from .pools import require_fixed_cards
# Developer-confirmed exclusions: wishes must not generate another replay.
REPLAY_EXCLUSIONS=('EX1_144','EX1_049','EX1_057','ULD_003')

STAGED_RULES={'ULD_003':('none',[('historical_zephrys_begin',)]),'TOY_700t9t2':('none',[('historical_zephrys_wish',)])}

@dataclass(frozen=True)
class ZephrysPolicy:
 source:str
 build:str
 pool:tuple
 evaluator:object
 complete:bool=False
 approximate:bool=False


def public_snapshot(game,owner):
 sides=[]
 for index,p in enumerate(game.players):
  board=[]
  for entity in p.board:
   data=game.cards[entity.card_id]
   row=dict(uid=entity.uid,card_id=entity.card_id,kind=data['type'])
   if data['type']=='MINION':
    from .selectors import effective_tribes
    row['tribes']=tuple(sorted(effective_tribes(game._card_data(entity))))
    row.update(attack=entity.attack,health=entity.health,max_health=entity.max_health,
               keywords=tuple(sorted(game._effective_keywords(entity))),dormant=bool(entity.dormant),frozen_until=entity.frozen_until)
   else:
    for field in ('durability','ready_turn'):
     if hasattr(entity,field):row[field]=getattr(entity,field)
   if data['type']=='MINION':
    for field in ('attacks','summoned_turn','silenced','temporary_attack'):
     if hasattr(entity,field):row[field]=getattr(entity,field)
   board.append(row)
  weapon=None if p.weapon is None else {key:p.weapon[key] for key in ('card_id','attack','durability')}
  sides.append(dict(hero_attack=game._hero_attack(index),hero_attacks=p.hero_attacks,
                    frozen=p.frozen_until>=0,divine_shield=p.divine_shield,
                    immune=game._hero_immune(index),stealth=game._hero_stealth(index),
                    power_used=p.power_used,power_cost=game._power_cost(index),
                    hero_attack_limit=game._hero_attack_limit(index),
                    spell_damage=game._spell_damage(index),
                    mana_capacity=p.mana_capacity,
                    next_turn_mana_baseline=max(0,min(p.mana_capacity,p.max_mana+1)-p.overload_next),
                    overload_next=p.overload_next,
                    quest=deepcopy(p.quest),whizbang_quests=deepcopy(getattr(p,'whizbang_quests',[])),
                    owner=index,hero_class=p.hero_class,health=p.health,max_health=p.max_health,armor=p.armor,
                    mana=p.mana,max_mana=p.max_mana,locked_mana=p.locked_mana,
                    hand_count=len(p.hand),deck_count=len(p.deck),secret_count=len(p.secrets),
                    board=tuple(board),weapon=weapon,hero_power=None if p.primary_power is None else p.primary_power['card_id']))
 return dict(snapshot_version=3,owner=owner,current=game.current,turn=game.turn,players=tuple(sides))


def checked_policy(game):
 policy=getattr(game,'historical_zephrys_policy',None)
 if policy is None:
  from .zephrys_approximation import policy as approximate_policy
  policy=approximate_policy(game.cards)
 if not isinstance(policy,ZephrysPolicy) or (policy.complete is not True and policy.approximate is not True) or policy.build!='36.6.0.251952' or not policy.source or not callable(policy.evaluator):raise UnsupportedCard('Missing complete sourced pinned Zephrys policy')
 if not isinstance(policy.pool,tuple) or not policy.pool or any(not isinstance(cid,str) for cid in policy.pool):raise UnsupportedCard('Invalid complete Zephrys pool')
 require_fixed_cards(policy.pool,game.cards)
 resolve=identity_resolver(game.cards)
 identities=[resolve(game.cards[cid]) for cid in policy.pool]
 if len(set(identities))!=len(identities):raise UnsupportedCard('Duplicate canonical Zephrys pool identity')
 excluded={resolve(game.cards[cid]) for cid in REPLAY_EXCLUSIONS if cid in game.cards}
 if excluded.intersection(identities):raise UnsupportedCard('Zephrys cannot offer Shadowstep, Brewmasters or itself')
 for cid in policy.pool:
  data=game.cards[cid]
  if not data.get('collectible') or data.get('set') not in ('LEGACY','EXPERT1') or data['type'] not in ('MINION','SPELL','WEAPON','HERO'):
   raise UnsupportedCard('Zephrys pool must use its original Basic/Classic identities')
 return policy


def execute(game,op,ctx):
 if op[0] not in ('historical_zephrys_begin','historical_zephrys_wish'):return False
 owner=ctx['owner'];resolve=identity_resolver(game.cards)
 identities=[resolve(game._card_data(card)) for card in game.players[owner].deck]
 if op[0]=='historical_zephrys_begin' and len(set(identities))!=len(identities):return True
 if game.pending_choice is not None:raise UnsupportedCard('Zephrys cannot overwrite an active choice')
 policy=checked_policy(game)
 # The evaluator receives no Game, Card, hand IDs, deck IDs or Secret IDs.
 # Changes to this detached public snapshot cannot alter live game state.
 ids=policy.evaluator(deepcopy(public_snapshot(game,owner)))
 if not isinstance(ids,(tuple,list)) or len(ids)!=3 or any(cid not in policy.pool for cid in ids):raise UnsupportedCard('Zephrys must offer three identities from the complete declared pool')
 if len({resolve(game.cards[cid]) for cid in ids})!=3:raise UnsupportedCard('Zephrys offer repeats a canonical identity')
 game._log('zephrys_evaluation',player=owner,approximate=policy.approximate)
 game.pending_choice=dict(owner=owner,kind='historical_zephrys',approximate=policy.approximate,options=[dict(card_id=cid) for cid in ids],_automatic=bool(ctx.get('automatic_choices',False)))
 game.phase='choice'
 return True


def resolve_choice(game,choice,selected):
 if choice['kind']!='historical_zephrys':return False
 cid=selected.get('card_id')
 if cid not in {row['card_id'] for row in choice['options']}:raise UnsupportedCard('Zephrys card was not offered')
 game._add(choice['owner'],cid)
 return True
