"""Persistent Imbue progress and patch-pinned class power identities.

Power bodies and card consumers are connected separately; this module does not
claim the Imbue family is playable. Unsupported power bodies fail explicitly.
"""
import json
from pathlib import Path
from engine.cards import UnsupportedCard
from .selectors import has_tribe
from .generation_cards import pool, random_cards
from engine.game import Card

PINNED_VALUES=json.loads(Path(__file__).with_name('imbue_values.json').read_text())['cards']

IMBUE_POWERS={
    'DEATHKNIGHT':'END_003p', 'DRUID':'EDR_847p', 'HUNTER':'EDR_850p',
    'MAGE':'EDR_851p', 'PALADIN':'EDR_445p', 'PRIEST':'EDR_449p',
    'ROGUE':'END_000p', 'SHAMAN':'EDR_448p',
}
GOLEMS=('EDR_847pt2','EDR_847pt3','EDR_847pt4')
TOKEN_IDS=set(IMBUE_POWERS.values())|set(GOLEMS)
PLAYABLE_TOKENS=set(GOLEMS)

class Imbue:
    def _imbue(self,owner,amount=1):
        if owner not in (0,1) or type(amount) is not int or amount<1:
            raise ValueError('Invalid Imbue owner/count')
        player=self.players[owner]
        # Even a class without an Imbued power records progress for payoffs.
        player.imbue_count+=amount
        cid=IMBUE_POWERS.get(player.hero_class)
        if cid is not None:
            if player.primary_power and player.primary_power['card_id']==cid:
                player.primary_power['imbue_level']=player.imbue_count
            else:
                used=player.power_used
                self._replace_primary_power(owner,dict(card_id=cid,imbue_level=player.imbue_count))
                # Imbue is not a refresh operation. First-replacement timing is
                # kept as a documented assumption pending pinned-client traces.
                player.power_used=used
        self._log('imbue',player=owner,count=player.imbue_count,power=cid)

    def _imbue_power_operations(self,owner):
        p=self.players[owner];power=p.primary_power
        if not power or power['card_id'] not in IMBUE_POWERS.values():
            raise UnsupportedCard('No Imbued Hero Power')
        cid=power['card_id'];level=power['imbue_level']
        amount=int(PINNED_VALUES[cid]['TAG_SCRIPT_DATA_NUM_1'])+level-1
        if cid=='EDR_445p':return (('on_draw_shuffle','EDR_445pt3',2,0),)
        if cid=='EDR_449p':return (('imbue_priest_choose',amount),)
        if cid=='END_000p':return (random_cards(pool(card_type='MINION',classes='other'),cost_delta=-amount),)
        if cid=='EDR_847p':
            token=GOLEMS[0 if amount<5 else 1 if amount<10 else 2]
            return (('power_summon',token,1,amount-1,amount-1),)
        if cid=='EDR_448p':return (('imbue_evolve',amount),)
        if cid=='EDR_850p':return (('imbue_beast_buff',amount),)
        if cid=='EDR_851p':
            return (('power_summon','EDR_851t',min(amount,max(0,7-len(p.board))),0,0),
                    ('missiles','enemies',amount))
        raise UnsupportedCard('Imbued Hero Power body not connected: '+cid)

    def _imbue_split(self,op,ctx):
        if op[0]!='power_summon':return None
        cid,count,attack,health=op[1:]
        if count<=0:return ('batch30_noop',),()
        tail=(('power_summon',cid,count-1,attack,health),) if count>1 else ()
        return ('power_summon_one',cid,attack,health),tail

    def _imbue_effect(self,op,ctx):
        owner=ctx['owner'];p=self.players[owner]
        if op[0]=='imbue':self._imbue(owner,op[1] if len(op)>1 else 1)
        elif op[0]=='power_summon_one':
            self._summon(owner,op[1],attack_bonus=op[2],health_bonus=op[3],
                         entry_origin='hero_power',entry_site='imbued_power')
        elif op[0]=='imbue_portal':
            cost=p.imbue_count
            candidates=self._generation_candidates(pool(card_type='MINION',tribe='DRAGON',minimum=cost,maximum=cost),owner)
            if candidates:self._generation_place(self.rng.choice(candidates),'board',(),ctx)
        elif op[0]=='imbue_priest_choose':
            # Validate BOTH complete pools before sampling either. Eligibility
            # uses remaining mana after payment and the generated discount.
            groups=[self._generation_candidates(pool(card_type=kind,classes='PRIEST'),owner)
                    for kind in ('MINION','SPELL')]
            eligible=[]
            for candidates in groups:
                group=[]
                for cid in candidates:
                    probe=Card(0,cid);probe.cost_delta=-op[1]
                    if self._cost(probe,owner)<=p.mana:group.append(cid)
                eligible.append(group)
            options=[dict(card_id=self.rng.choice(group)) for group in eligible if group]
            if options:
                if self.pending_choice is not None:raise UnsupportedCard('Imbue cannot overwrite a choice')
                self.pending_choice=dict(owner=owner,kind='imbue_priest',discount=op[1],options=options)
                self.phase='choice'
        elif op[0]=='imbue_evolve':
            target=next((m for m in p.minions if m.uid==ctx.get('target') and m.health>0 and not m.dormant),None)
            if target is None:return True
            cost=self.cards[target.card_id].get('cost',0)+op[1]
            request=pool(card_type='MINION',minimum=cost,maximum=cost)
            candidates=self._generation_candidates(request,owner)
            if candidates:self._transform(target,self.rng.choice(candidates))
        elif op[0]=='imbue_beast_buff':
            choices=[c for c in p.hand if self.cards[c.card_id]['type']=='MINION' and has_tribe(self.cards[c.card_id],'BEAST')]
            if choices:
                card=self.rng.choice(choices);card.attack_bonus+=op[1]
                card.cost_delta=getattr(card,'cost_delta',0)-op[1]
                self._refresh_auras()
        else:return False
        return True

    def _imbue_choice(self,choice,selected):
        if choice['kind']!='imbue_priest':return False
        self._generation_place(selected['card_id'],'hand',
            (('cost_delta',-choice['discount']),('temporary',True)),dict(owner=choice['owner']))
        return True
