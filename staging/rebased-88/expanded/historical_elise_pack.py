"""Elise's shuffle/draw and sealed pack, pending exact joint distribution.

All non-Quest Un'Goro identities remain eligible. No rarity probabilities,
retail pity timers, duplicate protection or replacement distribution assumed.
"""
from engine.cards import UnsupportedCard
from engine.game import Card
from .pools import require_fixed_cards
from .identities import identity_resolver
from .pack_contracts import sample_pack
OUTCOMES=('UNG_001', 'UNG_002', 'UNG_004', 'UNG_009', 'UNG_010', 'UNG_011', 'UNG_015', 'UNG_018', 'UNG_019', 'UNG_020', 'UNG_021', 'UNG_022', 'UNG_024', 'UNG_025', 'UNG_027', 'UNG_029', 'UNG_030', 'UNG_032', 'UNG_034', 'UNG_035', 'UNG_037', 'UNG_047', 'UNG_049', 'UNG_057', 'UNG_058', 'UNG_060', 'UNG_061', 'UNG_063', 'UNG_064', 'UNG_065', 'UNG_070', 'UNG_071', 'UNG_072', 'UNG_073', 'UNG_075', 'UNG_076', 'UNG_078', 'UNG_079', 'UNG_082', 'UNG_083', 'UNG_084', 'UNG_085', 'UNG_086', 'UNG_087', 'UNG_088', 'UNG_089', 'UNG_099', 'UNG_100', 'UNG_101', 'UNG_103', 'UNG_108', 'UNG_109', 'UNG_111', 'UNG_113', 'UNG_201', 'UNG_202', 'UNG_205', 'UNG_208', 'UNG_211', 'UNG_800', 'UNG_801', 'UNG_803', 'UNG_806', 'UNG_807', 'UNG_808', 'UNG_809', 'UNG_810', 'UNG_812', 'UNG_813', 'UNG_814', 'UNG_816', 'UNG_817', 'UNG_818', 'UNG_823', 'UNG_830', 'UNG_831', 'UNG_832', 'UNG_833', 'UNG_834', 'UNG_835', 'UNG_836', 'UNG_838', 'UNG_840', 'UNG_843', 'UNG_844', 'UNG_845', 'UNG_846', 'UNG_847', 'UNG_848', 'UNG_851', 'UNG_852', 'UNG_854', 'UNG_856', 'UNG_900', 'UNG_907', 'UNG_910', 'UNG_912', 'UNG_913', 'UNG_914', 'UNG_915', 'UNG_916', 'UNG_917', 'UNG_919', 'UNG_922', 'UNG_923', 'UNG_925', 'UNG_926', 'UNG_927', 'UNG_928', 'UNG_929', 'UNG_933', 'UNG_937', 'UNG_938', 'UNG_941', 'UNG_946', 'UNG_948', 'UNG_950', 'UNG_952', 'UNG_953', 'UNG_955', 'UNG_956', 'UNG_957', 'UNG_960', 'UNG_961', 'UNG_962', 'UNG_963')
STAGED_RULES={
 'UNG_851':('none',[('historical_elise_shuffle',)]),
 'UNG_851t1':('none',[('historical_elise_open',)]),
}

def checked_contract(game):
 contract=getattr(game,'ungoro_pack_contract',None)
 if not isinstance(contract,dict) or not contract.get('source'):
  raise UnsupportedCard('Elise pack requires its reviewed in-game distribution')
 model=contract.get('model','joint')
 if model=='rarity_patterns':
  from .pack_contracts import prepare_rarity_patterns
  def validate_identity(game,card,owner):
   if card.card_id not in OUTCOMES or card.card_id not in game.cards:raise UnsupportedCard('Ineligible Elise pack identity')
  patterns,pools=prepare_rarity_patterns(game,contract,0,validate_identity)
  if any(not any(r in ('EPIC','LEGENDARY') for r in pattern) for _,pattern in patterns):raise UnsupportedCard('Every Elise rarity pattern must guarantee Epic or better')
  if {cid for values,_ in pools.values() for cid in values}!=set(OUTCOMES):raise UnsupportedCard('Elise rarity pools omit eligible identities')
  return contract
 model=contract.get('model','joint');groups=contract.get('outcomes') if model=='joint' else contract.get('slots')
 if model not in ('joint','independent_slots') or not isinstance(groups,(tuple,list)) or not groups:
  raise UnsupportedCard('Invalid Elise pack distribution')
 seen=set();guaranteed=False
 if model=='joint':groups=(groups,)
 elif len(groups)!=5:raise UnsupportedCard('Elise pack requires five slots')
 for group in groups:
  if not isinstance(group,(tuple,list)) or not group:raise UnsupportedCard('Empty Elise pack distribution group')
  all_epic=True
  for entry in group:
   if not isinstance(entry,(tuple,list)) or len(entry)!=2:raise UnsupportedCard('Invalid Elise weighted outcome')
   weight,value=entry
   if type(weight) is not int or weight<=0:raise UnsupportedCard('Invalid Elise outcome weight')
   values=value if model=='joint' else (value,)
   if not isinstance(values,(tuple,list)) or len(values)!=(5 if model=='joint' else 1):raise UnsupportedCard('Invalid Elise pack outcome size')
   if any(not isinstance(cid,str) or cid not in OUTCOMES for cid in values):raise UnsupportedCard('Elise pack contains an ineligible outcome')
   seen.update(values)
   has_epic=any(game.cards[cid].get('rarity') in ('EPIC','LEGENDARY') for cid in values)
   if model=='joint' and not has_epic:raise UnsupportedCard('Elise pack must guarantee Epic or better')
   all_epic=all_epic and has_epic
  guaranteed=guaranteed or all_epic
 if model=='independent_slots' and not guaranteed:raise UnsupportedCard('Elise slots do not guarantee Epic or better')
 if seen!=set(OUTCOMES):raise UnsupportedCard('Elise distribution omits eligible identities')
 return contract

def execute(game,op,ctx):
 owner=ctx['owner'];p=game.players[owner]
 if op[0]=='historical_elise_shuffle':
  require_fixed_cards(('UNG_851t1',),game.cards)
  card=Card(game._new_id(),'UNG_851t1');p.deck.append(card);game.rng.shuffle(p.deck)
  game._record_deck_insertion(owner,owner,1,'shuffle',cards=(card,))
  resolve=identity_resolver(game.cards)
  identities=[resolve(game._card_data(value)) for value in p.deck]
  if len(identities)==len(set(identities)):
   index=next((i for i,value in enumerate(p.deck) if value is card),None)
   if index is not None:game._draw_index(owner,index)
  return True
 if op[0]=='historical_elise_open':
  require_fixed_cards(OUTCOMES,game.cards)
  contract=checked_contract(game)
  # This adds cards to hand; it does not automatically cast their effects.
  def available(game,card,owner):
   if card.card_id not in OUTCOMES or card.card_id not in game.cards:raise UnsupportedCard('Unavailable Elise pack identity')
  ids=sample_pack(game,contract,owner,validator=available)
  for cid in ids:game._add(owner,cid)
  return True
 return False
