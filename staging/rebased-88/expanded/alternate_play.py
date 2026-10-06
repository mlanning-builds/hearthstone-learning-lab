"""Explicit controller choice and alternate payment for Constructed cards."""
from .selectors import has_tribe
from .health_generation import HEALTH_PAYMENT_IDS
EITHER_SIDE={'CAP_004','JAIL_442','JAIL_452','JAIL_455','JAIL_461'}
RULES={
 'CAP_004':('none',[]),'JAIL_442':('none',[]),'JAIL_452':('none',[]),
 'JAIL_455':('none',[('alternate_damage_others',1),('alternate_damage_others',1)]),
 'JAIL_461':('none',[('alternate_destroy_neighbor',)]),
 'CATA_180':('none',[('alternate_next_payment','murloc_health')]),
 'CORE_ETC_523':('none',[]),
 'EDR_489':('none',[('alternate_next_payment','enemy_health')]),
 'TLC_436':('none',[]),
}
DEATH_EFFECTS={'CAP_004':[('alternate_enemy_draw',),('alternate_enemy_draw',)],
               'JAIL_442':[('on_draw_shuffle','JAIL_443t',4,0)]}

class AlternatePlay:
    def _payment_kind(self,card,owner,cost=None):
        p=self.players[owner];cost=self._cost(card,owner) if cost is None else cost
        kind='corpses' if card.card_id=='TLC_436' else 'health' if card.card_id=='CORE_ETC_523' and p.hero_healed_turn else 'mana'
        state=getattr(card,'rule_state',{})
        if card.card_id in HEALTH_PAYMENT_IDS or (state.get('health_payment') and self.turn<=state.get('health_payment_until',self.turn)):
            kind='health'
        for effect in p.payment_effects:
            if effect=='enemy_health':kind='enemy_health'
            elif effect=='murloc_health' and cost<=3 and has_tribe(self.cards[card.card_id],'MURLOC'):kind='health'
        return kind

    def _can_pay(self,card,owner):
        p=self.players[owner];cost=self._cost(card,owner);kind=self._payment_kind(card,owner,cost)
        if kind=='mana':return cost<=p.mana
        if kind=='corpses':return cost<=p.corpses
        if kind=='health':return cost<p.health or self._onyxia_active(owner)
        return cost<=10

    def _pay_card(self,card,owner,cost):
        p=self.players[owner];kind=self._payment_kind(card,owner,cost)
        p.payment_effects[:]=[e for e in p.payment_effects if e!='enemy_health' and not (e=='murloc_health' and cost<=3 and has_tribe(self.cards[card.card_id],'MURLOC'))]
        if kind=='mana':p.mana-=cost;self._b60_spend_mana(owner,cost)
        elif kind=='corpses':
            self._spend_corpses(owner,cost)
        else:
            recipient=1-owner if kind=='enemy_health' else owner
            if not self._replace_hero_health_loss(recipient,cost):
                self.players[recipient].health-=cost
                if cost:self.players[recipient].hero_health_changed_turn=True
            self._log('pay_health',player=recipient,amount=cost)

    def _alternate_effect(self,op,ctx):
        owner=ctx['owner'];p=self.players[owner];source=ctx.get('source')
        if op[0]=='alternate_next_payment':p.payment_effects.append(op[1])
        elif op[0]=='alternate_enemy_draw':self._draw(1-owner)
        elif op[0]=='alternate_damage_others':
            with self._damage_batch():
                for m in list(p.minions):
                    if m is not source:self._deal_effect(m.uid,op[1],ctx)
        elif op[0]=='alternate_destroy_neighbor':
            if source in p.board:
                i=p.board.index(source)
                choices=[p.board[j] for j in (i-1,i+1) if 0<=j<len(p.board) and p.board[j] in p.minions]
                if choices:self.rng.choice(choices).health=0
        else:return False
        return True
