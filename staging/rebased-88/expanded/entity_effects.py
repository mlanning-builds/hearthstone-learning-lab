"""Physical entity changes, hidden copy enchantments and source-bound cards."""
from copy import deepcopy
from engine.game import Card, Minion

RULES={
 'CATA_185':('none',[]),
 'DINO_414':('minion',[('entity_tribute',)]),
 'EDR_780':('none',[('entity_illusion',)]),
 'JAIL_502':('none',[]),
 'TLC_241':('none',[]),
 'TLC_241t':('minion',[('buff',2,2),('keyword','DIVINE_SHIELD')]),
 'EDR_895':('none',[('entity_lunar_cycle',)]),
}
TOKEN_IDS={'TLC_241t'}
DEATH_EFFECTS={'CATA_185':[('entity_replicate_killer',)]}
START_EFFECTS={'JAIL_502':('owner',[('entity_swap_hand',)])}

class EntityEffects:
    def _entity_checkpoint(self):
        changed=False
        for owner,p in enumerate(self.players):
            sources=[m for m in p.minions if m.card_id=='TLC_241' and not m.silenced and m.health>0]
            active={m.uid for m in sources}
            for card in list(p.hand):
                bound=getattr(card,'_provided_by',None)
                if bound is not None and bound not in active:
                    p.hand.remove(card);changed=True
            for source in sources:
                if len(p.hand)<10 and not any(getattr(c,'_provided_by',None)==source.uid for c in p.hand):
                    card=Card(self._new_id(),'TLC_241t');card._provided_by=source.uid
                    self._enter_hand(owner,card);changed=True
        return changed

    def _entity_damage(self,minion,source,dealt):
        if dealt<=0:return
        if getattr(minion,'_fragile_illusion',False) and not minion.silenced:
            minion.health=0
        if minion.card_id=='CATA_185' and minion.health<=0 and isinstance(source,Minion):
            minion.rule_state['killed_by_minion']=source.uid

    def _entity_choice(self,choice,selected):
        if choice['kind']!='entity_tribute':return False
        target=self._force_live(choice['target_uid']);model=self._force_live(selected['uid'])
        if target is not None and model is not None:
            if target.card_id=='EDR_529' and not target.silenced:
                self._transform(target,model.card_id)
                return True
            owner=target.owner;position=self.players[owner].board.index(target)
            self._colossal_preflight(model.card_id,owner=owner,copy_from=model)
            self._herald_entry_preflight(owner,model.card_id,model)
            self.players[owner].board.remove(target)
            result=self._create_minion(owner,model.card_id,position,copy_from=model)
            self._colossal_enter(result)
            self._refresh_auras()
            self._log('transform',entity=target.uid,replacement=result.uid,card=result.card_id)
        return True

    def _entity_split(self,op,ctx):
        if op[0]!='entity_illusion':return None
        group={}
        return ('entity_illusion_copy',group),(('entity_illusion_mark',group),)

    def _entity_effect(self,op,ctx):
        name=op[0];owner=ctx['owner'];p=self.players[owner];source=ctx.get('source')
        if name=='entity_tribute':
            options=[dict(card_id=m.card_id,uid=m.uid) for player in self.players for m in player.minions
                     if m.health>0 and m.uid!=ctx['target'] and m.uid in self._visible_targets(owner,magic=True)]
            if options:
                self.pending_choice=dict(owner=owner,kind='entity_tribute',options=options,target_uid=ctx['target'])
                self.phase='choice'
        elif name=='entity_illusion':
            group={};self._entity_effect(('entity_illusion_copy',group),ctx);self._entity_effect(('entity_illusion_mark',group),ctx)
        elif name=='entity_illusion_copy':
            if source is not None and source in p.minions:
                copy=self._summon(owner,source.card_id,p.board.index(source)+1,copy_from=source,
                                  entry_origin='effect',entry_site='entity_illusion')
                op[1]['members']=[source]+([copy] if copy is not None else [])
        elif name=='entity_illusion_mark':
            members=op[1].get('members',[])
            if members:
                for m in members:m._illusion_possible=True
                self.rng.choice(members)._fragile_illusion=True
        elif name=='entity_replicate_killer':
            killer=self._force_live(getattr(source,'rule_state',{}).get('killed_by_minion',0))
            if killer is not None:self._transform(killer,'CATA_185')
        elif name=='entity_swap_hand':
            enemy=self.players[1-owner]
            choices=[c for c in enemy.hand if self.cards[c.card_id]['type']=='MINION']
            if source is not None and source in p.minions and choices:
                card=self.rng.choice(choices);index=enemy.hand.index(card);position=p.board.index(source)
                enemy.hand.pop(index);p.board.remove(source)
                # Battlefield -> hand resets damage/enchantments. The incoming
                # held card keeps its hand buffs but does not play a Battlecry.
                returned=Card(self._new_id(),source.card_id);self._carry_origin(source,returned)
                self._enter_hand(1-owner,returned);enemy.hand.remove(returned);enemy.hand.insert(index,returned)
                self._summon(owner,card.card_id,position,card.attack_bonus,card.health_bonus,
                             entry_origin='recruit',entry_site='entity_swap_hand',entry_zone='hand',entry_source=card)
                self._refresh_auras()
        elif name=='entity_lunar_cycle':
            self._schedule_turn_effect(owner,'start',3,1,(('entity_full_moon',),),source_card_id='EDR_895')
        elif name=='entity_full_moon':
            if not p.full_moon:p.cost_effects.append(dict(selector='ALL',set_cost=1,expires=None,consume_on_play=False))
            p.full_moon=True
        else:return False
        return True
