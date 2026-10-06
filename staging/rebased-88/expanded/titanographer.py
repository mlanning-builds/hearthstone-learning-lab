"""Frozen Osk forms: explicit Titan-derived abilities, no text parsing."""
from engine.cards import UnsupportedCard
from .generation_cards import pool,discover,random_cards
FORMS=tuple('TLC_452t'+str(n) for n in (*range(1,10),*range(13,25),*range(26,36)))
RULES={'TLC_452':('none',[])}
SIX=pool(card_type='MINION',minimum=6,maximum=6)
DR=pool(card_type='MINION',mechanic='DEATHRATTLE')
TOKENS={'TTN_737t2','TTN_862t4','TTN_960t5','YOG_514'}
TOKEN_RULES={
 'TLC_452t1':('enemy_minion',[('osk_consume',)]),
 'TLC_452t2':('none',[('osk_next_spell',)]),
 'TLC_452t3':('none',[('summon','TTN_737t2',2)]),
 'TLC_452t4':('none',[discover(DR,cost_delta=-3)]),
 'TLC_452t5':('none',[('osk_discount_minions',2)]),
 'TLC_452t6':('none',[('summon','TTN_862t4',4)]),
 'TLC_452t7':('none',[('draw_until',10)]),
 'TLC_452t8':('none',[('osk_full_heal',)]),
 'TLC_452t9':('none',[('refresh_mana',99)]),
 'TLC_452t13':('character',[('damage',5)]),
 'TLC_452t14':('none',[('autocast_random',pool(card_type='SPELL',mechanic='SECRET',classes='MAGE'),1)]),
 'TLC_452t15':('none',[('opponent_next_turn_cost','ALL',1)]),
 'TLC_452t16':('none',[('set_enemies_stats',2,2)]),
 'TLC_452t17':('none',[('buff_others',2,2)]),
 'TLC_452t18':('none',[('osk_draw_twos',),('osk_draw_twos',)]),
 'TLC_452t19':('minion',[('osk_copy',)]),
 'TLC_452t20':('none',[('osk_six',)]),
 'TLC_452t21':('enemy_minion',[('osk_remove_pair',)]),
 'TLC_452t22':('none',[('buff_self',2,1),('damage_random_enemy',4)]),
 'TLC_452t23':('none',[('buff_self',1,2),('draw',1)]),
 'TLC_452t24':('none',[('buff_self',0,3),('keyword_self','ELUSIVE')]),
 'TLC_452t26':('minion',[('damage',20)]),
 'TLC_452t27':('none',[('area_damage','enemies',3),('area_heal',6)]),
 'TLC_452t28':('none',[('summon','TTN_960t5',2)]),
 'TLC_452t29':('none',[('osk_nether',)]),
 'TLC_452t30':('none',[('buff_self',0,5),('armor',5)]),
 'TLC_452t31':('none',[('buff_self',5,0),('hero_attack',5)]),
 'TLC_452t32':('none',[('buff_self',2,2),('filtered_draw',(('type','eq','WEAPON'),),1)]),
 'TLC_452t33':('none',[('fill_hand','YOG_514')]),
 'TLC_452t34':('none',[('osk_enemy_fights',)]),
 'TLC_452t35':('enemy_minion',[('osk_control',)]),
 'YOG_514':('none',[('osk_tendril',)]),
}
def requests_for(cid):
    if cid=='TLC_452':return {SIX,DR,pool(card_type='SPELL',mechanic='SECRET',classes='MAGE')}
    return set()
class Titanographer:
    def _osk_roll(self,card):
        # The full 31-form set must exist; never prune unimplemented choices.
        missing=[cid for cid in FORMS if cid not in self.cards]
        if missing:raise UnsupportedCard('Missing Osk forms: '+', '.join(missing))
        card.card_id=self.rng.choice(FORMS)
    def _osk_held_entries(self,phase):
        if phase!='end':return []
        return [dict(source=None,order=c.uid,operations=(('osk_reroll',c.uid),)) for c in self.players[self.current].hand if c.card_id in FORMS or c.card_id=='TLC_452']
    def _osk_split(self,op,ctx):
        if op[0]=='osk_tendril':
            p=self.players[ctx['owner']];cost=min(10,getattr(p,'tendril_cost',1))
            ids=self._autocast_candidates(pool(card_type='SPELL',minimum=cost,maximum=cost),ctx['owner'])
            p.tendril_cost=min(10,cost+1)
            return (('batch30_noop',),(('cast_fixed_spell',self.rng.choice(ids),'random'),)) if ids else (('batch30_noop',),())
        if op[0]=='osk_enemy_fights':
            ids=[m.uid for m in self.players[1-ctx['owner']].minions]
            return ('batch30_noop',),tuple(('osk_enemy_attack',uid) for uid in ids)
        if op[0]=='osk_enemy_attack':
            source=self._force_live(op[1]);targets=[m.uid for m in self.players[1-ctx['owner']].minions if m.uid!=op[1] and m.health>0]
            return (('batch30_noop',),(('force_pair',op[1],self.rng.choice(targets)),)) if source and targets else (('batch30_noop',),())
    def _osk_effect(self,op,ctx):
        name=op[0];owner=ctx['owner'];p=self.players[owner];q=self.players[1-owner];source=ctx.get('source');target=ctx.get('target',0)
        if name=='osk_reroll':
            card=next((c for c in p.hand if c.uid==op[1] and (c.card_id in FORMS or c.card_id=='TLC_452')),None)
            if card:self._osk_roll(card)
        elif name=='osk_consume':
            m=self._force_live(target)
            if m and m.owner!=owner:
                health=max(0,m.health);m.health=0
                if source in p.minions:self._buff(source,0,health)
                p.max_health+=health;p.health+=health
        elif name=='osk_next_spell':
            p.cost_effects.append(dict(selector='SPELL',amount=3,expires=None));p._next_spell_bonus=getattr(p,'_next_spell_bonus',0)+3
        elif name=='osk_discount_minions':
            for c in p.hand:
                if self.cards[c.card_id]['type']=='MINION':c.cost_delta=getattr(c,'cost_delta',0)-op[1]
        elif name=='osk_full_heal':self._heal(self.hero_id(owner),p.max_health,healer=owner)
        elif name=='osk_draw_twos':
            c=self._draw_filtered(owner,(('type','eq','MINION'),))
            if c:
                d=self.cards[c.card_id];c.attack_bonus=2-d['attack'];c.health_bonus=2-d['health'];self._set_card_cost(c,2)
        elif name=='osk_copy':
            m=self._force_live(target)
            if m and 'TITAN' not in self.cards[m.card_id].get('mechanics',[]):
                copy=self._summon(owner,m.card_id,copy_from=m,entry_origin='effect',entry_site='osk_copy')
                if copy:self._buff(copy,2,2)
        elif name=='osk_six':
            ids=self._generation_candidates(SIX,owner)
            if ids:
                m=self._summon(owner,self.rng.choice(ids),entry_origin='effect',entry_site='osk_six')
                if m:m.keywords.update(('TAUNT','LIFESTEAL'))
        elif name=='osk_remove_pair':
            m=self._force_live(target)
            if m and m in q.minions:q.board.remove(m)
            options=[dict(card_id=m.card_id,uid=m.uid) for m in q.minions if m.health>0]
            if options:self.pending_choice=dict(owner=owner,kind='osk_remove_second',options=options);self.phase='choice'
            self._refresh_auras()
        elif name=='osk_nether':
            for player in self.players:
                for m in player.minions:
                    if m is not source:m.health=0
        elif name=='osk_control':
            m=self._force_live(target)
            if m and m.owner!=owner and len(p.board)<7:
                self.players[m.owner].board.remove(m);m.owner=owner;p.board.append(m);m.summoned_turn=self.turn;m.attacks=0;self._refresh_auras()
        else:return False
        return True
    def _osk_choice(self,choice,selected):
        if choice['kind']!='osk_remove_second':return False
        p=self.players[1-choice['owner']];m=next((m for m in p.minions if m.uid==selected['uid']),None)
        if m:p.board.remove(m);self._refresh_auras()
        return True
