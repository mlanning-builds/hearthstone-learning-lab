"""Offline allowlisted continuation preparation; never starts learning or games."""
import copy
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from hearthstone_sim.neural.checkpoints import load,save,digest
from hearthstone_sim.neural.runner import prepare
from hearthstone_sim.neural.ppo import PPOConfig
from dataclasses import asdict
from tools.migrate_400_game_checkpoint import equal
PARENT=ROOT/'runs/neural_ppo/0d3dd5ca163b4bb88900da6965095d3d/training-000301-evaluation.pt'
PARENT_SHA='39b8ae2dfbfa9652d0e07658e1d9c56536f5e36ba07afb2d9620b0a58f60ec78'
OLD_ENGINE='86e0a823dc7a474078b1ab423e05f182e5ca24b4b297d03766f3f8a1529e3db2'
OLD_CODE='1a0f07a7fa2c75ddbd73aaaefb0d7185d01318af521454ae81a56a7b3e6cb4c8'
NEW_ENGINE='8a920dccfee769121ccd3e2a9672008085ae02248a769c12aadb6518df28b105'
NEW_CODE='5ce0329b628eb6869825ee659caa58330303d8fd97c36a5a16067a5764fe444c'
UNCHANGED={'encoding.py':'847e1aac749c13d81b3bd1e913625b86220e079c53ca8af2828b6dec9b221908','model.py':'d3220c0709d728a3b1e65d7a3a20b3c7cfa4b51ff7f07848b55193f73819ae7d'}
DEST=ROOT/'runs/neural_migrations/improved-learning-from-2408'


def main():
    current=prepare()[2]
    if (current['engine'],current['neural_code'])!=(NEW_ENGINE,NEW_CODE):raise ValueError('Unapproved repaired source')
    for name,h in UNCHANGED.items():
        if digest(ROOT/'hearthstone_sim/neural'/name)!=h:raise ValueError('Architecture/encoder changed')
    old=dict(current,engine=OLD_ENGINE,neural_code=OLD_CODE)
    previous=load(PARENT,old,PARENT_SHA)
    if (previous['iteration'],previous['global_game'],previous['stopped'])!=(301,2408,False):raise ValueError('Unexpected parent position')
    descs=previous['league']+list(previous['evaluation_anchors'].values())
    originals={d['name']:load(PARENT.parent/d['name'],old,d['sha256']) for d in descs}
    earlier=ROOT/'runs/neural_ppo/d1d5463d1b554ee0880268b7f0551d75/training-000051-evaluation.pt'
    earlier_compat=dict(current,engine='245c5073fdcfd14eb82e68f1185720522e15984848a4a5622b386e0183b329c5',neural_code='ed5adc4952a2886f5331c55a38bbd31e7352fe91e7344a1f1a2570814ad7fb59')
    trial=load(earlier,earlier_compat,'5f7d68c900ca4dc4b0f05cd056833fb4a9a5b5d63e564dbdc25e72dcfb2be8ac')
    DEST.mkdir(parents=True,exist_ok=False)
    lineage=dict(kind='owner-authorized-learning-settings-migration',parent=str(PARENT),parent_sha256=PARENT_SHA,
        old_compatibility=old,compatibility=current,original_completed_games=2408,
        changes=['Departed healing target fizzles','Heuristic 50%, current 25%, archived 25%',
                 '64-game rollouts; 64-decision minibatches; learning rate 0.0001',
                 '128 supervised warm-up steps on 24 scripted lessons; owner start only',
                 'Complete-rollout diagnostics; 128-case evaluation with named anchors'],
        training_started=False,evaluation_started=False)
    mapped={}
    for name,payload in originals.items():
        cp=save(DEST/name,dict(payload,compatibility=current,migration=lineage))
        assert equal(payload['model'],load(cp['path'],current)['model'])
        mapped[name]=dict(name=name,sha256=cp['sha256'])
    def anchor(name,weights):
        cp=save(DEST/(name+'.pt'),dict(schema=previous['schema'],kind='opponent',compatibility=current,model=weights,migration=lineage))
        assert equal(weights,load(cp['path'],current)['model'])
        return dict(name=Path(cp['path']).name,sha256=cp['sha256'])
    anchors={'initial-neural':mapped[previous['evaluation_anchors']['initial-neural']['name']],
             '400-game':anchor('evaluation-400-game',trial['model']),
             'pre-change-2408':anchor('evaluation-pre-change-2408',previous['model'])}
    result=copy.deepcopy(previous);result.update(compatibility=current,migration=lineage,
        evaluation_history=[],evaluation_anchors=anchors,tactical_state=dict(completed=0))
    result['league']=[mapped[d['name']] for d in previous['league']]
    settings=result['settings'];settings.update(games_per_iteration=64,ppo=asdict(PPOConfig(learning_rate=0.0001,minibatch=64)),
        heuristic_fraction=0.5,tactical_steps=128,checkpoint_every_iterations=1,
        evaluation=dict(every_iterations=8,games_per_opponent=128,seed=1000010000),
        evaluation_at=[512],trace_first=6,trace_every=4)
    for group in result['optimizer']['param_groups']:group['lr']=0.0001
    lineage['retired_verified_heal_signature']=result['safety']['signatures'].pop('ValueError:_find',0)
    if lineage['retired_verified_heal_signature']!=1:raise ValueError('Unexpected failure history')
    cp=save(DEST/'training-000301-improved.pt',result)
    restored=load(cp['path'],current,cp['sha256'])
    for field in ('model','action_rng','shuffle_rng','league_rng','iteration','global_game','evaluation_safety','updates_since_snapshot'):
        assert equal(previous[field],restored[field]),field
    assert equal(previous['optimizer']['state'],restored['optimizer']['state'])
    expected=copy.deepcopy(previous['optimizer']);
    for group in expected['param_groups']:group['lr']=0.0001
    assert equal(expected,restored['optimizer'])
    expected_safety=copy.deepcopy(previous['safety']);expected_safety['signatures'].pop('ValueError:_find')
    assert equal(expected_safety,restored['safety'])
    (DEST/'previous-evaluation-history.json').write_text(json.dumps(previous['evaluation_history'],indent=2)+'\n')
    receipt=dict(lineage,checkpoint=cp,settings=settings,previous_settings=previous['settings'],preserved_state_verified=True,
                 new_training_games=512,expected_global_games=2920)
    (DEST/'migration.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
    return cp

if __name__=='__main__':main()
