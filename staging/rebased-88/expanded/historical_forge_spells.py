"""Forged spell pairs and explicit generated enchantment programs."""
from engine.game import Card
from .selectors import has_tribe
from .historical_saidan import add as add_stat
FORMS={cid:cid+'t' for cid in ('TTN_753','TTN_865','TTN_951','YOG_502')}
TOKEN_RULES={
 'TTN_753':('minion',[('damage',5)]),
 'TTN_753t':('minion',[('damage',5),('missiles','enemy_minions',5)]),
 'TTN_865':('none',[('draw',2)]),
 'TTN_865t':('none',[('historical_forge_spell_draw_match',)]),
 'TTN_951':('none',[('filtered_draw',(('mechanic','eq','CHOOSE_ONE'),),1)]),
 'TTN_951t':('none',[('historical_forge_spell_draw_combined',)]),
 'YOG_502':('none',[('historical_forge_spell_armor_damage',)]),
 'YOG_502t':('none',[('armor',3),('historical_forge_spell_armor_damage',)]),
 'ETC_417':('none',[('historical_forge_spell_blackrock',)]),
 'TOY_805':('none',[('historical_forge_spell_ensmallen',)]),
 'YOG_505':('none',[('historic_zone_buff','hand_deck',None,1,0),('board_buff',1,0)]),
 'ETC_305':('minion',[('historical_forge_spell_distort',)]),
 'RLK_909':('minion',[('historical_forge_spell_zombies',)]),
 'NX2_016':('none',[('historical_forge_spell_implocs',)]),
 'RLK_910':('none',[('historical_forge_spell_suffusion',)]),
 'TOY_527':('friendly_minion',[('historical_forge_spell_campaign',)]),
 'RLK_909t':('none',[]),'NX2_016t':('none',[]),
}
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)


def split(game,op,ctx):
 owner=ctx['owner'];name=op[0]
 if name=='historical_forge_spell_draw_match':return ('draw_until',len(game.players[1-owner].hand)),(('draw',2),)
 if name=='historical_forge_spell_draw_combined':
  state={}
  return ('historical_draw_capture',(('mechanic','eq','CHOOSE_ONE'),),'random',state),(('historical_forge_spell_combine',state),)
 if name=='historical_forge_spell_campaign_death':
  source=ctx.get('source')
  if source is None:return ('batch30_noop',),()
  operation=('historical_forge_spell_campaign_copy',source)
  return operation,(operation,)
 return None


def execute(game,op,ctx):
 owner=ctx['owner'];p=game.players[owner];name=op[0]
 target=next((m for player in game.players for m in player.minions if m.uid==ctx.get('target') and m.health>0),None)
 if name=='historical_forge_spell_combine':
  card=op[1].get('card')
  if card is not None and any(card is held for held in p.hand):game._b60_state(card)['choose_both']=True
 elif name=='historical_forge_spell_armor_damage':game._effect(('area_damage','all_minions',p.armor),ctx)
 elif name in ('historical_forge_spell_blackrock','historical_forge_spell_ensmallen'):
  for index,value in enumerate(p.deck):
   if game._card_data(value)['type']!='MINION':continue
   card=value if isinstance(value,Card) else Card(game._new_id(),value)
   if name=='historical_forge_spell_blackrock':
    amount=game._card_stat(card,'cost',owner);add_stat(card,'attack_bonus',amount);add_stat(card,'health_bonus',amount)
   else:card.cost_delta=getattr(card,'cost_delta',0)-(1);add_stat(card,'attack_bonus',-1)
   p.deck[index]=card
 elif name=='historical_forge_spell_distort':
  if target is not None:
   game._buff(target,-5,-5)
   if target.attack<=0 and not game._fire_immune_target(target.uid,ctx):target.health=0
 elif name=='historical_forge_spell_zombies':
  if target is not None:target.attached_death_effects.append(('summon','RLK_909t',2))
 elif name=='historical_forge_spell_implocs':
  for minion in p.minions:
   if any(has_tribe(game._card_data(minion),tribe) for tribe in ('DEMON','MURLOC')):minion.attached_death_effects.append(('summon','NX2_016t',1))
 elif name=='historical_forge_spell_suffusion':
  for minion in p.minions:minion.attached_death_effects.append(('historical_forge_spell_random_damage',3))
 elif name=='historical_forge_spell_random_damage':
  values=[game.hero_id(1-owner)]+[m.uid for m in game.players[1-owner].minions if m.health>0]
  if values:game._deal_effect(game.rng.choice(values),op[1],ctx)
 elif name=='historical_forge_spell_campaign':
  if target is not None:target.attached_death_effects.append(('historical_forge_spell_campaign_death',))
 elif name=='historical_forge_spell_campaign_copy':
  source=op[1]
  game._summon(owner,source.card_id,copy_from=source,dormant_turns=2,entry_origin='copy',entry_site='cursed_campaign',entry_source=source)
 else:return False
 return True
