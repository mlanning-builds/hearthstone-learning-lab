"""Game-matched scoreboards and timing graphs; never runs models or games."""

from pathlib import Path
import json
import html
import base64
from .models import ARMS, CONTENDERS
from .storage import state, atomic_json


def build_report(output):
    out = Path(output)
    study = json.loads((out / "study.json").read_text())
    cfg = study["config"]
    states = {a: state(out, a, verify=False) for a in ARMS}
    rows = []
    for arm, meta in states.items():
        rows.append(
            dict(
                arm=arm,
                games=meta["games"],
                train_seconds=meta["train_seconds"],
                cpu_seconds=meta["cpu_seconds"],
                failed=meta["failed"],
                capped=meta["capped"],
                pending_games=meta.get("pending_games", 0),
                checkpoint=meta["checkpoint"],
                blocked=meta.get("blocked"),
            )
        )
    references = {}
    for arm, folder in [
        ("transformer", "reference-evaluation"),
        ("transformer_search", "reference-search-evaluation"),
    ]:
        p = out / folder / "summary.json"
        references[arm] = json.loads(p.read_text()) if p.exists() else None
    milestones = []
    for games in cfg["milestones_games"]:
        reports = {a: r for a, r in references.items() if r is not None}
        for arm in ARMS:
            p = out / "evaluations" / ("%09d" % games) / arm / "summary.json"
            if p.exists():
                reports[arm] = json.loads(p.read_text())
        complete = len(reports) == len(CONTENDERS)
        matched = complete and all(reports[a]["games"] == games for a in ARMS)
        valid = matched and all(
            r["summary"]["completed"] > 0
            and not r["summary"]["failed"]
            and not r["summary"]["capped"]
            for r in reports.values()
        )
        leader = max(ARMS, key=lambda a: reports[a]["summary"]["score"]) if valid else None
        milestones.append(
            dict(
                games=games,
                complete=complete,
                all_alternative_game_counts_match=matched,
                valid_checkpoint=valid,
                reports=reports,
                provisional_alternative_leader=leader,
                interpretation="Historical reference always has all 19,931 games. Different training histories accepted. Search adds decision-time compute. Single-seed pilot, not an architecture-only causal ranking.",
            )
        )
    report = dict(
        schema="matched-game-results-v1",
        reference=study["reference"],
        arms=rows,
        milestones=milestones,
        single_seed=True,
        scope=cfg["scope"],
        references=references,
        head_to_head=[
            json.loads(p.read_text())
            for p in sorted((out / "head-to-head").glob("*/*/summary.json"))
        ],
    )
    atomic_json(out / "results.json", report)
    from .graphs import render

    png = render(out, states, milestones, references)
    body = [
        '<!doctype html><meta charset="utf-8"><title>Hearthstone matched-game comparison</title><style>body{font:15px system-ui;max-width:1400px;margin:28px auto;color:#172331}table{border-collapse:collapse;width:100%;margin:20px 0}td,th{text-align:left;padding:9px;border-bottom:1px solid #dce3e8}.note{background:#eef5fa;padding:16px}h1{font-size:28px}img{width:100%}</style><h1>Which player learns best from the same number of games?</h1><p class="note">Target: 19,931 completed games per alternative. Graphs at each 1,000 games, plus the final 19,931. Your saved Transformer is preserved, with and without bounded combat look-ahead. Training time is measured rather than matched. Different historical conditions are accepted.</p><table><tr><th>Alternative</th><th>Completed games</th><th>Saved, pending PPO</th><th>Training hours</th><th>Recorded CPU hours</th><th>New errors / caps</th></tr>'
    ]
    for r in rows:
        body.append(
            "<tr><td>%s</td><td>%s / 19,931</td><td>%d</td><td>%.2f</td><td>%.2f</td><td>%d / %d</td></tr>"
            % (
                html.escape(r["arm"]),
                format(r["games"], ","),
                r["pending_games"],
                r["train_seconds"] / 3600,
                r["cpu_seconds"] / 3600,
                r["failed"],
                r["capped"],
            )
        )
    body.append(
        '</table><img alt="Game-matched strength, tactical and time curves" src="data:image/png;base64,'
        + base64.b64encode(png.read_bytes()).decode()
        + '"><p>*The historical time marker is only recovered collection/learning timers; it excludes other work and is not exact lifetime CPU usage. Blank strength curves mean no completed scored checkpoints yet. Shading: 95% win-rate intervals.</p>'
    )
    for m in milestones:
        if not any(a in m["reports"] for a in ARMS):
            continue
        label = (
            "Shared game checkpoint completed"
            if m["valid_checkpoint"]
            else "Incomplete/invalid evaluation: do not rank yet"
        )
        body.append(
            "<h2>%s-game checkpoint</h2><p>%s</p><table><tr><th>Contender</th><th>Training games</th><th>Hours</th><th>Score</th><th>95%% win interval</th><th>Tactics</th><th>Search coverage</th><th>Seconds / action*</th></tr>"
            % (format(m["games"], ","), label)
        )
        for arm, r in m["reports"].items():
            s = r["summary"]
            rate = s["score"]
            interval = s["wilson95"]
            coverage = (
                r["searched_decisions"] / r["search_decisions"] if r["search_decisions"] else 0
            )
            body.append(
                "<tr><td>%s</td><td>%s</td><td>%.2f</td><td>%s</td><td>%s</td><td>%s/%s</td><td>%s</td><td>%.3f</td></tr>"
                % (
                    html.escape(arm),
                    format(r["games"], ","),
                    r["actual_train_seconds"] / 3600,
                    "—" if rate is None else "%.1f%%" % (100 * rate),
                    "—"
                    if interval is None
                    else "%.1f–%.1f%%" % (100 * interval[0], 100 * interval[1]),
                    r["tactics"]["correct"],
                    r["tactics"]["total"],
                    "%.1f%%" % (100 * coverage) if arm == "transformer_search" else "—",
                    r["mean_seconds_per_action"],
                )
            )
        body.append("</table>")
    body.append(
        "<p>*Whole-game elapsed seconds per action includes simulator/opponent work. Raw timing, opponent breakdowns and errors are in results.json. Head-to-head results are collected at the final budget. Equal games measure sample efficiency; hardware scaling is not established by this study.</p>"
    )
    (out / "dashboard.html").write_text("".join(body))
    return report
