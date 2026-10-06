"""Player-bound effects, physical deck replacement and defensive auras.

All selectors use pinned identities or actual deck contents. No global pool is
silently narrowed to the implemented subset.
"""
from engine.game import Card
from .pools import deck_choice_options

RULES={
 'CATA_307':('none',[('lasting_life',)]),
 'CATA_591':('none',[('lasting_draw',)]),
 'CORE_EDR_003':('none',[('lasting_corpse_draw',)]),
 'EDR_258':('none',[]),
 'EDR_525':('none',[]),
 'JAIL_703':('none',[]),
}
DEATH_EFFECTS={'JAIL_703':[('lasting_sorry',)]}
CHOICES={'EDR_525':[
 ('Barbed Thorn: Poisonous','none',[('lasting_weapon_poison',)]),
 ('Barbed Thorn: Deathrattle','none',[('lasting_weapon_death',)])]}
# Explicit spender identities in the frozen catalog. Falric, the corpse-gain
# minion, the spend quest and the hero-power provider do not spend themselves.
CORPSE_SPENDERS=frozenset('CATA_465 CORE_RLK_066 CORE_RLK_118 CORE_RLK_505 CORE_RLK_506 CORE_RLK_712 CORE_RLK_745 CORE_WW_374 DINO_416 EDR_811 EDR_813 EDR_815 END_005 FIR_951 JAIL_451 RLK_060 RLK_061 RLK_707 TIME_618 TLC_434 TLC_436'.split())

class LastingRules:
    def _gain_corpses(self,owner,amount):
        multipliers=sum(m.card_id=='CORE_EDR_003' and not m.silenced and m.health>0
                        for m in self.players[owner].minions)
        actual=amount*(2**multipliers)
        self.players[owner].corpses+=actual
        return actual

    def _lasting_checkpoint(self):
        for owner,p in enumerate(self.players):
            if p.life_rewards and p.health>=p.max_health and p.health>0:
                count=p.life_rewards;p.life_rewards=0
                self._rule_events.append(('captured_effects',dict(
                    operations=tuple(('damage_enemy_hero',15) for _ in range(count)),
                    context=dict(owner=owner,source=None,target=0,bonus=0,lifesteal=False)),[]))
                return True
        return False

    def _turn_card_draw(self,owner):
        p=self.players[owner]
        if not p.geddon_draw or not p.deck:return self._draw(owner)
        options=deck_choice_options(p.deck,self.cards,3,self.rng)
        self.pending_choice=dict(owner=owner,kind='lasting_deck',options=options)
        self.phase='choice'

    def _lasting_choice(self,choice,selected):
        if choice['kind']!='lasting_deck':return False
        owner=choice['owner'];p=self.players[owner]
        card=p.deck[selected['index']]
        for index in sorted((option['index'] for option in choice['options']),reverse=True):
            removed=p.deck.pop(index)
            if index!=selected['index']:
                self._log('deck_card_destroyed',player=owner,card=self._card_data(removed)['id'])
        if not isinstance(card,Card):card=Card(self._new_id(),card)
        card.cost_delta=getattr(card,'cost_delta',0)-3
        self._discovery_result=self._enter_hand(owner,card)
        self._refresh_auras()
        return True

    def _lasting_shield_hit(self,entity,owner):
        # The aura changes how many hits break a shield; granting a shield that
        # is still present doesn't refresh it. Multiple Toreths don't stack.
        state=entity.rule_state if hasattr(entity,'rule_state') else None
        hits=state.get('shield_hits',0) if state is not None else entity.shield_hits
        hits=hits+1 if self._active('EDR_258',owner) else 3
        retained=hits<3
        if state is not None:state['shield_hits']=hits if retained else 0
        else:entity.shield_hits=hits if retained else 0
        return retained

    def _lasting_effect(self,op,ctx):
        name=op[0];owner=ctx['owner'];p=self.players[owner]
        if name=='lasting_life':
            p.health=min(15,p.max_health);p.hero_health_changed_turn=True;p.life_rewards+=1
        elif name=='lasting_draw':p.geddon_draw=True
        elif name=='lasting_corpse_draw':self._draw(owner,lambda d:d['id'] in CORPSE_SPENDERS)
        elif name=='lasting_sorry':p.sorry_enabled=True
        elif name=='lasting_weapon_poison':
            if p.weapon:p.weapon['poisonous_until']=self.turn
        elif name=='lasting_weapon_death':
            if p.weapon:p.weapon.setdefault('attached_death_effects',[]).append(('area_damage','enemies',2))
        elif name=='lasting_clearing':
            m=self._find(ctx['target']);self._buff(m,0,2);m.keywords.add('TAUNT')
            self._sleep_minion(m,-1)
            self._schedule_turn_effect(owner,'end',1,1,(('lasting_awaken',m.uid),))
        elif name=='lasting_awaken':self._awaken(self._dormant_entity(op[1]))
        else:return False
        return True
