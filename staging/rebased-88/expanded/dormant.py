"""Inactive board entities with explicit owner-turn and conditional awakening."""
from .dormant_cards import INITIAL
from .selectors import has_tribe


class Dormancy:
    def _dormant_entity(self, uid):
        return next((m for p in self.players for m in p.all_minions if m.uid == uid), None)

    def _sleep_minion(self, minion, turns):
        if minion is None or minion.health <= 0 or minion.dormant:
            return
        minion.dormant = turns
        self._refresh_auras()
        self._log('dormant', player=minion.owner, entity=minion.uid, turns=turns)

    def _awaken(self, minion):
        if minion is None or not minion.dormant or minion not in self.players[minion.owner].board:
            return
        minion.dormant = 0
        minion.summoned_turn = self.turn
        minion.attacks = 0
        self._refresh_auras()
        self._log('awaken', player=minion.owner, entity=minion.uid)
        if minion.card_id == 'EDR_840t' and not minion.silenced:
            self.players[minion.owner].temporary_attack += 3

    def _dormant_full_board(self):
        for p in self.players:
            if len(p.board) == 7:
                for m in list(p.all_minions):
                    if m.card_id == 'MEND_040' and m.dormant and not m.silenced:
                        self._awaken(m)

    def _dormant_turn_entries(self, phase):
        entries = []
        for m in self.players[self.current].all_minions:
            if not m.dormant:
                continue
            ops = []
            if phase == 'start':
                if m.dormant > 0:
                    ops = [('dormant_reduce',)]
                if m.card_id == 'TLC_253' and not m.silenced:
                    ops.append(('dormant_ogre',))
            elif m.card_id == 'EDR_979' and not m.silenced:
                ops = [('armor', 3), ('draw', 1)]
            if ops:
                entries.append(dict(source=m, operations=tuple(ops), dormant_entry=True))
        return entries

    def _dormant_trigger_matches(self, wanted, kind, data, minion):
        if wanted == 'dormant_power_used':
            return bool(minion.dormant and kind == 'hero_power_used' and data['owner'] == minion.owner)
        if wanted == 'dormant_newest_played':
            return bool(minion.dormant and kind in ('minion_played', 'spell_cast', 'dormant_other_card_played')
                        and data['owner'] == minion.owner
                        and self.cards[data['card_id']]['set'] == 'ESCAPEFROM_VIOLET_HOLD')
        return None

    def _dormant_effect(self, op, ctx):
        name = op[0]
        if not name.startswith('dormant_'):
            return False
        owner = ctx['owner']; source = ctx.get('source')
        target = self._dormant_entity(ctx.get('target', 0))
        if name == 'dormant_reduce':
            if source is not None and source.dormant > 0:
                source.dormant -= 1
                if source.dormant == 0:
                    source.dormant = -1
                    self._awaken(source)
        elif name == 'dormant_ogre':
            if source is not None and source.dormant:
                if self.rng.randrange(2) == 0:
                    self._awaken(source)
                else:
                    # This is the explicit exception to ordinary Dormant immunity.
                    self._adjust_minion_attack(source, 2)
                    source.health += 2; source.max_health += 2
        elif name == 'dormant_awaken_source':
            self._awaken(source)
        elif name == 'dormant_maiev':
            target = self._dormant_entity(ctx['event']['source'])
            if target is not None and not target.dormant and target.health > 0:
                self._buff(target, 3, 3)
                self._sleep_minion(target, 1)
        elif name == 'dormant_confinement':
            if target is not None and not target.dormant:
                if target.owner == owner and has_tribe(self.cards[target.card_id], 'DEMON'):
                    self._buff(target, 3, 3)
                else:
                    self._sleep_minion(target, 2)
        elif name == 'dormant_imprison':
            if target is not None and not target.dormant and source is not None:
                source.rule_state['imprisoned_entity'] = target.uid
                self._sleep_minion(target, 10000)
        elif name == 'dormant_release':
            if source is not None:
                self._awaken(self._dormant_entity(source.rule_state.get('imprisoned_entity')))
        else:
            return False
        return True
