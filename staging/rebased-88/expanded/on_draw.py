"""On-draw cards resolve through queued, resumable effect operations.

Overdraw burns the card before its automatic effect. Replacement draws are
ordinary draws; explicitly casting a Shred from deck does not replace it.
"""
from copy import deepcopy
from engine.game import Card
from .on_draw_cards import CAST_EFFECTS,SUMMON_DRAW,IMP,SHRED

class OnDraw:
    def _on_draw_receive(self,owner,value,private):
        cid=self._card_data(value)['id']
        if cid not in CAST_EFFECTS and cid not in SUMMON_DRAW:return False
        card=value if isinstance(value,Card) else Card(self._new_id(),cid)
        if not private:
            self._log('draw',player=owner)
            self._queue_event('card_drawn',owner=owner,card=deepcopy(card))
        context=dict(owner=owner,source=None,target=0,spell=cid in CAST_EFFECTS,card_id=cid,bonus=0,lifesteal=False)
        operations=(('on_draw_summon',card),) if cid in SUMMON_DRAW else CAST_EFFECTS[cid]
        operations=tuple(operations)+(('draw',1),)
        self._rule_events.append(('captured_effects',dict(operations=operations,context=context),[]))
        return True

    def _on_draw_split(self,op,ctx):
        if op[0]!='on_draw_consume_shred':return None
        p=self.players[ctx['owner']]
        choices=[i for i,c in enumerate(p.deck) if self._card_data(c)['id']==SHRED]
        if not choices:return ('batch30_noop',),()
        p.deck.pop(self.rng.choice(choices));self._refresh_auras()
        context=dict(owner=ctx['owner'],source=None,target=0,spell=True,card_id=SHRED,bonus=0,lifesteal=False)
        return ('replay_one',('on_draw_hurt_owner',3),context),(('on_draw_shred_reward',op[1]),)

    def _on_draw_effect(self,op,ctx):
        owner=ctx['owner'];p=self.players[owner]
        if op[0]=='on_draw_shuffle':
            cid,count,enemy=op[1:];destination=1-owner if enemy else owner
            self.players[destination].deck.extend(Card(self._new_id(),cid) for _ in range(count))
            self.rng.shuffle(self.players[destination].deck)
            self._record_deck_insertion(destination,owner,count,'shuffle');self._refresh_auras()
        elif op[0]=='on_draw_summon':
            card=op[1];recipient=owner if SUMMON_DRAW[card.card_id]==0 else 1-owner
            card._drawn_minion=self._summon(recipient,card.card_id,attack_bonus=card.attack_bonus,health_bonus=card.health_bonus,entry_origin='recruit',entry_zone='deck',entry_source=card,entry_site='summoned_when_drawn')
        elif op[0]=='on_draw_hurt_owner':self._deal_effect(self.hero_id(owner),op[1],ctx)
        elif op[0]=='on_draw_shred_reward':
            source=ctx.get('source')
            if source is not None and source in p.minions and source.health>0:
                if op[1]=='buff':self._buff(source,3,3)
                else:self._summon(owner,source.card_id,copy_from=source,entry_origin='copy',entry_site='shred_reward')
        elif op[0]=='on_draw_imp_upgrade':p.imp_upgrades=getattr(p,'imp_upgrades',0)+1
        elif op[0]=='on_draw_top_imp':
            deck=self.players[1-owner].deck
            choices=[i for i,c in enumerate(deck) if self._card_data(c)['id']==IMP]
            if choices:
                card=deck.pop(self.rng.choice(choices))
                if not isinstance(card,Card):card=Card(self._new_id(),card)
                card.attack_bonus+=2;card.health_bonus+=2;deck.append(card);self._refresh_auras()
        else:return False
        return True
