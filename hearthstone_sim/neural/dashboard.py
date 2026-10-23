"""Pure HTML/SVG progress display for Jupyter; importing starts no work."""

from html import escape


def duration(seconds):
    if seconds is None:
        return "—"
    seconds = max(0, int(seconds))
    return f"{seconds // 3600:d}h {(seconds % 3600) // 60:02d}m {seconds % 60:02d}s"


class Dashboard:
    def __init__(self, total):
        self.total = total
        self.done = 0
        self.capped = 0
        self.completed = 0
        self.updates = 0
        self.status = "Ready — not started"
        self.elapsed = 0
        self.eta = None
        self.checkpoint = None
        self.folder = None
        self.history = []
        self.safety = {}
        self.timing = {}
        self.evaluation_safety = {}
        self.session_start_safety = {}
        self.session_start_evaluation_safety = {}

    def consume(self, event):
        kind = event.get("event")
        self.safety = event.get("safety", self.safety)
        self.timing = event.get("timing", self.timing)
        self.evaluation_safety = event.get("evaluation_safety", self.evaluation_safety)
        if kind == "stopped":
            self.status = "Stopped: " + event["reason"] + " · " + event["failures"]
        self.elapsed = event.get("elapsed_seconds", self.elapsed)
        if kind == "started":
            self.session_start_safety = dict(event.get("session_start_safety", {}))
            self.session_start_evaluation_safety = dict(
                event.get("session_start_evaluation_safety", {})
            )
            self.safety = dict(self.session_start_safety)
            self.evaluation_safety = dict(self.session_start_evaluation_safety)
            self.folder = event["folder"]
            self.status = "Starting"
        elif kind == "tactical_progress":
            self.status = (
                f"Tactical lessons: {event['done']}/{event['total']} — supervised learning"
            )
        elif kind == "tactical_finished":
            self.checkpoint = event["checkpoint"]["path"]
            self.status = "Tactical lessons saved; starting PPO"
        elif kind == "game_started":
            self.status = "Playing: " + event["learner_deck"] + " vs " + event["opponent_deck"]
        elif kind == "game_finished":
            self.capped += int(event["truncated"])
            self.completed += int(event["terminated"])
        elif kind == "training_progress":
            self.done = event["done"]
            self.total = event["total"]
            self.eta = event["eta_seconds"]
            self.status = "Collecting games"
        elif kind == "iteration_saved":
            self.updates += event["metrics"]["optimizer_steps"]
            if event.get("checkpoint"):
                self.checkpoint = event["checkpoint"]["path"]
            self.status = "PPO batch finished"
        elif kind == "evaluation_started":
            self.status = "Evaluating — no learning"
        elif kind == "evaluation_game":
            self.status = (
                f"Evaluating {event['opponent']}: {event['done']}/{event['total']} — no learning"
            )
        elif kind == "evaluation_finished":
            if event.get("checkpoint"):
                self.checkpoint = event["checkpoint"]["path"]
            self.history = [r for r in self.history if r["global_game"] != event["global_game"]]
            self.history.append(event)
            self.status = "Evaluation saved: " + event.get("evaluation_kind", "monitoring")
        elif kind == "complete":
            self.checkpoint = event["checkpoint"]["path"]
            self.status = "Run completed"
            self.eta = 0

    def chart(self):
        if not self.history:
            return "<p>Strength chart appears after the first evaluation. Training activity alone is not a strength measurement.</p>"
        names = list(self.history[-1]["by_opponent"])
        low = min(r["global_game"] for r in self.history)
        high = max(r["global_game"] for r in self.history)
        colors = ["#2563eb", "#d97706", "#059669", "#9333ea"]
        svg = [
            '<svg viewBox="0 0 680 220" role="img" aria-label="Evaluation score over training games" style="width:100%;max-width:800px">',
            '<path d="M40 15V185H660" fill="none" stroke="#94a3b8"/>',
            '<text x="5" y="22" font-size="12">1.0</text><text x="5" y="188" font-size="12">0.0</text>',
            f'<text x="40" y="212" font-size="12">{low} games</text><text x="570" y="212" font-size="12">{high} games</text>',
        ]
        legend = []
        for i, name in enumerate(names):
            color = colors[i % len(colors)]
            points = []
            for r in self.history:
                score = r["by_opponent"].get(name, {}).get("score")
                if score is not None:
                    x = 40 + 620 * (r["global_game"] - low) / max(1, high - low)
                    y = 185 - 170 * score
                    points.append(f"{x:.1f},{y:.1f}")
                    svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="{color}"/>')
            if points:
                svg.append(
                    f'<polyline points="{" ".join(points)}" fill="none" stroke="{color}" stroke-width="2"/>'
                )
            legend.append(f'<span style="color:{color};margin-right:15px">● {escape(name)}</span>')
        svg.append("</svg>")
        return (
            "<h4>Evaluation score (win = 1, draw = ½, loss = 0)</h4>"
            + "".join(svg)
            + "<div>"
            + "".join(legend)
            + "</div>"
        )

    def html(self):
        pct = 100 * self.done / max(1, self.total)
        rows = []
        if self.history:
            for name, r in self.history[-1]["by_opponent"].items():
                interval = r["win_rate_wilson95"]
                rate = "—" if r["win_rate"] is None else f"{r['win_rate']:.1%}"
                ci = "—" if interval is None else f"{interval[0]:.1%}–{interval[1]:.1%}"
                rows.append(
                    f"<tr><td>{escape(name)}</td><td>{r['wins']} / {r['draws']} / {r['losses']}</td><td>{rate} ({ci})</td><td>{r['capped']}</td></tr>"
                )
        table = (
            '<table style="width:100%;text-align:left"><tr><th>Fixed opponent</th><th>W / D / L</th><th>Win rate (95% interval)</th><th>Caps</th></tr>'
            + "".join(rows)
            + "</table>"
            if rows
            else ""
        )
        deck_rows = []
        if self.history:
            for name, r in self.history[-1].get("by_deck", {}).items():
                score = "—" if r["score"] is None else f"{r['score']:.1%}"
                interval = r["win_rate_wilson95"]
                ci = "—" if interval is None else f"{interval[0]:.1%}–{interval[1]:.1%}"
                deck_rows.append(
                    f"<tr><td>{escape(name)}</td><td>{r['wins']} / {r['draws']} / {r['losses']}</td><td>{score}</td><td>{ci}</td></tr>"
                )
        deck_table = (
            (
                '<h4>Deck + pilot on this evaluation panel</h4><table style="width:100%;text-align:left"><tr><th>Deck</th><th>W / D / L</th><th>Score</th><th>Win-rate interval</th></tr>'
                + "".join(deck_rows)
                + '</table><p style="font-size:12px">These results combine this pilot with each deck; they are not a ranking of intrinsic deck strength.</p>'
            )
            if deck_rows
            else ""
        )
        return f'''<div style="font-family:system-ui;padding:18px;border:1px solid #cbd5e1;border-radius:12px;max-width:900px">
<h3>Hearthstone neural training</h3><p>{escape(self.status)}</p>
<progress value="{self.done}" max="{self.total}" style="width:100%"></progress>
<p><b>{self.done:,} / {self.total:,} training games ({pct:.1f}%)</b> · {self.completed:,} finished · {self.capped:,} capped · {self.updates:,} PPO updates</p>
<p>Elapsed: {duration(self.elapsed)} · Rough time remaining: {duration(self.eta)}</p>
<p>This run — training attempts: {self.safety.get("attempted", 0) - self.session_start_safety.get("attempted", 0)} · Failures: {self.safety.get("failed", 0) - self.session_start_safety.get("failed", 0)}</p>
<p>This run — evaluation attempts / failures: {self.evaluation_safety.get("attempted", 0) - self.session_start_evaluation_safety.get("attempted", 0)} / {self.evaluation_safety.get("failed", 0) - self.session_start_evaluation_safety.get("failed", 0)}</p>
<p>Batch engine / inference / PPO seconds: {escape(str(self.timing))}</p>
<p>Approximation executions by learner deck: {escape(str(self.safety.get("approximations", {})))}</p>
<p>Approximation card-use proxies (not executions): {escape(str(self.safety.get("approximation_proxies", {})))}</p>
{self.chart()}{table}{deck_table}
<p style="font-size:12px">Evaluation games are separate and never update weights. Caps are excluded from win rates. Intervals are approximate for this fixed matchup panel. These opponents are baselines, not expert players.</p>
<p>Latest durable checkpoint: <code>{escape(self.checkpoint or "No new checkpoint yet")}</code></p>
</div>'''
