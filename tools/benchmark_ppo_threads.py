"""Bounded forward/backward timing probe. No games, training or optimizer steps."""
import argparse
import gc
import hashlib
import json
import os
from pathlib import Path
import random
import statistics
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import torch
from torch.distributions import Categorical
from hearthstone_sim.neural.model import TransformerPolicyValue
from hearthstone_sim.neural.encoding import VisibleEncoder
from hearthstone_sim.neural.ppo import PPOConfig,objective

DEFAULT_PARENT=ROOT/'runs/neural_ppo/4c5fc45ad8bf4c2a9039e868c597f229/training-000309-evaluation.pt'
PARENT_SHA='abb3d50a6c121e3d24cad5969230bdba6332fd3f8610e4cdeab7820e34b5b366'


def tensor_hash(model):
    h=hashlib.sha256()
    for k,v in sorted(model.state_dict().items()):h.update(k.encode());h.update(v.detach().cpu().contiguous().numpy().tobytes())
    return h.hexdigest()


def positions():
    """Construct static legal engine fixtures; never play complete games or sample actions."""
    from hearthstone_sim._bootstrap import activate
    activate()
    from expanded import Game,Action
    from expanded.cards import registry
    from hearthstone_sim.neural.decks import load_panel
    decks,_=load_panel();encoder=VisibleEncoder(card_definitions=registry());items=[]
    for size in (0,2,5,6):
        game=Game(list(decks.values())[:2],seed=781+size)
        game.step(Action('mulligan'));game.step(Action('mulligan'))
        game.phase='play';game.turn=12;game.current=0
        for owner,p in enumerate(game.players):
            p.hand=[];p.board=[];p.mana=p.max_mana=10
            for _ in range(size):game._summon(owner,'CORE_CS2_179')
            for _ in range(min(9,3+size)):game._add(owner,'CORE_CS2_029')
        view=game.observe(0);decision=dict(actor=0,observation=view,actions=view['legal_actions'])
        items.append(encoder.encode(decision))
    return dict(mixed=[items[i%4] for i in range(64)],crowded=[items[2+i%2] for i in range(64)])


def targets(model,batch):
    with torch.no_grad():
        logits,values=model(batch)
        old_logp=torch.stack([x.log_softmax(-1)[0] for x in logits])
    advantages=torch.linspace(-1,1,len(batch));advantages=(advantages-advantages.mean())/advantages.std(unbiased=False).clamp_min(1e-8)
    return dict(old_logp=old_logp,old_values=values.detach(),returns=torch.linspace(-1,1,len(batch)),advantages=advantages)


def compute(model,batch,target):
    """Same PPO loss/backprop/clipping computation, WITHOUT applying any gradient."""
    model.zero_grad(set_to_none=True)
    logits,values=model(batch)
    distributions=[Categorical(logits=x) for x in logits]
    logp=torch.stack([d.log_prob(torch.tensor(0)) for d in distributions]);entropy=torch.stack([d.entropy() for d in distributions])
    loss,_,_,kl=objective(logp,target['old_logp'],target['advantages'],values,target['old_values'],target['returns'],entropy,PPOConfig(learning_rate=.0001,minibatch=64))
    if not torch.isfinite(loss):raise ValueError('Nonfinite fixture loss')
    loss.backward()
    norm=torch.nn.utils.clip_grad_norm_(model.parameters(),.5,error_if_nonfinite=True)
    return float(loss.detach()),float(kl.detach()),float(norm.detach())


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);parser.add_argument('--repeats',type=int,default=3);args=parser.parse_args()
    if not 1<=args.repeats<=5:raise ValueError('Use 1–5 bounded repetitions')
    # A lower scheduling priority leaves the owner's active trainer untouched and preferred.
    os.nice(10);torch.set_num_threads(2)
    before=hashlib.sha256(DEFAULT_PARENT.read_bytes()).hexdigest()
    if before!=PARENT_SHA:raise ValueError('Saved parent identity differs')
    from tools.long_training_campaign import source_payload
    payload=source_payload(DEFAULT_PARENT);model=TransformerPolicyValue().eval();model.load_state_dict(payload['model']);del payload;gc.collect()
    weights_before=tensor_hash(model);batches=positions();fixed={name:targets(model,batch) for name,batch in batches.items()}
    settings=(1,2,4,6,8);measurements={n:{name:[] for name in batches} for n in settings};checks={};reference=None
    started=time.monotonic()
    # Each trial starts with the same weights/inputs; order alternates to expose contention noise.
    for round_index in range(args.repeats):
        order=list(settings);random.Random(741+round_index).shuffle(order)
        for threads in order:
            torch.set_num_threads(threads)
            for name,batch in batches.items():
                compute(model,batch,fixed[name]) # untimed warm-up after the thread-count change
                start=time.perf_counter();loss,kl,norm=compute(model,batch,fixed[name]);elapsed=time.perf_counter()-start
                measurements[threads][name].append(elapsed)
                if name=='mixed' and threads==2 and reference is None:
                    reference=torch.cat([p.grad.detach().flatten().clone() for p in model.parameters() if p.grad is not None])
                print(json.dumps(dict(event='probe',round=round_index+1,threads=threads,fixture=name,seconds=elapsed)),flush=True)
            if time.monotonic()-started>240:raise RuntimeError('Probe exceeded its four-minute bound; no weights changed')
    # Compare numerical gradients using the baseline thread count; do not apply them.
    torch.set_num_threads(2);compute(model,batches['mixed'],fixed['mixed'])
    reference=torch.cat([p.grad.detach().flatten().clone() for p in model.parameters() if p.grad is not None])
    for threads in settings:
        torch.set_num_threads(threads);loss,kl,norm=compute(model,batches['mixed'],fixed['mixed'])
        grad=torch.cat([p.grad.detach().flatten() for p in model.parameters() if p.grad is not None])
        checks[threads]=dict(loss=loss,kl=kl,gradient_max_abs_difference=float((grad-reference).abs().max()),gradient_relative_l2=float((grad-reference).norm()/reference.norm().clamp_min(1e-12)))
    if tensor_hash(model)!=weights_before:raise AssertionError('Probe changed model weights')
    if hashlib.sha256(DEFAULT_PARENT.read_bytes()).hexdigest()!=before:raise AssertionError('Parent file changed')
    rows=[]
    for threads in settings:
        stats={name:dict(median_seconds=statistics.median(values),min_seconds=min(values),max_seconds=max(values)) for name,values in measurements[threads].items()}
        median=sum(x['median_seconds'] for x in stats.values())/len(stats)
        rows.append(dict(threads=threads,mean_of_fixture_medians=median,fixtures=stats,numerics=checks[threads]))
    baseline=next(r['mean_of_fixture_medians'] for r in rows if r['threads']==2)
    for r in rows:r['speedup_vs_two_threads']=baseline/r['mean_of_fixture_medians']
    report=dict(scope='Static legal-position 64-decision PPO forward/loss/backward/gradient-clip probe. No complete games, action sampling, optimizer steps or weight updates. Adam step and full-rollout diagnostics are not timed.',concurrent_training=True,background_priority=True,checkpoint=str(DEFAULT_PARENT),checkpoint_sha256=before,weights_unchanged=True,checkpoint_unchanged=True,repeats=args.repeats,batch_size=64,positions={k:dict(state_tokens_min=min(len(e['state']) for e in b),state_tokens_max=max(len(e['state']) for e in b),legal_actions_min=min(len(e['actions']) for e in b),legal_actions_max=max(len(e['actions']) for e in b)) for k,b in batches.items()},rows=rows,elapsed_seconds=time.monotonic()-started)
    args.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(event='probe_complete',output=str(args.output),weights_unchanged=True)),flush=True)
if __name__=='__main__':main()
