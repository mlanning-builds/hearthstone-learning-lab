"""Owner-started all-class campaign. Preparation never runs games or learning."""
import argparse
import fcntl
import copy
import json
import os
import signal
from pathlib import Path
import subprocess
import sys
import uuid
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from hearthstone_sim.neural.checkpoints import load,save,digest
from hearthstone_sim.neural.runner import prepare
from tools.migrate_400_game_checkpoint import equal

PANEL=ROOT/'configs/neural_all_classes.json'
CAMPAIGN=ROOT/'runs/all_class_campaign'
PILOT=ROOT/'runs/neural_ppo/4c5fc45ad8bf4c2a9039e868c597f229'
SEED_CHECKPOINT=ROOT/'runs/neural_migrations/improved-learning-from-2408/training-000301-improved.pt'
PILOT_ENGINE='8a920dccfee769121ccd3e2a9672008085ae02248a769c12aadb6518df28b105'
PILOT_CODE='5ce0329b628eb6869825ee659caa58330303d8fd97c36a5a16067a5764fe444c'
# These exact repaired sources are pinned after non-training checks.
PRE_REPAIR_ENGINE='7ff7d54270d01b72c4317f931b3ec5cc7126d783eb702348c6728240331844df'
PRE_STAGED_ENGINE='6375d2791cba908d5ce8fd134629997807a6841499f1244e96852e4a612b1fc8'
PRE_RESUME_ENGINE='5043618fc78bab850375f87e668e976e1bb7babdc6136310dbfc35f2cc9f3c7d'
PRE_CRAFTED_ENGINE='abafd14451c13506b01d740d512384813cefc03b520f718890e5567caad93f4c'
PRE_RARITY_ENGINE='dfa26c1004d12ef54567496a0844a81459a9cd484e05422655a50d19a2cdf980'
PRE_RUNTIME_BATCH_ENGINE='72948c6cbfc1e8bc3edea4ab3acb492c24c8e5af041d16a3c1d38557440f3c61'
PRE_HEAL_REPAIR_ENGINE='0b0437ea555047bc0321fbfb37c86687d0b6baf47ee470dacb80bd66b6327d14'
APPROVED_ENGINE='df32dbcaa2f132b537bac80c23205e1c214147845dc0211b8d54ad3ff1444c10'
SERIAL_CAMPAIGN_CODE='5ce0329b628eb6869825ee659caa58330303d8fd97c36a5a16067a5764fe444c'
PRE_CACHE_CODE='0b7add806d799c5d05a405ce7b1bc755ebbd2d1f780a38c2806842d8a1534466'
CACHE_CODE='1f9f0bd27eb3fc120b5213013ff7f41ab93126b3665780bc4cfd5fdd3050609e'
BUDGET_CODE='90009e18a44a840ebdd9125b454d7af71da86639650187d2e05d792f36466994'
PRE_STAGED_CODE='7afbe0e08c2bef29198bf146763a71ff9285542d3230491e97c7f9d20882f814'
PRE_EVALUATION_CODE='dfa9fbdfc31e31c93aa98f1de6037dfa533f18e8e32f2ce4bffc70da986666fe'
PRE_LEARNING_CODE='a47bfd3f54b5aa3b2315030a7cafd548fd98442d485f7151b03f9ec6215894ea'
PRE_TACTICAL_CODE='5447a2538f45ea90b065174f8451fb6977a2f491275158fb8e6ef658947a2594'
APPROVED_CODE='f5d85e5cd3861b6c2992140c48de134872465e4b0a3b33cbbe8a286e236cf8d4'
COLLECTION_WORKERS=4
LEARNING_THREADS=6
SESSION_SECONDS=2*60*60
TOTAL_GAMES=10048
CURRENT_SELF_PLAY_FRACTION=0.60
HEURISTIC_FRACTION=0.10


def source_payload(path):
    """Read verified local receipts; accept only the authorized source lineage."""
    receipt=json.loads(path.with_suffix('.json').read_text())
    if digest(path)!=receipt['sha256']:raise ValueError('Checkpoint integrity failure: '+str(path))
    import torch
    header=torch.load(path,map_location='cpu',weights_only=True)
    compat=header['compatibility']
    payload=load(path,compat)
    if payload.get('kind')!='resume':raise ValueError('Not a full resume checkpoint')
    if payload.get('migration',{}).get('kind') not in ('owner-authorized-learning-settings-migration','owner-authorized-all-class-campaign'):
        raise ValueError('Checkpoint outside approved lineage')
    return payload


def latest_source():
    candidates=[SEED_CHECKPOINT]
    candidates+=list(PILOT.glob('training-*.pt'))
    candidates+=list((CAMPAIGN/'training').glob('*/training-*.pt'))
    candidates+=list((CAMPAIGN/'migrations').glob('*/training-*.pt'))
    ranked=[]
    for path in candidates:
        if not path.with_suffix('.json').exists():continue # Incomplete writes cannot be resumed.
        p=source_payload(path)
        ranked.append(((p['global_game'],p['iteration'],p.get('tactical_state',{}).get('completed',0),path.stat().st_mtime_ns),path))
    if not ranked:raise ValueError('No durable checkpoint; refusing to initialize a fresh model')
    return max(ranked)[1]


def reconcile_history(source,previous):
    """Recover a fully completed evaluation saved just after its checkpoint."""
    history_path=source.parent/'monitoring-history.json'
    if not history_path.exists():return previous.get('evaluation_history',[])
    history=json.loads(history_path.read_text());accepted=[]
    # A reviewed source migration preserves old evaluation reports verbatim.
    # Accept only compatibility values on its integrity-verified parent chain.
    allowed=[previous['compatibility']]
    ancestor=previous
    seen=set()
    while ancestor.get('migration',{}).get('parent'):
        parent=Path(ancestor['migration']['parent']).resolve()
        if parent in seen:raise ValueError('Cyclic checkpoint lineage')
        seen.add(parent)
        if len(seen)>64:raise ValueError('Checkpoint lineage too deep')
        if ROOT/'runs' not in parent.parents:raise ValueError('Checkpoint lineage outside local runs')
        if digest(parent)!=ancestor['migration']['parent_sha256']:raise ValueError('Parent checkpoint integrity failure')
        import torch
        ancestor=torch.load(parent,map_location='cpu',weights_only=True)
        allowed.append(ancestor['compatibility'])
    expected=previous['settings']['evaluation']['games_per_opponent']*(1+len(previous.get('evaluation_anchors',{})))
    for item in history:
        if item['global_game']>previous['global_game']:continue
        report=json.loads(Path(item['report']).read_text())
        if report.get('compatibility') not in allowed:raise ValueError('Evaluation history source mismatch')
        if report.get('global_game')!=item['global_game']:raise ValueError('Evaluation history position mismatch')
        if report.get('stopped') or report.get('summary',{}).get('attempted')!=expected:continue
        accepted.append(item)
    return accepted


def retire_reviewed_rarity_failures(safety):
    """Retire six archived missing-rarity errors, retaining totals and other errors.

    All six matching receipts were reviewed before this specific engine migration.
    The handler-level signature is shared: any excess occurrences stay active.
    """
    signature='UnsupportedCard:_choicegen_effect'
    remaining=max(0,safety['signatures'].get(signature,0)-6)
    if remaining:safety['signatures'][signature]=remaining
    else:safety['signatures'].pop(signature,None)


def prepare_campaign():
    source=latest_source();previous=source_payload(source);old=previous['compatibility']
    from hearthstone_sim.neural.deck_continuum import build_panel
    saved_panels=[path for path in (CAMPAIGN/'panels').glob('continuum-*.json') if digest(path)==old['decks_sha256']]
    # This prepared continuation retains the exact existing 176-deck snapshot.
    active_panel=saved_panels[0] if saved_panels else build_panel(PANEL,CAMPAIGN/'panels'/('continuum-%09d.json'%previous['global_game']),previous['global_game'])
    current=prepare(active_panel)[2]
    anchor_hash=prepare(PANEL)[2]['decks_sha256']
    approved_panels={anchor_hash}
    for path in (CAMPAIGN/'panels').glob('continuum-*.json'):
        approved_panels.add(prepare(path)[2]['decks_sha256'])
    if old['decks_sha256'] not in approved_panels:raise ValueError('Checkpoint panel outside approved campaign')
    if (current['engine'],current['neural_code'])!=(APPROVED_ENGINE,APPROVED_CODE):
        raise ValueError('Source changed since campaign approval; review and explicitly migrate before training')
    expected=dict(current,decks_sha256=old['decks_sha256'])
    if old!=current:
        pilot=dict(current,engine=PILOT_ENGINE,neural_code=PILOT_CODE,decks_sha256=prepare()[2]['decks_sha256'])
        serial=dict(expected,engine=PRE_REPAIR_ENGINE,neural_code=SERIAL_CAMPAIGN_CODE)
        parallel=dict(expected,engine=PRE_REPAIR_ENGINE,neural_code=PRE_CACHE_CODE)
        pre_cache=dict(expected,engine=PRE_STAGED_ENGINE,neural_code=PRE_CACHE_CODE)
        cached=dict(expected,engine=PRE_STAGED_ENGINE,neural_code=CACHE_CODE)
        budget=dict(expected,engine=PRE_STAGED_ENGINE,neural_code=BUDGET_CODE)
        staged=dict(expected,engine=PRE_STAGED_ENGINE,neural_code=PRE_STAGED_CODE)
        pre_resume=dict(expected,engine=PRE_RESUME_ENGINE)
        pre_evaluation=dict(expected,neural_code=PRE_EVALUATION_CODE)
        pre_learning=dict(expected,neural_code=PRE_LEARNING_CODE)
        pre_crafted=dict(expected,engine=PRE_CRAFTED_ENGINE,neural_code=PRE_LEARNING_CODE)
        pre_rarity=dict(expected,engine=PRE_RARITY_ENGINE)
        pre_tactical=dict(expected,neural_code=PRE_TACTICAL_CODE)
        pre_runtime_batch=dict(expected,engine=PRE_RUNTIME_BATCH_ENGINE)
        pre_heal_repair=dict(expected,engine=PRE_HEAL_REPAIR_ENGINE)
        if old not in (pilot,serial,parallel,pre_cache,cached,budget,staged,pre_resume,pre_evaluation,pre_learning,pre_crafted,pre_rarity,pre_tactical,pre_runtime_batch,pre_heal_repair,expected):raise ValueError('Unapproved source architecture, engine, encoder or panel')
    CAMPAIGN.mkdir(parents=True,exist_ok=True)
    state_path=CAMPAIGN/'campaign.json'
    if state_path.exists():state=json.loads(state_path.read_text())
    else:
        state=dict(schema='all-class-campaign-v1',start_global=previous['global_game'],target_games=TOTAL_GAMES,panel_sha256=current['decks_sha256'])
        with state_path.open('x') as f:json.dump(state,f,indent=2)
    if state['panel_sha256']!=anchor_hash:raise ValueError('Campaign anchor roster changed')
    remaining=max(0,state['start_global']+state['target_games']-previous['global_game'])
    iterations=(remaining+63)//64
    previous['evaluation_history']=reconcile_history(source,previous) if old['decks_sha256']==current['decks_sha256'] else previous.get('evaluation_history',[])
    # Baseline once for this roster. Existing evaluation history is kept separately.
    # A repaired engine needs one COMPLETE baseline of its own. Repeated
    # preparation must not mistake an ancestor engine's evaluation for that baseline.
    def current_baseline(item):
        path=Path(item.get('report',''))
        if item.get('evaluation_kind') not in ('resumed-start','fresh-start') or not path.is_file():return False
        report=json.loads(path.read_text())
        expected=previous['settings']['evaluation']['games_per_opponent']*(1+len(previous.get('evaluation_anchors',{})))
        return report.get('compatibility',{}).get('engine')==current['engine'] and report.get('compatibility',{}).get('neural_code')==current['neural_code'] and not report.get('stopped') and report.get('summary',{}).get('attempted')==expected
    baseline=not any(current_baseline(item) for item in previous.get('evaluation_history',[]))
    settings=copy.deepcopy(previous['settings'])
    settings.update(self_play_fraction=CURRENT_SELF_PLAY_FRACTION,heuristic_fraction=HEURISTIC_FRACTION,threads=LEARNING_THREADS,collection_workers=COLLECTION_WORKERS,games_per_iteration=64,checkpoint_every_iterations=1,evaluation=dict(every_iterations=16,games_per_opponent=128,seed=1000020000),evaluation_at=[],evaluate_at_start=baseline)
    if old==current and settings==previous['settings']:
        cp=dict(path=str(source),sha256=digest(source))
    else:
        dest=CAMPAIGN/'migrations'/uuid.uuid4().hex;dest.mkdir(parents=True)
        lineage=dict(kind='owner-authorized-all-class-campaign',parent=str(source),parent_sha256=digest(source),old_compatibility=old,compatibility=current,start_global=state['start_global'],training_started=False)
        result=copy.deepcopy(previous);result.update(compatibility=current,settings=settings,migration=lineage)
        if old['decks_sha256']!=current['decks_sha256']:result['evaluation_history']=[]
        mapping={}
        for d in previous['league']+list(previous['evaluation_anchors'].values()):
            if d['name'] in mapping:continue
            payload=load(source.parent/d['name'],old,d['sha256'])
            payload.update(compatibility=current,migration=lineage)
            saved=save(dest/d['name'],payload);mapping[d['name']]=dict(name=d['name'],sha256=saved['sha256'])
        result['league']=[mapping[d['name']] for d in previous['league']]
        result['evaluation_anchors']={n:mapping[d['name']] for n,d in previous['evaluation_anchors'].items()}
        # This specific repaired failure retains its cumulative count, but cannot trip repeat-stop after repair.
        if old!=current:result['evaluation_safety']['signatures'].pop('KeyError:_dormant_trigger_matches',None)
        if old!=current:
            # Preserve cumulative failures and receipts; retire only the repaired
            # PoolRequest encoder signature so it cannot immediately re-stop.
            for name in ('safety','evaluation_safety'):
                result[name]['signatures'].pop('ValueError:visit',None)
                if old['engine']==PRE_RARITY_ENGINE:
                    retire_reviewed_rarity_failures(result[name])
                if old['engine']==PRE_CRAFTED_ENGINE and current['engine']==APPROVED_ENGINE:
                    result[name]['signatures'].pop('UnsupportedCard:_counterfeit_effect',None)
                if old['engine']==PRE_RESUME_ENGINE:
                    for signature in ('UnsupportedCard:_forge_effect','UnsupportedCard:_counterfeit_effect'):
                        result[name]['signatures'].pop(signature,None)
        expected_evaluation_safety=copy.deepcopy(result['evaluation_safety'])
        cp=save(dest/('training-%06d-campaign.pt'%previous['iteration']),result)
        restored=load(cp['path'],current,cp['sha256'])
        for field in ('model','optimizer','action_rng','shuffle_rng','league_rng','global_game','iteration','tactical_state'):
            if field in previous and not equal(previous[field],restored[field]):raise ValueError('Migration changed '+field)
        if not equal(expected_evaluation_safety,restored['evaluation_safety']):raise ValueError('Migration changed evaluation safety state')
        expected_safety=copy.deepcopy(previous['safety'])
        if old['engine']==PRE_RARITY_ENGINE:
            retire_reviewed_rarity_failures(expected_safety)
        if old!=current:expected_safety['signatures'].pop('ValueError:visit',None)
        if old['engine']==PRE_CRAFTED_ENGINE and current['engine']==APPROVED_ENGINE:
            expected_safety['signatures'].pop('UnsupportedCard:_counterfeit_effect',None)
        if old['engine']==PRE_RESUME_ENGINE:
            for signature in ('UnsupportedCard:_forge_effect','UnsupportedCard:_counterfeit_effect'):
                expected_safety['signatures'].pop(signature,None)
        if not equal(expected_safety,restored['safety']):raise ValueError('Migration changed unrelated safety state')
        (dest/'migration.json').write_text(json.dumps(dict(lineage,checkpoint=cp,preserved_state_verified=True),indent=2)+'\n')
    command=[sys.executable,str(ROOT/'tools/train_neural.py'),'--panel',str(active_panel),'--output',str(CAMPAIGN/'training'),'--resume',cp['path'],'--iterations',str(max(1,iterations))]
    flags={'seed':'--seed','games_per_iteration':'--games-per-iteration','max_actions':'--max-actions','device':'--device','threads':'--threads','collection_workers':'--collection-workers','self_play_fraction':'--self-play-fraction','league_size':'--league-size','heuristic_fraction':'--heuristic-fraction','tactical_steps':'--tactical-steps','checkpoint_every_iterations':'--checkpoint-every-iterations','failure_fraction':'--failure-fraction','failure_min_attempts':'--failure-min-attempts','failure_repeats':'--failure-repeats','retry_cap':'--retry-cap','trace_first':'--trace-first','trace_every':'--trace-every'}
    for k,flag in flags.items():command += [flag,str(settings[k])]
    for k in ('learning_rate','epochs','minibatch'):command += ['--'+k.replace('_','-'),str(settings['ppo'][k])]
    for k in ('every_iterations','games_per_opponent','seed'):command += ['--evaluation-'+k.replace('_','-'),str(settings['evaluation'][k])]
    command += ['--evaluate-at-start' if baseline else '--no-evaluate-at-start','--session-seconds',str(SESSION_SECONDS)]
    return dict(command=command,checkpoint=cp,global_game=previous['global_game'],remaining_games=iterations*64,complete=not remaining,baseline=baseline,target_games=state['target_games'],collection_workers=COLLECTION_WORKERS,threads=LEARNING_THREADS,session_seconds=SESSION_SECONDS,panel=str(active_panel),deck_count=176,opponent_mix=dict(current=CURRENT_SELF_PLAY_FRACTION,older=round(1-CURRENT_SELF_PLAY_FRACTION-HEURISTIC_FRACTION,10),heuristic=HEURISTIC_FRACTION))


def acquire_campaign_lock(path):
    """OS-owned lock releases even if Jupyter kills the launcher abruptly."""
    stream=Path(path).open('a+')
    try:
        fcntl.flock(stream.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
    except BlockingIOError:
        stream.close()
        raise RuntimeError('Another campaign launcher is active')
    stream.seek(0);stream.truncate();stream.write(str(os.getpid()));stream.flush()
    return stream


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--train',action='store_true');args=parser.parse_args()
    # Prevent overlapping owner-started runs, including the existing pilot.
    if args.train:
        processes=subprocess.check_output(['ps','-axo','args='],text=True)
        if any(any(tool in line for tool in ('tools/train_neural.py','tools/run_architecture_comparison.py')) and '--train' in line for line in processes.splitlines()):
            raise RuntimeError('Another training run is active. Let it finish before starting this campaign.')
    plan=prepare_campaign();print(json.dumps(dict(event='campaign_ready',**{k:v for k,v in plan.items() if k!='command'})),flush=True)
    if plan['complete']:return
    if not args.train:
        subprocess.run(plan['command']+['--preflight'],cwd=ROOT,check=True);return
    # Exclusive lock prevents two campaign launches racing each other.
    lock=acquire_campaign_lock(CAMPAIGN/'active.lock')
    child=None
    def stop(signum,frame):
        if child is not None:child.terminate()
        raise KeyboardInterrupt('Owner interrupted campaign')
    old_handler=signal.signal(signal.SIGTERM,stop)
    try:
        child=subprocess.Popen(plan['command']+['--train'],cwd=ROOT)
        code=child.wait()
        if code:raise subprocess.CalledProcessError(code,child.args)
    finally:
        signal.signal(signal.SIGTERM,old_handler)
        if child is not None and child.poll() is None:
            child.terminate()
            try:child.wait(timeout=10)
            except subprocess.TimeoutExpired:child.kill();child.wait()
        lock.close()

if __name__=='__main__':main()
