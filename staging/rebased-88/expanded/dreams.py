"""Closed Dream pools and physical held-card upgrade state.

Regular constructed cards only. Membership is explicit, not a global supported
subset. Delayed destruction is an enchantment that follows the board entity.
"""
from engine.game import Card
from .pools import GenerationPool, require_fixed_cards

DREAMS=('DREAM_01','DREAM_02','DREAM_03','DREAM_04','DREAM_05')
CORRUPTED=tuple('EDR_846t'+str(n) for n in range(1,6))
DREAM_POOL=GenerationPool('Five Dream cards',DREAMS,
    'Pinned Dream token family; Shaladrassil and Hopeful Dryad explicit rewards')
YSERAS=frozenset({'EX1_572','CORE_EX1_572','VAN_EX1_572','CS3_033','CORE_CS3_033','DRG_320','EDR_000'})
RULES={
    'EDR_001':('none',[('dream_random',)]),
    'EDR_846':('none',[('dream_all',)]),
}
TOKEN_RULES={
    'DREAM_02':('none',[('dream_awaken',False)]),
    'DREAM_04':('minion',[('dream_bounce',)]),
    'DREAM_05':('minion',[('dream_nightmare',)]),
    'EDR_846t1':('minion',[('buff',5,5),('temporary_keyword_target','IMMUNE','end')]),
    'EDR_846t2':('minion',[('dream_shuffle',)]),
    'EDR_846t4':('none',[('dream_destroy_yseras',),('area_damage','enemies',5)]),
}
TOKEN_IDS=set(DREAMS+CORRUPTED)

class Dreams:
    def _hero_elusive(self,owner):return self._active('EDR_846t3',owner)

    def _dream_higher_play(self,owner,played,cost):
        # Called after shared one-use discounts are consumed, but before the
        # card effect can discount Shaladrassil or draw another copy.
        for card in self.players[owner].hand:
            if card is not played and card.card_id=='EDR_846' and cost>self._cost(card,owner):
                self._b60_state(card)['dream_corrupted']=True

    def _dream_turn_entries(self,phase):
        if phase!='start':return []
        owner=self.current;now=self.players[owner].turns_taken;entries=[]
        for player in self.players:
            for m in player.minions:
                for timer in m.rule_state.get('dream_nightmares',[]):
                    if timer['owner']==owner and timer['due']<=now:
                        entries.append(dict(source=None,order=m.uid,
                            operations=(('dream_expire',m.uid,owner,timer['due']),)))
        return entries

    def _dream_split(self,op,ctx):
        if op[0]!='dream_all':return None
        corrupted=self._b60_state(ctx.get('physical_card')).get('dream_corrupted',False) if ctx.get('physical_card') is not None else False
        pool=CORRUPTED if corrupted else DREAMS
        require_fixed_cards(pool,self.cards)
        ordered=list(pool);self.rng.shuffle(ordered)
        ops=tuple(('add',cid,1) for cid in ordered)
        return ops[0],ops[1:]

    def _dream_effect(self,op,ctx):
        name=op[0];owner=ctx['owner'];target=ctx.get('target',0)
        if name=='dream_random':
            pool=DREAM_POOL.resolve(self.cards,self.cards)
            self._add(owner,self.rng.choice(pool))
        elif name=='dream_all':
            first,rest=self._dream_split(op,ctx)
            for effect in (first,)+rest:self._effect(effect,ctx)
        elif name=='dream_bounce':
            if target:self._bounce(self._find(target))
        elif name=='dream_shuffle':
            if target:
                m=self._find(target);p=self.players[m.owner]
                p.board.remove(m)
                card=Card(self._new_id(),m.card_id);self._carry_origin(m,card)
                p.deck.append(card);self.rng.shuffle(p.deck)
                self._record_deck_insertion(m.owner,owner,1,'shuffle')
                self._refresh_auras()
        elif name=='dream_nightmare':
            if target:
                m=self._find(target);self._buff(m,5,5)
                m.rule_state.setdefault('dream_nightmares',[]).append(
                    dict(owner=owner,due=self.players[owner].turns_taken+1))
        elif name=='dream_expire':
            uid,caster,due=op[1:]
            m=next((m for p in self.players for m in p.minions if m.uid==uid),None)
            if m and dict(owner=caster,due=due) in m.rule_state.get('dream_nightmares',[]):m.health=0
        elif name=='dream_awaken':
            targets=[self.hero_id(i) for i in (0,1)]+[m.uid for p in self.players for m in p.minions if m.card_id not in YSERAS]
            with self._damage_batch():
                for uid in targets:self._deal_effect(uid,5,ctx)
        elif name=='dream_destroy_yseras':
            for p in self.players:
                for m in p.minions:
                    if m.card_id in YSERAS:m.health=0
        else:return False
        return True
