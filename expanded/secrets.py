"""Explicit secret rules. Opponents receive counts, never secret identities."""
from engine.game import Card

SECRETS = {
    'CORE_EX1_287': 'counterspell',
    'CORE_EX1_289': 'ice_barrier',
    'CORE_EX1_610': 'explosive_trap',
    'CORE_EX1_611': 'freezing_trap',
    'CORE_GIL_577': 'rat_trap',
    'CORE_ULD_152': 'pressure_plate',
}


class Secrets:
    def _reveal_secret(self, owner, secret):
        self.players[owner].secrets.remove(secret)
        self._log('secret_revealed',player=owner,card=secret.card_id)

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
                if rule == 'freezing_trap' and attacker:
                    self._reveal_secret(owner,secret)
                    self._bounce(attacker,2)
                    canceled = True
                elif rule == 'ice_barrier' and data['target']==self.hero_id(owner):
                    self._reveal_secret(owner,secret)
                    p.armor += 8
                elif rule == 'explosive_trap' and data['target']==self.hero_id(owner):
                    self._reveal_secret(owner,secret)
                    self._effect(('area_damage','enemies',2),ctx)
                self._settle()
                if self.terminal or (attacker and attacker not in q.board):
                    canceled = True
            elif event=='after_spell' and rule=='pressure_plate' and q.minions:
                self._reveal_secret(owner,secret)
                self.rng.choice(q.minions).health=0
                self._settle()
            elif event=='after_card' and rule=='rat_trap' and q.cards_played==3 and len(p.board)<7:
                self._reveal_secret(owner,secret)
                self._summon(owner,'GIL_577t')
            if self.terminal:
                break
        return canceled
