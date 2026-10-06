"""Replay captured operation lists inside the caller's resumable frame."""
from copy import deepcopy
from .cards import END_EFFECTS, END_EVERY_EFFECTS
from .selectors import has_tribe
from engine.game import Card

class EffectReplay:
    def _replay_split(self, op, ctx):
        name=op[0];owner=ctx['owner'];player=self.players[owner]
        if name=='replay_context':
            operations,context=op[1:]
            if not operations:return ('batch30_noop',),()
            first,tail=self._split_fixed_summon(operations[0],context)
            remaining=tuple(tail)+tuple(operations[1:])
            return ('replay_one',first,context),((('replay_context',remaining,context),) if remaining else ())
        if name=='replay_live_end':
            m=next((m for m in player.minions if m.uid==op[1] and m.health>0 and not m.silenced),None)
            if m is None:return ('batch30_noop',),()
            context=dict(owner=owner,source=m,target=0,bonus=0,lifesteal=False)
            return self._replay_split(('replay_context',deepcopy(op[2]),context),ctx)
        if name=='replay_friendly_deathrattle':
            targets=[m for m in player.minions if m.uid==ctx.get('target')]
            ops=[]
            for m in targets:
                context=dict(owner=owner,source=m,target=0,bonus=0,lifesteal=False,death_position=player.board.index(m))
                ops.append(('replay_context',deepcopy(self._death_operations(m)),context))
        elif name=='replay_dead_minions':
            records=[r for r in player.death_records if r['operations']]
            selected=self.rng.sample(records,min(op[1],len(records)))
            ops=[]
            for r in selected:
                source=deepcopy(r['entity']);source.owner=owner
                context=dict(owner=owner,source=source,target=0,bonus=0,lifesteal=False,death_position=len(player.board))
                ops.append(('replay_context',deepcopy(r['operations']),context))
        elif name=='replay_random_end':
            effects={cid:list(END_EFFECTS.get(cid,()))+list(END_EVERY_EFFECTS.get(cid,())) for cid in END_EFFECTS.keys()|END_EVERY_EFFECTS.keys()}
            effects.update(NEW1_009=[('_turn_heal_minions',)],CS2_058=[('_turn_buff_other',)])
            candidates=[m for m in player.minions if m.health>0 and not m.silenced and effects.get(m.card_id)]
            ops=[]
            if candidates:
                m=self.rng.choice(candidates)
                context=dict(owner=owner,source=m,target=0,bonus=0,lifesteal=False)
                ops=[('replay_live_end',m.uid,tuple(effects[m.card_id])) for _ in range(self._end_trigger_count(owner))]
        elif name=='sawbones_destroy':
            victims=[m for m in player.minions if m is not ctx.get('source')]
            state={'victims':victims}
            return ('sawbones_destroy_wave',state),(('sawbones_reward',state),)
        elif name=='sawbones_reward':
            count=sum(any(r['entity'].uid==m.uid for r in player.death_records) for m in op[1]['victims'])
            ops=[action for _ in range(count) for action in [('draw',1),('refresh_mana',1)]]
        else:return None
        if not ops:return ('batch30_noop',),()
        first,tail=self._split_fixed_summon(ops[0],ctx)
        return first,tuple(tail)+tuple(ops[1:])

    def _replay_effect(self,op,ctx):
        owner=ctx['owner'];player=self.players[owner]
        if op[0]=='_turn_add':
            for _ in range(op[2]):self._add(self.current,op[1])
        elif op[0]=='_turn_heal_minions':
            for m in list(player.minions):self._heal(m.uid,1,healer=owner)
        elif op[0]=='_turn_buff_other':
            candidates=[m for m in player.minions if m is not ctx.get('source')]
            if candidates:self._buff(self.rng.choice(candidates),1,0)
        elif op[0]=='replay_random_end':
            self._rule_events.append(('captured_effects',dict(operations=(op,),context=dict(ctx)),[]))
        elif op[0]=='replay_one':self._effect(op[1],op[2])
        elif op[0]=='sawbones_destroy_wave':
            for m in op[1]['victims']:
                if m in player.minions:m.health=0
        elif op[0]=='moragg_recruit':
            choices=[i for i,c in enumerate(player.deck) if has_tribe(self._card_data(c),'DEMON')]
            if choices and len(player.board)<7:
                value=player.deck.pop(self.rng.choice(choices));cid=self._card_data(value)['id']
                m=self._summon(owner,cid,attack_bonus=getattr(value,'attack_bonus',0),health_bonus=getattr(value,'health_bonus',0),entry_origin='recruit',entry_zone='deck',entry_source=value,entry_site='moragg')
                if m is not None:m.attached_death_effects.append(('death_summon','JAIL_906',1))
        elif op[0]=='gain_summoned_stats':
            m=next((m for m in player.minions if m.uid==ctx['event']['source']),None)
            if m is not None:self._buff(ctx['source'],m.attack,m.health)
        else:return False
        return True
