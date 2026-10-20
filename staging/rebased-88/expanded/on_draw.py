"""On-draw cards resolve through queued, resumable effect operations.

Overdraw burns the card before its automatic effect. Replacement draws are
ordinary draws; explicitly casting a Shred from deck does not replace it.
"""
from .historical_saidan import add as _saidan_add
from copy import deepcopy
from engine.game import Card
from .on_draw_cards import CAST_EFFECTS,SUMMON_DRAW,IMP,SHRED

class OnDraw:
    def _on_draw_receive(self,owner,value,private):
        cid=self._card_data(value)['id'];player=self.players[owner]
        card=value if isinstance(value,Card) else Card(self._new_id(),cid)
        spell=self._card_data(card)['type']=='SPELL';jotun=False;converted=False
        if spell:
            seen=getattr(player,'historical_first_spell_draw_turn',None)==self.turn
            player.historical_first_spell_draw_turn=self.turn
            jotun=not seen and getattr(player,'historical_jotun',False)
            charges=getattr(player,'historical_draw_cast_charges',0)
            if charges:player.historical_draw_cast_charges=charges-1;converted=True
        intrinsic=cid in CAST_EFFECTS or cid in SUMMON_DRAW or spell and bool(getattr(card,'rule_state',{}).get('historical_cast_when_drawn'))
        if not intrinsic and not converted:
            if jotun:card._historical_jotun_copy_pending=True
            return False
        if not private:
            self._log('draw',player=owner)
            self._queue_event('card_drawn',owner=owner,card=deepcopy(card))
        context=dict(owner=owner,source=None,target=0,spell=spell,card_id=cid,bonus=self._spell_damage(owner,cid,card) if spell else 0,lifesteal=False,physical_card=card,cast_when_drawn=True)
        operations=[]
        if jotun:operations.append(('cast_physical_spell',self._copy_card(card,source_owner=owner),'enemies'))
        if cid in SUMMON_DRAW:operations.append(('on_draw_summon',card))
        elif cid in CAST_EFFECTS:operations.extend(CAST_EFFECTS[cid])
        else:operations.append(('cast_physical_spell',card,'random'))
        operations.append(('draw',1))
        if cid=='TRL_541t':operations.append(('on_draw_shuffle','TRL_541t',2,0))
        self._rule_events.append(('captured_effects',dict(operations=tuple(operations),context=context),[]))
        return True

    def _on_draw_post_receive(self,owner,card):
        if not getattr(card,'_historical_jotun_copy_pending',False):return
        del card._historical_jotun_copy_pending
        copy=self._copy_card(card,source_owner=owner)
        context=dict(owner=owner,source=None,target=0,bonus=0,lifesteal=False)
        self._rule_events.append(('captured_effects',dict(operations=(('cast_physical_spell',copy,'enemies'),),context=context),[]))

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
            cards=[Card(self._new_id(),cid) for _ in range(count)]
            self.players[destination].deck.extend(cards)
            self.rng.shuffle(self.players[destination].deck)
            self._record_deck_insertion(destination,owner,count,'shuffle',cards=cards);self._refresh_auras()
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
                _saidan_add(card,'attack_bonus',2);_saidan_add(card,'health_bonus',2);deck.append(card);self._refresh_auras()
        else:return False
        return True
