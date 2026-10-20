"""Explicit Prime chains and the complete seven-card Spare Part family."""
from engine.game import Card
from .generation_cards import pool,random_cards
from .pools import require_fixed_cards

PRIMES={'BT_019':'BT_019t','BT_028':'BT_028t','BT_109':'BT_109t',
 'BT_123':'BT_123t','BT_136':'BT_136t','BT_197':'BT_197t',
 'BT_210':'BT_210t','BT_713':'BT_713t','CFM_324':'CFM_324t'}
PARTS=('PART_001','PART_002','PART_003','PART_004','PART_005','PART_006','PART_007')
RULES={cid:('none',[]) for cid in PRIMES}
DEATH_EFFECTS={cid:[('historical_prime_shuffle',prime)] for cid,prime in PRIMES.items()}
RULES.update({
 'GVG_082':('none',[]),'GVG_115':('none',[('historical_prime_part',)]),
 'GVG_034':('none',[]),
 'GVG_102':('none',[('historic_when',('board_tribe','MECHANICAL'),(('buff_self',1,1),('historical_prime_part',)))]),
 'BAR_031':('none',[]),
})
DEATH_EFFECTS.update({'GVG_082':[('historical_prime_part',)],'GVG_115':[('historical_prime_part',)]})
TRIGGERS={'GVG_034':('damaged_self',[('historical_prime_part',)]),
 'BT_123t':(('historical_event','source_attack_kill'),[('armor',10)])}
TOKEN_RULES={
 'BT_019t':('none',[random_cards(pool(card_type='MINION',tribe='MURLOC'),4,'board',keyword='DIVINE_SHIELD')]),
 'BT_028t':('none',[('historical_prime_mage_casts',5)]),
 'BT_109t':('none',[('filtered_draw',(('type','eq','SPELL'),),3,-3)]),
 'BT_123t':('none',[]),
 'BT_136t':('none',[]),
 'BT_197t':('none',[]),
 'BT_210t':('none',[('copy_self_right',3)]),
 'BT_713t':('none',[]),'CFM_324t':('none',[]),
 'BT_136tt':('none',[]),'BT_136tt2':('none',[]),'BT_136tt3':('none',[]),
 'PART_001':('minion',[('buff',0,1)]),
 'PART_002':('friendly_minion',[('bounce',)]),
 'PART_003':('minion',[('keyword','TAUNT')]),
 'PART_004':('friendly_minion',[('temporary_keyword_target','STEALTH','next_start')]),
 'PART_005':('minion',[('freeze',)]),
 'PART_006':('minion',[('swap_stats',)]),
 'PART_007':('minion',[('buff',1,0)]),
}
CHOICES={'BT_136t':[('Fungal Guardian','none',[('summon','BT_136tt',1)]),('Fungal Bruiser','none',[('summon','BT_136tt2',1)])]}
COMBINED_CHOICES={'BT_136t':(('summon','BT_136tt3',1),)}
GENERATED_IDS=frozenset(RULES)
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)
SPELL_DAMAGE_VALUES={'BT_028':1,'BT_028t':1,'BT_109':1,'BT_109t':1}


def split(game,op,ctx):
 if op[0]!='historical_prime_mage_casts':return None
 values=game._autocast_candidates(pool(card_type='SPELL',classes='MAGE'),ctx['owner'])
 if op[1]<=0 or not values:return ('batch30_noop',),()
 first,tail=game._cast_spell_split(('cast_fixed_spell',game.rng.choice(values),'prefer_enemies'),ctx)
 return first,tuple(tail)+((('historical_prime_mage_casts',op[1]-1),) if op[1]>1 else ())


def execute(game,op,ctx):
 if not op[0].startswith('historical_prime_'):return False
 owner=ctx['owner'];p=game.players[owner];source=ctx.get('source')
 if op[0]=='historical_prime_shuffle':
  require_fixed_cards((op[1],),game.cards)
  card=Card(game._new_id(),op[1]);p.deck.insert(game.rng.randrange(len(p.deck)+1),card);game._record_deck_insertion(owner,owner,1,'shuffle',cards=(card,))
 elif op[0]=='historical_prime_part':
  require_fixed_cards(PARTS,game.cards)
  game._add(owner,game.rng.choice(PARTS))
 elif op[0]=='historical_prime_raptor':
  if source is not None:
   from .base_stats import base_stats
   attack,health=base_stats(game,source);card=Card(game._new_id(),'BAR_031');card.base_stat_override=(attack+op[1],health+op[2]);p.deck.insert(game.rng.randrange(len(p.deck)+1),card);game._record_deck_insertion(owner,owner,1,'shuffle',cards=(card,))
 else:return False
 return True

from .historical_pool_closure import COMBINED_CHOICES as POOL_COMBINED_CHOICES
COMBINED_CHOICES.update(POOL_COMBINED_CHOICES)
