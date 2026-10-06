"""Versioned sparse baseline features from the policy-visible boundary only.

No Game object, replay header, outcome, event log or opponent hand is consumed.
This deliberately lossy baseline is not a sufficient representation for optimal
play: temporal reasoning and richer state/action interactions remain future work.
"""
import json
import math

SCHEMA = 'visible-action-features-v58'
PLAYER_FIELDS = ('kindred_twice','next_spell_bonus','counterfeit_coin','jade_size','tendril_cost','forge_sidequests','turn_time_limit','turn_time_elapsed','contraband_beasts','hand_investigations','next_heal_damage','crystal_core','extra_turns_pending','time_warp_used','ashalon_adaptations','gorishi_stacks','avatar_form','bwonsamdi_boons','broxigar_waiting','void_remaining','eternal_life','damaged_characters_turn','hamuul_active','hamuul_spells','undead_played_this_turn','full_moon','life_rewards','geddon_draw','sorry_enabled','shield_hits','reborn_history','starting_hand','set_aside_cards','imbue_count','spell_repeat_charges','end_repeat_turns','murloc_summon_bonus','ninja_returns','elusive','quest','quests_played','secondary_power','primary_power','hero_card_id','discoveries_this_turn','discoveries_total','payment_effects','hero_healed_turn','imp_upgrades','health','max_health','turns_taken','armor','mana','max_mana','mana_capacity','manastorm_effects','companion_extra','companion_upgrades','void_soul_level','herald_count','deathwing_discount','overdraw_return_active','overdraw_cache_count','hero_lifesteal','corpses','fatigue',
                 'hand_count','deck_count','power_used','hero_attacks','hero_attacks_total','skipped_turns_pending','leyline_discount','leyline_effect','leyline_repeats','hero_class',
                 'hero_attack','immune','divine_shield','frozen','locked_mana','overload_next','secret_count',
                 'hero_power_cost','weapon','board','cards_played','fire_spell_played',
                 'undead_died_since_last_turn','hero_power_uses','next_power_increase','scheduled_effects','minion_played_this_turn','minion_played_last_turn','hero_health_changed_turn','recruit_attack_bonus','recruit_health_bonus','dragons_have_rush','dragons_played_turn','minions_set_cost')
RULE_COUNTER_FIELDS = ('fel_spells_cast','friendly_attacks','last_paid_cost',
                       'spell_damage_turn','hero_damage_taken_turn','hero_damage_events_turn',
                       'minions_died_turn','overloaded_total','healing_done_turn','permanent_healing_bonus','permanent_end_damage')


def encode_decision(decision):
    """Return one feature map per legal candidate in its original order.

    Entity identifiers are resolved to visible card attributes and relative
    positions, never learned as arbitrary episode-specific numeric IDs.
    """
    view=decision['observation'];viewer=view['viewer']
    if type(viewer) is not int or viewer not in (0,1) or decision['actor']!=viewer:
        raise ValueError('Decision must belong to the observation viewer')
    actions=decision['actions']
    if actions!=view['legal_actions']:raise ValueError('Legal candidate mismatch')
    if not actions:raise ValueError('No legal candidates to encode')
    players=view['players'];entities={}
    state={'phase':view['phase'],'turn':view['turn']}
    for owner in (viewer,1-viewer):
        side='self' if owner==viewer else 'opponent';p=players[owner]
        state[side]={k:p[k] for k in PLAYER_FIELDS if k in p}
        if owner==viewer and 'cost_effects' in p:state[side]['cost_effects']=p['cost_effects']
        if owner==viewer and 'toki_tasks_remaining' in p:state[side]['toki_tasks_remaining']=p['toki_tasks_remaining']
        if owner==viewer and 'overdraw_cache' in p:state[side]['overdraw_cache']=p['overdraw_cache']
        if owner==viewer and 'companion_ids' in p:state[side]['companion_ids']=list(p['companion_ids'])
        played_counts={}
        for entry in p.get('played_history',[]):
            if not isinstance(entry,dict) or not isinstance(entry.get('card_id'),str):
                raise ValueError('Invalid visible play history')
            card_id=entry['card_id']
            if card_id!='SECRET':played_counts[card_id]=played_counts.get(card_id,0)+1
        state[side]['played_card_counts']=played_counts
        if 'next_power_cost_effects' in p:

            effects=[]
            for effect in p['next_power_cost_effects']:
                if (not isinstance(effect,dict) or effect.get('kind') not in ('set','add') or
                    type(effect.get('amount')) is not int or effect['amount']<0):
                    raise ValueError('Invalid public Hero Power cost modifier')
                effects.append({'kind':effect['kind'],'amount':effect['amount']})
            state[side]['next_power_cost_effects']=effects
        counters=p.get('rule_counters',{})
        state[side]['rule_counters']={key:counters[key] for key in RULE_COUNTER_FIELDS if key in counters}
        for history in ('discard_history','death_history','shuffle_history'):
            if history in p:state[side][history+'_count']=len(p[history])
        if 'healing_block_expiry_players' in p:
            expiry=p['healing_block_expiry_players']
            if any(type(player) is not int or player not in (0,1) for player in expiry):
                raise ValueError('Invalid healing prevention expiry player')
            state[side]['healing_blocked']=bool(expiry)
            state[side]['healing_block_until_self_turn']=viewer in expiry
            state[side]['healing_block_until_opponent_turn']=1-viewer in expiry
        entities[-1-owner]={'side':side,'zone':'hero','health':p['health'],
                            'max_health':p.get('max_health',30),'armor':p['armor'],'attack':p.get('hero_attack',0),
                            'immune':bool(p.get('immune',False)),
                            'divine_shield':bool(p.get('divine_shield',False)),
                            'healing_blocked':bool(p.get('healing_block_expiry_players',[]))}
        for zone in ('board','hand') if owner==viewer else ('board',):
            for index,entity in enumerate(p.get(zone,[])):
                entities[entity['uid']]={'side':side,'zone':zone,'slot':index,
                                          'entity':entity}
                if owner==viewer and zone=='hand':
                    entities[entity['uid']]['previous_visible_plays']=played_counts.get(entity.get('card_id'),0)
        if owner==viewer:
            state[side]['nonstarting_cards_played']=p.get('nonstarting_cards_played',0)
            state[side]['hand']=p.get('hand',[])
            state[side]['secrets']=p.get('secrets',[])
    def flatten(value,path,out):
        if isinstance(value,dict):
            for key,item in sorted(value.items()):
                if key == 'imprisoned_entity':
                    linked=entities.get(item)
                    relation={k:linked[k] for k in ('side','zone','slot') if k in linked} if linked else None
                    flatten(relation,path+[key],out)
                elif key not in ('uid','owner','colossal_parent','colossal_appendages'):
                    flatten(item,path+[key],out)
        elif isinstance(value,(list,tuple)):
            for i,item in enumerate(value):flatten(item,path+[i],out)
        elif isinstance(value,bool):out[json.dumps(path)]=float(value)
        elif isinstance(value,(int,float)):
            if not math.isfinite(value):raise ValueError('Nonfinite visible feature')
            out[json.dumps(path)]=value/(1+abs(value))
        elif isinstance(value,str):out[json.dumps(path+[value])]=1.0
        elif value is not None:raise ValueError('Unsupported visible feature')
    rows=[]
    for action in actions:
        kind=action['kind'];row={json.dumps(['kind',kind]):1.0}
        # Condition state on action kind; state-only terms cancel in softmax.
        flatten(state,['state',kind],row)
        for role in ('source','target'):
            uid=action.get(role,0)
            if uid:
                if uid not in entities:raise ValueError('Action references a nonvisible entity')
                flatten(entities[uid],[role],row)
        flatten(action.get('position',-1),['position'],row)
        choices=action.get('choices',())
        if kind=='mulligan':
            for index,uid in enumerate(choices):
                if uid not in entities:raise ValueError('Nonvisible mulligan card')
                flatten(entities[uid],['mulligan',index],row)
        elif kind=='choose':
            options=(view.get('pending_choice') or {}).get('options',[])
            for index,option in enumerate(choices):
                if type(option) is not int or not 0<=option<len(options):
                    raise ValueError('Invalid visible choice')
                flatten(options[option],['choice',index],row)
                choice=view.get('pending_choice') or {}
                if choice.get('kind')=='herald_cataclysm':
                    flatten({'remaining':choice.get('remaining'),'picks':choice.get('picks',[])},['cataclysm_context',option],row)
                if choice.get('kind')=='rewind' and 'remaining' in choice:
                    remaining=choice['remaining']
                    if type(remaining) is not int or remaining<1:raise ValueError('Invalid visible Rewind budget')
                    # Distinct Keep/Rewind weights; a state-only term cancels in softmax.
                    flatten(remaining,['rewind_budget',option],row)
        else:flatten(choices,['choices'],row)
        rows.append(row)
    return rows
