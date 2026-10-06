"""Reusable conditional, history, generation and hand/deck operations.

Explicit effect declarations select these operations; card text is never run.
"""
from copy import deepcopy
from engine.game import Card
from .pools import require_fixed_cards


class SharedBatch30:
    def _batch30_state(self,condition,owner):
        p=self.players[owner]
        if condition=='power_used':return p.power_used
        if condition=='no_minion_last_turn':return not p.minion_played_last_turn
        if condition=='no_deck_minions':return not any(self._card_data(c)['type']=='MINION' for c in p.deck)
        if condition=='no_neutral_in_deck':return not any(self._card_data(c).get('cardClass')=='NEUTRAL' for c in p.deck)
        if condition=='aura_active':
            from .gelbin import AURA_IDS
            return self._end_trigger_count(owner)>1 or any(e.get('source_card_id') in AURA_IDS|{'EDR_259'} for e in p.scheduled_effects) or any(e.get('aura_owner')==owner for e in self.players[1-owner].timed_cost_increases)
        raise ValueError('Unknown state condition: '+condition)

    def _batch30_effect(self,op,ctx):
        name=op[0];owner=ctx['owner'];p=self.players[owner];q=self.players[1-owner]
        target=ctx.get('target',0);source=ctx.get('source')
        if name=='when_state':
            if self._batch30_state(op[1],owner):self._effect(op[2],ctx)
        elif name=='shield_character':
            if target<0:self.players[-target-1].divine_shield=True
            elif target:self._find(target).keywords.add('DIVINE_SHIELD')
        elif name=='damage_history':
            n=len(p.death_history) if op[1]=='deaths' else self._own_shuffle_count(owner)
            self._deal_effect(target,op[2]+n,ctx)
        elif name=='armor_board_identity':
            self._gain_armor(owner,op[2]+sum(self.cards[m.card_id]['name']==op[1] for m in p.minions))
        elif name=='death_area_by_turn':
            self._effect(('area_damage','enemies',op[1] if self.current==owner else op[2]),ctx)
        elif name=='equalize_hand_stats':
            for c in p.hand:
                if self.cards[c.card_id]['type']=='MINION':
                    attack=self._card_stat(c,'attack',owner);health=self._card_stat(c,'health',owner);value=max(attack,health)
                    c.attack_bonus+=value-attack;c.health_bonus+=value-health
        elif name=='reset_hand_costs':
            for player in self.players:
                for c in player.hand:self._set_card_cost(c,self.cards[c.card_id]['cost'])
        elif name=='copy_deck_spells':
            copies=[]
            for value in list(p.deck):
                if self._card_data(value)['type']=='SPELL':
                    card=self._copy_card(value);copies.append(card)
            if copies:
                p.deck.extend(copies);self.rng.shuffle(p.deck)
                self._record_deck_insertion(owner,owner,len(copies),'shuffle')
        elif name=='insert_fixed':
            require_fixed_cards((op[1],),self.cards)
            cards=[Card(self._new_id(),op[1]) for _ in range(op[2])]
            if len(op)>4:
                for c in cards:self._set_card_cost(c,op[4])
            if op[3]=='bottom':p.deck[0:0]=cards
            elif op[3]=='shuffle':
                p.deck.extend(cards);self.rng.shuffle(p.deck)
                if cards:self._record_deck_insertion(owner,owner,len(cards),'shuffle')
            else:raise ValueError('Unknown insertion mode')
        elif name=='batch30_noop':
            pass
        elif name=='summon_after_target_death':
            dead=any(r.get('entity') is not None and r['entity'].uid==target
                     for player in self.players for r in player.death_records)
            if dead and not self.terminal:
                self._summon(owner,op[1],entry_origin='effect',entry_source=source,entry_site='damage_then_summon_if_dead')
        elif name=='bounce_then_summon':
            if target:
                m=self._find(target);self._bounce(m)
                if m not in p.board:
                    self._summon(owner,op[1],entry_origin='effect',entry_source=source,entry_site='bounce_then_summon')
        elif name=='health_by_relation':
            if target:
                m=self._find(target);self._buff(m,0,op[1] if m.owner==owner else -op[1])
        elif name=='copy_deaths_this_turn':
            for record in p.death_records:
                if record['turn']==self.turn:
                    card=Card(self._new_id(),record['card_id']);card.attack_bonus=op[1];card.health_bonus=op[2]
                    self._clone_hand_card(owner,card)
        elif name=='control_target':
            if target:
                m=self._find(target)
                if m.owner!=owner and source is not None and m.health<=source.health and len(p.board)<7:
                    self.players[m.owner].board.remove(m);m.owner=owner;m.summoned_turn=self.turn;m.attacks=0
                    p.board.append(m);self._refresh_auras()
        else:return False
        return True
