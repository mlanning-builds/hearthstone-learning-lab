"""Read-only fixed-position throughput probe. No games, action sampling or learning."""
import argparse
from concurrent.futures import ProcessPoolExecutor
import multiprocessing
import json
from pathlib import Path
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import torch

G=ENCODER=MODEL=None

def setup(threads,checkpoint):
    global G,ENCODER,MODEL
    torch.set_num_threads(threads)
    from hearthstone_sim.neural.runner import prepare
    from hearthstone_sim.neural.encoding import VisibleEncoder
    from hearthstone_sim.neural.model import TransformerPolicyValue
    from tools.long_training_campaign import source_payload
    from hearthstone_sim._bootstrap import activate
    activate()
    from expanded import Game,Action
    from expanded.cards import registry
    decks,_,_=prepare()
    G=Game(list(decks.values())[:2],seed=902)
    G.step(Action('mulligan'));G.step(Action('mulligan'))
    for p in G.players:
        p.hand=[];p.board=[];p.mana=p.max_mana=10
        for _ in range(5):G._summon(p.owner if hasattr(p,'owner') else G.players.index(p),'CORE_CS2_179')
    for owner in (0,1):
        for _ in range(6):G._add(owner,'CORE_CS2_029')
    from hearthstone_sim.neural import parallel
    from hearthstone_sim.neural.model import ModelConfig
    from hearthstone_sim.neural.encoding import EncoderConfig
    parallel.initialize(ModelConfig(),EncoderConfig(),source_payload(Path(checkpoint))['model'])
    torch.set_num_threads(threads)
    ENCODER=parallel._ENCODER;MODEL=parallel._LEARNER
    probe(1)

def probe(repetitions):
    checksum=0.
    start=time.perf_counter()
    with torch.inference_mode():
        for _ in range(repetitions):
            G._refresh_auras()
            view=G.observe(G.current)
            decision=dict(actor=G.current,observation=view,actions=view['legal_actions'])
            encoded=ENCODER.encode(decision)
            logits,value=MODEL([encoded]);checksum+=float(logits[0].sum()+value.sum())
    return dict(seconds=time.perf_counter()-start,checksum=checksum)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--checkpoint',required=True);parser.add_argument('--output',required=True);args=parser.parse_args()
    jobs=16;repetitions=24;rows=[]
    for workers,threads in ((1,2),(1,1),(2,1),(4,1)):
        begin=time.perf_counter()
        with ProcessPoolExecutor(max_workers=workers,mp_context=multiprocessing.get_context('spawn'),initializer=setup,initargs=(threads,args.checkpoint)) as pool:
            # Warm every process before steady-state timing. Startup is reported separately.
            warm=list(pool.map(probe,[repetitions]*workers))
            startup=time.perf_counter()-begin
            start=time.perf_counter();result=list(pool.map(probe,[repetitions]*jobs));elapsed=time.perf_counter()-start
        row=dict(workers=workers,threads_per_worker=threads,startup_seconds=startup,steady_seconds=elapsed,positions=jobs*repetitions,positions_per_second=jobs*repetitions/elapsed,checksum=sum(r['checksum'] for r in result))
        rows.append(row);print(json.dumps(row),flush=True)
    base=rows[0]['steady_seconds']
    for row in rows:row['probe_speedup']=base/row['steady_seconds']
    Path(args.output).write_text(json.dumps(dict(scope='Fixed-position observe/legal-action/encoding/frozen forward only. No completed games or optimizer steps; not end-to-end collection performance.',rows=rows),indent=2)+'\n')
if __name__=='__main__':main()
