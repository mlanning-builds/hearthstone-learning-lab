"""One healing-effect replacement; nested targets share an effect frame."""
RULES={'CATA_301':('none',[('ruby_sanctum',)])}
class HealingReplacement:
 def _ruby_effect(self,op,ctx):
  if op[0]!='ruby_sanctum':return False
  self.players[ctx['owner']].ruby_until=self.turn
  return True
 def _ruby_heal(self,target,amount,healer):
  if healer is None or amount<=0:return False
  p=self.players[healer];frame=getattr(self,'_healing_replacement_frame',None)
  active=self._active('EX1_591',healer) or (frame is not None and healer in frame) or getattr(p,'historical_healing_damage_turn',None)==self.turn
  if not active and getattr(p,'historical_healing_damage_charges',0)>0:
   p.historical_healing_damage_charges-=1;active=True
   if frame is not None:frame.add(healer)
  if getattr(p,'ruby_until',-1)==self.turn:
   p.ruby_until=-1;active=True
   if frame is not None:frame.add(healer)
  if not active:return False
  self._damage(target,amount,damage_owner=healer,damage_source=None)
  return True
