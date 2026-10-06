# Observed local environment

`observed.json` records Python, platform and installed package versions used on this machine. `requirements-observed.txt` contains the exact observed package versions. Its checksum is recorded in the JSON. Neither file contains credentials, local package paths or package download URLs.

From the project root, compare the current interpreter environment without installing anything:

```sh
.venv/bin/python tools/record_environment.py --check
```

The command reports differences and returns a nonzero exit code for drift. Recording refuses to overwrite an existing snapshot; use `--output` with another directory for a new environment.

This is not a cross-platform lockfile: artifact hashes are absent, transitive distribution availability is not guaranteed, and macOS-specific packages may not install elsewhere. A same-platform clean installation and bounded notebook check are now recorded below; cross-platform reproducibility remains unverified. The unpinned `requirements.txt` remains the general setup entry point.

## Project relocation check

The bounded notebook check now passes from a temporary copy containing the project code, notebooks and frozen data. It preserves the candidate's relative data link and starts a new kernel using the selected Python interpreter. It does not reuse the project's saved validation reports, and does not execute training notebooks.

```sh
.venv/bin/python tools/check_relocated_notebook.py --max-actions 3
```

Each run saves an executed notebook and a receipt under `runs/relocation_checks/<unique-id>/`. The receipt records the source notebook hash, engine fingerprint, Python version, action cap and results. The initial check completed 11 intentionally capped games and encoded 33 decisions without errors. Capped games are not completed matches or strength evidence. This relocation harness alone reuses installed dependencies. The fresh-install check below creates a separate environment before invoking it.

## Fresh installation verified on the recorded platform

A new temporary virtual environment installed all 97 versions from `requirements-observed.txt`. Environment comparison matched exactly and `pip check` passed. Notebook 09 then ran in a relocated project using that interpreter: 11 terminal games, no errors/caps and 1,422 feature decisions checked. No training ran.

See `fresh-install-check.json` for hashes, platform, immutable receipt and notebook evidence. The notebook harness still labels its own result as using existing dependencies: the parent fresh-install receipt supplies the separate installation evidence. The original observed snapshot remains unchanged.

Reproduce by creating a new virtual environment with the recorded Python version, installing `environment/requirements-observed.txt`, running `tools/record_environment.py --check` and `python -m pip check`, then invoking `tools/check_relocated_notebook.py --max-actions 500` with the new interpreter. This verifies this platform only, and does not lock downloaded artifact hashes.
