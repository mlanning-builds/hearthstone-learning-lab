"""Staged Herald armies. Candidate timing is explicit; no live admission.

A Soldier snapshots the level BEFORE its Herald increments the counter. Existing
board entities retain their snapshot. These timing choices need client traces;
off-class routing and independent sequencing/pool review remain hard gates.
"""
import json
from pathlib import Path
from engine.cards import UnsupportedCard
from .generation_cards import pool, random_cards

VALUES=json.loads(Path(__file__).with_name('herald_values.json').read_text())['values']
SOLDIERS={'WARRIOR':'CATA_580t','DEMONHUNTER':'CATA_525t','SHAMAN':'CATA_565t',
          'ROGUE':'CATA_158t','DEATHKNIGHT':'CATA_780t','WARLOCK':'CATA_725t'}
ARMIES={
 'WARRIOR':('CATA_580t','CATA_150t','CATA_150t1'),
 'DEMONHUNTER':('CATA_525t','CATA_151t','CATA_151t1'),
 'SHAMAN':('CATA_565t','CATA_153t','CATA_153t1'),
 'ROGUE':('CATA_158t','CATA_154t','CATA_154t1'),
 'DEATHKNIGHT':('CATA_780t','CATA_155t','CATA_155t1'),
 'WARLOCK':('CATA_725t','CATA_726t','CATA_726t1'),
}
ARMY_OF={cid:army for army,ids in ARMIES.items() for cid in ids}
DEATHWINGS=frozenset(('CATA_190h','CORE_DRG_026','DRG_026','CS3_036','LEG_CS3_036','NEW1_030','VAN_NEW1_030','OG_317'))
LEGENDARY_DRAGONS=pool(card_type='MINION',tribe='DRAGON',rarity='LEGENDARY')
CATACLYSMS={
 'CATA_190t10':(('summon','CATA_190t14',1),),
 'CATA_190t11':(('herald_topple',),),
 'CATA_190t12':(('area_damage','enemy_minions',4),),
 'CATA_190t13':(random_cards(LEGENDARY_DRAGONS,5,destination='deck',set_cost=1),),
}
H=('herald',)
RULES={
 'CATA_497':('none',[('herald_ultraxion',)]),
 'CATA_190h':('none',[('herald_cataclysms',)]),
 'CATA_156':('none',[H,('area_damage','enemy_minions',4)]),
 'CATA_158':('none',[]),
 'CATA_160':('none',[('herald','RUSH')]),
 'CATA_492':('none',[]),
 'CATA_525':('none',[H]),
 'CATA_530':('none',[H,('herald_hero_lifesteal',)]),
 'CATA_561':('none',[H,('add','CATA_561t',2)]),
 'CATA_565':('none',[H]),
 'CATA_580':('none',[H]),
 'CATA_722':('none',[H]),
 'CATA_725':('none',[H]),
 'CATA_780':('none',[H]),
 'CATA_785':('combo_character',[H,('combo_damage',3)]),
}
LOCATION_RULES={'CATA_492':'none'}
LOCATION_EFFECTS={'CATA_492':[H,('draw',1)]}
DEATH_EFFECTS={'CATA_158':[H],'CATA_725':[('heal_own_hero',3)],
               **{cid:[('herald_death_damage',)] for cid in ARMIES['WARRIOR']}}
END_EFFECTS={cid:[('herald_consume_right',)] for cid in ARMIES['WARLOCK']}
UNRESOLVED={}

def multiplier(count):
    if type(count) is not int or count<0:raise ValueError('Invalid Herald count')
    return 1 << min(count//2,2)

def requests_for(cid):
    # Broad planning superset for sources playable in any of the six classes.
    if cid=='CATA_190h':return {LEGENDARY_DRAGONS}
    if cid in RULES:return {pool(card_type='SPELL',classes='other')}|{pool(card_type='MINION',minimum=n,maximum=n) for n in (2,4,8)}
    return set()

class Herald:
    def _herald_split(self,op,ctx):
        if op[0]!='herald_ultraxion':return None
        # Snapshot before this Battlecry's Herald; its own use is the base one.
        amount=1+self.players[ctx['owner']].herald_count
        return ('herald',),(('herald_deathwing_discount',amount),)

    def _herald_choice(self,choice,selected):
        if choice['kind']!='herald_cataclysm':return False
        picks=choice['picks']+(selected['card_id'],)
        remaining=choice['remaining']-1
        if remaining:
            self.pending_choice=dict(choice,picks=picks,remaining=remaining)
            self.phase='choice'
        else:
            # Cataclysms are Battlecry operations, not spell casts or Discover.
            operations=tuple(op for cid in picks for op in CATACLYSMS[cid])
            self._rule_events.append(('captured_effects',dict(operations=operations,
                context=dict(owner=choice['owner'],source=None,target=0,bonus=0,lifesteal=False)),[]))
        return True

    def _herald_value(self,source):
        return VALUES[source.card_id]*source.rule_state.get('herald_multiplier',1)

    def _herald_request(self,cid,level):
        army=ARMY_OF.get(cid)
        if army=='ROGUE':return pool(card_type='SPELL',classes='other')
        if army=='DEATHKNIGHT':
            cost=VALUES[cid]*level
            return pool(card_type='MINION',minimum=cost,maximum=cost)
        return None

    def _herald_entry_preflight(self,owner,cid,copy_from=None):
        if cid not in ARMY_OF:return
        level=(copy_from.rule_state.get('herald_multiplier',1) if copy_from is not None
               else multiplier(self.players[owner].herald_count))
        request=self._herald_request(cid,level)
        if request is not None:self._generation_candidates(request,owner)

    def _herald_on_summon(self,m):
        if m is None or m.card_id not in ARMY_OF or m.silenced or m.dormant:return
        army=ARMY_OF[m.card_id];value=self._herald_value(m)
        if army=='DEMONHUNTER':operations=(('hero_attack',value),)
        elif army=='ROGUE':operations=(random_cards(self._herald_request(m.card_id,m.rule_state.get('herald_multiplier',1)),cost_delta=-value),)
        elif army=='DEATHKNIGHT':operations=(random_cards(self._herald_request(m.card_id,m.rule_state.get('herald_multiplier',1)),health_payment='turn'),)
        else:return
        self._rule_events.append(('captured_effects',dict(operations=operations,
            context=dict(owner=m.owner,source=m,target=0,bonus=0,lifesteal=False)),[]))

    def _herald(self,owner,keyword=None):
        p=self.players[owner];cid=SOLDIERS.get(p.hero_class)
        if cid is None:raise UnsupportedCard('Off-class Herald army selection requires reviewed routing')
        if self.cards.get(cid,{}).get('type')!='MINION':raise UnsupportedCard('Missing Herald Soldier: '+cid)
        self._herald_entry_preflight(owner,cid)
        soldier=self._summon(owner,cid,entry_origin='herald',entry_site='herald.action')
        if soldier is not None and keyword is not None:soldier.keywords.add(keyword)
        p.herald_count+=1
        self._log('herald',player=owner,count=p.herald_count,soldier=soldier.uid if soldier else None)

    def _herald_effect(self,op,ctx):
        name=op[0];owner=ctx['owner'];p=self.players[owner];source=ctx.get('source')
        if name=='herald':self._herald(owner,op[1] if len(op)>1 else None)
        elif name=='herald_deathwing_discount':p.deathwing_discount+=op[1]
        elif name=='herald_cataclysms':
            required=set(CATACLYSMS)|{'CATA_190t14','CATA_190p'}
            if required-set(self.cards):raise UnsupportedCard('Missing Deathwing dependencies')
            self._generation_candidates(LEGENDARY_DRAGONS,owner)
            self.pending_choice=dict(owner=owner,kind='herald_cataclysm',remaining=multiplier(p.herald_count),
                picks=(),options=[dict(card_id=cid,label=self.cards[cid]['name']) for cid in CATACLYSMS])
            self.phase='choice'
        elif name=='herald_topple':
            targets=[m for m in self.players[1-owner].minions if m.health>0]
            if targets:
                health=max(m.health for m in targets)
                self.rng.choice([m for m in targets if m.health==health]).health=0
        elif name=='herald_hero_lifesteal':p.hero_lifesteal_until=self.turn
        elif name=='herald_death_damage':
            if source is None or source.card_id not in ARMIES['WARRIOR']:
                raise UnsupportedCard('Herald Deathrattle requires the source snapshot')
            targets=[self.hero_id(1-owner)]+[m.uid for m in self.players[1-owner].minions if m.health>0]
            self._deal_effect(self.rng.choice(targets),self._herald_value(source),ctx)
        elif name=='herald_consume_right':
            if source is None or source not in p.minions or source.health<=0 or source.silenced:return True
            if any(m.card_id=='CATA_726' and not m.silenced and m.health>0 for m in p.minions):
                # Candidate semantics: sample physical minion slots uniformly.
                # No board death/draw callbacks: the victim never entered play.
                # Independent targeting/empty-deck evidence still gates admission.
                deck=self.players[1-owner].deck
                choices=[i for i,value in enumerate(deck) if self._card_data(value)['type']=='MINION']
                if choices:
                    value=deck.pop(self.rng.choice(choices))
                    self._zone_card_removed(1-owner,value,'deck','destroy')
                    self._log('destroy_deck',player=1-owner,card=self._card_data(value)['id'])
                    amount=self._herald_value(source);self._buff(source,amount,amount)
                    self._refresh_auras()
                return True
            index=p.board.index(source)+1
            if index<len(p.board):
                victim=p.board[index]
                if victim in p.minions and victim.health>0:
                    victim.health=0
                    amount=self._herald_value(source);self._buff(source,amount,amount)
        else:return False
        return True
