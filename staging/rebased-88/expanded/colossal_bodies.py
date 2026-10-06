"""Staged Colossal bodies composed with shared entry and army abilities.

No registration. Pool closure and independent entry/trigger ordering remain
admission gates; a runtime declaration is not a conformance certificate.
"""
from engine.cards import UnsupportedCard
from .generation_cards import pool, random_cards
from .selectors import classes, HERO_CLASSES

FIRE=pool(card_type='SPELL',school='FIRE')
RULES={
    'CATA_150':('none',[]),
    'CATA_151':('none',[]),
    'CATA_153':('none',[('colossal_attack_cost',)]),
    'CATA_488':('none',[]),
    'CATA_154':('none',[]),
    'CATA_300':('none',[]),
    'CATA_726':('none',[]),
    **{cid:('none',[]) for cid in ('CATA_139','CATA_155','CATA_432','CATA_550')},
}
LEGS=('CATA_139t','CATA_139t2','CATA_139t3','CATA_139t4')
HEADS=dict(zip(('CATA_432t1','CATA_432t2','CATA_432t3','CATA_432t4'),('TAUNT','LIFESTEAL','ELUSIVE','DIVINE_SHIELD')))
MAGMA_PARTS=('CATA_550t',)+tuple('CATA_550t'+str(i) for i in range(2,7))
DEATH_EFFECTS={**{cid:[('colossal_remove_keyword',keyword)] for cid,keyword in HEADS.items()},
               **{cid:[('colossal_random_buff',2,0)] for cid in MAGMA_PARTS}}
END_EFFECTS={
    **{cid:[('buff_self',1,1)] for cid in LEGS},
    'CATA_150':[('colossal_friendly_deathrattles',)],
    'CATA_488':[('area_damage','other_minions',3)],
    **{cid:[('colossal_heal_damaged',3)] for cid in ('CATA_300t1','CATA_300t2','CATA_300t3')},
}
TRIGGERS={cid:('damaged_self',[random_cards(FIRE,cost_delta=-3)])
          for cid in ('CATA_488t','CATA_488t2')}

def requests_for(cid):
    if cid=='CATA_488':return {FIRE}
    if cid=='CATA_154':return {pool(card_type='SPELL',classes='other')}
    # Planning superset only. Execution uses exact, current source Attack.
    if cid=='CATA_155':return {pool(card_type='MINION')}
    if cid=='CATA_153':return {pool(card_type='MINION')}
    return set()

class ColossalBodies:
    def _onyxia_active(self,owner):
        return self.current==owner and self._active('CATA_155',owner)

    def _replace_hero_health_loss(self,owner,amount):
        if amount<=0 or not self._onyxia_active(owner):return False
        p=self.players[owner]
        # A maximum-health increase preserves damage already taken; it is not
        # healing and must not fire healing/Lifesteal callbacks.
        p.max_health+=amount;p.health+=amount;p.hero_health_changed_turn=True
        self._log('health_loss_replaced',player=owner,amount=amount,card='CATA_155')
        return True

    def _colossal_stat_checkpoint(self):
        # Track Attack/max Health, never current Health (damage/healing).
        # Observe every recipient, including silenced Legs receiving buffs.
        for p in self.players:
            for leg in p.minions:
                if leg.card_id not in LEGS:continue
                now=(leg.attack,leg.max_health)
                before=getattr(leg,'_colossal_stat_snapshot',now)
                leg._colossal_stat_snapshot=now
                attack=max(0,now[0]-before[0]);health=max(0,now[1]-before[1])
                if leg.health<=0 or not (attack or health):continue
                # Candidate named-card scope: all friendly Wickerfang bodies,
                # including standalone/copied Legs; parent IDs are not a filter.
                for body in tuple(p.minions):
                    if body.card_id=='CATA_139' and body.health>0 and not body.silenced:
                        self._buff(body,attack,health)

    def _colossal_repeats_spell(self,owner,cid,other_repeat=False):
        values=classes(self.cards[cid])
        if self.cards[cid]['type']!='SPELL' or self.players[owner].hero_class in values or not (values & HERO_CLASSES):return False
        sources=[m for m in self.players[owner].minions if m.card_id=='CATA_154' and m.health>0 and not m.silenced]
        if sources and (len(sources)>1 or other_repeat):
            raise UnsupportedCard('Sinestra repetition stacking needs reviewed semantics')
        return bool(sources)

    def _colossal_healed(self,owner,restored):
        if restored<=0:return
        sources=[m.uid for m in self.players[owner].minions
                 if m.card_id=='CATA_300' and m.health>0 and not m.silenced]
        if sources:
            self._rule_events.append(('captured_effects',dict(
                operations=tuple(('colossal_heal_attack',uid) for uid in sources),
                context=dict(owner=owner,source=None,target=0,bonus=0,lifesteal=False)),[]))

    def _colossal_body_effect(self,op,ctx):
        owner=ctx['owner'];p=self.players[owner]
        if op[0]=='colossal_remove_keyword':
            # Candidate named-card scope, not linked-parent scope. A stolen
            # head's Deathrattle follows its controller like other Deathrattles.
            for m in p.minions:
                if m.card_id=='CATA_432' and m.health>0:
                    m.keywords.discard(op[1])
                    m.temporary_keywords[:]=[e for e in m.temporary_keywords if e['keyword']!=op[1]]
            return True
        if op[0]=='colossal_random_buff':
            targets=[m for m in p.minions if m.health>0]
            if targets:self._buff(self.rng.choice(targets),op[1],op[2])
            return True
        if op[0]!='colossal_heal_damaged':return False
        targets=([self.hero_id(owner)] if 0<p.health<p.max_health else [])
        targets += [m.uid for m in p.minions if 0<m.health<m.max_health]
        if targets:self._heal(self.rng.choice(targets),op[1],healer=owner)
        return True

    def _hero_attack_limit(self,owner):
        weapon=self.players[owner].weapon
        keywords=set(self.cards[weapon['card_id']].get('mechanics',[])) if weapon else set()
        if 'MEGA_WINDFURY' in keywords:return 4
        if 'WINDFURY' in keywords:return 2
        return 2 if any(m.card_id=='CATA_151' and m.health>0 and not m.silenced
                        for m in self.players[owner].minions) else 1

    def _colossal_body_split(self,op,ctx):
        owner=ctx['owner'];p=self.players[owner]
        if op[0]=='colossal_heal_attack':
            source=next((m for m in p.minions if m.uid==op[1] and m.health>0 and not m.silenced),None)
            targets=[m.uid for m in self.players[1-owner].minions if m.health>0]
            if source is None or not targets:return ('batch30_noop',),()
            return self._force_split(('force_pair',source.uid,self.rng.choice(targets)),ctx)
        if op[0]=='colossal_attack_cost':
            source=ctx.get('source')
            if source is None:raise UnsupportedCard("Al'Akir Battlecry requires its source Attack")
            cost=max(0,source.attack)
            request=pool(card_type='MINION',minimum=cost,maximum=cost)
            # Snapshot the Cost once, before either random result or its triggers.
            return self._generation_split(random_cards(request,2,set_cost=1),ctx)
        if op[0]=='colossal_friendly_deathrattles':
            operations=tuple(('colossal_live_deathrattle',m.uid) for m in p.minions
                             if m.health>0 and self._death_operations(m))
            if not operations:return ('batch30_noop',),()
            first,tail=self._colossal_body_split(operations[0],ctx)
            return first,tuple(tail)+operations[1:]
        if op[0]=='colossal_live_deathrattle':
            m=next((m for m in p.minions if m.uid==op[1] and m.health>0),None)
            if m is None:return ('batch30_noop',),()
            context=dict(ctx,target=m.uid)
            return self._replay_split(('replay_friendly_deathrattle',),context)
        return None
