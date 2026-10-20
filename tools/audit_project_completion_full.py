"""Rebuild the non-training static completion audit; writes docs only."""
from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
runpy.run_path(str(root/'tools/audit_project_source_limits.py'),run_name='__main__')
runpy.run_path(str(root/'tools/audit_project_cast_admission.py'),run_name='__main__')
