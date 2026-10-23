"""No training, evaluation games or optimizer updates."""
import ast
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from tools import long_training_campaign as campaign

class CampaignTests(unittest.TestCase):
    def test_stale_lock_file_does_not_block_but_live_lock_does(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'active.lock';path.write_text('12734')
            first=campaign.acquire_campaign_lock(path)
            try:
                with self.assertRaisesRegex(RuntimeError,'launcher is active'):
                    campaign.acquire_campaign_lock(path)
            finally:first.close()
            resumed=campaign.acquire_campaign_lock(path);resumed.close()

    def test_all_eleven_classes_have_valid_fixed_decks(self):
        from hearthstone_sim.neural.decks import load_panel
        decks,_=load_panel(campaign.PANEL)
        self.assertEqual(len(decks),11)
        self.assertEqual(len({d.hero_class for d in decks.values()}),11)
        original,_=load_panel()
        for name,deck in original.items():self.assertEqual(decks[name],deck)

    def test_newest_progress_beats_old_seed_even_with_newer_timestamp(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);pilot=root/'pilot';pilot.mkdir();camp=root/'campaign';seed=root/'seed.pt'
            paths=[seed,pilot/'training-new.pt',pilot/'training-partial.pt']
            for p in paths:p.touch()
            for p in paths[:2]:p.with_suffix('.json').write_text('{}')
            def payload(p):return dict(global_game=2408 if p==seed else 2472,iteration=301 if p==seed else 302,tactical_state=dict(completed=128))
            with patch.multiple(campaign,SEED_CHECKPOINT=seed,PILOT=pilot,CAMPAIGN=camp),patch.object(campaign,'source_payload',side_effect=payload):
                self.assertEqual(campaign.latest_source(),paths[1])

    def test_notebook_source_parses_without_touching_live_outputs(self):
        notebook=json.loads((campaign.ROOT/'notebooks/18_all_class_long_training.ipynb').read_text())
        for c in notebook['cells']:
            if c['cell_type']=='code':
                ast.parse(''.join(c['source']))

    def test_campaign_has_bounded_complete_batches(self):
        self.assertEqual(campaign.TOTAL_GAMES,10048)
        self.assertEqual(campaign.TOTAL_GAMES%64,0)

class HistoryRecoveryTests(unittest.TestCase):
    def test_complete_baseline_after_checkpoint_is_recovered_but_partial_is_not(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);source=root/'model.pt';report=root/'report.json'
            previous=dict(settings=dict(evaluation=dict(games_per_opponent=3)),evaluation_anchors={'anchor':{}},global_game=12,compatibility={'engine':'fixed'},evaluation_history=[])
            item=dict(global_game=12,report=str(report),evaluation_kind='resumed-start')
            (root/'monitoring-history.json').write_text(json.dumps([item]))
            data=dict(compatibility=previous['compatibility'],global_game=12,summary=dict(attempted=6),stopped=None)
            report.write_text(json.dumps(data));self.assertEqual(campaign.reconcile_history(source,previous),[item])
            data['summary']['attempted']=5;report.write_text(json.dumps(data))
            self.assertEqual(campaign.reconcile_history(source,previous),[])
            data['compatibility']={'engine':'wrong'};report.write_text(json.dumps(data))
            with self.assertRaises(ValueError):campaign.reconcile_history(source,previous)

if __name__=='__main__':unittest.main()
