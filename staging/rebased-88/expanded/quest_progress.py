"""Pure objective tracking for regular-game Quests and Sidequests.

Events are explicit public facts supplied by engine adapters, never parsed card
text or hidden card records. The caller owns reward execution and event timing.
Compound states retain completed branches to prevent repeated reward delivery.
This module does not register cards or certify their rewards.
"""
from copy import deepcopy


def advance_count(progress,total,amount):
    if any(type(v) is not int for v in (progress,total,amount)):
        raise ValueError('Objective counts must be integers')
    if total<1 or not 0<=progress<=total or amount<0:
        raise ValueError('Invalid objective count')
    return min(total,progress+amount)


def objective(spec):
    """Create a private definition plus JSON-compatible public progress state."""
    spec=deepcopy(spec);kind=spec.get('kind')
    if kind in ('sequence','parallel'):
        children=spec.get('children')
        if not isinstance(children,list) or not children:
            raise ValueError('Compound objective requires children')
        return dict(kind=kind,children=[objective(child) for child in children],complete=False)
    if kind not in ('count','distinct','value'):
        raise ValueError('Unknown objective kind')
    if not isinstance(spec.get('event'),str) or not spec['event']:
        raise ValueError('Objective requires an explicit event')
    conditions=spec.get('where',{})
    if not isinstance(conditions,dict):raise ValueError('Invalid event conditions')
    if any(not isinstance(k,str) or type(v) not in (int,str,bool) for k,v in conditions.items()):
        raise ValueError('Conditions require public scalar facts')
    state=dict(kind=kind,event=spec['event'],where=conditions,complete=False)
    if kind=='value':
        if not isinstance(spec.get('field'),str) or type(spec.get('equals')) is not int:
            raise ValueError('Value objective requires an integer equality')
        state.update(field=spec['field'],equals=spec['equals'])
    else:
        total=spec.get('total');advance_count(0,total,0)
        state.update(total=total,progress=0)
        if kind=='distinct':
            if not isinstance(spec.get('field'),str):raise ValueError('Distinct objective requires a field')
            allowed=spec.get('allowed')
            if not isinstance(allowed,list) or not allowed or any(type(v) not in (int,str) for v in allowed):
                raise ValueError('Distinct objective requires an explicit scalar domain')
            if len(set(allowed))!=len(allowed) or total>len(allowed):raise ValueError('Invalid distinct domain')
            state.update(field=spec['field'],allowed=allowed,seen=[])
    return state


def advance_objective(state,event):
    """Return a new state and paths completed by this event, children first.

    A sequence exposes only its first incomplete child to an event. Parallel
    objectives see the same event independently. Replaying an event after an
    objective completed cannot complete it a second time. Exactly-once event
    delivery before completion is the engine adapter's responsibility.
    """
    if not isinstance(event,dict) or not isinstance(event.get('kind'),str):
        raise ValueError('Objective event requires kind')
    result=deepcopy(state);completed=[]
    def visit(node,path):
        if node['complete']:return
        kind=node['kind']
        if kind in ('sequence','parallel'):
            pending=[(i,child) for i,child in enumerate(node['children']) if not child['complete']]
            for i,child in pending[:1] if kind=='sequence' else pending:visit(child,path+(i,))
            node['complete']=all(child['complete'] for child in node['children'])
        else:
            if event['kind']!=node['event'] or any(k not in event or type(event[k]) is not type(v) or event[k]!=v for k,v in node['where'].items()):return
            if kind=='value':
                value=event.get(node['field'])
                node['complete']=type(value) is int and value==node['equals']
            elif kind=='count':
                # One event is one occurrence; amounts such as damage are
                # conditions, never silently converted into occurrence counts.
                node['progress']=advance_count(node['progress'],node['total'],1)
                node['complete']=node['progress']==node['total']
            else:
                value=event.get(node['field'])
                if type(value) not in (int,str):return
                if not any(type(v) is type(value) and v==value for v in node['allowed']):return
                if value not in node['seen']:node['seen'].append(value)
                node['progress']=len(node['seen']);node['complete']=node['progress']==node['total']
        if node['complete']:completed.append(path)
    visit(result,())
    return result,tuple(completed)
