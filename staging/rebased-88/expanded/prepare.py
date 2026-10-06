"""Prepare is a non-play action on a physical hand card.

The discount survives hand copies; ordinary zone-reset helpers remove it.
Preparing never fires Battlecries, Combo, after-play, or spell listeners.
"""
from .prepare_cards import PREPARE_IDS

class Prepare:
    def _can_prepare(self, card, owner):
        state = getattr(card, 'rule_state', {})
        lock = getattr(card, 'play_lock', None)
        played_lock=state.get('locked_until_play')
        if played_lock and played_lock['owner']==owner and len(self.players[owner].played_history)<played_lock['count']:return False
        return ((card.card_id in PREPARE_IDS or card.card_id in ('JAIL_407','JAIL_321') or state.get('prepare')) and not state.get('prepared')
                and self.players[owner].mana >= 1 and self._cost(card, owner) > 0
                and not (lock and lock['owner'] == owner
                         and self.players[owner].turns_taken < lock['until']))

    def _prepare_card(self, uid):
        owner = self.current
        player = self.players[owner]
        card = next(c for c in player.hand if c.uid == uid)
        cost = self._cost(card, owner)
        paid = min(player.mana, max(1, cost - 1))
        reduction = min(cost, paid + 1)
        player.mana -= paid
        card.cost_delta = getattr(card, 'cost_delta', 0) - reduction
        self._b60_state(card).update(prepared=True, prepared_turn=self.turn)
        card.play_lock = dict(owner=owner, until=player.turns_taken + 1)
        for held in player.hand:
            if held.card_id == 'JAIL_453':
                held.cost_delta = getattr(held, 'cost_delta', 0) - reduction
        self._b60_spend_mana(owner, paid)
        self._log('prepare', player=owner, card=card.card_id, spent=paid, reduction=reduction)

    def _prepare_effect(self, op, ctx):
        if op[0] == 'prepare_judgment':
            target = next((m for p in self.players for m in p.minions
                           if m.uid == ctx.get('target')), None)
            if target is not None:
                attack, health = target.attack, target.health
                for player in self.players:
                    for minion in list(player.minions):
                        self._effect(('set_target_stats', attack, health), dict(ctx, target=minion.uid))
        elif op[0] == 'prepare_combo_stats':
            if ctx.get('combo'):
                amount = self.players[ctx['owner']].cards_played
                self._buff(ctx['source'], amount, amount)
        else:
            return False
        return True
