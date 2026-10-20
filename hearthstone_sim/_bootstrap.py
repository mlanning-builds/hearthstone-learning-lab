"""Select the active checkout without replacing already-loaded legacy modules."""
from importlib import import_module
from pathlib import Path
import sys
from types import ModuleType

CANDIDATE_ROOT = Path(__file__).resolve().parents[1] / "staging" / "rebased-88"

def activate() -> ModuleType:
    """Reject mixed engines, then load the current candidate implementation."""
    if not (CANDIDATE_ROOT / "expanded" / "game.py").is_file():
        raise RuntimeError("Use an editable installation with the complete repository checkout.")
    for name, module in list(sys.modules.items()):
        if name.split(".")[0] not in {"expanded", "engine", "standard", "lab"}:
            continue
        filename = getattr(module, "__file__", None)
        if filename is not None:
            try:
                Path(filename).resolve().relative_to(CANDIDATE_ROOT.resolve())
            except ValueError as exc:
                raise RuntimeError(
                    f"{name} is already loaded from another simulator. "
                    "Restart the notebook kernel or use a fresh process before importing hearthstone_sim."
                ) from exc
    candidate = str(CANDIDATE_ROOT)
    if candidate in sys.path:
        sys.path.remove(candidate)
    sys.path.insert(0, candidate)
    return import_module("expanded")
