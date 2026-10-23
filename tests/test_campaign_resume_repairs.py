"""Applied source checks; no games, model updates or live source changes."""
import importlib.util
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest

ROOT=Path(__file__).resolve().parents[1]
STAGE=ROOT
sys.path.insert(0,str(ROOT))
from hearthstone_sim.neural.runner import prepare
prepare()

def module(name,path):
    spec=importlib.util.spec_from_file_location(name,STAGE/path)
    result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result)
    return result

effects=module('expanded._prepared_batch_effects','staging/rebased-88/expanded/batch_effects.py')
casting=module('expanded._prepared_spell_casting','staging/rebased-88/expanded/spell_casting.py')
Dashboard=module('_prepared_dashboard','hearthstone_sim/neural/dashboard.py').Dashboard

class PreparedChecks(unittest.TestCase):
    def test_hero_targets_include_both_heroes_and_exclude_minions(self):
        from types import MethodType
        sys.path.insert(0,str(ROOT/'staging/rebased-88/tests'))
        from test_expanded_generation import GenerationTests
        from engine.game import Card
        staged_game=module('expanded._prepared_game','staging/rebased-88/expanded/game.py')
        g=GenerationTests().game()
        g._unrestricted_targets_for=MethodType(staged_game.Game._unrestricted_targets_for,g)
        g._summon(0,'CORE_CS2_179');g._summon(1,'CORE_CS2_179')
        for owner in (0,1):self.assertEqual(set(g._targets_for('EX1_561',owner)),{-1,-2})
        g.players[g.current].hand=[Card(g._new_id(),'EX1_561')]
        g.players[g.current].mana=10
        actions=[a for a in g.legal_actions() if a.kind=='play']
        self.assertTrue(actions)
        self.assertEqual({a.target for a in actions},{-1,-2})

    def test_portal_internal_cast_consumes_card_and_runs_existing_effect(self):
        from types import MethodType
        from unittest.mock import patch
        sys.path.insert(0,str(ROOT/'staging/rebased-88/tests'))
        from test_expanded_generation import GenerationTests
        from engine.game import Card
        g=GenerationTests().game()
        g._supports_internal_operations=MethodType(casting.SpellCasting._supports_internal_operations,g)
        g._supports_internal_spell=MethodType(casting.SpellCasting._supports_internal_spell,g)
        self.assertTrue(g._supports_internal_spell('EDR_445pt3',0))
        self.assertFalse(g._supports_internal_operations((('unknown_fake_effect',),)))
        portal=Card(g._new_id(),'EDR_445pt3');g.players[0].deck=[portal]
        g.players[0].imbue_count=3
        with patch.object(g,'_generation_candidates',return_value=['CORE_CS2_179']) as candidates:
            g._start_play_effects([('cast_zone_spell','deck',portal.uid,'random')],dict(owner=0,source=None,target=0,bonus=0,lifesteal=False))
            g._settle()
        self.assertNotIn(portal,g.players[0].deck)
        self.assertEqual(len(g.players[0].board),1)
        request=candidates.call_args.args[0]
        self.assertEqual((request.card_type,request.tribe,request.minimum,request.maximum),('MINION','DRAGON',3,3))

    def test_fire_destroy_live_departed_and_inactive(self):
        a=SimpleNamespace(uid=1,health=4);b=SimpleNamespace(uid=2,health=6)
        g=SimpleNamespace(players=[SimpleNamespace(fire_spell_played=True,minions=[a]),SimpleNamespace(minions=[b])])
        for uid in (0,999):effects.BatchEffects._batch_effect(g,('fire_turn_destroy',),dict(owner=0,target=uid))
        self.assertEqual((a.health,b.health),(4,6))
        effects.BatchEffects._batch_effect(g,('fire_turn_destroy',),dict(owner=0,target=2))
        self.assertEqual(b.health,0)
        g.players[0].fire_spell_played=False
        effects.BatchEffects._batch_effect(g,('fire_turn_destroy',),dict(owner=0,target=1))
        self.assertEqual(a.health,4)

    def test_only_current_run_failures_are_shown(self):
        d=Dashboard(100)
        d.consume(dict(event='started',folder='fixture',session_start_safety=dict(attempted=4000,failed=11),session_start_evaluation_safety=dict(attempted=3500,failed=11)))
        self.assertIn('training attempts: 0 · Failures: 0',d.html())
        d.consume(dict(event='training_progress',done=64,total=100,eta_seconds=1,safety=dict(attempted=4065,failed=12)))
        self.assertIn('training attempts: 65 · Failures: 1',d.html())
        self.assertNotIn('All sessions',d.html())
        self.assertNotIn('training attempts: 4065',d.html())
        self.assertIn('evaluation attempts / failures: 0 / 0',d.html())

if __name__=='__main__':unittest.main()
