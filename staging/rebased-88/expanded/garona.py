"""Staged Garona bundle: opening transfer, assassination and physical reshuffle."""
from engine.game import Card
from engine.cards import UnsupportedCard

RULES={'TIME_875':('none',[('garona_assassinate',)])}
TOKEN_RULES={'TIME_875t':('none',[('draw',1),('garona_king_shuffle',)]),'TIME_875t1':('none',[])}
WEAPON_TRIGGERS={'TIME_875t1':[('garona_kingslayers',)]}

class Garona:
 def _garona_start(self):
  # Snapshot both decks before transferring, so two Llanes cannot bounce back.
  moving=[(owner,c) for owner,p in enumerate(self.players) for c in p.deck
          if isinstance(c,Card) and c.card_id=='TIME_875t' and (self._started_in_deck(c,owner) or getattr(c,'_copied_opening_effect',False))]
  for owner,card in moving:
   self.players[owner].deck.remove(card);self.players[1-owner].deck.append(card)
  for owner in sorted({1-owner for owner,_ in moving}):self.rng.shuffle(self.players[owner].deck)
  for owner,_ in moving:self._log('king_llane_hides',player=owner,destination=1-owner)

 def _garona_effect(self,op,ctx):
  owner=ctx['owner'];p=self.players[owner];q=self.players[1-owner];name=op[0]
  if name=='garona_assassinate':
   kings=[c for c in q.hand if c.card_id=='TIME_875t']
   if len(kings)>1:raise UnsupportedCard('Multiple held King Llane copies require independent resolution evidence')
   if kings:
    q.hand.remove(kings[0]);q.health//=2;q.hero_health_changed_turn=True
    self._log('destroy_hand_card',player=1-owner,card='TIME_875t')
    self._refresh_auras()
  elif name=='garona_king_shuffle':
   source=ctx.get('source')
   if source is not None and source in p.minions:
    p.board.remove(source);card=Card(self._new_id(),source.card_id);self._carry_origin(source,card)
    p.deck.append(card);self.rng.shuffle(p.deck)
    self._record_deck_insertion(owner,owner,1,'shuffle');self._refresh_auras()
    self._log('shuffle_from_board',player=owner,card=source.card_id)
  elif name=='garona_kingslayers':
   # Weapon triggers may be dispatched without a play frame. Queue one so a
   # draw-trigger choice or death settles before the second player's draw.
   self._rule_events.append(('captured_effects',dict(
    operations=(('garona_legend_draw',owner),('garona_legend_draw',1-owner)),
    context=dict(owner=owner,source=None,target=0,bonus=0,lifesteal=False)),[]))
  elif name=='garona_legend_draw':
   self._draw(op[1],predicate=lambda d:d.get('rarity')=='LEGENDARY')
  else:return False
  return True
