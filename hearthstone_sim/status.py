"""Coverage and validation state of the active candidate."""
from importlib import import_module
from typing import Any, Dict
from ._bootstrap import activate

def readiness() -> Dict[str, Any]:
    activate()
    return dict(import_module("expanded.status").readiness())

def code_fingerprint() -> str:
    activate()
    return str(import_module("expanded.status").code_fingerprint())
