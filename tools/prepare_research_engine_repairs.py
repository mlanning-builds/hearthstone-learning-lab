"""Offline, allowlisted repair of the unstarted research study's engine binding."""
import copy
import json
import os
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from hearthstone_sim.research.comparison import OUTPUT,CONFIG,code_hash
from hearthstone_sim.neural.runner import prepare
from hearthstone_sim.neural.checkpoints import digest
OLD_ENGINE='7ff7d54270d01b72c4317f931b3ec5cc7126d783eb702348c6728240331844df'
NEW_ENGINE='6375d2791cba908d5ce8fd134629997807a6841499f1244e96852e4a612b1fc8'
PARENT_SHA='abb3d50a6c121e3d24cad5969230bdba6332fd3f8610e4cdeab7820e34b5b366'


def main():
    path=OUTPUT/'study.json';old=json.loads(path.read_text())
    if list(OUTPUT.glob('*/checkpoint-*.pt')) or list(OUTPUT.glob('round-*.json')):
        raise ValueError('Research has started; create a new reviewed study instead of rewriting results')
    current=prepare(ROOT/old['config']['panel'])[2]
    if current['engine']!=NEW_ENGINE:raise ValueError('Unexpected repaired engine')
    expected=copy.deepcopy(current);expected['engine']=OLD_ENGINE
    fingerprint=dict(simulator=expected,research=code_hash(),config=digest(CONFIG))
    if old['fingerprint']!=fingerprint:raise ValueError('Unexpected original research configuration/source')
    opponent=Path(old['opponent']['path'])
    if old['opponent']['global_game']!=2920 or old['opponent']['sha256']!=PARENT_SHA or digest(opponent)!=PARENT_SHA:
        raise ValueError('2920-game opponent identity changed')
    new=copy.deepcopy(old);new['fingerprint']['simulator']=current
    archive=OUTPUT/'pre-repair-study.json'
    with archive.open('x') as f:json.dump(old,f,indent=2)
    temporary=OUTPUT/'study-repair.partial'
    with temporary.open('x') as f:
        json.dump(new,f,indent=2);f.flush();os.fsync(f.fileno())
    os.replace(temporary,path)
    receipt=dict(kind='owner-authorized-unstarted-research-engine-repair',old_engine=OLD_ENGINE,new_engine=NEW_ENGINE,
        fixes=['Optional cost_delta initialization in Dragon/zone/extreme discounts','Live generated Deathrattle captures board position'],
        opponent_unchanged=old['opponent']==new['opponent'],opponent_sha256=digest(opponent),
        research_games_started=False,training_started=False,original_manifest=str(archive))
    with (OUTPUT/'engine-repair.json').open('x') as f:json.dump(receipt,f,indent=2)
    print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
