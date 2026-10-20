"""Historical combat grants and Garrote; behavioral validation pending.

Uses the frozen modern Shadowform text, not its removed Classic upgrade.
"""
def op(name,*args):return ('historical_utility_final_combat_'+name,)+args
TOKEN_RULES={
 'EX1_625':('none',[('historical_copy_replace_power','EX1_625t')]),
 'SW_311':('none',[('damage_enemy_hero',2),('on_draw_shuffle','SW_311t',3,0)]),
 'SW_311t':('none',[('damage_enemy_hero',2)]),
 'DAL_062':('minion',[op('cleave')]),
 'ONY_023':('none',[('hero_attack',10),op('hero_minions_only')]),
 'WORK_022':('none',[('hero_attack',3),op('hero_cleave')]),
}
CAST_EFFECTS={'SW_311t':(('damage_enemy_hero',2),)}
FIXED_TOKEN_IDS=frozenset(TOKEN_RULES)

def execute(game,operation,ctx):
 name=operation[0];owner=ctx['owner'];p=game.players[owner]
 if name==op('cleave')[0]:
  m=game._force_live(ctx.get('target'))
  if m is not None:
   entries=tuple(m.rule_state.get('forge_intrinsics',()))
   if ('cleave',True) not in entries:m.rule_state['forge_intrinsics']=entries+(('cleave',True),)
 elif name==op('hero_minions_only')[0]:p.historical_hero_minions_only_turn=game.turn
 elif name==op('hero_cleave')[0]:p.historical_hero_cleave_turn=game.turn
 else:return False
 return True
