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
  active=frame is not None and healer in frame
  if getattr(p,'ruby_until',-1)==self.turn:
   p.ruby_until=-1;active=True
   if frame is not None:frame.add(healer)
  if not active:return False
  self._damage(target,amount,damage_owner=healer,damage_source=None)
  return True
