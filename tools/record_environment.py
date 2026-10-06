"""Record or compare local Python dependencies; never installs packages.

The snapshot is an observed environment, not a hash-locked distribution bundle
or evidence that a fresh installation has been verified.
"""
import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import re
import sys

ROOT=Path(__file__).resolve().parents[1]


def package_rows(distributions):
    rows={}
    for distribution in distributions:
        name=distribution.metadata['Name'];version=distribution.version
        if not name or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]*',name):
            raise ValueError('Invalid distribution name')
        if not version or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9.!+_-]*',version):
            raise ValueError('Invalid distribution version')
        name=re.sub(r'[-_.]+','-',name).lower()
        if name in rows:raise ValueError('Duplicate normalized distribution: '+name)
        rows[name]=version
    return [dict(name=name,version=rows[name]) for name in sorted(rows)]


def snapshot():
    packages=package_rows(importlib.metadata.distributions())
    pins=''.join(f"{row['name']}=={row['version']}\n" for row in packages)
    report=dict(schema=1,python_version=platform.python_version(),python_implementation=platform.python_implementation(),
                system=platform.system(),machine=platform.machine(),platform=platform.platform(),
                packages=packages,pins_sha256=hashlib.sha256(pins.encode()).hexdigest(),
                fresh_install_verified=False,limitations=['Versions observed locally; package artifact hashes are not captured.',
                'OS-specific packages may not install on another platform.',
                'This does not certify a fresh notebook installation.'])
    return report,pins


def differences(saved,current):
    changes={}
    for key in ('python_version','python_implementation','system','machine','packages'):
        if saved.get(key)!=current.get(key):changes[key]=dict(recorded=saved.get(key),current=current.get(key))
    return changes


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true')
    parser.add_argument('--output',type=Path,default=ROOT/'environment')
    args=parser.parse_args();report,pins=snapshot();out=args.output
    if args.check:
        saved=json.loads((out/'observed.json').read_text())
        raw=(out/'requirements-observed.txt').read_bytes()
        if hashlib.sha256(raw).hexdigest()!=saved['pins_sha256']:raise ValueError('Recorded dependency pins changed')
        delta=differences(saved,report)
        print(json.dumps(dict(matches=not delta,differences=delta)))
        return int(bool(delta))
    out.mkdir(parents=True,exist_ok=True)
    # Explicitly refuse to replace a recorded environment with a different one.
    for name,payload in [('observed.json',json.dumps(report,indent=2)+'\n'),('requirements-observed.txt',pins)]:
        if (out/name).exists():raise FileExistsError(out/name)
    (out/'requirements-observed.txt').write_text(pins)
    (out/'observed.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(path=str(out.resolve()),packages=len(report['packages']),python=report['python_version'],fresh_install_verified=False)))
    return 0

if __name__=='__main__':raise SystemExit(main())
