"""On-policy episodes, read-only evaluations and resumable training."""
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import random
import time

from lab import population
from engine.cards import supported_pool
from engine.game import Game
from engine.experiment import fingerprint as engine_fingerprint, random_policy
from .policy import Policy, Adam, FEATURE_NAMES

ROOT=Path(__file__).resolve().parent.parent


def fingerprint():
    h=hashlib.sha256(engine_fingerprint().encode())
    for path in sorted((ROOT/'learner').glob('*.py')):
        h.update(path.name.encode()); h.update(path.read_bytes())
    return h.hexdigest()


def save_json(path,data):
    temp=path.with_suffix('.tmp')
    temp.write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')
    temp.replace(path)


def make_pools(seed):
    # Disjoint decks and random streams for training, monitoring, and final test.
    pools=[]; seen=set()
    for offset in (0,10000000,20000000):
        decks=population(supported_pool(),per_profile=2,seed=seed+offset)
        keys={tuple(d['cards']) for d in decks}
        if seen&keys: raise RuntimeError('Deck split overlap; choose a different seed.')
        seen|=keys; pools.append(decks)
    return pools


def episode(policy,opponent,decks,seed,first_player,learn=False):
    rng=random.Random(seed)
    pair=rng.sample(decks,2)
    game=Game([d['cards'] for d in pair],[tuple(d['runes'].values()) for d in pair],
              seed=seed,first_player=first_player,record=False)
    choices=[random.Random(seed+101),random.Random(seed+202)]
    total=[0.0]*len(FEATURE_NAMES); ent=[0.0]*len(FEATURE_NAMES); decisions=0
    while not game.terminal:
        if len(game.history)>=10000: raise RuntimeError('Game action safety limit reached.')
        viewer=game.current
        observation=game.observe(viewer,include_events=False)
        if viewer==0:
            action,gradient,entropy=policy.choose(observation,choices[0],learn=learn)
            if learn:
                for i,g in enumerate(gradient): total[i]+=g
                for i,g in enumerate(entropy): ent[i]+=g
                decisions+=1
        elif opponent is None:
            action=random_policy(observation,choices[1])
        else:
            action,_,_=opponent.choose(observation,choices[1])
        game.step(action)
    return dict(reward=game.rewards()[0],winner=game.winner,turns=game.turn,
                reason=game.end_reason,decisions=decisions,gradient=total,entropy_gradient=ent)


def score_summary(rewards):
    n=len(rewards); wins=rewards.count(1); losses=rewards.count(-1); draws=rewards.count(0)
    if not n or n%2: raise ValueError('Need complete evaluation pairs.')
    p=wins/n
    # Games within an initiative-swapped pair can be correlated. Treat each pair
    # as one bounded observation; Hoeffding bounds need no within-pair independence.
    radius=math.sqrt(math.log(40)/(2*(n//2)))
    return dict(games=n,wins=wins,losses=losses,draws=draws,win_rate=p,
                score=(wins+0.5*draws)/n,win_interval=[max(0,p-radius),min(1,p+radius)],
                interval_method='95% conservative Hoeffding bounds over independent game pairs')


def evaluate(policy,opponent,decks,games,seed,progress=None):
    if games<2 or games%2: raise ValueError('Evaluation games must be positive and even.')
    rewards=[]; turns=[]; reasons=Counter()
    for i in range(games):
        # Paired games use identical seeds/deck pairs, reversed initiative.
        result=episode(policy,opponent,decks,seed+i//2,i%2,learn=False)
        rewards.append(result['reward']); turns.append(result['turns']); reasons[result['reason']]+=1
        if progress: progress(i+1,games)
    summary=score_summary(rewards)
    summary.update(mean_turns=sum(turns)/games,turn_limit_games=reasons['turn_limit'])
    return summary


def train(total_games=1000,eval_every=250,eval_games=100,seed=42,learning_rate=0.01,
          entropy_bonus=0.01,output_dir=None,progress=None):
    for name,value in [('total_games',total_games),('eval_every',eval_every),('eval_games',eval_games)]:
        if type(value) is not int or value<2 or value%2: raise ValueError(name+' must be a positive even integer.')
    if type(seed) is not int or seed<0: raise ValueError('seed must be a nonnegative integer.')
    if not math.isfinite(learning_rate) or not 0<learning_rate<=0.1: raise ValueError('learning_rate must be in (0, 0.1].')
    if not math.isfinite(entropy_bonus) or not 0<=entropy_bonus<=1: raise ValueError('entropy_bonus must be in [0, 1].')
    # total_games is intentionally not part of identity: increase the target to continue training.
    config=dict(version=Policy.VERSION,seed=seed,eval_every=eval_every,eval_games=eval_games,
                learning_rate=learning_rate,entropy_bonus=entropy_bonus,fingerprint=fingerprint(),
                opponent_mix='random first 250; then 50% random / 50% frozen checkpoint')
    run_id=hashlib.sha256(json.dumps(config,sort_keys=True).encode()).hexdigest()[:12]
    folder=Path(output_dir or ROOT/'runs')/('training_'+run_id); folder.mkdir(parents=True,exist_ok=True)
    checkpoint=folder/'checkpoint.json'
    training_decks,monitor_decks,test_decks=make_pools(seed)
    if checkpoint.exists():
        state=json.loads(checkpoint.read_text())
        if state['config']!=config: raise ValueError('Checkpoint configuration does not match.')
        policy=Policy.restore(state['policy']); optimizer=Adam.restore(state['optimizer'])
        initial=Policy.restore(state['initial']); frozen=Policy.restore(state['frozen'])
        if state['completed']!=len(state['results']) or optimizer.steps!=state['completed']:
            raise ValueError('Incomplete checkpoint history or optimizer state.')
    else:
        policy=Policy(seed); initial=Policy(weights=policy.weights); frozen=Policy(weights=policy.weights)
        optimizer=Adam(len(FEATURE_NAMES))
        state=dict(config=config,completed=0,policy=policy.export(),initial=initial.export(),frozen=frozen.export(),
                   optimizer=optimizer.export(),baselines={'random':0.0,'checkpoint':0.0},evaluations=[],
                   results=[],final_tests={},status='ready')
        save_json(checkpoint,state)
    start=time.monotonic(); resumed=state['completed']
    def report(phase,phase_done=0,phase_total=0):
        if progress:
            progress(dict(phase=phase,completed=state['completed'],total=total_games,resumed=resumed,
                          elapsed=time.monotonic()-start,phase_done=phase_done,phase_total=phase_total,
                          evaluations=state['evaluations']))
    def commit(status):
        state.pop('error',None)
        state.update(policy=policy.export(),optimizer=optimizer.export(),frozen=frozen.export(),status=status)
        save_json(checkpoint,state)
    def monitor():
        count=state['completed']
        if any(e['trained_games']==count for e in state['evaluations']): return
        report('evaluation',0,eval_games)
        score=evaluate(policy,None,monitor_decks,eval_games,seed+30000000,
                       lambda a,b:report('evaluation',a,b))
        state['evaluations'].append(dict(trained_games=count,**score))
        commit('training')
    try:
        if not state['evaluations'] or state['completed']%eval_every==0: monitor()
        report('training')
        for index in range(state['completed'],total_games):
            # Deterministic per-episode streams make resumption independent of evaluation.
            selector=random.Random(seed+40000000+index)
            kind='random' if index<250 or selector.random()<0.5 else 'checkpoint'
            opponent=None if kind=='random' else frozen
            result=episode(policy,opponent,training_decks,seed+50000000+index,index%2,learn=True)
            advantage=result['reward']-state['baselines'][kind]
            # Fixed scaling preserves relative episode contributions; no length-based reward shaping.
            gradient=[(advantage*g+entropy_bonus*h)/20 for g,h in zip(result['gradient'],result['entropy_gradient'])]
            optimizer.update(policy,gradient,learning_rate)
            state['baselines'][kind]=0.95*state['baselines'][kind]+0.05*result['reward']
            state['results'].append(dict(game=index+1,reward=result['reward'],opponent=kind,
                                         turns=result['turns'],reason=result['reason']))
            state['completed']=index+1
            # Refresh the self-play opponent on fixed boundaries, not when the requested run ends.
            if state['completed']%250==0: frozen=Policy(weights=policy.weights)
            commit('training')
            report('training')
            if state['completed']%eval_every==0: monitor()
        monitor()
        # Independent final test: never used for updates or best-model selection.
        final_key=str(state['completed'])
        if final_key not in state['final_tests']:
            report('final_test',0,eval_games*2)
            versus_random=evaluate(policy,None,test_decks,eval_games,seed+60000000,
                                   lambda a,b:report('final_test',a,eval_games*2))
            versus_initial=evaluate(policy,initial,test_decks,eval_games,seed+70000000,
                                    lambda a,b:report('final_test',eval_games+a,eval_games*2))
            state['final_tests'][final_key]=dict(versus_random=versus_random,versus_initial=versus_initial)
        commit('complete')
        # Versioned exports preserve earlier policies when the training target is increased.
        save_json(folder/f"model_{state['completed']:06d}.json",dict(config=config,trained_games=state['completed'],policy=policy.export()))
        report('complete')
    except KeyboardInterrupt:
        # Reload the last atomic commit: an interrupted episode/update is discarded in full.
        state=json.loads(checkpoint.read_text()); state['status']='interrupted'; save_json(checkpoint,state)
        report('interrupted'); raise
    except Exception as error:
        state=json.loads(checkpoint.read_text()); state.update(status='failed',error=str(error)); save_json(checkpoint,state)
        report('failed'); raise
    return dict(directory=str(folder),state=state,policy=policy,initial=initial)
