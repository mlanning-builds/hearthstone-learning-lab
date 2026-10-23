"""Check tracked publication artifacts; never runs notebooks or learning."""
import json
from pathlib import Path
import re
import subprocess


def main():
    root = Path(__file__).resolve().parents[1]
    tracked = subprocess.check_output(
        ['git', 'ls-files', '-z'], cwd=root
    ).decode().split('\0')
    errors = []
    for name in filter(None, tracked):
        path = root / name
        if not path.is_file():
            continue
        if path.suffix in {'.pt', '.pth', '.pem', '.key'} or 'runs' in Path(name).parts:
            errors.append(name + ': private/runtime artifact')
        if path.suffix != '.ipynb':
            continue
        notebook = json.loads(path.read_text())
        for cell in notebook['cells']:
            if cell['cell_type'] == 'code' and (
                cell.get('outputs') or cell.get('execution_count') is not None
            ):
                errors.append(name + ': executed notebook output')
        # Match a concrete macOS home, rather than documentation examples.
        if re.search(r'/Users/[^/\s]+/', path.read_text()):
            errors.append(name + ': machine-specific home path')
    if errors:
        raise SystemExit('\n'.join(errors))
    print('Tracked notebooks are clean; runtime artifacts remain local.')


if __name__ == '__main__':
    main()
