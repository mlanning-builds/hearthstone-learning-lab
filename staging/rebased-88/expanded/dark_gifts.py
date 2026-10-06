"""Ten Constructed Dark Gifts and physical deck-Discover/consumer cards.

Pinned EDR_100* data; excludes unused Nightmare Scales and Battlegrounds gifts.
Eligibility follows the Constructed update in Blizzard's 32.2 patch notes:
https://news.blizzard.com/en-gb/article/24198086/32-2-patch-notes
"""
from copy import deepcopy
from itertools import product
from engine.game import Card
from engine.cards import UnsupportedCard

# attack, health, cost change, keywords
GIFTS={
 'EDR_100t':(3,0,0,('LIFESTEAL',)),
 'EDR_100t1':(2,2,0,('ELUSIVE',)),
 'EDR_100t2':(-2,0,-2,()),
 'EDR_100t3':(0,4,0,('TAUNT',)),
 'EDR_100t5':(0,0,0,()),
 'EDR_100t6':(0,0,0,('CHARGE',)),
 'EDR_100t7':(0,0,0,()),
 'EDR_100t8':(4,5,0,()),
 'EDR_100t9':(0,0,0,('REBORN',)),
 'EDR_100t13':(0,0,0,('DIVINE_SHIELD','WINDFURY')),
}
# Archive-only alternatives EDR_100t4 and EDR_100t10 are not in this pool.
RULES={
 'EDR_487':('none',[]),
 'EDR_654':('none',[('dark_discount',2)]),
 'EDR_856':('none',[('dark_deck_discover','own',True)]),
 'EDR_528':('none',[('dark_deck_discover','opponent','combo')]),
 'FIR_901':('none',[('dark_if_holding',(('summon','FIR_901t',2),))]),
 'FIR_922':('none',[('dark_if_holding',(('weapon_buff',3,0),))]),
 'FIR_956':('none',[('dark_if_holding',(('hero_attack',3),('armor',6)))]),
}
TOKEN_IDS={'FIR_901t'}

class DarkGifts:
    def _dark_list(self,card):return list(getattr(card,'rule_state',{}).get('dark_gifts',[]))
    def _dark_keywords(self,card):return {key for gift in self._dark_list(card) for key in GIFTS[gift][3]}
    def _dark_eligible(self,card):
        keys=self._card_mechanics(card);attack=self._card_stat(card,'attack')
        return [gift for gift,(_,_,_,keywords) in GIFTS.items()
                if not keys.intersection(keywords)
                and (gift!='EDR_100t6' or attack>0)
                and (gift!='EDR_100t2' or attack>=3)
                and (gift!='EDR_100t7' or 'BATTLECRY' in keys)]
    def _dark_assign(self,cards):
        combinations=[gifts for gifts in product(*(self._dark_eligible(c) for c in cards)) if len(set(gifts))==len(gifts)]
        if not combinations:raise UnsupportedCard('No distinct eligible Dark Gift assignment')
        return self.rng.choice(combinations)
    def _dark_attach(self,owner,card,gift,*,notify=True):
        if gift not in GIFTS:raise UnsupportedCard('Unknown Constructed Dark Gift')
        if self._card_data(card)['type']!='MINION':raise UnsupportedCard('Dark Gift requires a minion')
        a,h,c,_=GIFTS[gift]
        card.attack_bonus+=a;card.health_bonus+=h;card.cost_delta=getattr(card,'cost_delta',0)+c
        self._b60_state(card).setdefault('dark_gifts',[]).append(gift)
        player=self.players[owner]
        if gift=='EDR_100t8' and any(card is held for held in player.hand):
            player.hand.remove(card)
            # Sweet Dreams returns to deck; Wallow keeps all Dark Gifts only.
            keep=self._dark_list(card) if card.card_id=='EDR_487' else [gift]
            clean=Card(card.uid,card.card_id);self._carry_origin(card,clean)
            for effect in keep:self._dark_attach(owner,clean,effect,notify=False)
            player.deck.append(clean);card=clean
        elif gift=='EDR_100t8' and any(card is value for value in player.deck):
            player.deck.remove(card);player.deck.append(card)
        if notify:
            wallows=[]
            for zone in (player.hand,player.deck):
                for i,value in enumerate(zone):
                    if self._card_data(value)['id']=='EDR_487' and value is not card:
                        if not isinstance(value,Card):value=Card(self._new_id(),value);zone[i]=value
                        wallows.append(value)
            for wallow in wallows:self._dark_attach(owner,wallow,gift,notify=False)
        return card
    def _dark_entry(self,minion,card):
        gifts=self._dark_list(card)
        if gifts:
            minion.rule_state['dark_gifts']=gifts
            minion.keywords.update(self._dark_keywords(card))
    def _dark_play_operations(self,operations,card,source):
        gifts=self._dark_list(card)
        operations=list(operations)
        if 'EDR_100t7' in gifts and 'BATTLECRY' in self._card_mechanics(card):operations=operations*2
        operations.extend(('dark_play_copy',source.uid) for gift in gifts if gift=='EDR_100t5' and source is not None)
        return operations
    def _dark_split(self,op,ctx):
        if op[0]!='dark_if_holding':return None
        ops=op[1] if any(self._dark_list(c) for c in self.players[ctx['owner']].hand if self._card_data(c)['type']=='MINION') else ()
        if not ops:return ('batch30_noop',),()
        first,tail=self._split_fixed_summon(ops[0],ctx)
        return first,tuple(tail)+tuple(ops[1:])
    def _dark_effect(self,op,ctx):
        name=op[0];owner=ctx['owner'];player=self.players[owner]
        if name=='dark_discount':
            for c in player.hand:
                if self._dark_list(c) and self._card_data(c)['type']=='MINION':c.cost_delta=getattr(c,'cost_delta',0)-op[1]
        elif name=='dark_deck_discover':
            recipient=owner if op[1]=='own' else 1-owner
            representatives={}
            for index,value in enumerate(self.players[recipient].deck):
                if self._card_data(value)['type']=='MINION':representatives.setdefault(self._card_data(value)['id'],index)
            ids=self.rng.sample(list(representatives),min(3,len(representatives)))
            if ids:
                cards=[self.players[recipient].deck[representatives[cid]] for cid in ids]
                gifted=op[2] is True or op[2]=='combo' and ctx.get('combo')
                gifts=self._dark_assign(cards) if gifted else [None]*len(cards)
                self.pending_choice=dict(owner=owner,kind='dark_deck',deck_owner=recipient,copy=op[1]!='own',
                    options=[dict(card_id=cid,index=representatives[cid],dark_gift=gift) for cid,gift in zip(ids,gifts)])
                self.phase='choice'
        elif name=='dark_play_copy':
            source=self._force_live(op[1])
            if source is not None:
                copy=self._summon(owner,source.card_id,copy_from=source,entry_origin='copy',entry_site='dark_gift')
                if copy is not None:
                    self._set_minion_attack(copy,2+copy.aura_attack);copy.health=copy.max_health=2+copy.aura_health
        else:return False
        return True
    def _dark_choice(self,choice,selected):
        if choice['kind']!='dark_deck':return False
        owner=choice['owner'];deck=self.players[choice['deck_owner']].deck
        value=deck[selected['index']]
        if self._card_data(value)['id']!=selected['card_id']:raise UnsupportedCard('Dark Gift selected deck position changed')
        if choice['copy']:card=self._copy_card(value,source_owner=choice['deck_owner'])
        else:
            value=deck.pop(selected['index']);card=value if isinstance(value,Card) else Card(self._new_id(),value)
        result=self._enter_hand(owner,card)
        if result is not None and selected['dark_gift']:result=self._dark_attach(owner,result,selected['dark_gift'])
        self._discovery_result=result;self._refresh_auras()
        return True
