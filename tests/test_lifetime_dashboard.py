"""Presentation-only checks: no models, games or learning."""
import json
import tempfile
import unittest
from pathlib import Path
from tools.lifetime_dashboard import Dashboard, saved_history


def report(game, engine='one', rate=.5):
    return dict(global_game=game, summary=dict(attempted=128,failed=0),
                compatibility=dict(engine=engine,decks_sha256='panel'),seed=1,
                by_opponent={'heuristic':dict(wins=64,draws=0,losses=64,win_rate=rate,
                    score=rate,capped=0,win_rate_wilson95=[.4,.6])})


class LifetimeDashboardTests(unittest.TestCase):
    def test_restores_past_but_not_future_or_failed_reports(self):
        with tempfile.TemporaryDirectory() as root:
            p=Path(root)/'runs/example';p.mkdir(parents=True)
            for game in (208,12550,12614):
                (p/f'evaluation-{game}.json').write_text(json.dumps(report(game)))
            bad=report(300);bad['summary']['failed']=1
            (p/'evaluation-failed.json').write_text(json.dumps(bad))
            self.assertEqual([r['global_game'] for r in saved_history(root,12550)],[208,12550])
            ui=Dashboard(10048,root=root,start_global=12550)
            html=ui.html()
            self.assertIn('12,550 lifetime training games',html)
            self.assertIn('Earliest saved measurement: 208',html)
            ui.consume(dict(event='training_progress',done=64,total=10048,eta_seconds=20))
            self.assertIn('12,614 lifetime training games',ui.html())
            self.assertEqual(ui.saved_global,12550)
            ui.consume(dict(event='iteration_saved',metrics={'optimizer_steps':2}))
            self.assertEqual(ui.saved_global,12614)
            self.assertEqual(len(ui.history),2)

    def test_displays_configured_training_mix(self):
        ui=Dashboard(100,start_global=12550,opponent_mix=dict(current=.6,older=.3,heuristic=.1))
        self.assertIn('60% current self-play · 30% older models · 10% heuristic',ui.html())

    def test_breaks_curves_when_conditions_change_and_escapes(self):
        ui=Dashboard(100,start_global=20)
        ui.history=[report(1),report(2),report(3,engine='changed')]
        chart=ui.chart()
        self.assertEqual(chart.count('fill="none"/>'),1)  # only 1→2 connects
        ui.checkpoint='<script>'
        self.assertNotIn('<script>',ui.html())
        ui.consume(dict(event='started',folder='test',session_start_safety={'attempted':500,'failed':9}))
        self.assertIn('training attempts: 0 · Failures: 0',ui.html())


if __name__=='__main__':unittest.main()
