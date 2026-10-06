"""Temporary hand cards and expiring, transferable after-play effects.

Generation pools are never reduced to the currently implemented subset.
"""
from copy import deepcopy
from engine.game import Card
from .pools import deck_choice_options
from .selectors import has_tribe

from .choice_generators import STEALTH,choice

FOLLOW_RULES={
 'CAP_002':(choice(STEALTH,follow='CAP_002'),),
 'CAP_402':(('on_draw_shuffle','CAP_400t2t',1,1),('follow_attach','CAP_402')),
 'CAP_101':(('damage_random_enemy',2),('follow_attach','CAP_101')),
 'CAP_802':(('summon','CAP_802t',1),('follow_attach','CAP_802')),
}

class TemporaryCards:
    def _is_temporary(self,card):
        return bool(getattr(card,'rule_state',{}).get('temporary'))

    def _make_temporary(self,card):
        self._b60_state(card)['temporary']=True
        return card

    def _expire_temporary_hand(self,owner):
        cards=[c for c in self.players[owner].hand if self._is_temporary(c)]
        if cards:self._discard_cards(owner,cards)

    def _expire_follow(self):
        for p in self.players:
            for c in p.hand+p.deck:
                if hasattr(c,'_follow_effects'):
                    c._follow_effects[:]=[e for e in c._follow_effects if e['end']>self.turn]

    def _capture_follow(self,owner,card):
        self._pending_follow=dict(owner=owner,card_id=card.card_id,
            effects=deepcopy([e for e in getattr(card,'_follow_effects',[]) if e['end']>=self.turn]))

    def _publish_follow(self,owner,source=None):
        pending=getattr(self,'_pending_follow',None);self._pending_follow=None
        if pending is None or not pending['effects'] or self.terminal:return
        assert pending['owner']==owner
        pending['source']=source
        self._rule_events.append(('follow_after_play',pending,[]))

    def _follow_event_frame(self,event,allow_choices):
        kind,data,_=event
        if kind!='follow_after_play':return None
        owner=data['owner'];is_spell=self.cards[data['card_id']]['type']=='SPELL'
        source=data['source'] if not is_spell and hasattr(data['source'],'owner') else None
        ctx=dict(owner=owner,source=source,target=0,spell=is_spell,
                 bonus=self._spell_damage(owner) if is_spell else 0,lifesteal=False)
        ops=tuple(op for e in data['effects'] for op in
                  ((('map_follow_choice',e),) if 'map_options' in e else FOLLOW_RULES[e['card_id']]))
        return dict(kind=kind,data=data,listeners=[],listener=0,operations=ops,
                    operation=0,context=ctx,key=None,allow_choices=allow_choices,post_operation=False)

    def _temporary_choice(self,choice,selected):
        if choice['kind']!='temporary_deck':return False
        owner=choice['owner'];value=self.players[owner].deck.pop(selected['index'])
        card=value if isinstance(value,Card) else Card(self._new_id(),value)
        self._make_temporary(card)
        # Discover moves the selected card; it is not a draw and must not
        # activate Casts/Summons When Drawn or successful-draw listeners.
        self._discovery_result=self._enter_hand(owner,card)
        self._refresh_auras()
        return True

    def _temporary_effect(self,op,ctx):
        owner=ctx['owner'];p=self.players[owner]
        if op[0]=='temporary_next_discount':
            p.cost_effects.append(dict(selector='TEMPORARY',amount=op[1],expires=None))
        elif op[0]=='temporary_deck_discover':
            indexed=[(i,c) for i,c in enumerate(p.deck) if self._card_data(c)['id']!='TLC_451']
            values=[c for _,c in indexed]
            options=deck_choice_options(values,self.cards,3,self.rng)
            for option in options:option['index']=indexed[option['index']][0]
            if options:
                self.pending_choice=dict(owner=owner,kind='temporary_deck',options=options)
                self.phase='choice'
        elif op[0]=='follow_attach':
            cid=op[1]
            if cid not in FOLLOW_RULES:raise ValueError('Unimplemented Follow effect')
            # Full action legality, including target, capacity, cost and locks.
            playable={a.source for a in self._hand_actions(owner) if a.kind=='play'}
            candidates=[c for c in p.hand if c.uid in playable and
                        (cid!='CAP_101' or has_tribe(self.cards[c.card_id],'PIRATE'))]
            if candidates:
                c=self.rng.choice(candidates)
                c._follow_effects=getattr(c,'_follow_effects',[])+[dict(card_id=cid,end=self.turn)]
        else:return False
        return True
