"""Explicit secret rules. Opponents receive counts, never secret identities."""
from engine.game import Card
from engine.cards import UnsupportedCard

SECRET_SUMMONS = {'CORE_BAR_812':'CS2_033'}

SECRETS = {
    'TIME_620': 'untimely_death',
    'JAIL_315': 'mystic_misdirection',
    'CORE_LOOT_101': 'explosive_runes',
    'CORE_BAR_812': 'oasis_ally',
    'CORE_EX1_287': 'counterspell',
    'CORE_EX1_289': 'ice_barrier',
    'CORE_EX1_610': 'explosive_trap',
    'CORE_EX1_611': 'freezing_trap',
    'CORE_GIL_577': 'rat_trap',
    'CORE_ULD_152': 'pressure_plate',
}


class Secrets:
    def _place_secret(self,owner,cid,physical=None):
        if cid not in SECRETS:raise UnsupportedCard('Secret rule not implemented: '+cid)
        player=self.players[owner]
        reason=('duplicate' if any(c.card_id==cid for c in player.secrets) else
                'capacity' if len(player.secrets)+self._quest_slots(owner)>=5 else None)
        if reason:
            self._log('secret_fizzle',player=owner,card=cid,reason=reason)
            return None
        card=physical if physical is not None and physical.card_id==cid else Card(self._new_id(),cid)
        player.secrets.append(card)
        return card

    def _reveal_secret(self, owner, secret):
        self.players[owner].secrets.remove(secret)
        self._log('secret_revealed',player=owner,card=secret.card_id)

    def _secret_capture_death(self,minion,position):
        # Queue a physical death snapshot. A second death cannot retarget the
        # first pending Secret; activation rechecks the exact Secret instance.
        if minion.owner==self.current or minion.played_turn<0 or minion.played_turn!=self.turn-1:
            return
        for secret in self.players[minion.owner].secrets:
            if secret.card_id=='TIME_620':
                self._rule_events.append(('captured_effects',dict(
                    operations=(('secret_resummon',secret.uid,minion.card_id,position),),
                    context=dict(owner=minion.owner,source=None,target=0,bonus=0,lifesteal=False)),[]))

    def _secret_effect(self,op,ctx):
        if op[0]!='secret_resummon':return False
        owner=ctx['owner'];player=self.players[owner]
        secret=next((c for c in player.secrets if c.uid==op[1] and c.card_id=='TIME_620'),None)
        if secret is not None and len(player.board)<7 and self.current!=owner:
            self._reveal_secret(owner,secret)
            self._summon(owner,op[2],min(op[3],len(player.board)),
                         entry_origin='secret',entry_site='untimely_death',entry_source=secret)
        return True

    def _secret_event(self, event, actor, **data):
        """Resolve in play order, rechecking the trigger against the updated state."""
        owner = 1-actor
        if self.current == owner:
            return False
        canceled = False
        for secret in list(self.players[owner].secrets):
            rule = SECRETS[secret.card_id]
            p = self.players[owner]
            q = self.players[actor]
            ctx = dict(owner=owner,source=None,target=0,
                       bonus=self._spell_damage(owner),lifesteal=False)
            if event == 'before_spell' and rule == 'counterspell' and not canceled:
                self._reveal_secret(owner,secret)
                canceled = True
            elif event == 'attack':
                attacker = next((m for m in q.minions if m.uid == data['source']),None)
                if canceled or (data['source']>0 and attacker is None):
                    break
                if rule == 'oasis_ally' and any(m.uid==data['target'] for m in p.minions) and len(p.board)<7:
                    self._reveal_secret(owner,secret)
                    self._summon(owner,SECRET_SUMMONS[secret.card_id], entry_origin='secret', entry_site='secrets._secret_event', entry_source=secret)
                elif rule == 'mystic_misdirection' and attacker:
                    self._reveal_secret(owner,secret)
                    self._transform(attacker,'CS2_tk1')
                    canceled=True
                elif rule == 'freezing_trap' and attacker:
                    self._reveal_secret(owner,secret)
                    self._bounce(attacker,2)
                    canceled = True
                elif rule == 'ice_barrier' and data['target']==self.hero_id(owner):
                    self._reveal_secret(owner,secret)
                    self._gain_armor(owner,8)
                elif rule == 'explosive_trap' and data['target']==self.hero_id(owner):
                    self._reveal_secret(owner,secret)
                    self._effect(('area_damage','enemies',2),ctx)
                self._settle()
                if self.terminal or (attacker and attacker not in q.board):
                    canceled = True
            elif event=='after_card' and rule=='explosive_runes':
                minion=next((m for m in q.minions if m.uid==data.get('source') and m.health>0 and not m.dormant),None)
                if minion is not None:
                    self._reveal_secret(owner,secret)
                    amount=6+ctx['bonus'];excess=max(0,amount-minion.health)
                    with self._damage_batch():
                        self._damage(minion.uid,amount,damage_source=None,damage_owner=owner)
                        if excess:self._damage(self.hero_id(actor),excess,damage_source=None,damage_owner=owner)
                    self._settle()
            elif event=='after_spell' and rule=='pressure_plate' and q.minions:
                self._reveal_secret(owner,secret)
                self.rng.choice(q.minions).health=0
                self._settle()
            elif event=='after_card' and rule=='rat_trap' and q.cards_played==3 and len(p.board)<7:
                self._reveal_secret(owner,secret)
                self._summon(owner,'GIL_577t', entry_origin='secret', entry_site='secrets._secret_event', entry_source=secret)
            if self.terminal:
                break
        return canceled
