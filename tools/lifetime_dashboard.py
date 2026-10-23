"""Read-only lifetime view over saved evaluation reports and live training events.

Kept outside neural sources: presentation changes do not migrate model checkpoints.
"""
import json
from pathlib import Path
from html import escape
from hearthstone_sim.neural.dashboard import Dashboard as BatchDashboard, duration


def saved_history(root, through):
    """Use complete reports, never cache fragments or future/other-position results."""
    records = {}
    for path in sorted((Path(root) / 'runs').glob('**/evaluation-*.json')):
        try:
            report = json.loads(path.read_text())
            game = report['global_game']
            summary = report['summary']
            if game > through or report.get('stopped') or not report.get('by_opponent'):
                continue
            if summary.get('failed', 0) or not summary.get('attempted'):
                continue
            context = json.dumps([report.get('compatibility', {}).get(k) for k in ('engine', 'decks_sha256')] + [report.get('seed')])
            item = dict(report, report=str(path), context=context)
            records[(game, context)] = item
        except (OSError, ValueError, KeyError, TypeError):
            continue
    return sorted(records.values(), key=lambda r: (r['global_game'], r['report']))


class Dashboard(BatchDashboard):
    def __init__(self, total, *, root=None, start_global=0, session_seconds=7200, opponent_mix=None):
        super().__init__(total)
        self.start_global = start_global
        self.saved_global = start_global
        self.session_seconds = session_seconds
        self.history = saved_history(root, start_global) if root else []
        self.checkpoint = None
        self.deck_count = 176
        self.opponent_mix = opponent_mix

    def consume(self, event):
        # The base display handles current-session counters and failure deltas.
        super().consume(event)
        if event.get('event') == 'evaluation_finished' and event.get('report'):
            try:
                report = json.loads(Path(event['report']).read_text())
                self.history[-1].update(report)
            except (OSError, ValueError):
                pass
        if event.get('event') in ('iteration_saved', 'evaluation_finished', 'complete', 'tactical_finished'):
            # A saved batch contains one scheduled slot per game, including caps.
            self.saved_global = max(self.saved_global, self.start_global + self.done,
                                    event.get('global_game', 0))

    def chart(self):
        if not self.history:
            return '<h3>Lifetime strength</h3><p>No saved evaluation yet. More games do not automatically mean greater strength.</p>'
        colors = ['#2563eb', '#d97706', '#059669', '#9333ea', '#dc2626']
        high = max(1, max(r['global_game'] for r in self.history))
        names = list(dict.fromkeys(n for r in self.history for n in r['by_opponent']))
        svg = ['<svg viewBox="0 0 760 250" role="img" aria-label="Lifetime evaluation win rates from earliest saved measurement" style="width:100%">',
               '<path d="M45 15V210H735" fill="none" stroke="#94a3b8"/>',
               '<path d="M45 112.5H735" stroke="#cbd5e1" stroke-dasharray="4 4"/>',
               '<text x="0" y="24" font-size="12">100%</text><text x="6" y="117" font-size="12">50%</text><text x="12" y="213" font-size="12">0%</text>',
               f'<text x="45" y="240" font-size="12">0 games</text><text x="620" y="240" font-size="12">{high:,} games</text>']
        legends = []
        for i, name in enumerate(names):
            color = colors[i % len(colors)]
            previous = None
            for record in self.history:
                result = record['by_opponent'].get(name)
                if not result or result.get('win_rate') is None:
                    previous = None
                    continue
                compat = record.get('compatibility', {})
                context = (compat.get('engine'), compat.get('decks_sha256'), record.get('seed'))
                x = 45 + 690 * record['global_game'] / high
                y = 210 - 195 * result['win_rate']
                if previous and previous[2] == context:
                    svg.append(f'<path d="M{previous[0]:.1f} {previous[1]:.1f}L{x:.1f} {y:.1f}" stroke="{color}" fill="none"/>')
                svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="{color}"><title>{escape(name)}: {result["win_rate"]:.1%} at {record["global_game"]:,} games</title></circle>')
                previous = (x, y, context)
            legends.append(f'<span style="color:{color};margin-right:16px">● {escape(name)}</span>')
        svg.append('</svg>')
        return '<h3>Lifetime strength · measured wins against saved opponents</h3>' + ''.join(svg) + '<div>' + ''.join(legends) + '</div><p style="font-size:12px">Earliest saved measurement: ' + f'{self.history[0]["global_game"]:,} games. No zero-game baseline is available. Lines break when the engine, deck panel or evaluation seed changes. Older conditions are context, not a controlled comparison. Failed/incomplete evaluations are omitted.</p>'

    def html(self):
        lifetime = max(self.saved_global, self.start_global + self.done)
        time_pct = min(100, 100 * self.elapsed / max(1, self.session_seconds))
        latest = self.history[-1] if self.history else None
        strength = ''
        if latest:
            rows = []
            for name, result in latest['by_opponent'].items():
                rate = result.get('win_rate')
                if rate is not None:
                    rows.append(f'<span style="display:inline-block;margin:6px 18px 6px 0"><b>{rate:.1%}</b> vs {escape(name)}</span>')
            strength = f'<p>Latest strength measurement · game {latest["global_game"]:,}</p><div>' + ''.join(rows) + '</div>'
            tactical = latest.get('tactical_assessment', {})
            if tactical:
                strength += f'<p>Tactical questions ({escape(tactical.get("version", "basic-tactics-v1"))}): {tactical["correct"]}/{tactical["total"]} correct</p>'
        mix = ''
        if self.opponent_mix:
            m = self.opponent_mix
            mix = f'<p>Training opponents: <b>{m["current"]:.0%} current self-play · {m["older"]:.0%} older models · {m["heuristic"]:.0%} heuristic</b></p>'
        hero = f'''<div style="font-family:system-ui;max-width:900px;padding:22px;border-radius:14px;background:#eef7ef;border:1px solid #bbd3be">
<h2 style="margin-top:0">🌳 Your model’s lifetime growth</h2>
<div style="font-size:38px;font-weight:750">{lifetime:,} lifetime training games</div>
<p>Resumed at {self.start_global:,} · {self.done:,} additional games this session · saved through {self.saved_global:,}</p>
<p>176 decks · all 11 classes · 6 learning threads · 4 collectors</p>
{strength}
{mix}
<p><b>{self.session_seconds / 3600:g}-hour session</b> · {duration(self.elapsed)} elapsed / {duration(self.session_seconds)} budget</p>
<progress value="{time_pct}" max="100" style="width:100%"></progress>
<p style="font-size:12px">Game totals track scheduled training slots, including capped games; failed attempts are reported below. They measure experience, not skill. Strength comes from the evaluations. The time limit is soft so in-flight work and checkpoint saving can finish.</p>
</div>'''
        body = super().html().replace('<h3>Hearthstone neural training</h3>', '<h3>Current session activity</h3>')
        body = body.replace('training games (', 'remaining campaign game budget (')
        body = body.replace('<p>Batch engine / inference / PPO seconds:', '<details><summary>Batch timing</summary><p>Batch engine / inference / PPO seconds:').replace('<p>Approximation executions', '</details><p>Approximation executions')
        return hero + body
