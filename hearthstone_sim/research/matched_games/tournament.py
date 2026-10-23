"""Same-budget head-to-head cases; saved separately from common-opponent scores."""

from itertools import combinations
import json
import time
from .models import CONTENDERS
from .runner import specification, load_weights, evaluation_schedule, _pool, _task
from .storage import state, atomic_json
from .budget import summarize
from .study import ROOT
from .collection import execute


def tournament(study, decks, milestone, deadline, emit):
    cfg = study["config"]
    out = ROOT / cfg["output"]
    directory = out / "head-to-head" / ("%09d" % milestone)
    for left, right in combinations(CONTENDERS, 2):
        path = directory / (left + "--" + right) / "summary.json"
        if path.exists():
            continue
        lbase = "transformer" if left.endswith("_search") else left
        rbase = "transformer" if right.endswith("_search") else right
        reference = dict(study["reference"], actual_train_seconds=48270.724491532, games=19931)
        ld = (
            reference if lbase == "transformer" else state(out, lbase)["milestones"][str(milestone)]
        )
        rd = (
            reference if rbase == "transformer" else state(out, rbase)["milestones"][str(milestone)]
        )
        learner = specification(lbase, load_weights(ld), ld["sha256"])
        opponent = specification(
            right if right.endswith("_search") else rbase, load_weights(rd), rd["sha256"]
        )
        records = []
        schedule = evaluation_schedule(decks, cfg["evaluation_cases_per_opponent"])
        with _pool(lbase, cfg) as pool:
            for start in range(0, len(schedule), cfg["workers"]):
                tasks = []
                for i, case in enumerate(schedule[start : start + cfg["workers"]], start=start):
                    case_path = path.parent / ("case-%04d.json" % i)
                    if case_path.exists():
                        records.append(json.loads(case_path.read_text()))
                        continue
                    if time.monotonic() >= deadline:
                        return False
                    task = _task(
                        cfg,
                        decks,
                        lbase,
                        learner,
                        opponent,
                        False,
                        i,
                        500000 + i,
                        path.parent / "diagnostics",
                        True,
                        case,
                        left.endswith("_search"),
                    )
                    task["op_search"] = cfg["search"]
                    tasks.append((case_path, task))
                futures = [pool.submit(execute, t) for _, t in tasks]
                for (case_path, task), future in zip(tasks, futures):
                    _, result = future.result()
                    atomic_json(case_path, result)
                    records.append(result)
                    emit(
                        dict(
                            event="head_to_head_case",
                            left=left,
                            right=right,
                            done=len(records),
                            total=len(schedule),
                        )
                    )
        atomic_json(
            path,
            dict(
                left=left,
                right=right,
                milestone_games=milestone,
                left_actual_seconds=ld["actual_train_seconds"],
                right_actual_seconds=rd["actual_train_seconds"],
                summary_from_left=summarize(records),
            ),
        )
    return True
