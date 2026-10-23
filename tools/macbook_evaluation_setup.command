#!/bin/zsh
set -e
cd "${0:A:h}"
PYTHON=python3
if [[ -x /Library/Developer/CommandLineTools/usr/bin/python3 ]]; then
  PYTHON=/Library/Developer/CommandLineTools/usr/bin/python3
fi
if [[ "$("$PYTHON" -c 'import platform; print(platform.python_version())')" != "3.9.6" ]]; then
  echo "This worker needs Python 3.9.6 to match the saved run. Stop here and report the Python version for setup assistance."
  read "?Press Enter to close"
  exit 1
fi
"$PYTHON" -m venv .venv
.venv/bin/python -m pip install "torch==2.8.0" "numpy>=1.24,<2.1"
echo "Setup complete. Run START-EVALUATION.command when ready."
read "?Press Enter to close"
