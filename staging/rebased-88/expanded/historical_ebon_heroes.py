"""Two historical Hero cards and their full weapon/power outcome families."""
HORSEMEN=('ICC_829t2','ICC_829t3','ICC_829t4','ICC_829t5')
ROOT_RULES={'ICC_829':('none',[('equip','ICC_829t')]),'ICC_834':('none',[('equip','ICC_834w')])}
TOKEN_RULES={cid:('none',[]) for cid in HORSEMEN+('ICC_829t','ICC_834w')}
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)|{'ICC_829p','ICC_834h'}

def split(game,op,ctx):
 if op[0]!='historical_ebon_horsemen':return None
 owner=ctx['owner'];player=game.players[owner]
 from .pools import require_fixed_cards
 require_fixed_cards(HORSEMEN,game.cards)
 present={m.card_id for m in player.minions if m.health>0}
 available=[cid for cid in HORSEMEN if cid not in present]
 if not available:return ('historical_ebon_check',),()
 if len(player.board)>=7:return ('batch30_noop',),()
 head,tail=game._split_fixed_summon(('summon',game.rng.choice(available),1),ctx)
 return head,tuple(tail)+(('historical_ebon_check',),)

def execute(game,op,ctx):
 name=op[0]
 if name=='historical_ebon_check':
  owner=ctx['owner'];present={m.card_id for m in game.players[owner].minions if m.health>0}
  if set(HORSEMEN)<=present:
   # Destruction bypasses Armor, damage prevention and damage triggers.
   game.players[1-owner].health=0
   game._log('horsemen_destroy_hero',player=owner)
  return True
 if name=='historical_ebon_bladestorm':
  targets=[m.uid for player in game.players for m in player.minions if m.health>0]
  with game._damage_batch():
   for uid in targets:game._effect(('historical_copy_power_hit','target',1),dict(ctx,target=uid))
  return True
 return False
