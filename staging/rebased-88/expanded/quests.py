"""Explicit regular-game Quests and shared resource progress.

Progress is public and independent of optional event recording. Card rewards wait for hand space after completion. Other Quests remain unavailable until closed.
"""
from .selectors import has_tribe
from .quest_progress import advance_count

QUESTS = {'SW_031':(3,'SW_031t'),'SW_031t':(3,'SW_031t2'),'SW_031t2':(2,'SW_031t7'),'UNG_942':(8,'UNG_942t'),'ULD_291':(6,'ULD_291p'),'ULD_140':(20,'ULD_140p'),'TLC_426': (6, 'TLC_426t'), 'TLC_513': (5, 'TLC_513t'), 'TLC_446': (6, 'TLC_446t'), 'TLC_239': (3, 'TLC_239t'), 'TLC_433': (15, 'TLC_433t')}
from .historical_stormwind_questline_finish import QUESTS as STORMWIND_QUESTS
QUESTS.update(STORMWIND_QUESTS)
RULES = {cid: ('none', [('quest_start', cid)]) for cid in QUESTS}
RULES['TLC_987'] = ('quest_enemy_minion', [('quest_assistant',)])
RULES['TLC_426t'] = ('none', [('quest_murloc_reward',)])
TOKEN_IDS = {'TLC_426t', 'TLC_239t', 'TLC_433t', 'TLC_433t2'}
DEATH_EFFECTS = {'TLC_433t': [('quest_grave',)]}

class Quests:
    def _quest_opening_hand(self, owner):
        p=self.players[owner]
        size=3 if owner==self.first_player else 4
        quests=[c for c in p.deck if c.card_id=='TOY_700t14' or self._is_quest(c.card_id)]
        for card in quests[:size]:
            p.deck.remove(card)
            self._enter_hand(owner,card)
        for _ in range(size-len(p.hand)):self._draw(owner,private=True)

    def _quest_progress(self, owner, amount):
        p=self.players[owner];quest=p.quest
        if quest is None or amount<=0:return
        goal,reward=QUESTS[quest['card_id']]
        if quest['progress']==goal:
            self._quest_deliver_ready(owner)
            return
        quest['progress']=advance_count(quest['progress'],goal,amount)
        self._log('quest_progress',player=owner,card=quest['card_id'],progress=quest['progress'])
        if quest['progress']==goal:
            self._log('quest_complete',player=owner,card=quest['card_id'])
            if quest['card_id']=='TLC_426':
                p.murloc_summon_bonus+=1
                quest['progress']=0
                quest['completions']=quest.get('completions',0)+1
                self._log('quest_restarted',player=owner,card=quest['card_id'])
            else:
                self._quest_deliver_ready(owner)

    def _quest_deliver_ready(self,owner=None):
        if getattr(self,'_delivering_quest_rewards',False):return
        self._delivering_quest_rewards=True
        try:
            for side in (range(2) if owner is None else (owner,)):
                from .historical_whizbang_quests import deliver as whizbang_deliver
                whizbang_deliver(self,side)
                from .historical_stormwind_questline_finish import deliver as stormwind_deliver
                if stormwind_deliver(self,side):continue
                if self._quest_family_deliver(side):continue
                from .historical_elemental_questline import deliver as elemental_deliver
                if elemental_deliver(self,side):continue
                p=self.players[side];quest=p.quest
                if not quest or quest['card_id']=='TLC_426':continue
                spec=QUESTS.get(quest['card_id'])
                if spec and quest['card_id'] in ('ULD_140','ULD_291') and quest['progress']>=spec[0]:
                    p.quest=None
                    self._replace_primary_power(side,dict(card_id=spec[1]))
                    self._log('quest_reward_delivered',player=side,card=spec[1])
                    continue
                if not spec or quest['progress']<spec[0] or len(p.hand)>=getattr(p,'hand_capacity',10):continue
                p.quest=None
                self._add(side,spec[1])
                self._log('quest_reward_delivered',player=side,card=spec[1])
        finally:self._delivering_quest_rewards=False

    def _quest_capture_summon(self,minion):
        p=self.players[minion.owner]
        return (not minion.dormant and has_tribe(self._card_data(minion),'MURLOC')
                and bool(p.murloc_summon_bonus or (p.quest and p.quest['card_id'] in ('TLC_426','UNG_942')) or any(q['card_id']=='UNG_942' for q in getattr(p,'whizbang_quests',()))))

    def _quest_publish_summon(self,data):
        if not data.get('quest_murloc'):return
        owner=data['owner'];p=self.players[owner]
        minion=next((m for m in p.minions if m.uid==data['source']),None)
        if minion is None:return
        # The completing Murloc receives only the previous cycle's bonus.
        # Publication follows Reborn initialization and precedes forced attacks.
        if p.murloc_summon_bonus:
            self._buff(minion,p.murloc_summon_bonus,p.murloc_summon_bonus)
        if p.quest and p.quest['card_id'] in ('TLC_426','UNG_942'):self._quest_progress(owner,1)
        from .historical_whizbang_quests import progress as whizbang_progress
        whizbang_progress(self,owner,'murloc')

    def _spend_corpses(self, owner, amount):
        p=self.players[owner]
        if type(amount) is not int or amount<0 or amount>p.corpses:
            raise ValueError('Invalid Corpse payment')
        p.corpses-=amount
        p.historical_corpses_spent=getattr(p,'historical_corpses_spent',0)+amount
        if amount:
            self._log('spend_corpses',player=owner,amount=amount)
            if p.quest and p.quest['card_id']=='TLC_433':self._quest_progress(owner,amount)

    def _quest_card_played(self,owner,card,paid_cost=None):
        from .historical_stormwind_questline_finish import played as stormwind_played
        stormwind_played(self,owner,card,paid_cost)
        from .historical_eudora import played as eudora_played
        eudora_played(self,owner,card)
        self._forge_played(owner,card)
        self._quest_family_card_played(owner,card)
        if 'BATTLECRY' in self._card_data(card).get('mechanics',()):
            from .historical_whizbang_quests import progress as whizbang_progress
            whizbang_progress(self,owner,'battlecry')
        quest=self.players[owner].quest
        if quest and quest['card_id']=='ULD_291' and 'BATTLECRY' in self._card_data(card).get('mechanics',()):
            self._quest_progress(owner,1)
        if quest and quest['card_id']=='TLC_446' and self._is_temporary(card):
            self._quest_progress(owner,1)

    def _quest_check_board(self):
        if self.phase=='mulligan' or self.terminal:return
        p=self.players[self.current];quest=p.quest
        if (quest and quest['card_id']=='TLC_239' and len(p.board)==7
                and quest.get('last_turn')!=self.turn):
            quest['last_turn']=self.turn
            self._quest_progress(self.current,1)

    def _refresh_auras(self):
        self._quest_deliver_ready()
        super()._refresh_auras()
        self._quest_check_board()

    def _quest_effect(self, op, ctx):
        owner=ctx['owner'];p=self.players[owner]
        if op[0]=='quest_start':
            reason='active_quest' if p.quest is not None else 'capacity' if len(p.secrets)+self._quest_slots(owner)>=5 else None
            if reason:
                self._log('quest_fizzle',player=owner,card=op[1],reason=reason)
                return True
            p.quest=dict(card_id=op[1],progress=0,total=QUESTS[op[1]][0])
            if op[1] in STORMWIND_QUESTS:p._stormwind_draw_cards=dict(turn=self.turn,cards=[])
            self._quest_check_board()
        elif op[0]=='quest_assistant':
            if p.quests_played and ctx.get('target'):self._deal_effect(ctx['target'],3,ctx)
        elif op[0]=='quest_grave':
            self._place_location(owner,'TLC_433t2',min(ctx.get('death_position',len(p.board)),len(p.board)))
        elif op[0]=='quest_murloc_reward':
            p.murloc_summon_bonus+=1
        else:return False
        return True
