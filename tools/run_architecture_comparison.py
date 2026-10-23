"""Jupyter-owned comparison; default is configuration checks only."""
import argparse
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

def main():
    p=argparse.ArgumentParser();p.add_argument('--train',action='store_true');args=p.parse_args()
    from hearthstone_sim.research.comparison import preflight,run
    if args.train:run(allow_training=True,emit=lambda e:print(json.dumps(e),flush=True))
    else:print(json.dumps(preflight(),indent=2))
if __name__=='__main__':main()
