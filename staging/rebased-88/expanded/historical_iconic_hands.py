"""Staged Harth hand replacement. Exact ordered hands remain a data contract.

No production registration, default hand, supported-only filtering or inferred
random distribution. Historical/launch printed definitions must be supplied as
physical compiled definitions rather than mutating frozen global card data.
"""
from copy import deepcopy
from dataclasses import dataclass
from engine.game import Card
from engine.cards import UnsupportedCard
CLASSES=frozenset(('DEATHKNIGHT','DEMONHUNTER','DRUID','HUNTER','MAGE','PALADIN','PRIEST','ROGUE','SHAMAN','WARLOCK','WARRIOR'))
EXPECTED_KEYS=frozenset(('DEATHKNIGHT_BLOOD','DEATHKNIGHT_FROST','DEATHKNIGHT_UNHOLY','DEMONHUNTER','DRUID','HUNTER','MAGE','PALADIN','PRIEST','ROGUE','SHAMAN','WARLOCK','WARRIOR'))
# Current ordered source lists and actual launch-edition physical identities.
ORDERED_NAMES={'DEATHKNIGHT_BLOOD': ('Blood Boil', 'Soulstealer', 'Gnome Muncher', 'Alexandros Mograine', 'Vampiric Blood', 'Obliterate', 'Asphyxiate', 'Patchwerk'), 'DEATHKNIGHT_FROST': ('Glacial Advance', 'Lady Deathwhisper', 'School Teacher', "Frostwyrm's Fury", 'Howling Blast', 'Frost Strike', 'Thassarian', 'Horn of Winter'), 'DEATHKNIGHT_UNHOLY': ('Amalgam of the Deep', 'Grave Strength', 'Nerubian Swarmguard', 'Hawkstrider Rancher', 'Skeletal Sidekick', 'Blightfang', 'Plague Strike', 'Battlefield Necromancer'), 'DEMONHUNTER': ('Twin Slice', "Skull of Gul'dan", 'Warglaives of Azzinoth', 'Altruis the Outcast', 'Metamorphosis', 'Imprisoned Antaen', 'Priestess of Fury', 'Eye Beam'), 'DRUID': ('King Togwaggle', 'Twig of the World Tree', 'Malfurion the Pestilent', 'Naturalize', 'Azalina Soulthief', 'Lesser Jasper Spellstone', 'Spreading Plague', 'Branching Paths'), 'HUNTER': ('Lesser Emerald Spellstone', 'Wandering Monster', 'Misdirection', 'Explosive Trap', 'Cat Trick', 'Deathstalker Rexxar', 'Cloaked Huntress', 'Freezing Trap'), 'MAGE': ('Alexstrasza', 'Ice Block', 'Frost Nova', 'Doomsayer', 'Ice Lance', 'Fireball', 'Frostbolt', 'Archmage Antonidas'), 'PALADIN': ('Lady Liadrin', 'Aldor Truthseeker', 'Libram of Hope', 'Pen Flinger', 'Libram of Judgment', 'Libram of Justice', 'Libram of Wisdom', 'Aldor Attendant'), 'PRIEST': ('Galakrond, the Unspeakable', 'Soul Mirror', 'Kronx Dragonhoof', 'Devoted Maniac', 'Shield of Galakrond', 'Disciple of Galakrond', 'Fate Weaver', 'Time Rip'), 'ROGUE': ('Youthful Brewmaster', 'Gang Up', 'Preparation', 'Coldlight Oracle', 'Brann Bronzebeard', 'Antique Healbot', 'Shadowstep', 'Vanish'), 'SHAMAN': ('Healing Rain', 'Saronite Chain Gang', 'Grumble, Worldshaker', 'Glacial Shard', 'Zola the Gorgon', 'Lifedrinker', 'Shudderwock', 'Volcano'), 'WARLOCK': ("Skull of the Man'ari", 'Carnivorous Cube', "Bloodreaver Gul'dan", 'Faceless Manipulator', 'Doomguard', 'Voidlord', 'Defile', 'Dark Pact'), 'WARRIOR': ('Whirlwind', 'Grim Patron', 'Inner Rage', 'Execute', 'Frothing Berserker', "Death's Bite", 'Emperor Thaurissan', 'Warsong Commander')}
DEMON_HUNTER_IDS=('TOY_400t3', 'TOY_401t', 'TOY_400t7', 'TOY_401t2', 'TOY_400t6', 'TOY_400t4', 'TOY_400t5', 'TOY_400t8')
@dataclass(frozen=True)
class IconicCard:
 card_id:str
 # Physical compiled definitions must already have passed their independent
 # effect/identity review. Presence here is not behavioral certification.
 definition:object=None
@dataclass(frozen=True)
class IconicHand:
 key:str
 hero_class:str
 cards:tuple
 weight:int
@dataclass(frozen=True)
class IconicHandsContract:
 hands:tuple
 source:str
 build:str
 complete:bool
 distribution_source:str

def validate(game,contract):
 if not isinstance(contract,IconicHandsContract) or contract.complete is not True:raise UnsupportedCard('Harth requires a complete exact iconic-hand contract')
 if contract.build!='36.6.0.251952' or not isinstance(contract.source,str) or not contract.source.strip() or not isinstance(contract.distribution_source,str) or not contract.distribution_source.strip():raise UnsupportedCard('Harth contract requires pinned build and hand/distribution references')
 if not isinstance(contract.hands,tuple) or any(not isinstance(hand,IconicHand) for hand in contract.hands):raise UnsupportedCard('Harth hands must be immutable typed records')
 from .cards import registry
 written=registry()
 if len(contract.hands)!=13 or {h.key for h in contract.hands}!=EXPECTED_KEYS:raise UnsupportedCard('Harth contract must cover all eleven classes and three Death Knight hands exactly')
 if len({h.key for h in contract.hands})!=len(contract.hands):raise UnsupportedCard('Duplicate iconic hand')
 for hand in contract.hands:
  if not isinstance(hand,IconicHand) or hand.hero_class not in CLASSES or type(hand.weight) is not int or hand.weight<=0:raise UnsupportedCard('Invalid iconic hand class or explicit weight')
  expected='DEATHKNIGHT' if hand.key.startswith('DEATHKNIGHT_') else hand.key
  if hand.hero_class!=expected or not isinstance(hand.cards,tuple) or len(hand.cards)!=8:raise UnsupportedCard('Iconic hand class/order/card count mismatch')
  if tuple(game.cards.get(item.card_id,{}).get('name') for item in hand.cards if isinstance(item,IconicCard))!=ORDERED_NAMES[hand.key]:raise UnsupportedCard('Iconic hand card order differs from the current documented list')
  if hand.key=='DEMONHUNTER' and tuple(item.card_id for item in hand.cards)!=DEMON_HUNTER_IDS:raise UnsupportedCard('Harth Demon Hunter requires actual launch-edition tokens')
  for item in hand.cards:
   if not isinstance(item,IconicCard) or not isinstance(item.card_id,str) or item.card_id not in game.cards:raise UnsupportedCard('Unknown iconic card definition')
   if item.definition is None:
    if item.card_id not in written:raise UnsupportedCard('Unwritten iconic hand dependency: '+item.card_id)
   else:
    raise UnsupportedCard('Harth uses current printed cards or literal launch-edition tokens; arbitrary historical overlays are not exact')
 return contract

def replace_hand(game,owner,contract=None):
 p=game.players[owner]
 if getattr(p,'historical_harth_used',False):return
 contract=validate(game,contract if contract is not None else getattr(game,'historical_harth_contract',None))
 total=sum(hand.weight for hand in contract.hands);roll=game.rng.randrange(total);selected=None
 for hand in contract.hands:
  if roll<hand.weight:selected=hand;break
  roll-=hand.weight
 cards=[]
 for item in selected.cards:
  card=Card(game._new_id(),item.card_id)
  if item.definition is not None:
   card.rule_state=deepcopy(item.definition['state'])
   if item.definition['cost'] is not None:card.set_cost=item.definition['cost']
   if item.definition['stats'] is not None:card.base_stat_override=deepcopy(item.definition['stats'])
  cards.append(card)
 # Replacement is not a discard or draw. Clear first so hand-entry observers
 # never see an old card still occupying a slot during the replacement.
 p.historical_harth_used=True;p.hand=[]
 for card in cards:game._enter_hand(owner,card)
 game._refresh_auras();game._log('harth_hand_replaced',player=owner,count=len(cards))

STAGED_RULE=('none',[('historical_utility_harth',)])
