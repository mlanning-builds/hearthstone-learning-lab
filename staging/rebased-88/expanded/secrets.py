"""Explicit secret rules. Opponents receive counts, never secret identities."""
from copy import deepcopy
from engine.game import Card
from engine.cards import UnsupportedCard

SECRET_SUMMONS = {'CORE_BAR_812':'CS2_033'}

SECRETS = {
    'EX1_287':'counterspell',
    'EX1_289':'ice_barrier',
    'TIME_620': 'untimely_death',
    'JAIL_315': 'mystic_misdirection',
    'CORE_LOOT_101': 'explosive_runes',
    'CORE_BAR_812': 'oasis_ally',
    'CORE_EX1_287': 'counterspell',
    'CORE_EX1_289': 'ice_barrier',
    'CORE_EX1_610': 'explosive_trap',
    'CORE_EX1_611': 'freezing_trap',
    'CORE_GIL_577': 'rat_trap',
    'CORE_ULD_152': 'pressure_plate',
}

from .infinity import SECRETS as INFINITY_SECRETS
SECRETS.update(INFINITY_SECRETS)
SECRETS['CFM_620']='potion_polymorph'
SECRETS.update({'AV_113t1':'improved_explosive','AV_113t2':'improved_freezing','AV_113t3':'improved_snake','AV_113t7':'improved_pack','AV_113t8':'improved_cages','AV_113t9':'improved_ice'})

from .historical_secret_events import SECRETS as ADDITIONAL_SECRETS
SECRETS.update(ADDITIONAL_SECRETS)

class Secrets:
    def _trigger_secret_program(self,owner,secret,operations,context):
        from .historical_rhyssa import trigger
        return trigger(self,owner,secret,operations,context)

    def _place_secret(self,owner,cid,physical=None):
        if cid not in SECRETS:raise UnsupportedCard('Secret rule not implemented: '+cid)
        player=self.players[owner]
        from .identities import canonical_identity
        identity=canonical_identity(self.cards[cid],self.cards)
        reason=('duplicate' if any(canonical_identity(self._card_data(c),self.cards)==identity for c in player.secrets) else
                'capacity' if len(player.secrets)+self._quest_slots(owner)>=5 else None)
        if reason:
            self._log('secret_fizzle',player=owner,card=cid,reason=reason)
            return None
        card=physical if physical is not None and physical.card_id==cid else Card(self._new_id(),cid)
        card._secret_entry_order=self._new_id()
        player.secrets.append(card)
        return card

    def _reveal_secret(self, owner, secret):
        self.players[owner].secrets.remove(secret)
        from .historical_movements import record
        record(self,'destroyed')
        player=self.players[owner]
        if not hasattr(player,'historical_triggered_secrets'):player.historical_triggered_secrets=[]
        player.historical_triggered_secrets.append(Card(self._new_id(),secret.card_id))
        souls=getattr(secret,'rule_state',{}).get('historical_halkias_souls',0)
        if souls:self._rule_events.append(('captured_effects',dict(operations=(('summon','REV_829',1),)*souls,context=dict(owner=owner,source=None,target=0,bonus=0,lifesteal=False)),[]))
        if player.weapon and player.weapon['card_id']=='EX1_536':player.weapon['durability']+=1
        self._log('secret_revealed',player=owner,card=secret.card_id)
        self._queue_event('historical_secret_revealed',owner=owner,card_id=secret.card_id)

    def _secret_capture_death(self,minion,position):
        from .historical_secret_batches import blocked
        from copy import deepcopy
        if blocked(self) or minion.owner==self.current:return
        for secret in self.players[minion.owner].secrets:
            if secret.card_id=='TIME_620' and minion.played_turn>=0 and minion.played_turn==self.turn-1:
                operation=('secret_resummon',secret.uid,minion.card_id,position)
            elif secret.card_id in ('CFM_800','LOOT_204','EX1_136','FP1_020'):
                operation=('historical_secret_v2_archive_death',secret.uid,deepcopy(minion),position)
            elif secret.card_id in ('AT_002','FP1_018'):
                operation=('historical_secret_v2_death',secret.uid,deepcopy(minion),self._card_stat(minion,'cost',minion.owner))
            elif secret.card_id=='TSC_929':
                operation=('historical_secret_v3_emergency',secret.uid,deepcopy(minion),position)
            else:continue
            self._rule_events.append(('captured_effects',dict(operations=(operation,),
                context=dict(owner=minion.owner,source=None,target=0,bonus=0,lifesteal=False)),[]))

    def _secret_effect(self,op,ctx):
        if op[0]!='secret_resummon':return False
        from .historical_secret_batches import blocked
        if blocked(self):return True
        owner=ctx['owner'];player=self.players[owner]
        secret=next((c for c in player.secrets if c.uid==op[1] and c.card_id=='TIME_620'),None)
        if secret is not None and len(player.board)<7 and self.current!=owner:
            context=dict(ctx,secret_card=secret)
            self._trigger_secret_program(owner,secret,(('historical_rhyssa_resummon',op[2],op[3]),),context)
        return True

    def _secret_event(self, event, actor, *, _only_secret_uid=None, **data):
        """Resolve in play order, rechecking the trigger against the updated state."""
        from .historical_secret_batches import blocked
        if blocked(self):return False
        owner = 1-actor
        if self.current == owner:
            return False
        canceled = False
        for secret in list(self.players[owner].secrets):
            if _only_secret_uid is not None and secret.uid!=_only_secret_uid:continue
            rule = SECRETS[secret.card_id]
            p = self.players[owner]
            q = self.players[actor]
            ctx = dict(owner=owner,source=None,target=0,
                       bonus=self._spell_damage(owner,secret.card_id),lifesteal=False)
            from .historical_secret_events import event_program
            program=event_program(self,secret,event,owner,actor,data) if not canceled else None
            if program is None and not canceled:
                from .historical_secret_v3 import event_program as v3_event_program
                program=v3_event_program(self,secret,event,owner,actor,data)
            if program is not None:
                self._trigger_secret_program(owner,secret,program,ctx)
                self._settle(allow_event_choices=True)
                if secret.card_id=='EX1_594' and event=='attack':canceled=True
            elif event=='before_minion' and rule=='objection' and not canceled:
                self._trigger_secret_program(owner,secret,(),ctx)
                canceled=True
            elif event == 'before_spell' and rule == 'counterspell' and not canceled:
                self._trigger_secret_program(owner,secret,(),ctx)
                canceled = True
            elif event=='before_spell' and rule=='oh_my_yogg' and not canceled and data.get('physical_card') is not None:
                from .generation_cards import pool
                paid=data.get('paid_cost')
                cost=self._cost(data['physical_card'],actor) if paid is None else paid
                self._autocast_candidates(pool(card_type='SPELL',minimum=cost,maximum=cost),actor)
                self._trigger_secret_program(owner,secret,(('historical_secret_v2_archive_yogg_replace',actor,cost),),ctx)
                canceled=True
            elif event=='before_spell' and rule=='ice_trap' and not canceled and data.get('physical_card') is not None:
                self._trigger_secret_program(owner,secret,(('historical_secret_v2_archive_ice_return',data['physical_card'],actor),),ctx)
                canceled=True
            elif event=='before_spell' and rule=='improved_ice' and not canceled and data.get('physical_card') is not None:
                self._trigger_secret_program(owner,secret,(('historical_tavish_ice',data['physical_card'],actor),),ctx)
                canceled=True
            elif event == 'attack':
                attacker = next((m for m in q.minions if m.uid == data['source']),None)
                if canceled or (data['source']>0 and attacker is None):
                    break
                from .historical_tavish import attack_program
                tavish=attack_program(self,secret,owner,actor,data)
                if tavish is not None:
                    operations,canceled=tavish
                    self._trigger_secret_program(owner,secret,operations,ctx)
                elif rule == 'oasis_ally' and any(m.uid==data['target'] for m in p.minions) and len(p.board)<7:
                    self._trigger_secret_program(owner,secret,(('summon',SECRET_SUMMONS[secret.card_id],1),),ctx)
                elif rule == 'mystic_misdirection' and attacker:
                    self._trigger_secret_program(owner,secret,(('historical_rhyssa_transform',attacker.uid),),ctx)
                    canceled=True
                elif rule == 'freezing_trap' and attacker:
                    self._trigger_secret_program(owner,secret,(('historical_rhyssa_bounce',attacker.uid),),ctx)
                    canceled = True
                elif rule == 'ice_barrier' and data['target']==self.hero_id(owner):
                    self._trigger_secret_program(owner,secret,(('armor',8),),ctx)
                elif rule == 'explosive_trap' and data['target']==self.hero_id(owner):
                    self._trigger_secret_program(owner,secret,(('area_damage','enemies',2),),ctx)
                self._settle()
                if self.terminal or (attacker and attacker not in q.board):
                    canceled = True
            elif event=='after_card' and rule=='potion_polymorph':
                minion=next((m for m in q.minions if m.uid==data.get('source') and m.health>0 and not m.dormant),None)
                if minion is not None:
                    self._trigger_secret_program(owner,secret,(('historical_rhyssa_transform',minion.uid),),ctx)
                    self._settle()
            elif event=='after_card' and rule=='explosive_runes':
                minion=next((m for m in q.minions if m.uid==data.get('source') and m.health>0 and not m.dormant),None)
                if minion is not None:
                    self._trigger_secret_program(owner,secret,(('historical_rhyssa_runes',minion.uid),),ctx)
                    self._settle()
            elif event=='after_spell' and rule=='pressure_plate' and q.minions:
                self._trigger_secret_program(owner,secret,(('historical_rhyssa_pressure',),),ctx)
                self._settle()
            elif event=='after_card' and rule=='rat_trap' and q.cards_played==3 and len(p.board)<7:
                self._trigger_secret_program(owner,secret,(('summon','GIL_577t',1),),ctx)
            if self.terminal:
                break
        return canceled

from .historical_secret_v3 import SECRETS as V3_SECRETS
SECRETS.update(V3_SECRETS)

SECRETS.update({'EX1_610': 'explosive_trap', 'VAN_EX1_610': 'explosive_trap', 'EX1_611': 'freezing_trap', 'VAN_EX1_611': 'freezing_trap'})
