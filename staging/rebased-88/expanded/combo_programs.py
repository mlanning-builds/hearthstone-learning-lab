"""Separate Combo triggers from independent Battlecries before repetition.

Generated-card Combo modifiers belong to that generated physical card. Repeating
its Combo strengthens that modifier; it does not generate another base card.
"""
CONDITIONAL=frozenset(('historical_if_combo','combo_operation','combo_damage','combo_buff','combo_summon','combo_copy_self','combo_cast_fixed_spell','combo_overload_keywords','prepare_combo_stats'))

def separate(operations,context,repetitions):
 base=[];combo=[]
 for operation in operations:
  name=operation[0]
  conditional=(name in CONDITIONAL or
   name=='historical_resurrection_draw_death' and operation[1] is True or
   context.get('combo') and (name=='historical_play_quick_or_combo_coin' or name=='historical_secret_deck' and operation[1]=='combo'))
  if conditional:combo.append(operation)
  elif name=='generate_random' and any(key in ('combo_attack','combo_cost_delta') for key,value in operation[4]):
   modifiers=tuple((key,value*repetitions if key in ('combo_attack','combo_cost_delta') else value) for key,value in operation[4])
   base.append(operation[:4]+(modifiers,))
  else:base.append(operation)
 return base,combo
