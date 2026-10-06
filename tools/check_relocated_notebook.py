"""Execute bounded notebook 09 validation from an isolated temporary project copy.

Uses already installed notebook dependencies. This is a relocation check, not a
fresh-install check, and never executes training notebooks.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import uuid

ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--max-actions',type=int,default=3)
    args=parser.parse_args()
    if not 1<=args.max_actions<=500:parser.error('Use 1..500 actions per game')
    import nbformat
    from nbclient import NotebookClient
    from jupyter_client import KernelManager
    from jupyter_client.kernelspec import KernelSpecManager
    notebook_path=ROOT/'notebooks/09_candidate_random_validation.ipynb'
    source=notebook_path.read_bytes()
    with tempfile.TemporaryDirectory(prefix='hearthstone-relocation-') as temporary:
        temporary=Path(temporary);project=temporary/'project';project.mkdir()
        ignore=shutil.ignore_patterns('__pycache__','runs','.ipynb_checkpoints','.DS_Store')
        for name in ('data','tools','notebooks','expanded','engine','standard'):
            shutil.copytree(ROOT/name,project/name,ignore=ignore,symlinks=True)
        candidate=project/'staging/rebased-88'
        shutil.copytree(ROOT/'staging/rebased-88',candidate,ignore=ignore,symlinks=True)
        if (candidate/'data').resolve()!=(project/'data').resolve():raise AssertionError('Candidate data link escaped copied project')
        kernels=temporary/'kernels';spec=kernels/'relocation-check';spec.mkdir(parents=True)
        (spec/'kernel.json').write_text(json.dumps(dict(argv=[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}'],display_name='Relocation check',language='python')))
        notebook=nbformat.reads(source.decode(),as_version=4)
        # Override only the explicit budget in the copied notebook.
        settings=notebook.cells[1].source
        marker='MAX_ACTIONS_PER_GAME = 500'
        if settings.count(marker)!=1:raise ValueError('Notebook budget cell changed; review harness')
        notebook.cells[1].source=settings.replace(marker,f'MAX_ACTIONS_PER_GAME = {args.max_actions}')
        manager=KernelManager(kernel_name='relocation-check',kernel_spec_manager=KernelSpecManager(kernel_dirs=[str(kernels)]))
        client=NotebookClient(notebook,km=manager,timeout=120,resources={'metadata':{'path':str(project/'notebooks')}})
        try:client.execute()
        finally:
            if manager.has_kernel:manager.shutdown_kernel(now=True)
        report=json.loads((candidate/'runs/random_validation/summary.json').read_text())
        if report['games']!=11 or report['errors'] or report['feature_decisions_checked']<11:
            raise AssertionError('Relocated notebook failed bounded validation')
        receipt=dict(schema=1,notebook_sha256=hashlib.sha256(source).hexdigest(),engine_fingerprint=report['fingerprint'],
                     python=sys.version,uses_existing_dependencies=True,fresh_install_verified=False,
                     scope='Copied project layout and notebook 09 execution only; no training or full Standard certification.',
                     games=report['games'],terminal=report['terminal'],capped=report['capped'],errors=report['errors'],
                     max_actions=args.max_actions,feature_decisions_checked=report['feature_decisions_checked'])
        out=ROOT/'runs/relocation_checks'/uuid.uuid4().hex;out.mkdir(parents=True)
        nbformat.write(notebook,out/'executed.ipynb')
        (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
        print(json.dumps(dict(receipt=str(out/'receipt.json'),**receipt)))
    return 0

if __name__=='__main__':raise SystemExit(main())
